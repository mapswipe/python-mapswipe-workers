import json
import os
import unittest

from osgeo import ogr

from mapswipe_workers.definitions import CustomError
from mapswipe_workers.utils.validate_input import (
    save_geojson_to_file,
    validate_and_collect_geometries_to_multipolyon,
    multipolygon_to_wkt,
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_project_draft(path):
    # pre steps for outputting result of function
    with open(os.path.join(CURRENT_DIR, path)) as json_file:
        project_draft = json.load(json_file)

    path_to_geometries = save_geojson_to_file(1, project_draft["geometry"])
    return project_draft, path_to_geometries


class TestValidateGeometries(unittest.TestCase):
    def test_area_is_too_large(self):
        """Test if validate_geometries throws an error
        if the provided geojson covers a too large area."""

        path = (
            "fixtures/tile_map_service_grid/projects/projectDraft_area_too_large.json"
        )
        project_draft, path_to_geometries = get_project_draft(path)
        self.assertRaises(
            CustomError,
            validate_and_collect_geometries_to_multipolyon,
            1,
            18,
            path_to_geometries,
        )

    def test_broken_geojson_string(self):
        """Test if validate_geometries throws an error
        if the provided geojson string is broken.
        This means we can't create the geo data layer with ogr."""

        path = (
            "fixtures/tile_map_service_grid/projects/projectDraft_broken_geojson.json"
        )
        project_draft, path_to_geometries = get_project_draft(path)
        self.assertRaises(
            CustomError,
            validate_and_collect_geometries_to_multipolyon,
            1,
            18,
            path_to_geometries,
        )

    def test_feature_is_none(self):
        """Test if validate_geometries throws an error
        if the provided geojson contains a not defined feature."""

        path = (
            "fixtures/tile_map_service_grid/projects/projectDraft_feature_is_none.json"
        )
        project_draft, path_to_geometries = get_project_draft(path)
        self.assertRaises(
            CustomError,
            validate_and_collect_geometries_to_multipolyon,
            1,
            18,
            path_to_geometries,
        )

    def test_no_features(self):
        """Test if validate_geometries throws an error
        if the provided geojson contains no features."""

        path = "fixtures/tile_map_service_grid/projects/projectDraft_no_features.json"
        project_draft, path_to_geometries = get_project_draft(path)
        self.assertRaises(
            CustomError,
            validate_and_collect_geometries_to_multipolyon,
            1,
            18,
            path_to_geometries,
        )

    def test_single_geom_validation(self):
        path = "fixtures/completeness/projectDraft_single.json"
        project_draft, path_to_geometries = get_project_draft(path)
        test_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(test_dir, "fixtures/completeness/single_polygon.geojson")
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(os.path.join(CURRENT_DIR, path), 0)

        geometry_collection = ogr.Geometry(ogr.wkbMultiPolygon)
        # Get the data layer
        layer = datasource.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            # add geometry to geometry collection
            if geom_name == "MULTIPOLYGON":
                for multi in feat_geom:
                    geometry_collection.AddGeometry(multi)
            if geom_name == "POLYGON":
                geometry_collection.AddGeometry(feat_geom)

        dissolved_geometry = geometry_collection.UnionCascaded()
        wkt_geometry_collection = dissolved_geometry.ExportToWkt()

        # results coming from the validate_geometries function
        wkt = multipolygon_to_wkt(
            validate_and_collect_geometries_to_multipolyon(1, 18, path_to_geometries)
        )
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(wkt, wkt_geometry_collection)

    def test_multiple_geom_validation(self):
        path = "fixtures/completeness/projectDraft_overlappingGeom.json"
        project_draft, path_to_geometries = get_project_draft(path)

        # prepare data that is expected
        test_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(test_dir, "fixtures/completeness/overlappingGeoms.geojson")

        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(os.path.join(CURRENT_DIR, path), 0)

        geometry_collection = ogr.Geometry(ogr.wkbMultiPolygon)
        # Get the data layer
        layer = datasource.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            # add geometry to geometry collection
            # check if input geom is multipolygon or polygon
            if geom_name == "MULTIPOLYGON":
                for multi in feat_geom:
                    geometry_collection.AddGeometry(multi)
                # apply union function if multiple geoms of polygons overlap
                dissolved_geometry = geometry_collection.UnionCascaded()
                wkt_geometry_collection = dissolved_geometry.ExportToWkt()
            if geom_name == "POLYGON":
                geometry_collection.AddGeometry(feat_geom)
                wkt_geometry_collection = geometry_collection.ExportToWkt()

        # results coming from the validate_geometries function
        wkt = multipolygon_to_wkt(
            validate_and_collect_geometries_to_multipolyon(1, 18, path_to_geometries)
        )
        # Test that sequence first contains the same elements as second
        self.assertEqual(wkt, wkt_geometry_collection)


if __name__ == "__main__":
    unittest.main()
