import os
import tempfile
import unittest

from mapswipe_workers.firebase_to_postgres.update_data import (
    get_contributor_count_from_postgres,
    get_project_progress,
)

from . import set_up, tear_down
from .base import BaseTestCase


class TestUpdateData(BaseTestCase):
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

    def test_get_contributor_count(self):
        contributor_count = get_contributor_count_from_postgres(self.project_id)
        self.assertEqual(contributor_count, 1)

    def test_get_project_progress(self):
        progress = get_project_progress(self.project_id)
        self.assertEqual(progress, round(100 / 60))


if __name__ == "__main__":
    unittest.main()
