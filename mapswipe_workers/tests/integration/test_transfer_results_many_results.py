import unittest

import set_up
import tear_down

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import transfer_results


class TestTransferManyResults(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project(
            "tile_map_service_grid", "build_area_heidelberg", results=True
        )

    def tearDown(self):
        tear_down.delete_test_data("test_build_area")
        tear_down.delete_test_data(self.project_id)

    def test_transfer_results(self):
        """Test if results are deleted from Firebase for given project id."""
        transfer_results.transfer_results(project_id_list=[self.project_id])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/results/{self.project_id}")
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


if __name__ == "__main__":
    unittest.main()
