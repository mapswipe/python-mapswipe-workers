import json
import os
import unittest
from unittest.mock import patch

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.project_types import DigitizationProject
from tests import fixtures


class TestDigitizationProject(unittest.TestCase):
    def setUp(self) -> None:
        project_draft = fixtures.get_fixture(
            os.path.join(
                "projectDrafts",
                "digitization.json",
            )
        )
        project_draft["projectDraftId"] = "foo"
        self.project = DigitizationProject(project_draft)

    def test_init(self):
        self.assertIsInstance(self.project.geometry, str)
        self.assertEqual(self.project.drawType, "Point")
        self.assertFalse("inputType" in vars(self.project).keys())

    def test_create_groups(self):
        with patch(
            "mapswipe_workers.project_types."
            + "arbitrary_geometry.digitization.project.urlretrieve"
        ):
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "feature_collection.json",
                ),
                "r",
            ) as file:
                output_file_path = (
                    f"{DATA_PATH}/input_geometries/"
                    + "raw_input_{self.project.projectId}.geojson"
                )
                with open(output_file_path, "w") as out_file:
                    json.dump(json.load(file), out_file)

            self.project.validate_geometries()
        self.project.create_groups()
        self.assertEqual(len(self.project.groups.keys()), 1)

    def test_create_tasks(self):

        with patch(
            "mapswipe_workers.project_types."
            + "arbitrary_geometry.digitization.project.urlretrieve"
        ):
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "feature_collection.json",
                ),
                "r",
            ) as file:
                output_file_path = (
                    f"{DATA_PATH}/input_geometries/"
                    + f"raw_input_{self.project.projectId}.geojson"
                )
                with open(output_file_path, "w") as out_file:
                    json.dump(json.load(file), out_file)
            self.project.validate_geometries()
        self.project.create_groups()
        self.project.create_tasks()
        self.assertEqual(len(self.project.tasks.keys()), 1)
        self.assertEqual(len(self.project.tasks["g100"]), 1)
        self.assertTrue("POLYGON" in self.project.tasks["g100"][0].geometry)


if __name__ == "__main__":
    unittest.main()
