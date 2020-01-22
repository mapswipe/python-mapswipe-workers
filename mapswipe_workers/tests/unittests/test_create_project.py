import unittest

import set_up
import tear_down
from mapswipe_workers import auth
from mapswipe_workers import mapswipe_workers


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.project_draft_id = set_up.create_test_project_draft("build_area")
        self.project_id = ""
        mapswipe_workers.run_create_projects()

    def tearDown(self):
        tear_down.delete_test_project_draft(self.project_draft_id)
        if self.project_id:
            tear_down.delete_test_project(self.project_id)
