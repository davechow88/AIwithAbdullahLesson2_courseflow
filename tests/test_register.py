import http.client
import json
import unittest
from datetime import date, timedelta
import store
from rules import validate_trainee
from helpers import TempDatabase, TempServer

# worked out when the tests run, so VALID never becomes a past date
NEXT_YEAR = (date.today() + timedelta(days=365)).isoformat()
VALID = {'name': 'Test Person', 'course': 'Access Control', 'expires_on': NEXT_YEAR}  # an existing course
FIXED_TODAY = date(2026, 10, 15)

class ValidationTests(unittest.TestCase):
    def test_valid_data_is_accepted_and_trimmed(self):
        clean, errors = validate_trainee({'name': '  Test Person ', 'course': ' Access Control ', 'expires_on': NEXT_YEAR})
        self.assertEqual(errors, {})
        self.assertEqual(clean, VALID)

    def test_blank_name_rejected(self):
        for blank in ('', '   '):
            with self.subTest(name=blank):
                self.assertEqual(validate_trainee({**VALID, 'name': blank})[1], {'name': 'is required'})

    def test_blank_course_rejected(self):
        self.assertEqual(validate_trainee({**VALID, 'course': '  '})[1], {'course': 'is required'})

    def test_missing_name_rejected(self):
        data = {'course': 'Fire Safety', 'expires_on': None}
        self.assertEqual(validate_trainee(data)[1], {'name': 'is required'})

    def test_non_text_name_rejected(self):
        self.assertEqual(validate_trainee({**VALID, 'name': 123})[1], {'name': 'must be text'})

    def test_name_longer_than_100_characters_rejected(self):
        self.assertEqual(validate_trainee({**VALID, 'name': 'x' * 100})[1], {})
        self.assertIn('name', validate_trainee({**VALID, 'name': 'x' * 101})[1])

    def test_null_or_missing_expiry_means_no_expiry(self):
        for data in ({**VALID, 'expires_on': None}, {'name': 'Test Person', 'course': 'Fire Safety'}):
            with self.subTest(data=data):
                clean, errors = validate_trainee(data)
                self.assertEqual(errors, {})
                self.assertIsNone(clean['expires_on'])

    def test_invalid_expiry_rejected(self):
        for bad in ('2026-02-30', '2026-13-01', '18/10/2026', '20261018', '', 123):
            with self.subTest(expires_on=bad):
                self.assertIn('expires_on', validate_trainee({**VALID, 'expires_on': bad})[1])

    def test_past_expiry_rejected(self):
        errors = validate_trainee({**VALID, 'expires_on': '2026-10-14'}, today=FIXED_TODAY)[1]
        self.assertEqual(errors, {'expires_on': 'must be today or later'})

    def test_today_expiry_accepted(self):
        self.assertEqual(validate_trainee({**VALID, 'expires_on': '2026-10-15'}, today=FIXED_TODAY)[1], {})

    def test_future_expiry_accepted(self):
        self.assertEqual(validate_trainee({**VALID, 'expires_on': '2026-10-16'}, today=FIXED_TODAY)[1], {})

class StoreAddTests(TempDatabase):
    def test_add_returns_record_with_new_id(self):
        row = store.add_trainee('Test Person', 'Fire Safety', None)
        self.assertEqual(row, {'id': 6, 'name': 'Test Person', 'course': 'Fire Safety', 'expires_on': None})

    def test_added_trainee_is_saved(self):
        store.add_trainee('Test Person', 'Fire Safety', '2027-01-31')
        rows = store.read_trainees()
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[-1]['name'], 'Test Person')
        self.assertEqual([row['name'] for row in store.read_trainees('fire')], ['Test Person'])

class ApiRegisterTests(TempServer):
    """Real HTTP requests to a test server on a free port, using the temporary database."""
    def post(self, data):
        return self.request('/api/trainees', 'POST', json.dumps(data).encode())

    def trainee_count(self):
        return len(self.request('/api/trainees')[1]['trainees'])

    def test_valid_post_returns_201_with_id(self):
        status, row = self.post({**VALID, 'name': '  Test Person  '})
        self.assertEqual(status, 201)
        self.assertIsInstance(row['id'], int)
        self.assertEqual(row['name'], 'Test Person')
        self.assertIn('renewal_soon', row)

    def test_saved_trainee_appears_in_later_get(self):
        _, row = self.post(VALID)
        status, data = self.request('/api/trainees')
        self.assertEqual(status, 200)
        self.assertEqual(len(data['trainees']), 6)
        self.assertIn(row, data['trainees'])

    def test_new_trainee_gets_renewal_badge(self):
        soon = (date.today() + timedelta(days=10)).isoformat()
        _, row = self.post({**VALID, 'expires_on': soon})
        self.assertTrue(row['renewal_soon'])

    def test_null_expiry_returns_201(self):
        status, row = self.post({**VALID, 'expires_on': None})
        self.assertEqual(status, 201)
        self.assertIsNone(row['expires_on'])

    def test_blank_name_returns_400_and_saves_nothing(self):
        status, data = self.post({**VALID, 'name': '   '})
        self.assertEqual(status, 400)
        self.assertEqual(data, {'error': 'invalid_fields', 'fields': {'name': 'is required'}})
        self.assertEqual(self.trainee_count(), 5)

    def test_invalid_expiry_returns_400(self):
        status, data = self.post({**VALID, 'expires_on': '2026-13-01'})
        self.assertEqual(status, 400)
        self.assertIn('expires_on', data['fields'])
        self.assertEqual(self.trainee_count(), 5)

    def test_past_expiry_returns_400_and_saves_nothing(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        status, data = self.post({**VALID, 'expires_on': yesterday})
        self.assertEqual(status, 400)
        self.assertEqual(data['fields'], {'expires_on': 'must be today or later'})
        self.assertEqual(self.trainee_count(), 5)

    def test_today_expiry_returns_201(self):
        status, row = self.post({**VALID, 'expires_on': date.today().isoformat()})
        self.assertEqual(status, 201)
        self.assertTrue(row['renewal_soon'])  # 0 days left still counts as renewal soon

    def test_broken_json_returns_400(self):
        status, data = self.request('/api/trainees', 'POST', b'{not json')
        self.assertEqual((status, data), (400, {'error': 'invalid_json'}))

    def test_json_that_is_not_an_object_returns_400(self):
        status, data = self.request('/api/trainees', 'POST', b'[]')
        self.assertEqual((status, data), (400, {'error': 'invalid_json'}))

    def test_post_to_other_path_returns_404(self):
        status, _ = self.request('/api/other', 'POST', json.dumps(VALID).encode())
        self.assertEqual(status, 404)

    def raw_post_status(self, content_length):
        """POST with only a Content-Length header and no body, to test the size checks."""
        conn = http.client.HTTPConnection('127.0.0.1', self.httpd.server_address[1])
        self.addCleanup(conn.close)
        conn.putrequest('POST', '/api/trainees')
        conn.putheader('Content-Length', content_length)
        conn.endheaders()
        with conn.getresponse() as res:
            return res.status

    def test_too_large_body_returns_413(self):
        self.assertEqual(self.raw_post_status('20000'), 413)

    def test_negative_content_length_returns_400(self):
        self.assertEqual(self.raw_post_status('-1'), 400)

if __name__ == '__main__':
    unittest.main()
