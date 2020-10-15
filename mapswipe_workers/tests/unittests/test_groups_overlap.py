import os
import unittest

from mapswipe_workers.utils import tile_grouping_functions as t


class TestGroupsOverlap(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def test_project_geometries_intersection(self):
        zoom = 18
        project_extent_file = os.path.join(
            self.test_dir, "fixtures/completeness/closed_polygons.geojson"
        )

        groups_with_overlaps = t.extent_to_groups(project_extent_file, zoom, 100)
        self.assertEqual(len(groups_with_overlaps), 117)


if __name__ == "__main__":
    unittest.main()
