import os
import unittest
from mapswipe_workers.utils import tile_grouping_functions as t


class TestGroupsOverlap(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def test_project_geometries_intersection(self):

        project_extent_file = os.path.join(
            self.test_dir, "fixtures/completeness/closed_polygons.geojson"
        )

        groups_with_overlaps = t.extent_to_slices(project_extent_file, 18, 100)
        t.save_vertical_slices_as_geojson(
            groups_with_overlaps, "groups_with_overlaps.geojson"
        )

        groups = t.adjust_overlapping_groups(groups_with_overlaps)

        # save files for visual inspection in qgis
        t.save_vertical_slices_as_geojson(groups, "groups.geojson")

        # we expect 117 groups
        self.assertEqual(len(groups), 117)

    def test_project_geometries_within(self):
        project_extent_file = os.path.join(
            self.test_dir, "fixtures/completeness/project_geometries_within.geojson"
        )

        groups_with_overlaps = t.extent_to_slices(project_extent_file, 18, 100)
        t.save_vertical_slices_as_geojson(
            groups_with_overlaps, "groups_with_overlaps.geojson"
        )

        groups = t.adjust_overlapping_groups(groups_with_overlaps)

        # save files for visual inspection in qgis
        t.save_vertical_slices_as_geojson(groups, "groups.geojson")

        # we expect 64 groups
        self.assertEqual(len(groups), 64)


if __name__ == "__main__":
    unittest.main()
