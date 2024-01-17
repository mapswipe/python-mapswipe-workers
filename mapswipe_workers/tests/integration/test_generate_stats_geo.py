import os
import unittest

import pandas as pd

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.generate_stats.generate_stats import generate_stats
from mapswipe_workers.utils.create_directories import (
    clear_directories,
    create_directories,
)
from tests.integration import set_up, tear_down
from tests.integration.base import BaseTestCase


class TestGenerateGeoStats(BaseTestCase):
    def setUp(self):

        super().setUp()
        self.project_id = project_type = fixture_name = "digitization"
        self.files = [
            f"{DATA_PATH}/api/results/results_{self.project_id}.csv.gz",
            f"{DATA_PATH}/api/tasks/tasks_{self.project_id}.csv.gz",
            f"{DATA_PATH}/api/groups/groups_{self.project_id}.csv.gz",
            f"{DATA_PATH}/api/history/history_{self.project_id}.csv",
        ]

        set_up.create_test_project(
            project_type,
            fixture_name,
            results=True,
            mapping_sessions_results="mapping_sessions_results_geometry",
        )
        create_directories()
        clear_directories(self.files)

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)
        clear_directories(self.files)

    def test_generate_stats_for_geo_result_project(self):
        """Test the generation of the stats for a geo project."""
        generate_stats([self.project_id])

        for file in self.files:
            self.assertTrue(os.path.exists(file))

        self.assertFalse(
            os.path.exists(
                f"{DATA_PATH}/api/results/results_{self.project_id}_temp.csv.gz",
            )
        )

        result_df = pd.read_csv(
            f"{DATA_PATH}/api/results/results_{self.project_id}.csv.gz"
        )
        # should have 4 rows
        self.assertEqual(4, len(result_df.index))


if __name__ == "__main__":
    unittest.main()
