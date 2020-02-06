import unittest

import set_up
import tear_down
from mapswipe_workers import mapswipe_workers


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project_draft("build_area")
        mapswipe_workers.run_create_projects()

    def tearDown(self):
        tear_down.delete_test_project(self.project_id)

    def test_test(self):
        print(self.project_id)


if __name__ == "__main__":
    unittest.main()
