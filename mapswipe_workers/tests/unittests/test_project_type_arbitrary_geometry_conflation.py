import os
import unittest

from mapswipe_workers.project_types import ConflationProject
from tests import fixtures


class TestCreateConflationProject(unittest.TestCase):
    def setUp(self) -> None:
        project_draft = fixtures.get_fixture(
            os.path.join(
                "projectDrafts",
                "conflation.json",
            )
        )
        project_draft["projectDraftId"] = "foo"
        self.project = ConflationProject(project_draft)

    def test_init(self):
        self.assertIsInstance(self.project.geometry, str)

    def test_create_groups(self):
        self.project.validate_geometries()
        self.project.create_groups()
        # self.assertEqual(len(self.project.groups.keys()), 1)
        # self.assertIsInstance(self.project.geometry, str)

    def test_create_tasks(self):
        self.project.validate_geometries()
        self.project.create_groups()
        self.project.create_tasks()
        # self.assertEqual(len(self.project.tasks.keys()), 1)
        # self.assertEqual(len(self.project.tasks["g100"]), 1)
        # self.assertTrue("POLYGON" in self.project.tasks["g100"][0].geometry)


if __name__ == "__main__":
    unittest.main()
