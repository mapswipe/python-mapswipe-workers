from collections import defaultdict
from typing import List

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import connections
from django.utils.functional import cached_property
from strawberry.dataloader import DataLoader

from .models import Result, UserGroupResult
from .types import SwipeStatType

DEFAULT_STAT = SwipeStatType(
    total_swipe=0,
    total_swipe_time=0,
)


USER_GROUP_SWIPE_STAT_QUERY = f"""
    WITH
        -- Group by project_id, group_id, user_id and user_group_id to get
        -- Max start_time and end_time as they are repeated for each task,
        -- but the value is at project_id, group_id, user_id level
        user_group_grouped_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                COUNT(*) swipe_count
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING
                    (project_id, group_id, user_id)
            WHERE UGR.user_group_id = ANY(%s)
            GROUP BY project_id, group_id, user_id, UGR.user_group_id
        )
    SELECT
        user_group_id,
        SUM(swipe_count) as total_swipe_count,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time
    From user_group_grouped_data
    GROUP BY user_group_id
"""


USER_GROUP_USER_SWIPE_STAT_QUERY = f"""
    WITH
        user_group_grouped_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                R.user_id as user_id,
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                COUNT(*) swipe_count
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING
                    (project_id, group_id, user_id)
            WHERE
                UGR.user_group_id = %s
                AND R.user_id = ANY(%s)
            GROUP BY project_id, group_id, user_id, UGR.user_group_id
        )
    SELECT
        user_group_id,
        user_id,
        SUM(swipe_count) as total_swipe_count,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time
    From user_group_grouped_data
    GROUP BY user_group_id, user_id
"""


def load_user_group_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_SWIPE_STAT_QUERY, [keys])
        aggregate_results = cursor.fetchall()

    _map = {
        user_group_id: SwipeStatType(
            total_swipe=swipe_count or 0,
            total_swipe_time=total_time or 0,
        )
        for user_group_id, swipe_count, total_time in aggregate_results
    }
    return [_map.get(key, DEFAULT_STAT) for key in keys]


def load_user_group_user_stats(keys: List[List[str]]):
    """
    Load user stats under user_group
    """
    user_group_users_map = defaultdict(list)
    for user_group_id, user_id in keys:
        user_group_users_map[user_group_id].append(user_id)

    _map = defaultdict()
    for user_group_id, users_id in user_group_users_map.items():
        # NOTE: N+1, but this should be used for one user_group at a time.
        with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
            cursor.execute(USER_GROUP_USER_SWIPE_STAT_QUERY, [user_group_id, users_id])
            aggregate_results = cursor.fetchall()
            for _, user_id, count, time in aggregate_results:
                _map[f"{user_group_id}-{user_id}"] = SwipeStatType(
                    total_swipe=count or 0,
                    total_swipe_time=time or 0,
                )
    return [
        _map.get(f"{user_group_id}-{user_id}", DEFAULT_STAT)
        for user_group_id, user_id in keys
    ]


class ExistingDatabaseDataLoader:
    @cached_property
    def load_user_group_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_stats))

    @cached_property
    def load_user_group_user_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_user_stats))
