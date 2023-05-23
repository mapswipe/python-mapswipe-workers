import unittest
from unittest.mock import MagicMock

from .. import fixtures
import os


from mapswipe_workers.project_types.tile_classification.project import (
    TileClassificationProject,
    TileClassificationGroup,
)


class TestTileClassificationProject(unittest.TestCase):
    def setUp(self):
        project_draft = fixtures.get_fixture(
            os.path.join("projectDrafts", "tile_classification.json")
        )
        project_draft["projectDraftId"] = "foo"
        self.project = TileClassificationProject(project_draft)

    def test_init(self):
        self.assertIsNotNone(self.project.geometry)
        self.assertEqual(self.project.zoomLevel, 19)
        self.assertIsNotNone(self.project.tileServer)

    def test_create_group(self):
        self.project.validate_geometries()
        self.project.create_groups()
        self.assertIsNotNone(self.project.groups)


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


if __name__ == "__main__":
    unittest.main()
