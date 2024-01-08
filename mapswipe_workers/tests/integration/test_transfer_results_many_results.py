import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import transfer_results
from tests.integration import base, set_up, tear_down


class TestTransferManyResults(base.BaseTestCase):
    def setUp(self):
        project_type = "tile_map_service_grid"
        fixture_name = "build_area_heidelberg"
        self.project_id = set_up.create_test_project(
            project_type, fixture_name, results=False
        )
        # add some results in firebase
        set_up.set_firebase_test_data(project_type, "users", "user", self.project_id)
        set_up.set_firebase_test_data(project_type, "userGroups", "user_group", "")
        set_up.set_firebase_test_data(
            project_type, "results", fixture_name, self.project_id
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def verify_mapping_results_in_postgres(self):
        """Check that mapping_sessions and mapping_sessions_results
        contain the expected data.
        """
        pg_db = auth.postgresDB()
        expected_items_count = 4938

        sql_query = (
            f"SELECT * "
            f"FROM mapping_sessions "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        # we expect 21 groups
        self.assertEqual(len(result), 21)

        sql_query = (
            f"SELECT sum(items_count) "
            f"FROM mapping_sessions "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(result[0][0], expected_items_count)

        q2 = (
            "SELECT msr.* "
            "FROM mapping_sessions_results msr "
            "JOIN mapping_sessions ms ON "
            "ms.mapping_session_id = msr.mapping_session_id "
            f"WHERE ms.project_id = '{self.project_id}' "
            f"AND ms.user_id = '{self.project_id}'"
        )
        result2 = pg_db.retr_query(q2)
        self.assertEqual(len(result2), expected_items_count)

    def test_transfer_results(self):
        """Test if results are deleted from Firebase for given project id."""
        transfer_results.transfer_results(project_id_list=[self.project_id])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/results/{self.project_id}")
        self.assertIsNone(ref.get())

        self.verify_mapping_results_in_postgres()


if __name__ == "__main__":
    unittest.main()
