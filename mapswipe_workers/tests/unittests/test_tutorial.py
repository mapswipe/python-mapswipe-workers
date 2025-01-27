import os
import unittest

from mapswipe_workers.project_types import ClassificationTutorial
from tests.fixtures import FIXTURE_DIR, get_fixture


class TestTutorial(unittest.TestCase):
    def test_init_tile_classification_project(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "tile_classification.json")
        )
        self.assertIsNotNone(ClassificationTutorial(tutorial_draft=tutorial_draft))

    def test_create_tile_classification_tasks(self):
        tutorial_draft = get_fixture(
            os.path.join(FIXTURE_DIR, "tutorialDrafts", "tile_classification.json")
        )
        tutorial = ClassificationTutorial(tutorial_draft=tutorial_draft)
        tutorial.create_tutorial_groups()
        tutorial.create_tutorial_tasks()
        self.assertTrue(tutorial.groups)
        self.assertTrue(tutorial.tasks)


if __name__ == "__main__":
    unittest.main()
