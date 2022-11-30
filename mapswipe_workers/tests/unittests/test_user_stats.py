import os
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from mapswipe_workers.generate_stats.user_stats import get_agg_results_by_user_id


class TestUserStats(unittest.TestCase):
    def setUp(self) -> None:
        test_dir = os.path.dirname(__file__)
        data_dir = os.path.join(test_dir, "fixtures", "tile_map_service_grid")
        results_file = os.path.join(
            data_dir, "results", "results_-M7nTGflMusNxFd4iSfD.csv"
        )
        agg_results_file = os.path.join(
            data_dir, "agg_results", "agg_results_-M7nTGflMusNxFd4iSfD.csv"
        )
        user_stats_file = os.path.join(
            data_dir, "users", "users_-M7nTGflMusNxFd4iSfD.csv"
        )
        self.results_df = pd.read_csv(results_file)
        self.agg_results_df = pd.read_csv(agg_results_file)
        self.user_stats_df = pd.read_csv(user_stats_file)
        self.user_stats_df.drop(columns=["idx"], inplace=True)
        self.user_stats_df.sort_index(inplace=True)

    def test_get_agg_results_by_user_id(self):

        agg_results_by_user_id_df = get_agg_results_by_user_id(
            self.results_df, self.agg_results_df
        )
        agg_results_by_user_id_df.sort_index(inplace=True)

        print(agg_results_by_user_id_df)

        print(self.user_stats_df)

        assert_frame_equal(
            agg_results_by_user_id_df, self.user_stats_df, check_dtype=False
        )


if __name__ == "__main__":
    unittest.main()
