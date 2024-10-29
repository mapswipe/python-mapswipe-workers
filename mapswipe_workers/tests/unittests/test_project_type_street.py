import json
import os
import unittest
from unittest.mock import patch

from mapswipe_workers.project_types import StreetProject
from tests import fixtures


class TestCreateStreetProject(unittest.TestCase):
    def setUp(self) -> None:
        project_draft = fixtures.get_fixture(
            os.path.join(
                "projectDrafts",
                "street.json",
            )
        )
        project_draft["projectDraftId"] = "foo"
        self.project = StreetProject(project_draft)

    def test_init(self):
        self.assertEqual(self.project.geometry["type"], "FeatureCollection")

    def test_create_group(self):
        self.project.create_groups()
        self.assertTrue(self.project.groups)

    def test_create_tasks(self):
        imageId = self.project.imageList[-1]
        self.project.create_groups()
        self.project.create_tasks()
        self.assertEqual(self.project.tasks["g0"][0].taskId, imageId)
        #self.assertEqual(self.project.groups["g0"].numberOfTasks, 1)


if __name__ == "__main__":
    unittest.main()
