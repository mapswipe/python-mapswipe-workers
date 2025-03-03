import os
import unittest

from mapswipe_workers.project_types import FootprintTutorial
from tests.fixtures import FIXTURE_DIR, get_fixture


class TestTutorial(unittest.TestCase):
    def test_init_arbitrary_geometry_footprint_project(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "footprint.json")
        )
        self.assertIsNotNone(FootprintTutorial(tutorial_draft=tutorial_draft))

    def test_create_arbitrary_geometry_footprint_tasks(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "footprint.json")
        )
        tutorial = FootprintTutorial(tutorial_draft=tutorial_draft)
        tutorial.create_tutorial_groups()
        tutorial.create_tutorial_tasks()
        self.assertTrue(tutorial.groups)
        self.assertTrue(tutorial.tasks)


if __name__ == "__main__":
    unittest.main()
