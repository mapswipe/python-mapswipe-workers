import os
import unittest
import json

from mapswipe_workers.definitions import CustomError
from mapswipe_workers.utils.validate_input import validate_geometries


class TestValidateGeometries(unittest.TestCase):
    def test_multiple_geom_validation(self):
        pass

    # todo: all the other tests

    def test_area_is_too_large(self):
        """Test if validate_geometries throws an error
        if the provided geojson covers a too large area."""

        path = (
            "fixtures/tile_map_service_grid/projects/projectDraft_area_too_large.json"
        )
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, path)) as json_file:
            project_draft = json.load(json_file)
            geometry = project_draft["geometry"]

        self.assertRaises(CustomError, validate_geometries, 1, geometry, 18)

        """
        project = create_project(path)


        
        # we expect that the function raises a CustomError due to the fact
        # that the area is too large
        self.assertRaises(CustomError, project.validate_geometries)
"""

if __name__ == "__main__":
    unittest.main()
