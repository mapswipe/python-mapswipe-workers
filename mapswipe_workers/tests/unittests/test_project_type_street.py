import json
import os
import unittest
from unittest.mock import patch
from shapely import wkt
import pandas as pd

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

        with patch(
            "mapswipe_workers.utils.process_mapillary.coordinate_download"
        ) as mock_get:
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "mapillary_response.csv",
                ),
                "r",
            ) as file:
                df = pd.read_csv(file)
                df['geometry'] = df['geometry'].apply(wkt.loads)

                mock_get.return_value = df
                self.project = StreetProject(project_draft)

    def test_init(self):
        self.assertEqual(self.project.geometry["type"], "FeatureCollection")

    def test_create_group(self):
        self.project.create_groups()
        self.assertTrue(self.project.groups)

    def test_create_tasks(self):
        imageId = self.project.imageIds[-1]
        self.project.create_groups()
        self.project.create_tasks()
        self.assertEqual(self.project.tasks["g0"][0].taskId, imageId)


if __name__ == "__main__":
    unittest.main()
