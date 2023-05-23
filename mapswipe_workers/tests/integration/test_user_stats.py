import os
import tempfile
import unittest

import pandas as pd

from mapswipe_workers.generate_stats.project_stats import (
    get_agg_results_by_task_id,
    get_results,
    get_tasks,
)
from mapswipe_workers.generate_stats.user_stats import get_agg_results_by_user_id

from . import set_up, tear_down
from .base import BaseTestCase


class TestUserStats(BaseTestCase):
    def setUp(self):
        super().setUp()
        project_type = "footprint"
        fixture_name = "osm_validation_malawi"
        self.project_id = "-NEaU7GXxWRqKaFUYp_2"

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

    def test_get_agg_results_by_user_id(self):
        results_df = get_results(self.results_filename, self.project_id)
        self.assertEqual(len(results_df), 210361)

        tasks_df = get_tasks(self.tasks_filename, self.project_id)
        self.assertEqual(len(tasks_df), 67436)

        agg_results_df = get_agg_results_by_task_id(
            results_df, tasks_df, pd.Series(data=["{0, 1, 2, 3}"])
        )
        self.assertEqual(len(agg_results_df), 67436)

        agg_results_by_user_id_df = get_agg_results_by_user_id(
            results_df, agg_results_df
        )
        self.assertEqual(len(agg_results_by_user_id_df), 477)


if __name__ == "__main__":
    unittest.main()
