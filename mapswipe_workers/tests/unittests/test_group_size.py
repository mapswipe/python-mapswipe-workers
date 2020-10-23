import os
import unittest

from mapswipe_workers.utils import tile_grouping_functions as t


class TestGroupSizeIsEven(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        zoom = 18
        project_extent_file = os.path.join(
            self.test_dir, "fixtures/tile_map_service_grid/project_extent.geojson"
        )

        self.groups_dict = t.extent_to_groups(project_extent_file, zoom, 100)

    def test_group_y_size_is_three(self):
        """Test if a group has 3 tiles in y direction."""

        for group_id, group in self.groups_dict.items():
            # check if group size is of factor 6
            y_group_size = int(group['yMax']) - int(group['yMin']) + 1
            self.assertEqual(y_group_size, 3)

    def test_group_x_size_is_even(self):
        """Test if a group has an even number of tiles in x direction."""

        for group_id, group in self.groups_dict.items():
            # check if group size is of factor 6
            x_group_size = int(group['xMax']) - int(group['xMin']) + 1
            self.assertEqual(x_group_size % 2, 0)


if __name__ == "__main__":
    unittest.main()
