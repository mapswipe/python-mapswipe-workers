import unittest

import set_up
import tear_down

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import transfer_results


class TestTranserResultsProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project(
            "tile_map_service_grid", "build_area", results=True
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_changes_given_project_id(self):
        """Test if results are deleted from Firebase for given project id."""
        transfer_results.transfer_results(project_id_list=[self.project_id])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        pg_db = auth.postgresDB()
        sql_query = (
            f"SELECT * "
            f"FROM results "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_changes(self):
        """Test if results are deleted from Firebase for given project id."""
        transfer_results.transfer_results()

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        pg_db = auth.postgresDB()
        sql_query = (
            f"SELECT * "
            f"FROM results "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_user_not_in_postgres(self):
        """Test if results are transfered for users which are not yet in Postgres."""
        pg_db = auth.postgresDB()

        # Make sure user and results are not yet in Postgres
        sql_query = (
            f"DELETE FROM results "
            f"WHERE user_id = '{self.project_id}' "
            f"AND project_id = '{self.project_id}'"
        )
        pg_db.query(sql_query)
        sql_query = "DELETE FROM users WHERE user_id = '{0}'".format(self.project_id)
        pg_db.query(sql_query)

        transfer_results.transfer_results()

        sql_query = "SELECT * FROM users WHERE user_id = '{0}'".format(self.project_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

        sql_query = (
            f"SELECT * "
            f"FROM results "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
