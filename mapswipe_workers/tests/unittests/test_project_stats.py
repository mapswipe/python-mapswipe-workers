import unittest
import pandas as pd
from mapswipe_workers.generate_stats.project_stats import (
    calc_agreement,
    calc_count,
    calc_share,
)
from tests.integration.base import BaseTestCase


class TestProjectStats(BaseTestCase):
    def test_calc_agreement(self):
        ds = pd.Series(
            data=[40, 15, 5, 17, 3],
            index=["total_count", "1_count", "2_count", "3_count", "4_count"],
        )
        agg2 = calc_agreement(ds)
        self.assertEqual(agg2, 0.32564102564102565)

    def test_calc_count(self):
        df = pd.DataFrame(
            data=[[1, 15, 5, 20], [1, 234, 45, 6]],
            columns=["taskId", "1_count", "2_count", "3_count"],
        )
        result = calc_count(df)
        self.assertEqual(result[0], 40)

    def test_calc_share(self):
        df = pd.DataFrame(
            data=[[1, 40, 15, 5, 20], [1, 285, 234, 45, 6]],
            columns=["taskId", "total_count", "1_count", "2_count", "3_count"],
        )
        share = calc_share(df)
        self.assertEqual(
            share.filter(like="share").iloc[0].tolist(), [0.375, 0.125, 0.5]
        )


if __name__ == "__main__":
    unittest.main()
