import unittest

import set_up
import tear_down
from click.testing import CliRunner
from mapswipe_workers import mapswipe_workers


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project_draft("build_area")

    def tearDown(self):
        tear_down.delete_test_project(self.project_id)

    def test_test(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_projects)


if __name__ == "__main__":
    unittest.main()
