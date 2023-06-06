import json
import os
import unittest
from unittest.mock import patch

from mapswipe_workers.project_types import FootprintProject
from tests import fixtures


class TestCreateFootprintProject(unittest.TestCase):
    def setUp(self) -> None:
        project_draft = fixtures.get_fixture(
            os.path.join(
                "projectDrafts",
                "footprint.json",
            )
        )
        project_draft["projectDraftId"] = "foo"
        self.project = FootprintProject(project_draft)

    def test_init(self):
        self.assertEqual(self.project.geometry["type"], "FeatureCollection")
        self.assertEqual(self.project.inputType, "aoi_file")

    def test_create_groups(self):
        with patch(
            "mapswipe_workers.project_types.arbitrary_geometry.footprint.project.ohsome"
        ) as mock_get:
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "feature_collection.json",
                ),
                "r",
            ) as file:
                mock_get.return_value = json.load(file)

            self.project.validate_geometries()
        self.project.create_groups()
        self.assertEqual(len(self.project.groups.keys()), 1)
        self.assertIsInstance(self.project.geometry, str)

    def test_create_tasks(self):
        with patch(
            "mapswipe_workers.project_types.arbitrary_geometry.footprint.project.ohsome"
        ) as mock_get:
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "feature_collection.json",
                ),
                "r",
            ) as file:
                mock_get.return_value = json.load(file)

            self.project.validate_geometries()
        self.project.create_groups()
        self.project.create_tasks()

        self.assertEqual(len(self.project.tasks.keys()), 1)
        self.assertEqual(len(self.project.tasks["g100"]), 1)
        self.assertTrue("POLYGON" in self.project.tasks["g100"][0].geometry)


if __name__ == "__main__":
    unittest.main()
