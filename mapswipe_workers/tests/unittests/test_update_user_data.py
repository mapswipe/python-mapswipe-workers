import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import transfer_results, update_data

import set_up
import tear_down


class TestArchiveProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up before tests are run."""
        cls.user_id = set_up.create_test_user()
        update_data.update_user_data([cls.user_id])
        transfer_results.transfer_results(project_id_list=[cls.project_id])

    @classmethod
    def tearDownClass(cls):
        """Tear down after tests are run."""
        tear_down.delete_test_data(cls.project_id, cls.user_id)

    def test_firebase_changes(self):
        """Test if results are deleted from Firebase."""
        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertFalse(ref.get())

    def test_postgres_changes(self):
        """Test if results are transfered to Firebase."""
        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM results WHERE project_id = {0} and user_id = {1}".format(
            self.project_id, self.user_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

        sql_query = "SELECT * FROM users WHERE user_id = {1}".format(self.user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
