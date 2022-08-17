from collections import defaultdict
from typing import List

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import connections
from django.utils.functional import cached_property
from strawberry.dataloader import DataLoader
from shapely.geometry import shape

from .models import (
    Result,
    UserGroupResult,
    Project,
    User,
    UserGroupUserMembership,
    UserGroup
)
from .types import (
    SwipeStatType,
    ContributorType,
    ProjectTypeStats,
    ProjectSwipeTypeStats,
    CommunityStatsType,
    ContributorTimeType,
    UserSwipeStatType,
    OrganizationTypeStats,
    MapContributionTypeStats,
    UserLatestStatusTypeStats,
    UserGroupLatestType,
    UserUserGroupTypeStats
)


DEFAULT_STAT = SwipeStatType(
    total_swipe=0,
    total_swipe_time=0,
    total_mapping_projects=0,
)

DEFAULT_CONTRIBUTION_STAT = ContributorType(
    task_date=None,
    total_swipe=0
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
                COUNT(*) swipe_count,
                R.project_id as project_id
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING
                    (project_id, group_id, user_id)
            WHERE UGR.user_group_id = ANY(%s)
            GROUP BY project_id, group_id, UGR.user_group_id
        )
    SELECT
        user_group_id,
        COUNT(DISTINCT project_id) as mapped_project_count,
        SUM(swipe_count) as total_swipe_count,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time
    From user_group_grouped_data
    GROUP BY user_group_id
"""

USER_SWIPE_STAT_QUERY = f"""
    SELECT
        R.user_id as user_id,
        SUM(
        EXTRACT(
            EPOCH FROM (R.end_time - R.start_time)
        )
        ) as total_time,
        COUNT(*) swipe_count,
        COUNT(DISTINCT R.project_id) as mapped_project_count,
        COUNT(DISTINCT R.task_id) as task_count,
        COUNT(DISTINCT UGR.user_group_id) as total_user_group
        From {Result._meta.db_table} R
            LEFT JOIN {User._meta.db_table} U USING (user_id)
            LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (project_id, group_id, user_id)
    WHERE R.user_id = ANY(%s)
    GROUP BY user_id, R.project_id, group_id
"""

USER_ORGANIZATION_TYPE_STATS = f"""
    WITH
        user_data AS (
            SELECT
                R.user_id as user_id,
                COUNT(*) swipe_count,
                P.organization_name as organization
            From {Result._meta.db_table} R
                LEFT JOIN {Project._meta.db_table} as P USING (project_id)
            WHERE P.organization_id != 'null'
            GROUP BY organization, R.user_id
        )
    SELECT
        user_id,
        SUM(swipe_count) as swipe_count,
        organization
    From user_data
    GROUP BY organization, user_id
"""

USER_GROUP_ORGANIZATION_TYPE_STATS = f"""
    WITH
        user_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                COUNT(*) swipe_count,
                P.organization_name as organization
            From {Result._meta.db_table} R
                LEFT JOIN {Project._meta.db_table} as P USING (project_id)
                LEFT JOIN {UserGroupResult._meta.db_table} as UGR USING (project_id)
            WHERE P.organization_name != 'null'
            GROUP BY organization, UGR.user_group_id
        )
    SELECT
        user_group_id,
        SUM(swipe_count) as swipe_count,
        organization
    From user_data
    GROUP BY organization, user_group_id
"""

USER_GROUP_CONTRIBUTORS_STAT_QUERY = f"""
    WITH
        user_group_grouped_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                R.timestamp as timestamp,
                COUNT(*) swipe_count
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (user_id, project_id)
            WHERE UGR.user_group_id = ANY(%s)
            GROUP BY UGR.user_group_id, timestamp
        )
    SELECT
        user_group_id,
        SUM(swipe_count) as task_count,
        timestamp::date as task_date
    From user_group_grouped_data
    WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '30 days')
    GROUP BY user_group_id, task_date
"""


USER_CONTRIBUTORS_STAT_QUERY = f"""
    WITH
        -- Group by project_id, group_id, user_id to get
        -- timestamp,
        -- but the value is at project_id, group_id, user_id level
        user_data AS (
            SELECT
                U.user_id as user_id,
                R.timestamp as timestamp,
                COUNT(*) swipe_count
            From {Result._meta.db_table} R
                LEFT JOIN {User._meta.db_table} U USING (user_id)
            WHERE U.user_id = ANY(%s)
            GROUP BY project_id, U.user_id, timestamp
        )
    SELECT
        user_id,
        SUM(swipe_count) as swipe_count,
        timestamp::date as task_date
    From user_data
    WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '30 days')
    GROUP BY user_id, task_date
"""


USER_TIME_SPENT_CONTRIBUTION_QUERY = f"""
    WITH
        user_data AS (
            SELECT
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                R.timestamp as timestamp,
                U.user_id as user_id
            From {Result._meta.db_table} R
                LEFT JOIN {User._meta.db_table} U USING (user_id)
            WHERE U.user_id = ANY(%s)
            GROUP BY project_id, U.user_id, timestamp
        )
    SELECT
        user_id,
        timestamp::date as task_date,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time
    From user_data
    WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '30 days')
    GROUP BY user_id, task_date
"""

USER_PROJECT_TYPE_STATS_QUERY = f"""
    WITH
        project_data_type1 AS (
            SELECT
                R.user_id as user_id,
                P.project_type as project_type,
                st_area(geom) as area_sum
                FROM {Project._meta.db_table} P
                    LEFT JOIN {Result._meta.db_table} R USING (project_id)
            WHERE R.user_id = ANY(%s)
            GROUP BY project_type, R.user_id, area_sum
        )
    SELECT
        user_id,
        SUM(area_sum) as area_sum,
        project_type
    From project_data_type1
    GROUP BY user_id, project_type
"""

USER_GROUP_PROJECT_TYPE_STATS_QUERY = f"""
    WITH
        project_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                P.project_type as project_type,
                st_area(geom) as area_sum
                FROM {Project._meta.db_table} P
                    LEFT JOIN {Result._meta.db_table} R USING (project_id)
                    LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (project_id)
            WHERE UGR.user_group_id = ANY(%s)
            GROUP BY project_type, UGR.user_group_id, area_sum
        )
    SELECT
        user_group_id,
        SUM(area_sum) as area_sum,
        project_type
    From project_data
    GROUP BY user_group_id, project_type
"""

USER_PROJECT_SWIPE_TYPE_STATS_QUERY = f"""
    WITH
        project_data_type1 AS (
            SELECT
                R.user_id as user_id,
                P.project_type as project_type,
                COUNT(*) as swipes
                FROM {Result._meta.db_table} R
                    LEFT JOIN {Project._meta.db_table } P  USING (project_id)
            WHERE R.user_id = ANY(%s)
            GROUP BY project_type, R.user_id
        )
    SELECT
        user_id,
        SUM(swipes) as total_swipe,
        project_type
    From project_data_type1
    GROUP BY user_id, project_type
"""

USER_GROUP_PROJECT_SWIPE_TYPE_STATS_QUERY = f"""
    WITH
        project_data_type1 AS (
            SELECT
                UGR.user_group_id as user_group_id,
                P.project_type as project_type,
                COUNT(*) as swipes
                FROM {Result._meta.db_table} R
                    LEFT JOIN {Project._meta.db_table } P  USING (project_id)
                    LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (project_id, group_id, user_id)
            WHERE UGR.user_group_id = ANY(%s)
            GROUP BY project_type, UGR.user_group_id
        )
    SELECT
        user_group_id,
        SUM(swipes) as total_swipe,
        project_type
    From project_data_type1
    GROUP BY user_group_id, project_type
"""

USER_GROUP_USER_SWIPE_STAT_QUERY = f"""
    WITH
        user_group_grouped_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                R.user_id as user_id,
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                COUNT(*) swipe_count,
                R.project_id as project_id,
                R.task_id as task_id
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING
                    (project_id, group_id, user_id)
            WHERE
                UGR.user_group_id = %s
                AND R.user_id = ANY(%s)
            GROUP BY project_id, group_id, user_id, UGR.user_group_id, task_id
        )
    SELECT
        user_group_id,
        user_id,
        COUNT(DISTINCT project_id) as mapped_project_count,
        COUNT(DISTINCT task_id) as task_count,
        SUM(swipe_count) as total_swipe_count,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time
    From user_group_grouped_data
    GROUP BY user_group_id, user_id
"""

USER_GROUP_USER_CONTRIBUTORS_STAT_QUERY = f"""
    WITH
        -- Group by project_id, group_id, user_id and user_group_id to get
        -- timestamp,
        -- but the value is at project_id, group_id, user_id level
        user_group_grouped_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                R.timestamp as timestamp,
                R.task_id as task_id
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING
                    (project_id, group_id, user_id)
            WHERE
                UGR.user_group_id = ANY(%s)
                AND R.user_id = ANY(%s)
            GROUP BY project_id, group_id, user_id, UGR.user_group_id, task_id
        )
    SELECT
        user_group_id,
        user_id,
        COUNT(DISTINCT task_id) as task_count,
        timestamp::date as task_date
    From user_group_grouped_data
    WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '30 days')
    GROUP BY user_group_id, user_id, task_date
"""

USER_LATEST_STATS_QUERY = f"""
    WITH
        dashboard_data AS (
            SELECT
                R.user_id as user_id,
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                COUNT(*) swipe_count,
                R.timestamp as timestamp
            From {Result._meta.db_table} R
                LEFT JOIN {User._meta.db_table} U USING (user_id)
            WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '30 days')
            AND U.user_id = ANY(%s)
            GROUP BY user_id, timestamp
        ),
        user_group AS (
            SELECT
                UGR.user_group_id as user_group_id
            From {UserGroupResult._meta.db_table} UGR
                LEFT JOIN  {Result._meta.db_table} R  USING (user_id, project_id, group_id)
            WHERE timestamp::date >= (CURRENT_DATE- INTERVAL '30 days')
            GROUP BY user_id, timestamp, user_group_id
        )
    SELECT
        user_id,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time,
        COUNT( DISTINCT user_group_id) as total_group,
        SUM(swipe_count) as total_swipe
    From dashboard_data, user_group
    GROUP BY user_id
"""

USER_GEO_CONTRIBUTION_STATS_QUERY = f"""
    WITH
        project_data AS (
            SELECT
                R.user_id as user_id,
                ST_AsText(ST_Centroid(P.geom)) as geom,
                COUNT(*) swipe_count
                FROM {Result._meta.db_table} R
                    LEFT JOIN {Project._meta.db_table} P USING (project_id)
            WHERE R.user_id = ANY(%s)
            GROUP BY R.user_id, P.geom
        )
    SELECT
        user_id,
        SUM(swipe_count) as total_swipes,
        geom
    From project_data
    GROUP BY user_id, geom
"""

USER_GROUP_GEO_CONTRIBUTION_STATS_QUERY = f"""
    WITH
        project_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                ST_AsText(ST_Centroid(P.geom)) geom,
                COUNT(*) swipe_count
                FROM {Result._meta.db_table} R
                    LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (project_id, group_id, user_id)
                    LEFT JOIN {Project._meta.db_table} P USING (project_id)
            WHERE UGR.user_group_id = ANY(%s)
            GROUP BY UGR.user_group_id, P.geom
        )
    SELECT
        user_group_id,
        SUM(swipe_count) as total_swipes,
        geom
    From project_data
    GROUP BY user_group_id, geom
"""


USER_DASHBOARD_STATS_QUERY = f"""
    WITH
        dashboard_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                R.user_id as user_id,
                R.timestamp as timestamp,
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (user_id)
            WHERE timestamp::date >= (CURRENT_DATE- INTERVAL '30 days')
            AND R.user_id = ANY(%s)
            GROUP BY user_group_id, user_id, timestamp
        ),
        dashboard_twenty_four AS(
            SELECT
                COUNT(*) swipe_count,
                R.timestamp as timestamp
            From {Result._meta.db_table} R
            WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '1 days')
            GROUP BY timestamp

        )
    SELECT
        user_id,
        COUNT(DISTINCT user_group_id) as total_groups,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time,
        SUM(swipe_count) as total_swipe
    From dashboard_data, dashboard_twenty_four
"""

USER_GROUP_DASHBOARD_STATS_QUERY = f"""
    WITH
        dashboard_data AS (
            SELECT
                UGR.user_group_id as user_group_id,
                UGR.user_id as user_id,
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                COUNT(*) swipe_count,
                R.timestamp as timestamp
            From {Result._meta.db_table} R
                LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (user_id, project_id)
            WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '30 days')
            AND UGR.user_group_id = ANY(%s)
            GROUP BY timestamp, UGR.user_group_id, UGR.user_id
        )
    SELECT
        user_group_id,
        SUM(
            EXTRACT(
                EPOCH FROM (end_time - start_time)
            )
        ) as total_time,
        COUNT( DISTINCT user_id) as total_contributors,
        SUM(swipe_count) as total_swipe
    From dashboard_data
    GROUP BY user_group_id
"""


USER_USER_GROUP_STATS_QUERY = f"""
    WITH
        user_data AS (
            SELECT
                UG.name as user_group,
                M.user_id as user_id,
                M.joined_at[0] as joined_at
            FROM {UserGroupResult._meta.db_table} UGR
                LEFT JOIN  {UserGroup._meta.db_table} UG USING (user_group_id)
                LEFT JOIN {UserGroupUserMembership._meta.db_table} M USING (user_id)
            WHERE UGR.user_id = ANY(%s)
            GROUP BY M.user_id, user_group, joined_at
        )
    SELECT
        user_id,
        user_group,
        joined_at,
        COUNT(user_id) as members_count
    FROM user_data
    GROUP BY user_id, user_group, joined_at
"""


def load_user_group_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_SWIPE_STAT_QUERY, [keys])
        aggregate_results = cursor.fetchall()

    _map = {
        user_group_id: SwipeStatType(
            total_swipe=swipe_count or 0,
            total_swipe_time=round(total_time / 60) or 0,  # swipe time in minutes
            total_mapping_projects=mapped_project_count or 0,
        )
        for user_group_id, mapped_project_count, swipe_count, total_time in aggregate_results
    }
    return [_map.get(key, DEFAULT_STAT) for key in keys]


def user_group_latest_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_DASHBOARD_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()

    _map = {
        user_group_id: UserGroupLatestType(
            total_swipes=total_swipe or 0,
            total_swipe_time=round(total_time / 60) or 0,  # swipe time in minutes
            total_contributors=total_contributors
        )
        for user_group_id, total_time, total_contributors, total_swipe in aggregate_results
    }
    return [_map.get(key) for key in keys]


def load_user_group_contributors_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_CONTRIBUTORS_STAT_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_group_id, swipe_count, task_date in aggregate_results:
        _map[user_group_id].append(
            ContributorType(
                total_swipe=swipe_count or 0,
                task_date=task_date
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_project_type_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_PROJECT_TYPE_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_group_id, area_sum, project_type in aggregate_results:
        _map[user_group_id].append(
            ProjectTypeStats(
                area=area_sum or 0,
                project_type=project_type
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_organization_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_ORGANIZATION_TYPE_STATS, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_group_id, swipe_count, organization in aggregate_results:
        _map[user_group_id].append(
            OrganizationTypeStats(
                total_swipe=swipe_count or 0,
                organization_name=organization
            )
        )
    return [_map.get(key) for key in keys]


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
            for _, user_id, mapped_project_count, task_count, count, time in aggregate_results:
                _map[f"{user_group_id}-{user_id}"] = SwipeStatType(
                    total_swipe=count or 0,
                    total_swipe_time=round(time / 60) or 0,  # swipe time in minutes
                    total_mapping_projects=mapped_project_count or 0,
                    total_task=task_count or 0,
                )
    return [
        _map.get(f"{user_group_id}-{user_id}", DEFAULT_STAT)
        for user_group_id, user_id in keys
    ]


def load_user_group_user_contributors_stats(keys: List[str]):
    user_group_users_map = defaultdict(list)
    for user_group_id, user_id in keys:
        user_group_users_map[user_group_id].append(user_id)
    _map = defaultdict(list)
    for user_group_id, user_id in user_group_users_map.items():
        with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
            cursor.execute(USER_GROUP_USER_CONTRIBUTORS_STAT_QUERY, [keys])
            aggregate_results = cursor.fetchall()
        for _, user_id, swipe_count, task_date in aggregate_results:
            _map[f"{user_group_id}-{user_id}"].append(
                ContributorType(
                    total_swipe=swipe_count or 0,
                    task_date=task_date
                )
            )
    return [_map.get(f"{user_group_id}-{user_id}") for user_group_id, user_id in keys]


## User User Stats
def load_user_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_SWIPE_STAT_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = {
        user_id: UserSwipeStatType(
            total_swipe=swipe_count or 0,
            total_swipe_time=round(total_time / 60) or 0,  # swipe time in minutes
            total_mapping_projects=mapped_project_count or 0,
            total_task=task_count or 0,
            total_user_group=total_user_group or 0
        )
        for user_id, total_time, swipe_count, mapped_project_count, task_count, total_user_group in aggregate_results
    }
    return [_map.get(key) for key in keys]


def load_user_contribution_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_CONTRIBUTORS_STAT_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, swipe_count, task_date in aggregate_results:
        _map[user_id].append(
            ContributorType(
                total_swipe=swipe_count or 0,
                task_date=task_date
            )
        )
    return [_map.get(key) for key in keys]


def load_user_time_spending(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_TIME_SPENT_CONTRIBUTION_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, task_date, total_time in aggregate_results:
        _map[user_id].append(
            ContributorTimeType(
                total_time=round(total_time / 60) or 0,
                task_date=task_date
            )
        )
    return [_map.get(key) for key in keys]


def load_user_stats_project_type(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_PROJECT_TYPE_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, area_sum, project_type in aggregate_results:
        _map[user_id].append(
            ProjectTypeStats(
                area=area_sum or 0,
                project_type=project_type
            )
        )
    return [_map.get(key) for key in keys]


def load_user_stats_project_swipe_type(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_PROJECT_SWIPE_TYPE_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, total_swipe, project_type in aggregate_results:
        _map[user_id].append(
            ProjectSwipeTypeStats(
                total_swipe=total_swipe or 0,
                project_type=project_type
            )
        )
    return [_map.get(key) for key in keys]


def load_user_organization_swipe_type(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_ORGANIZATION_TYPE_STATS, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, total_swipe, organization_name in aggregate_results:
        _map[user_id].append(
            OrganizationTypeStats(
                total_swipe=total_swipe or 0,
                organization_name=organization_name
            )
        )
    return [_map.get(key) for key in keys]


def load_user_latest_stats_query(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_LATEST_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = {
        user_id: UserLatestStatusTypeStats(
            total_user_group=total_group,
            total_swipe=total_swipe,
            total_swipe_time=round(total_time / 60) or 0,
        )
        for user_id, total_time, total_group, total_swipe in aggregate_results
    }
    return [_map.get(key) for key in keys]


def load_user_geo_contribution(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GEO_CONTRIBUTION_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, total_swipes, geom in aggregate_results:
        geom_centroid = {
            "type": "Point",
            "coordinates": geom
        }
        _map[user_id].append(
            MapContributionTypeStats(
                geojson=geom_centroid,
                total_contribution=total_swipes
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_geo_contributions(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_GEO_CONTRIBUTION_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, total_swipes, geom in aggregate_results:
        geom_centroid = {
            "type": "Point",
            "coordinates": geom
        }
        _map[user_id].append(
            MapContributionTypeStats(
                geojson=geom_centroid or None,
                total_contribution=total_swipes or 0
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_stats_project_swipe_type(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_GROUP_PROJECT_SWIPE_TYPE_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_group_id, total_swipe, project_type in aggregate_results:
        _map[user_group_id].append(
            ProjectSwipeTypeStats(
                total_swipe=total_swipe or 0,
                project_type=project_type
            )
        )
    return [_map.get(key) for key in keys]


def load_user_usergroup_stats(keys: List[str]):
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(USER_USER_GROUP_STATS_QUERY, [keys])
        aggregate_results = cursor.fetchall()
    _map = defaultdict(list)
    for user_id, user_group, joined_at, members_count in aggregate_results:
        _map[user_id].append(
            UserUserGroupTypeStats(
                user_group=user_group or None,
                joined_at=joined_at or None,
                members_count=members_count or 0
            )
        )
    return [_map.get(key) for key in keys]


class ExistingDatabaseDataLoader:
    @cached_property
    def load_user_group_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_stats))

    @cached_property
    def load_user_group_user_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_user_stats))

    @cached_property
    def load_user_group_contributors_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_contributors_stats))

    @cached_property
    def load_user_group_project_type_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_project_type_stats))

    @cached_property
    def load_user_group_user_contributors_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_user_contributors_stats))

    @cached_property
    def load_user_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_stats))

    @cached_property
    def load_user_contribution_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_contribution_stats))

    @cached_property
    def load_user_time_spending(self):
        return DataLoader(load_fn=sync_to_async(load_user_time_spending))

    @cached_property
    def load_user_stats_project_type(self):
        return DataLoader(load_fn=sync_to_async(load_user_stats_project_type))

    @cached_property
    def load_user_stats_project_swipe_type(self):
        return DataLoader(load_fn=sync_to_async(load_user_stats_project_swipe_type))

    @cached_property
    def load_user_organization_swipe_type(self):
        return DataLoader(load_fn=sync_to_async(load_user_organization_swipe_type))

    @cached_property
    def load_user_latest_stats_query(self):
        return DataLoader(load_fn=sync_to_async(load_user_latest_stats_query))

    @cached_property
    def load_user_geo_contribution(self):
        return DataLoader(load_fn=sync_to_async(load_user_geo_contribution))

    @cached_property
    def load_user_group_geo_contributions(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_geo_contributions))

    @cached_property
    def user_group_latest_stats(self):
        return DataLoader(load_fn=sync_to_async(user_group_latest_stats))

    @cached_property
    def load_user_group_stats_project_swipe_type(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_stats_project_swipe_type))

    @cached_property
    def load_user_group_organization_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_organization_stats))

    @cached_property
    def load_user_usergroup_stats(Self):
        return DataLoader(load_fn=sync_to_async(load_user_usergroup_stats))
