import os
import unittest

from mapswipe_workers.project_types.tile_map_service.classification.project import (
    ClassificationProject,
)
from tests import fixtures


class TestClassificationProject(unittest.TestCase):
    def setUp(self):
        project_draft = fixtures.get_fixture(
            os.path.join("projectDrafts", "classification.json")
        )
        project_draft["projectDraftId"] = "foo"
        self.project = ClassificationProject(project_draft)

    def test_init(self):
        self.assertIsNotNone(self.project.geometry)
        self.assertEqual(self.project.zoomLevel, 18)
        self.assertIsNotNone(self.project.tileServer)

    def test_create_groups(self):
        self.project.validate_geometries()
        self.project.create_groups()
        self.assertIsNotNone(self.project.groups)
        self.assertNotEqual(len(self.project.groups), 0)

    def test_create_tasks(self):
        self.project.validate_geometries()
        self.project.create_groups()
        self.project.create_tasks()
        self.assertNotEqual(len(self.project.tasks), 0)
        for group in self.project.groups.values():
            self.assertGreater(group.numberOfTasks, 0)


if __name__ == "__main__":
    unittest.main()
