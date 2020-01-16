import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import transfer_results

import set_up
import tear_down


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project("build_area")
        self.user_id = set_up.create_test_user()

    def tearDown(self):
        tear_down.delete_test_project(self.project_id)
        tear_down.delete_test_uster(self.user_id)

    def test_firebase_changes_given_project_id(self):
        """Test if results are deleted from Firebase for given project id."""
        transfer_results.transfer_results(project_id_list=[self.project_id])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

    def test_postgres_changes_given_project_id(self):
        """Test if results are transfered to Firebase for given project id."""
        transfer_results.transfer_results(project_id_list=[self.project_id])

        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM results WHERE project_id = {0} and user_id = {1}".format(
            self.project_id, self.user_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_firebase_changes(self):
        """Test if results are deleted from Firebase for given project id."""
        transfer_results.transfer_results()

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

    def test_postgres_changes(self):
        """Test if results are transfered to Firebase for given project id."""
        transfer_results.transfer_results()

        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM results WHERE project_id = {0} and user_id = {1}".format(
            self.project_id, self.user_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_user_not_in_postgres(self):
        """Test if results are transfered for users which are not yet in Postgres."""
        pg_db = auth.postgresDB()

        # Make sure user us not yet in Postgres
        sql_query = "DELETE FROM users WHERE user_id = {1}".format(self.user_id)
        pg_db.query(sql_query)

        transfer_results.transfer_results()

        sql_query = "SELECT * FROM users WHERE user_id = {1}".format(self.user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

        sql_query = "SELECT * FROM results WHERE project_id = {0} and user_id = {1}".format(
            self.project_id, self.user_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
