import json
import os
import unittest

from mapswipe_workers.utils import tile_grouping_functions
from mapswipe_workers.utils.validate_input import save_geojson_to_file


class TestTileGroupingFunctions(unittest.TestCase):
    def test_extent_to_group(self):

        project_draft_path = (
            "fixtures/tile_map_service_grid/projectDrafts/build_area.json"
        )
        groups_path = "fixtures/tile_map_service_grid/groups/build_area.json"

        test_dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(test_dir, project_draft_path)) as json_file:
            project_draft = json.load(json_file)
        path_to_geometries = save_geojson_to_file(1, project_draft["geometry"])

        created_groups = tile_grouping_functions.extent_to_groups(
            path_to_geometries, 18, project_draft["groupSize"]
        )

        with open(os.path.join(test_dir, groups_path)) as json_file:
            test_groups = json.load(json_file)

        self.assertEqual(len(test_groups), len(created_groups))
