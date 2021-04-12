import unittest

from firebase_admin.exceptions import FirebaseError

from mapswipe_workers import auth


class TestFirebaseConnection(unittest.TestCase):
    def setUp(self):
        self.fb_db = auth.firebaseDB()

    def tearDown(self):
        self.test_data_ref.delete()
        self.fb_db = None

    def test_connection(self):
        ref = self.fb_db.reference("/v2")
        try:
            self.test_data_ref = ref.push("test_connection")
        except FirebaseError as error:
            self.fail(error)


if __name__ == "__main__":
    unittest.main()
