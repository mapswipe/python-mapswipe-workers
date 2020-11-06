import json
import os
import unittest

from osgeo import ogr

from mapswipe_workers.definitions import CustomError, ProjectType


def create_project(path):
    # pre steps for outputting result of function
    test_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(test_dir, path)) as json_file:
        project_draft = json.load(json_file)
        project_type = project_draft["projectType"]
        project = ProjectType(project_type).constructor(project_draft)

    return project


class TestGeometryValidation(unittest.TestCase):
    def test_multiple_geom_validation(self):
        path = "fixtures/completeness/projectDraft_overlappingGeom.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project = create_project(path)

        # prepare data that is expected
        path = os.path.join(test_dir, "fixtures/completeness/overlappingGeoms.geojson")
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(path, 0)

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
        wkt = project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertEqual(wkt, wkt_geometry_collection)

    def test_single_geom_validation(self):
        path = "fixtures/completeness/projectDraft_single.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project = create_project(path)

        # prepare data that is expected
        path = os.path.join(test_dir, "fixtures/completeness/single_polygon.geojson")
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(path, 0)

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
        wkt = project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(wkt, wkt_geometry_collection)

    def test_no_features(self):
        """Test if validate_geometries throws an error
        if the provided geojson contains no features."""

        path = "fixtures/tile_map_service_grid/projects/projectDraft_no_features.json"
        project = create_project(path)

        # we expect that the function raises a CustomError due to the fact
        # that there are no features in the geojson
        self.assertRaises(CustomError, project.validate_geometries)

    def test_feature_is_none(self):
        """Test if validate_geometries throws an error
        if the provided geojson contains a not defined feature."""

        path = (
            "fixtures/tile_map_service_grid/projects/projectDraft_feature_is_none.json"
        )
        project = create_project(path)

        # we expect that the function raises a CustomError due to the fact
        # that one feature of the geojson is None
        self.assertRaises(CustomError, project.validate_geometries)

    def test_area_is_too_large(self):
        """Test if validate_geometries throws an error
        if the provided geojson covers a too large area."""

        path = (
            "fixtures/tile_map_service_grid/projects/projectDraft_area_too_large.json"
        )
        project = create_project(path)

        # we expect that the function raises a CustomError due to the fact
        # that the area is too large
        self.assertRaises(CustomError, project.validate_geometries)

    def test_broken_geojson_string(self):
        """Test if validate_geometries throws an error
        if the provided geojson string is broken.
        This means we can't create the geo data layer with ogr."""

        path = (
            "fixtures/tile_map_service_grid/projects/projectDraft_broken_geojson.json"
        )
        project = create_project(path)

        # we expect that the function raises a CustomError due to the fact
        # that the geojson string is not in the right format
        self.assertRaises(CustomError, project.validate_geometries)


if __name__ == "__main__":
    unittest.main()
