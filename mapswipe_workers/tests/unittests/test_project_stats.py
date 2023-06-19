import unittest

import pandas as pd

from mapswipe_workers.generate_stats.project_stats import (
    add_missing_result_columns,
    calc_agreement,
    calc_count,
    calc_parent_option_count,
    calc_share,
    get_custom_options,
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

    def test_get_custom_options(self):
        for raw_custom_options, excepted_values in [
            (
                [
                    {"value": 0},
                    {"value": 1},
                    {"value": 2},
                    {"value": 3}
                ],
                {0: set(), 1: set(), 2: set(), 3: set()},
            ),
            (
                [
                    {
                        "value": 0,
                        "subOptions": [
                            {"value": 4}, {"value": 5}
                        ],
                    },
                    {"value": 1},
                    {"value": 2},
                    {"value": 3}
                ],
                {0: {4, 5}, 1: set(), 2: set(), 3: set()},
            ),
            (
                [
                    {
                        "value": 0,
                        "subOptions": [
                            {"value": 4}, {"value": 5}
                        ],
                    },
                    {"value": 1},
                    {"value": 2},
                    {
                        "value": 3,
                        "subOptions": [
                            {"value": 10},
                            {"value": 12}
                        ],
                    },
                ],
                {0: {4, 5}, 1: set(), 2: set(), 3: {10, 12}},
            ),
        ]:
            pd_series = pd.Series(data=[str(raw_custom_options)])
            parsed_custom_options = get_custom_options(pd_series)
            assert parsed_custom_options == excepted_values

    def test_add_missing_result_columns(self):
        df = pd.DataFrame(
            data=[
                ["project-1-group-1-task-1", 1],
                ["project-1-group-1-task-1", 5],
                ["project-1-group-2-task-1", 1],
                ["project-1-group-2-task-1", 1],
                ["project-1-group-2-task-1", 1],
                ["project-2-group-3-task-1", 2],
                ["project-2-group-1-task-1", 3],
            ],
            columns=[
                "task_id",
                "result",
            ],
        )
        df = (
            df.groupby(["task_id", "result"])
            .size()
            .unstack(fill_value=0)
        )
        updated_df = add_missing_result_columns(
            df,
            {
                1: {4, 5},
                2: {6},
                3: set(),
            },
        )
        # Existing columns
        assert list(df.columns) == [1, 2, 3, 5]
        # New columns
        assert list(updated_df.columns) == [1, 2, 3, 4, 5, 6]
        # Existing data
        assert df.to_csv() == (
            'task_id,1,2,3,5\n'
            'project-1-group-1-task-1,1,0,0,1\n'
            'project-1-group-2-task-1,3,0,0,0\n'
            'project-2-group-1-task-1,0,0,1,0\n'
            'project-2-group-3-task-1,0,1,0,0\n'
        )
        # New data
        assert updated_df.to_csv() == (
            'task_id,1,2,3,4,5,6\n'
            'project-1-group-1-task-1,1,0,0,0,1,0\n'
            'project-1-group-2-task-1,3,0,0,0,0,0\n'
            'project-2-group-1-task-1,0,0,1,0,0,0\n'
            'project-2-group-3-task-1,0,1,0,0,0,0\n'
        )

    def test_calc_parent_option_count(self):
        df = pd.DataFrame(
            data=[
                [1, 40, 1, 0, 20, 0, 1, 0],
                [2, 41, 0, 5, 20, 0, 0, 0],
                [3, 42, 10, 10, 20, 0, 0, 1],
                [4, 281, 0, 1, 0, 1, 1, 4],
                [5, 282, 15, 10, 0, 1, 2, 4],
                [1, 283, 2, 20, 0, 1, 0, 0],
            ],
            columns=[
                "taskId",
                "total_count",
                "1_count",
                "2_count",
                "3_count",
                "4_count",  # Child of 1
                "5_count",  # Child of 1
                "6_count",  # Child of 2
            ],
        )
        updated_df = calc_parent_option_count(
            df,
            {
                1: {4, 5},
                2: {6},
                3: set(),
            },
        )
        # Columns without child shouldn't change
        for column in [
            "taskId",
            "total_count",
            "3_count",
            "4_count",
            "5_count",
            "6_count",
        ]:
            assert df[column].compare(updated_df[column]).size == 0
        # Columns with child should change
        for column, updated_index, updated_value in [
            ("1_count", [0, 3, 4, 5], [2, 2, 18, 3]),
            ("2_count", [2, 3, 4], [11, 5, 14]),
        ]:
            compared = df[column].compare(updated_df[column])
            assert list(compared['other'].index) == updated_index
            assert list(compared['other']) == updated_value


if __name__ == "__main__":
    unittest.main()
