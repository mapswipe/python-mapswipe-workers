import unittest
import os
import json
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, MultiLineString, GeometryCollection
import pandas as pd
from unittest.mock import patch, MagicMock
from mapswipe_workers.utils.process_mapillary import create_tiles, download_and_process_tile, coordinate_download, geojson_to_polygon


# Assuming create_tiles, download_and_process_tile, and coordinate_download are imported

class TestTileGroupingFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "fixtures",
                "feature_collection.json",
            ),
            "r",
        ) as file:
            cls.fixture_data = json.load(file)

        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "fixtures",
                "mapillary_response.csv",
            ),
            "r",
        ) as file:
            cls.fixture_df = pd.read_csv(file)

    def setUp(self):
        self.token = "test_token"
        self.level = 14
        self.test_polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.test_multipolygon = MultiPolygon([self.test_polygon, Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])])
        self.empty_polygon = Polygon()
        self.empty_geometry = GeometryCollection()

    def test_create_tiles_with_valid_polygon(self):
        tiles = create_tiles(self.test_polygon, self.level)
        self.assertIsInstance(tiles, pd.DataFrame)
        self.assertFalse(tiles.empty)

    def test_create_tiles_with_multipolygon(self):
        tiles = create_tiles(self.test_multipolygon, self.level)
        self.assertIsInstance(tiles, pd.DataFrame)
        self.assertFalse(tiles.empty)

    def test_create_tiles_with_empty_polygon(self):
        tiles = create_tiles(self.empty_polygon, self.level)
        self.assertIsInstance(tiles, pd.DataFrame)
        self.assertTrue(tiles.empty)

    def test_create_tiles_with_empty_geometry(self):
        tiles = create_tiles(self.empty_geometry, self.level)
        self.assertIsInstance(tiles, pd.DataFrame)
        self.assertTrue(tiles.empty)

    def test_geojson_to_polygon_feature_collection_with_multiple_polygons(self):
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]}},
                {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)]]}}
            ]
        }
        result = geojson_to_polygon(geojson_data)
        self.assertIsInstance(result, MultiPolygon)
        self.assertEqual(len(result.geoms), 2)

    def test_geojson_to_polygon_single_feature_polygon(self):
        geojson_data = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
            }
        }
        result = geojson_to_polygon(geojson_data)
        self.assertIsInstance(result, Polygon)

    def test_geojson_to_polygon_single_feature_multipolygon(self):
        geojson_data = {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]],
                    [[(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)]]
                ]
            }
        }
        result = geojson_to_polygon(geojson_data)
        self.assertIsInstance(result, MultiPolygon)
        self.assertEqual(len(result.geoms), 2)

    def test_geojson_to_polygon_non_polygon_geometry_in_feature_collection(self):
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [(0, 0), (1, 1)]}}
            ]
        }
        with self.assertRaises(ValueError) as context:
            geojson_to_polygon(geojson_data)
        self.assertEqual(str(context.exception), "Non-polygon geometries cannot be combined into a MultiPolygon.")

    def test_geojson_to_polygon_empty_feature_collection(self):
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }
        result = geojson_to_polygon(geojson_data)
        self.assertTrue(result.is_empty)

    def test_geojson_to_polygon_contribution_geojson(self):
        result = geojson_to_polygon(self.fixture_data)
        self.assertIsInstance(result, Polygon)

    @patch('mapswipe_workers.utils.process_mapillary.vt2geojson_tools.vt_bytes_to_geojson')
    @patch('mapswipe_workers.utils.process_mapillary.requests.get')
    def test_download_and_process_tile_success(self, mock_get, mock_vt2geojson):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'mock vector tile data'  # Example mock data
        mock_get.return_value = mock_response

        # Mock the return value of vt_bytes_to_geojson
        mock_vt2geojson.return_value = {
            "features": [
                {"geometry": {"type": "Point", "coordinates": [0, 0]}, "properties": {"id": 1}}
            ]
        }

        row = {'x': 1, 'y': 1, 'z': 14}
        token = 'test_token'

        result, failed = download_and_process_tile(row, token)

        # Assertions
        self.assertIsNone(failed)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result['geometry'][0].wkt, 'POINT (0 0)')

    @patch('mapswipe_workers.utils.process_mapillary.requests.get')
    def test_download_and_process_tile_failure(self, mock_get):
        # Mock a failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        row = pd.Series({'x': 1, 'y': 1, 'z': self.level})
        result, failed = download_and_process_tile(row, self.token)

        self.assertIsNone(result)
        self.assertIsNotNone(failed)

    @patch('mapswipe_workers.utils.process_mapillary.download_and_process_tile')
    def test_coordinate_download(self, mock_download_and_process_tile):
        mock_download_and_process_tile.return_value = (pd.DataFrame([{"geometry": None}]), None)

        metadata, failed = coordinate_download(self.test_polygon, self.level, self.token)

        self.assertIsInstance(metadata, pd.DataFrame)
        self.assertTrue(failed.empty)

    @patch('mapswipe_workers.utils.process_mapillary.download_and_process_tile')
    def test_coordinate_download_with_failures(self, mock_download_and_process_tile):
        mock_download_and_process_tile.return_value = (None, pd.Series({"x": 1, "y": 1, "z": self.level}))

        metadata, failed = coordinate_download(self.test_polygon, self.level, self.token)

        self.assertTrue(metadata.empty)
        self.assertFalse(failed.empty)


if __name__ == '__main__':
    unittest.main()
