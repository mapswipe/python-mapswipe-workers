import os
import unittest
from mapswipe_workers.utils import tile_grouping_functions as t
from mapswipe_workers.utils import tile_functions as s
from osgeo import ogr


class TestGroupsOverlap(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_extent_file = os.path.join(
            self.test_dir, "fixtures/completeness/closed_polygons.geojson"
        )

    def test_adjust_groups_overlap(self):
        groups = t.extent_to_slices(self.project_extent_file, 18, 100)
        group_ids = list(groups.keys())
        raw_groups = {}

        for group_id in group_ids:
            x_max = groups[group_id]["xMax"]
            x_min = groups[group_id]["xMin"]

            y_max = groups[group_id]["yMax"]
            y_min = groups[group_id]["yMin"]

            group_ids.remove(group_id)
            overlap_count = 0
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
                    overlap_count += 1
                    new_x_max = int(x_minB) + 1

                    # Calculate lat, lon of upper left corner of tile
                    PixelX = int(x_min) * 256
                    PixelY = (int(y_max) + 1) * 256
                    lon_left, lat_top = s.pixel_coords_zoom_to_lat_lon(
                        PixelX, PixelY, 18
                    )
                    # logging.info('lon_left: %s, lat_top: %s' % (lon_left, lat_top))

                    # Calculate lat, lon of bottom right corner of tile
                    PixelX = (int(new_x_max) - 1) * 256
                    PixelY = (int(y_min)) * 256
                    lon_right, lat_bottom = s.pixel_coords_zoom_to_lat_lon(
                        PixelX, PixelY, 18
                    )

                    # Create Geometry
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    ring.AddPoint(lon_left, lat_top)
                    ring.AddPoint(lon_right, lat_top)
                    ring.AddPoint(lon_right, lat_bottom)
                    ring.AddPoint(lon_left, lat_bottom)
                    ring.AddPoint(lon_left, lat_top)
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(ring)

                    # add info to groups_dict

                    raw_groups[group_id] = {
                        "xMin": str(x_min),
                        "xMax": str(int(new_x_max) - 1),
                        "yMin": str(y_min),
                        "yMax": str(int(y_max) + 1),
                        "group_polygon": poly,
                    }

            print(overlap_count)

            if overlap_count == 0:
                raw_groups[group_id_b] = groups[group_id_b]

        return raw_groups

    def test_display_groups(self):
        raw_groups = self.test_adjust_groups_overlap()
        t.save_vertical_slices_as_geojson(
            raw_groups, "fixtures/completeness/check_Groups.geojson"
        )


if __name__ == "__main__":
    unittest.main()
