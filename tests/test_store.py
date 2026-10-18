import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import store

class StorageTests(unittest.TestCase):
    def test_five_fake_trainees_in_isolated_database(self):
        with TemporaryDirectory() as folder:
            with patch.object(store, 'DB', Path(folder) / 'test.sqlite3'):
                store.initialize()
                rows = store.read_trainees()
                self.assertEqual(len(rows), 5)
                self.assertIsNone(rows[3]['expires_on'])

if __name__ == '__main__':
    unittest.main()
