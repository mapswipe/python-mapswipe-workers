import os

import unittest
import numpy as np
import pandas as pd
from shapely import wkt
from shapely.geometry import Point

from mapswipe_workers.utils.spatial_sampling  import distance_on_sphere, filter_points, calculate_spacing


class TestDistanceCalculations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "mapillary_sequence.csv",
                ),
                "r",
        ) as file:
            cls.fixture_df = pd.read_csv(file)

    def test_distance_on_sphere(self):
        p1 = Point(-74.006, 40.7128)
        p2 = Point(-118.2437, 34.0522)

        distance = distance_on_sphere((p1.x, p1.y), (p2.x, p2.y))
        expected_distance = 3940  # Approximate known distance in km

        self.assertTrue(np.isclose(distance, expected_distance, atol=50))

    def test_filter_points(self):
        data = {
            "data": [
                "POINT (-74.006 40.7128)",
                "POINT (-75.006 41.7128)",
                "POINT (-76.006 42.7128)",
                "POINT (-77.006 43.7128)"
            ]
        }
        df = pd.DataFrame(data)

        threshold_distance = 100
        filtered_df = filter_points(df, threshold_distance)

        self.assertIsInstance(filtered_df, pd.DataFrame)
        self.assertLessEqual(len(filtered_df), len(df))


    def test_calculate_spacing(self):
        data = {
            "data": [
                "POINT (-74.006 40.7128)",
                "POINT (-75.006 41.7128)",
                "POINT (-76.006 42.7128)",
                "POINT (-77.006 43.7128)"
            ],
            'timestamp': [1, 2, 3, 4]
        }
        df = pd.DataFrame(data)
        gdf = pd.DataFrame(df)

        interval_length = 100
        filtered_gdf = calculate_spacing(gdf, interval_length)

        self.assertTrue(filtered_gdf['timestamp'].is_monotonic_increasing)


    def test_calculate_spacing_with_sequence(self):
        threshold_distance = 5
        filtered_df = filter_points(self.fixture_df, threshold_distance)
        self.assertIsInstance(filtered_df, pd.DataFrame)
        self.assertLess(len(filtered_df), len(self.fixture_df))

        filtered_df.reset_index(drop=True, inplace=True)

        for i in range(len(filtered_df) - 1):
            geom1 = wkt.loads(filtered_df.loc[i, 'data'])
            geom2 = wkt.loads(filtered_df.loc[i + 1, 'data'])

            distance = geom1.distance(geom2)

            self.assertLess(distance, threshold_distance)




if __name__ == "__main__":
    unittest.main()
