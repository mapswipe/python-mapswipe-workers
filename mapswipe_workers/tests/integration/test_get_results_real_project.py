import os
import tempfile
import unittest

from . import set_up
from . import tear_down
from .base import BaseTestCase

from mapswipe_workers.generate_stats.project_stats import get_results


class TestGetResults(BaseTestCase):
    def setUp(self):
        super().setUp()
        project_type = "tile_map_service_grid"
        fixture_name = "build_area_sandoa"
        self.project_id = "-NFNr55R_LYJvxP7wmte"

        for data_type in [
            "projects",
            "groups",
            "tasks",
            "users",
            "mapping_sessions",
            "mapping_sessions_results",
        ]:
            set_up.set_postgres_test_data(project_type, data_type, fixture_name)

        self.results_filename = os.path.join(
            tempfile._get_default_tempdir(), f"results_{self.project_id}.csv.gz"
        )
        self.tasks_filename = os.path.join(
            tempfile._get_default_tempdir(), f"tasks_{self.project_id}.csv.gz"
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_get_results_df_from_postgres(self):
        df = get_results(self.results_filename, self.project_id)

        self.assertEqual(len(df), 7164)
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
