import json
import unittest
import store
from rules import validate_trainee
from helpers import TempDatabase, TempServer

STARTING_COURSES = ['Access Control', 'Incident Reporting', 'Security Refresher', 'Site Operations']
NEW_TRAINEE = {'name': 'Test Person', 'course': 'Site Operations', 'expires_on': None}

class CourseListTests(TempDatabase):
    def test_read_courses_is_unique_and_alphabetical(self):
        # "Security Refresher" belongs to 2 trainees but must appear once
        self.assertEqual(store.read_courses(), STARTING_COURSES)

class CourseRuleTests(unittest.TestCase):
    def test_existing_course_accepted(self):
        self.assertEqual(validate_trainee(NEW_TRAINEE, courses=STARTING_COURSES)[1], {})

    def test_unknown_course_rejected(self):
        errors = validate_trainee({**NEW_TRAINEE, 'course': 'Underwater Basket Weaving'}, courses=STARTING_COURSES)[1]
        self.assertEqual(errors, {'course': 'must be an existing course'})

class ApiCourseTests(TempServer):
    """Real HTTP requests to a test server on a free port, using the temporary database."""
    def post(self, data):
        return self.request('/api/trainees', 'POST', json.dumps(data).encode())

    def trainee_count(self):
        return len(self.request('/api/trainees')[1]['trainees'])

    def test_get_courses(self):
        self.assertEqual(self.request('/api/courses'), (200, {'courses': STARTING_COURSES}))

    def test_post_with_existing_course_returns_201(self):
        status, row = self.post(NEW_TRAINEE)
        self.assertEqual(status, 201)
        self.assertEqual(row['course'], 'Site Operations')

    def test_post_with_unknown_course_returns_400_and_saves_nothing(self):
        status, data = self.post({**NEW_TRAINEE, 'course': 'Underwater Basket Weaving'})
        self.assertEqual(status, 400)
        self.assertEqual(data['fields'], {'course': 'must be an existing course'})
        self.assertEqual(self.trainee_count(), 5)

    def test_post_with_different_capitalisation_returns_400(self):
        status, data = self.post({**NEW_TRAINEE, 'course': 'security refresher'})
        self.assertEqual(status, 400)
        self.assertEqual(data['fields'], {'course': 'must be an existing course'})

if __name__ == '__main__':
    unittest.main()
