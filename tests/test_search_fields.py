import unittest
from datetime import date, timedelta
from rules import matches_search
from helpers import TempServer

def row(name='Alex Tan', course='Security Refresher', expires_on='2026-11-12', renewal_soon=True):
    return {'id': 1, 'name': name, 'course': course, 'expires_on': expires_on, 'renewal_soon': renewal_soon}

class MatchesSearchTests(unittest.TestCase):
    def test_participant(self):
        self.assertTrue(matches_search(row(), 'alex'))

    def test_course(self):
        self.assertTrue(matches_search(row(), 'refresher'))

    def test_expiry_date_partial(self):
        self.assertTrue(matches_search(row(), '2026-11'))
        self.assertFalse(matches_search(row(), '2026-12'))

    def test_missing_expiry_matches_unknown(self):
        self.assertTrue(matches_search(row(expires_on=None), 'unknown'))
        self.assertFalse(matches_search(row(), 'unknown'))

    def test_status(self):
        soon, not_soon = row(renewal_soon=True), row(renewal_soon=False)
        self.assertTrue(matches_search(soon, 'soon'))
        self.assertFalse(matches_search(not_soon, 'soon'))
        self.assertTrue(matches_search(not_soon, 'upcoming'))
        self.assertFalse(matches_search(soon, 'upcoming'))

    def test_case_insensitive(self):
        self.assertTrue(matches_search(row(), 'ALEX'))
        self.assertTrue(matches_search(row(), 'rEnEwAl SoOn'))

    def test_no_match(self):
        self.assertFalse(matches_search(row(), 'zzz'))

class ApiSearchFieldsTests(TempServer):
    """Real HTTP requests to a test server, using a temporary database with the 5 starting trainees."""
    def names(self, query):
        status, data = self.request('/api/trainees' + query)
        self.assertEqual(status, 200)
        return [r['name'] for r in data['trainees']]

    def test_search_by_participant(self):
        self.assertEqual(self.names('?q=alex'), ['Alex Tan'])

    def test_search_by_course(self):
        self.assertEqual(self.names('?q=security'), ['Alex Tan', 'Priya Shah'])

    def test_search_by_expiry_date(self):
        alex_expiry = (date.today() + timedelta(days=25)).isoformat()  # how the starting data sets it
        self.assertEqual(self.names('?q=' + alex_expiry), ['Alex Tan'])

    def test_search_unknown_expiry(self):
        self.assertEqual(self.names('?q=unknown'), ['Jamie Wong'])

    def test_search_by_status(self):
        self.assertEqual(self.names('?q=renewal%20soon'), ['Alex Tan', 'Noor Ahmad'])
        self.assertEqual(self.names('?q=no%20upcoming'), ['Mei Lim', 'Jamie Wong', 'Priya Shah'])

    def test_no_match_returns_empty_list(self):
        self.assertEqual(self.names('?q=zzz'), [])

    def test_empty_search_returns_all(self):
        self.assertEqual(len(self.names('?q=')), 5)

    def test_course_and_q_together(self):
        self.assertEqual(self.names('?course=refresher&q=priya'), ['Priya Shah'])

if __name__ == '__main__':
    unittest.main()
