import os
import unittest
from mapswipe_workers.utils import tile_grouping_functions as t


class TestGroupsOverlap(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_extent_file = os.path.join(
            self.test_dir, "fixtures/completeness/closed_polygons.geojson"
        )

    def test_adjust_groups_overlap(self):
        groups = t.extent_to_slices(self.project_extent_file, 18, 100)
        group_ids = list(groups.keys())

        while len(group_ids) > 0:
            for group_id in group_ids:
                x_max = groups[group_id]["xMax"]
                x_min = groups[group_id]["xMin"]

                y_max = groups[group_id]["yMax"]
                y_min = groups[group_id]["yMin"]

                group_ids.remove(group_id)

                for group_id_b in group_ids:
                    y_minB = groups[group_id_b]["yMin"]
                    y_maxB = groups[group_id_b]["yMax"]
                    x_maxB = groups[group_id_b]["xMax"]
                    x_minB = groups[group_id_b]["xMin"]

                    # content from range_overlap
                    if (
                        (int(x_min) <= int(x_maxB))
                        and (int(x_minB) <= int(x_max))
                        and (int(y_min) <= int(y_maxB))
                        and (int(y_minB) <= int(y_max))
                    ):
                        print("x_min " + x_min + " x_maxB " + x_maxB)
                        x_min = int(x_maxB) - 1
                        x_max = int(x_minB) - 1
                        y_min = int(y_maxB) - 1
                        y_max = int(y_minB) - 1


if __name__ == "__main__":
    unittest.main()
