import unittest

from mapswipe_workers import auth


class TestFirebaseConnection(unittest.TestCase):
    def setUp(self):
        self.fb_db = auth.firebaseDB()

    def tearDown(self):
        self.fb_db = None

    def test_create_project(self):
        ref = self.fb_db.reference("/v2/test")
        ref.push("test")
        result = ref.get()
        self.assertIsNotNone(result)
        ref.set({})
        result = ref.get()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
