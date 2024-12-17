import os
import unittest

from mapswipe_workers.project_types import StreetTutorial
from tests.fixtures import FIXTURE_DIR, get_fixture


class TestTutorial(unittest.TestCase):
    def test_init_tile_classification_project(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "street.json")
        )
        self.assertIsNotNone(StreetTutorial(tutorial_draft=tutorial_draft))

    def test_create_tile_classification_tasks(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "street.json")
        )
        tutorial = StreetTutorial(tutorial_draft=tutorial_draft)
        tutorial.create_tutorial_groups()
        tutorial.create_tutorial_tasks()
        self.assertTrue(tutorial.groups)
        self.assertTrue(tutorial.tasks)
        breakpoint()


if __name__ == "__main__":
    unittest.main()
