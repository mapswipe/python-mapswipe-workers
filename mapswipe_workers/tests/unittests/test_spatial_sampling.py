import os
import unittest

import numpy as np
import pandas as pd
from shapely import wkt
from shapely.geometry import Point

from mapswipe_workers.utils.spatial_sampling import (
    distance_on_sphere,
    filter_points,
    spatial_sampling,
)


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
            df = pd.read_csv(file)
            df["geometry"] = df["geometry"].apply(wkt.loads)

            cls.fixture_df = df

    def test_distance_on_sphere(self):
        p1 = Point(-74.006, 40.7128)
        p2 = Point(-118.2437, 34.0522)

        distance = distance_on_sphere((p1.x, p1.y), (p2.x, p2.y))
        expected_distance = 3940  # Approximate known distance in km

        self.assertTrue(np.isclose(distance, expected_distance, atol=50))

    def test_filter_points(self):
        data = {
            "geometry": [
                "POINT (-74.006 40.7128)",
                "POINT (-75.006 41.7128)",
                "POINT (-76.006 42.7128)",
                "POINT (-77.006 43.7128)",
            ]
        }
        df = pd.DataFrame(data)

        df["geometry"] = df["geometry"].apply(wkt.loads)

        df["long"] = df["geometry"].apply(
            lambda geom: geom.x if geom.geom_type == "Point" else None
        )
        df["lat"] = df["geometry"].apply(
            lambda geom: geom.y if geom.geom_type == "Point" else None
        )
        threshold_distance = 100
        filtered_df = filter_points(df, threshold_distance)

        self.assertIsInstance(filtered_df, pd.DataFrame)
        self.assertLessEqual(len(filtered_df), len(df))

    def test_spatial_sampling_ordering(self):
        data = {
            "geometry": [
                "POINT (-74.006 40.7128)",
                "POINT (-75.006 41.7128)",
                "POINT (-76.006 42.7128)",
                "POINT (-77.006 43.7128)",
            ],
            "captured_at": [1, 2, 3, 4],
            "sequence_id": ["1", "1", "1", "1"],
        }
        df = pd.DataFrame(data)
        df["geometry"] = df["geometry"].apply(wkt.loads)

        interval_length = 0.1
        filtered_gdf = spatial_sampling(df, interval_length)

        self.assertTrue(filtered_gdf["captured_at"].is_monotonic_decreasing)

    def test_spatial_sampling_with_sequence(self):
        threshold_distance = 0.01
        filtered_df = spatial_sampling(self.fixture_df, threshold_distance)
        self.assertIsInstance(filtered_df, pd.DataFrame)
        self.assertLess(len(filtered_df), len(self.fixture_df))

        filtered_df.reset_index(drop=True, inplace=True)
        for i in range(len(filtered_df) - 1):
            geom1 = filtered_df.loc[i, "geometry"]
            geom2 = filtered_df.loc[i + 1, "geometry"]

            distance = geom1.distance(geom2)

            self.assertLess(distance, threshold_distance)


if __name__ == "__main__":
    unittest.main()
