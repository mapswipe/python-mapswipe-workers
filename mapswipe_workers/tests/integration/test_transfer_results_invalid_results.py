import json
import os
import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import transfer_results

from . import set_up, tear_down
from .base import BaseTestCase


class TestTransferInvalidResultsProject(BaseTestCase):
    def setUp(self):
        super().setUp()
        project_type = "tile_map_service_grid"
        fixture_name = "build_area"
        self.project_id = set_up.create_test_project(
            project_type, fixture_name, results=False
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def verify_mapping_results_in_postgres(self):
        """Check that mapping_sessions and mapping_sessions_results
        contain the expected data.
        """
        pg_db = auth.postgresDB()
        expected_items_count = 252

        sql_query = (
            f"SELECT * "
            f"FROM mapping_sessions "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][6], expected_items_count)

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

    def test_invalid_task_in_result(self):
        """Test for results that are not valid.

        In this test the results contain an additional task.
        This should raise a Database error due to a foreign key violation.
        Because results could not be stored in Postgres DB,
        they should also NOT be deleted in Firebase.
        """

        test_dir = os.path.dirname(__file__)
        fixture_name = "build_area_invalid_task.json"
        file_path = os.path.join(
            test_dir, "fixtures", "tile_map_service_grid", "results", fixture_name
        )

        with open(file_path) as test_file:
            test_data = json.load(test_file)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/results/{self.project_id}")
        ref.set(test_data)

        transfer_results.transfer_results(project_id_list=[self.project_id])

        self.verify_mapping_results_in_postgres()

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(
            f"v2/results/{self.project_id}/g115/test_build_area/results"
        )
        self.assertIsNone(ref.get(shallow=True))


if __name__ == "__main__":
    unittest.main()
