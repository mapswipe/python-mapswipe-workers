import json
import os
import unittest

from mapswipe_workers.project_types.tile_classification.project import (
    TileClassificationProject,
)


class TestInitProject(unittest.TestCase):
    def test_init_tile_classification_project(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        path = "fixtures/tile_map_service_grid/projectDrafts/tile_classification.json"

        with open(os.path.join(test_dir, path)) as json_file:
            project_draft = json.load(json_file)

        self.assertIsNotNone(TileClassificationProject(project_draft=project_draft))


if __name__ == "__main__":
    unittest.main()
