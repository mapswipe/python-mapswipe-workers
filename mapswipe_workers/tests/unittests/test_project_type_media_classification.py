import os
import unittest
from unittest.mock import patch

# TODO import MediaClassificationGroup
from mapswipe_workers.project_types.media_classification.project import (
    MediaClassificationProject,
)

from .. import fixtures


class TestMediaClassification(unittest.TestCase):
    def setUp(self):
        project_draft = fixtures.get_fixture(
            os.path.join("projectDrafts", "media_classification.json")
        )
        project_draft["projectDraftId"] = "bar"
        self.project = MediaClassificationProject(project_draft)

    def test_init(self):
        self.assertEqual(self.mediaCredits, "credits")
        self.assertEqual(self.mediaurl, "https://example.com")
        self.assertFalse(self.medialist)

    """
    def test_create_group(self):
        self.project.validate_geometries()
        self.project.create_groups()
        self.assertIsNotNone(self.project.groups)
    """

    def test_get_media(self):
        with patch(
            "mapswipe_workers.project_types.media_classification.project.requests.get"
        ) as mock_get:
            with open(os.path.join("..", "fixtures", "media.zip")) as file:
                mock_get.return_value.content = file.read()

            self.project.get_media()


"""
class TestTileClassificationGroup(unittest.TestCase):
    def setUp(self):
        project_draft = fixtures.get_fixture(
            os.path.join("projectDrafts", "tile_classification.json")
        )
        project_draft["projectDraftId"] = "foo"
        self.project = TileClassificationProject(project_draft)
        self.group = TileClassificationGroup(self.project, 1, MagicMock())

    def test_init(self):
        self.assertIsNotNone(self.group.xMax)
        self.assertIsNotNone(self.group.xMin)
        self.assertIsNotNone(self.group.yMax)
        self.assertIsNotNone(self.group.yMin)

    def test_create_tasks(self):
        self.group.create_tasks(self.project)
        self.assertIsNotNone(self.group.tasks)
        self.assertIsNotNone(self.group.numberOfTasks)
"""

if __name__ == "__main__":
    unittest.main()
