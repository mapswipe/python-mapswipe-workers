import json
import os
import unittest

import set_up
import tear_down

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import transfer_results


class TestTranserResultsProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project(
            "tile_map_service_grid", "build_area", results=False
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

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

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertDictEqual(ref.get(shallow=True), {"g115": True})


if __name__ == "__main__":
    unittest.main()
