import unittest
import os
import json
from shapely.geometry import (
    Polygon,
    MultiPolygon,
    Point,
    LineString,
    MultiLineString,
    GeometryCollection,
)
from shapely import wkt
import pandas as pd
from unittest.mock import patch, MagicMock
from mapswipe_workers.utils.process_mapillary import (
    create_tiles,
    download_and_process_tile,
    coordinate_download,
    geojson_to_polygon,
    filter_by_timerange,
    filter_results,
    get_image_metadata,
)


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
            df = pd.read_csv(file)
            df['geometry'] = df['geometry'].apply(wkt.loads)
            cls.fixture_df = df

    def setUp(self):
        self.level = 14
        self.test_polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.test_multipolygon = MultiPolygon(
            [self.test_polygon, Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])]
        )
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
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]],
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)]],
                    },
                },
            ],
        }
        result = geojson_to_polygon(geojson_data)
        self.assertIsInstance(result, MultiPolygon)
        self.assertEqual(len(result.geoms), 2)

    def test_geojson_to_polygon_single_feature_polygon(self):
        geojson_data = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]],
            },
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
                    [[(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)]],
                ],
            },
        }
        result = geojson_to_polygon(geojson_data)
        self.assertIsInstance(result, MultiPolygon)
        self.assertEqual(len(result.geoms), 2)

    def test_geojson_to_polygon_non_polygon_geometry_in_feature_collection(self):
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [(0, 0), (1, 1)]},
                }
            ],
        }
        with self.assertRaises(ValueError) as context:
            geojson_to_polygon(geojson_data)
        self.assertEqual(str(context.exception), "Non-polygon geometries cannot be combined into a MultiPolygon.")

    def test_geojson_to_polygon_empty_feature_collection(self):
        geojson_data = {"type": "FeatureCollection", "features": []}
        result = geojson_to_polygon(geojson_data)
        self.assertTrue(result.is_empty)

    def test_geojson_to_polygon_contribution_geojson(self):
        result = geojson_to_polygon(self.fixture_data)
        self.assertIsInstance(result, Polygon)

    @patch(
        "mapswipe_workers.utils.process_mapillary.vt2geojson_tools.vt_bytes_to_geojson"
    )
    @patch("mapswipe_workers.utils.process_mapillary.requests.get")
    def test_download_and_process_tile_success(self, mock_get, mock_vt2geojson):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"mock vector tile data"  # Example mock data
        mock_get.return_value = mock_response

        mock_vt2geojson.return_value = {
            "features": [
                {
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"id": 1},
                }
            ]
        }

        row = {"x": 1, "y": 1, "z": 14}

        result = download_and_process_tile(row)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result["geometry"][0].wkt, "POINT (0 0)")

    @patch("mapswipe_workers.utils.process_mapillary.requests.get")
    def test_download_and_process_tile_failure(self, mock_get):
        # Mock a failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        row = pd.Series({"x": 1, "y": 1, "z": self.level})
        result = download_and_process_tile(row)

        self.assertIsNone(result)

    @patch("mapswipe_workers.utils.process_mapillary.download_and_process_tile")
    def test_coordinate_download(self, mock_download_and_process_tile):
        mock_download_and_process_tile.return_value = (
            pd.DataFrame([{"geometry": None}]),
            None,
        )

        metadata = coordinate_download(
            self.test_polygon, self.level
        )

        self.assertIsInstance(metadata, pd.DataFrame)

    @patch("mapswipe_workers.utils.process_mapillary.download_and_process_tile")
    def test_coordinate_download_with_failures(self, mock_download_and_process_tile):
        mock_download_and_process_tile.return_value = (
            None,
            pd.Series({"x": 1, "y": 1, "z": self.level}),
        )

        metadata = coordinate_download(
            self.test_polygon, self.level
        )

        self.assertTrue(metadata.empty)

    def test_filter_within_time_range(self):
        start_time = "2016-01-20 00:00:00"
        end_time = "2022-01-21 23:59:59"
        filtered_df = filter_by_timerange(self.fixture_df, start_time, end_time)

        self.assertEqual(len(filtered_df), 3)
        self.assertTrue(all(filtered_df["captured_at"] >= pd.to_datetime(start_time)))
        self.assertTrue(all(filtered_df["captured_at"] <= pd.to_datetime(end_time)))

    def test_filter_without_end_time(self):
        start_time = "2020-01-20 00:00:00"
        filtered_df = filter_by_timerange(self.fixture_df, start_time)

        self.assertEqual(len(filtered_df), 3)
        self.assertTrue(all(filtered_df["captured_at"] >= pd.to_datetime(start_time)))

    def test_filter_time_no_data(self):
        start_time = "2016-01-30 00:00:00"
        end_time = "2016-01-31 00:00:00"
        filtered_df = filter_by_timerange(self.fixture_df, start_time, end_time)
        self.assertTrue(filtered_df.empty)

    def test_filter_default(self):
        filtered_df = filter_results(self.fixture_df)
        self.assertTrue(len(filtered_df) == len(self.fixture_df))

    def test_filter_pano_true(self):
        filtered_df = filter_results(self.fixture_df, is_pano=True)
        self.assertEqual(len(filtered_df), 3)

    def test_filter_pano_false(self):
        filtered_df = filter_results(self.fixture_df, is_pano=False)
        self.assertEqual(len(filtered_df), 3)

    def test_filter_organization_id(self):
        filtered_df = filter_results(self.fixture_df, organization_id=1)
        self.assertEqual(len(filtered_df), 1)

    def test_filter_time_range(self):
        start_time = "2016-01-20 00:00:00"
        end_time = "2022-01-21 23:59:59"
        filtered_df = filter_results(
            self.fixture_df, start_time=start_time, end_time=end_time
        )
        self.assertEqual(len(filtered_df), 3)

    def test_filter_no_rows_after_filter(self):
        filtered_df = filter_results(self.fixture_df, is_pano="False")
        self.assertTrue(filtered_df.empty)

    def test_filter_missing_columns(self):
        columns_to_check = ["is_pano", "organization_id", "captured_at"]  # Add your column names here
        for column in columns_to_check:
            df_copy = self.fixture_df.copy()
            df_copy[column] = None
            if column == "captured_at":
                column = "start_time"

            result = filter_results(df_copy, **{column: True})
            self.assertIsNone(result)

    @patch("mapswipe_workers.utils.process_mapillary.coordinate_download")
    def test_get_image_metadata(self, mock_coordinate_download):
        mock_coordinate_download.return_value = self.fixture_df
        result = get_image_metadata(self.fixture_data)
        self.assertIsInstance(result, dict)
        self.assertIn("ids", result)
        self.assertIn("geometries", result)


    @patch("mapswipe_workers.utils.process_mapillary.coordinate_download")
    def test_get_image_metadata_filtering(self, mock_coordinate_download):
        mock_coordinate_download.return_value = self.fixture_df

        params = {
            "is_pano": True,
            "start_time": "2016-01-20 00:00:00",
            "end_time": "2022-01-21 23:59:59",
        }

        result = get_image_metadata(self.fixture_data, **params)
        self.assertIsInstance(result, dict)
        self.assertIn("ids", result)
        self.assertIn("geometries", result)


    @patch("mapswipe_workers.utils.process_mapillary.coordinate_download")
    def test_get_image_metadata_no_rows(self, mock_coordinate_download):
        mock_coordinate_download.return_value = self.fixture_df

        params = {
            "is_pano": True,
            "start_time": "1916-01-20 00:00:00",
            "end_time": "1922-01-21 23:59:59",
        }
        with self.assertRaises(ValueError):
            get_image_metadata(self.fixture_data, **params)

    @patch("mapswipe_workers.utils.process_mapillary.coordinate_download")
    def test_get_image_metadata_empty_response(self, mock_coordinate_download):
        df = self.fixture_df.copy()
        df = df.drop(df.index)
        mock_coordinate_download.return_value = df

        with self.assertRaises(ValueError):
            get_image_metadata(self.fixture_data)

    @patch("mapswipe_workers.utils.process_mapillary.filter_results")
    @patch("mapswipe_workers.utils.process_mapillary.coordinate_download")
    def test_get_image_metadata_size_restriction(self, mock_coordinate_download, mock_filter_results):
        mock_filter_results.return_value = pd.DataFrame({'ID': range(1, 100002)})
        mock_coordinate_download.return_value = self.fixture_df

        with self.assertRaises(ValueError):
            get_image_metadata(self.fixture_data)


if __name__ == "__main__":
    unittest.main()
