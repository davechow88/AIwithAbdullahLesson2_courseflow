import unittest
import store
from helpers import TempDatabase, TempServer

REFRESHER_NAMES = ['Alex Tan', 'Priya Shah']

def names(rows):
    return [row['name'] for row in rows]

class StoreSearchTests(TempDatabase):
    def test_no_filter_returns_all(self):
        self.assertEqual(len(store.read_trainees()), 5)

    def test_partial_match(self):
        self.assertEqual(names(store.read_trainees('refresher')), REFRESHER_NAMES)

    def test_case_insensitive(self):
        for term in ('REFRESHER', 'rEfReShEr'):
            with self.subTest(term=term):
                self.assertEqual(names(store.read_trainees(term)), REFRESHER_NAMES)

    def test_unknown_course_returns_empty_list(self):
        self.assertEqual(store.read_trainees('zzz'), [])

    def test_blank_filter_returns_all(self):
        self.assertEqual(len(store.read_trainees('   ')), 5)

    def test_wildcard_characters_are_literal(self):
        for term in ('%', '_'):
            with self.subTest(term=term):
                self.assertEqual(store.read_trainees(term), [])

class ApiSearchTests(TempServer):
    """Real HTTP requests to a test server on a free port, using the temporary database."""
    def get(self, query=''):
        return self.request('/api/trainees' + query)

    def test_get_without_filter(self):
        status, data = self.get()
        self.assertEqual(status, 200)
        self.assertEqual(len(data['trainees']), 5)

    def test_get_with_course_filter(self):
        status, data = self.get('?course=refresher')
        self.assertEqual(status, 200)
        self.assertEqual(names(data['trainees']), REFRESHER_NAMES)
        for row in data['trainees']:
            self.assertIn('renewal_soon', row)

    def test_get_unknown_course(self):
        status, data = self.get('?course=zzz')
        self.assertEqual(status, 200)
        self.assertEqual(data['trainees'], [])

    def test_get_with_encoded_space(self):
        status, data = self.get('?course=security%20refresher')
        self.assertEqual(status, 200)
        self.assertEqual(names(data['trainees']), REFRESHER_NAMES)

if __name__ == '__main__':
    unittest.main()
