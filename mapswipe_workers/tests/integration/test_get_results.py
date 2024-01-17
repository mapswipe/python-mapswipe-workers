import os
import tempfile
import unittest

from mapswipe_workers.generate_stats.project_stats import get_results
from tests.integration import base, set_up, tear_down


class TestGetResults(base.BaseTestCase):
    def setUp(self):
        super().setUp()
        project_type = "tile_map_service_grid"
        fixture_name = "build_area"
        self.project_id = set_up.create_test_project(
            project_type, fixture_name, results=True
        )
        self.results_filename = os.path.join(
            tempfile._get_default_tempdir(), f"results_{self.project_id}.csv.gz"
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_get_results_df_from_postgres(self):
        df = get_results(self.results_filename, self.project_id)

        self.assertEqual(len(df), 252)
        self.assertListEqual(
            list(df.columns)[1:],
            [
                "project_id",
                "group_id",
                "user_id",
                "task_id",
                "timestamp",
                "start_time",
                "end_time",
                "result",
                "username",
                "day",
            ],
        )


if __name__ == "__main__":
    unittest.main()
