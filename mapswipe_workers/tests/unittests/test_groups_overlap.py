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

        groups_with_overlaps = t.extent_to_slices(project_extent_file, zoom, 100)
        t.save_vertical_slices_as_geojson(
            groups_with_overlaps, "groups_with_overlaps.geojson"
        )

        # remove groups within other groups
        groups_with_overlaps_2 = t.remove_groups_within_other_groups(
            groups_with_overlaps, zoom
        )
        t.save_vertical_slices_as_geojson(
            groups_with_overlaps, "groups_with_overlaps2.geojson"
        )

        # TODO: remove once implemented in real function
        groups, overlaps_total = t.adjust_overlapping_groups(
            groups_with_overlaps_2, zoom
        )
        t.save_vertical_slices_as_geojson(groups, "groups.geojson")

        groups_2, overlaps_total_2 = t.adjust_overlapping_groups(groups, zoom)
        t.save_vertical_slices_as_geojson(groups_2, "groups_2.geojson")

        # we expect 117 groups
        self.assertEqual(len(groups_2), 117)

    def test_project_geometries_within(self):
        zoom = 18
        project_extent_file = os.path.join(
            self.test_dir, "fixtures/completeness/project_geometries_within.geojson"
        )

        groups_with_overlaps = t.extent_to_slices(project_extent_file, zoom, 100)
        t.save_vertical_slices_as_geojson(
            groups_with_overlaps, "groups_with_overlaps.geojson"
        )

        # remove groups within other groups
        groups_with_overlaps_2 = t.remove_groups_within_other_groups(
            groups_with_overlaps, zoom
        )
        t.save_vertical_slices_as_geojson(
            groups_with_overlaps, "groups_with_overlaps2.geojson"
        )

        # TODO: remove once implemented in real function
        groups, overlaps_total = t.adjust_overlapping_groups(
            groups_with_overlaps_2, zoom
        )
        t.save_vertical_slices_as_geojson(groups, "groups.geojson")

        groups_2, overlaps_total_2 = t.adjust_overlapping_groups(groups, zoom)
        t.save_vertical_slices_as_geojson(groups_2, "groups_2.geojson")

        groups_3, overlaps_total_3 = t.adjust_overlapping_groups(groups_2, zoom)
        t.save_vertical_slices_as_geojson(groups_3, "groups_3.geojson")

        # we expect 64 groups
        self.assertEqual(len(groups_3), 64)

    """
    def test_project_geometries_very_small_and_close(self):
        project_extent_file = os.path.join(
            self.test_dir,
            "fixtures/completeness/project_geometries_very_small_and_close.geojson"
        )

        groups_with_overlaps = t.extent_to_slices(project_extent_file, 18, 100)
        t.save_vertical_slices_as_geojson(
            groups_with_overlaps, "groups_with_overlaps.geojson"
        )

        groups = t.adjust_overlapping_groups(groups_with_overlaps)

        # save files for visual inspection in qgis
        t.save_vertical_slices_as_geojson(groups, "groups.geojson")

        # TODO: add correct assertion, what is the expected output?
        # we expect 64 groups
        #self.assertEqual(len(groups), 64)
    """


if __name__ == "__main__":
    unittest.main()
