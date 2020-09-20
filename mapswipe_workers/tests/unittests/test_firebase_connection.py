import unittest

from mapswipe_workers import auth


class TestFirebaseConnection(unittest.TestCase):
    def setUp(self):
        self.fb_db = auth.firebaseDB()

    def tearDown(self):
        self.fb_db = None

    def test_connection(self):
        ref = self.fb_db.reference("/v2")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
