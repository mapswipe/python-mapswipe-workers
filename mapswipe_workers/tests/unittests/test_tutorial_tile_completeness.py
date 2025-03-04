import os
import unittest

from mapswipe_workers.project_types import CompletenessTutorial
from tests.fixtures import FIXTURE_DIR, get_fixture


class TestTutorial(unittest.TestCase):
    def test_init_tile_completeness_project(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "completeness.json")
        )
        self.assertIsNotNone(CompletenessTutorial(tutorial_draft=tutorial_draft))

    def test_create_tile_completeness_tasks(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "completeness.json")
        )
        tutorial = CompletenessTutorial(tutorial_draft=tutorial_draft)
        tutorial.create_tutorial_groups()
        tutorial.create_tutorial_tasks()
        self.assertTrue(tutorial.groups)
        self.assertTrue(tutorial.tasks)


if __name__ == "__main__":
    unittest.main()
