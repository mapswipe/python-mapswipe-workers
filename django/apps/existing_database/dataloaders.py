import json
import datetime
from collections import defaultdict
from typing import List

from asgiref.sync import sync_to_async
from django.utils import timezone
from django.db import models
from django.utils.functional import cached_property
from django.contrib.gis.db.models.functions import AsGeoJSON, Centroid
from strawberry.dataloader import DataLoader

from mapswipe.db import ArrayLength

from .models import (
    UserGroupUserMembership,
    UserGroupResult,
    AggregatedUserStatData,
    AggregatedUserGroupStatData,
)
from .types import (
    ContributorTimeType,
    ContributorType,
    MapContributionTypeStats,
    OrganizationTypeStats,
    ProjectSwipeTypeStats,
    ProjectTypeStats,
    SwipeStatType,
    UserGroupLatestType,
    UserGroupUserType,
    UserLatestStatusTypeStats,
    UserSwipeStatType,
    UserUserGroupTypeStats,
)

DEFAULT_STAT = SwipeStatType(
    total_swipe=0, total_swipe_time=0, total_mapping_projects=0, total_contributors=0
)

DEFAULT_CONTRIBUTION_STAT = ContributorType(task_date=None, total_swipe=0)


# USER_DASHBOARD_STATS_QUERY = f"""
#     WITH
#         dashboard_data AS (
#             SELECT
#                 UGR.user_group_id as user_group_id,
#                 R.user_id as user_id,
#                 R.timestamp as timestamp,
#                 MAX(R.start_time) as start_time,
#                 MAX(R.end_time) as end_time
#             From {Result._meta.db_table} R
#                 LEFT JOIN {UserGroupResult._meta.db_table} UGR USING (user_id)
#             WHERE timestamp::date >= (CURRENT_DATE- INTERVAL '30 days')
#             AND R.user_id = ANY(%s)
#             GROUP BY user_group_id, user_id, timestamp
#         ),
#         dashboard_twenty_four AS(
#             SELECT
#                 COUNT(*) swipe_count,
#                 R.timestamp as timestamp
#             From {Result._meta.db_table} R
#             WHERE timestamp::date >= (CURRENT_DATE - INTERVAL '1 days')
#             GROUP BY timestamp
#         )
#     SELECT
#         user_id,
#         COUNT(DISTINCT user_group_id) as total_groups,
#         SUM(
#             EXTRACT(
#                 EPOCH FROM (end_time - start_time)
#             )
#         ) as total_time,
#         SUM(swipe_count) as total_swipe
#     From dashboard_data, dashboard_twenty_four
# """


def load_user_group_stats(keys: List[str]):
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys)\
        .order_by().values('user_group_id')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
            total_swipe_time=models.Sum('total_time'),
            total_contributors=models.Count('user_id', distinct=True),
            total_project=models.Count('project_id', distinct=True),
        )
    _map = {
        user_group_id: SwipeStatType(
            total_swipe=swipe_count or 0,
            total_swipe_time=round(total_time or 0 / 60),  # swipe time in minutes
            total_mapping_projects=mapped_project_count or 0,
            total_contributors=total_contributors or 0,
        )
        for (
            user_group_id,
            swipe_count,
            total_time,
            total_contributors,
            mapped_project_count,
        ) in aggregate_results.values_list(
            'user_group_id',
            'total_swipe_count',
            'total_swipe_time',
            'total_contributors',
            'total_project',
        )
    }
    return [_map.get(key, DEFAULT_STAT) for key in keys]


def user_group_latest_stats(keys: List[str]):
    date_threshold = timezone.now() - datetime.timedelta(days=30)
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys, timestamp_date__gte=date_threshold)\
        .order_by().values('user_group_id')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
            total_swipe_time=models.Sum('total_time'),
            total_contributors=models.Count('user_id', distinct=True),
            total_project=models.Count('project_id', distinct=True),
        )
    _map = {
        user_group_id: UserGroupLatestType(
            total_swipes=total_swipe or 0,
            total_swipe_time=round(total_time or 0 / 60),  # swipe time in minutes
            total_contributors=total_contributors,
        )
        for (
            user_group_id,
            total_swipe,
            total_time,
            total_contributors,
        ) in aggregate_results.values_list(
            'user_group_id',
            'total_swipe_count',
            'total_swipe_time',
            'total_contributors',
        )
    }
    return [_map.get(key) for key in keys]


def load_user_group_contributors_stats(keys: List[str]):
    date_threshold = timezone.now() - datetime.timedelta(days=30)
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys, timestamp_date__gte=date_threshold)\
        .order_by().values('user_group_id', 'timestamp_date')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        ).order_by('timestamp_date')
    _map = defaultdict(list)
    for user_group_id, task_date, swipe_count in aggregate_results.values_list(
        'user_group_id',
        'timestamp_date',
        'total_swipe_count',
    ):
        _map[user_group_id].append(
            ContributorType(
                total_swipe=swipe_count or 0,
                task_date=task_date
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_project_type_stats(keys: List[str]):
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys)\
        .order_by().values('user_group_id', 'project__project_type')\
        .annotate(
            total_area_swiped=models.Sum('area_swiped'),
        )
    _map = defaultdict(list)
    for user_group_id, project_type, area_sum in aggregate_results.values_list(
        'user_group_id',
        'project__project_type',
        'total_area_swiped',
    ):
        _map[user_group_id].append(
            ProjectTypeStats(
                area=area_sum or 0,
                project_type=project_type,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_organization_stats(keys: List[str]):
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys)\
        .exclude(project__organization_name='null')\
        .order_by().values('user_group_id', 'project__organization_name')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        )
    _map = defaultdict(list)
    for user_group_id, organization, swipe_count in aggregate_results.values_list(
        'user_group_id',
        'project__organization_name',
        'total_swipe_count',
    ):
        _map[user_group_id].append(
            OrganizationTypeStats(
                total_swipe=swipe_count or 0,
                organization_name=organization,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_user_stats(keys: List[str]):
    """
    Load user stats under user_group
    """
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys)\
        .order_by().values('user_group_id', 'user_id')\
        .annotate(
            total_project=models.Count('project', distinct=True),
            total_swipe_count=models.Sum('task_count'),
            total_swipe_time=models.Sum('total_time'),
        )
    _map = defaultdict(list)
    for (
        user_group_id,
        user_id,
        username,
        mapped_project_count,
        total_swipe_count,
        total_time,
    ) in aggregate_results.values_list(
        'user_group_id',
        'user_id',
        'user__username',
        'total_project',
        'total_swipe_count',
        'total_swipe_time',
    ):
        _map[user_group_id].append(
            UserGroupUserType(
                user_id=user_id,
                user_name=username,
                total_swipes=total_swipe_count or 0,
                total_swipe_time=round(total_time or 0 / 60),  # swipe time in minutes
                total_mapping_projects=mapped_project_count or 0,
            )
        )
    return [_map.get(key) for key in keys]


# def load_user_group_user_contributors_stats(keys: List[str]):
#     aggregate_results = AggregatedUserGroupStatData.objects\
#         .filter(user_group_id__in=keys)\
#         .order_by().values('user_group_id', 'user_id')\
#         .annotate(
#             total_swipe_count=models.Sum('task_count'),
#             total_swipe_time=models.Sum('total_time'),
#         )
#     _map = defaultdict(list)
#     for (
#         user_group_id,
#         user_id,
#         swipe_count,
#         task_date,
#     ) in aggregate_results.values_list(
#         'user_group_id',
#         'user_id',
#         'total_swipe_count',
#         'total_swipe_time',
#     ):
#         _map[f"{user_group_id}-{user_id}"].append(
#             ContributorType(total_swipe=swipe_count or 0, task_date=task_date)
#         )
#     return [_map.get(f"{user_group_id}-{user_id}") for user_group_id, user_id in keys]


def load_user_group_contribution_time(keys: List[str]):
    date_threshold = timezone.now() - datetime.timedelta(days=30)
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys, timestamp_date__gte=date_threshold)\
        .order_by().values('user_group_id', 'timestamp_date')\
        .annotate(
            total_swipe_time=models.Sum('total_time'),
        ).order_by('timestamp_date')
    _map = defaultdict(list)
    for user_group_id, task_date, total_time in aggregate_results.values_list(
        'user_group_id',
        'timestamp_date',
        'total_swipe_time',
    ):
        _map[user_group_id].append(
            ContributorTimeType(
                date=task_date,
                total=round(total_time or 0 / 60),
            )
        )
    return [_map.get(key) for key in keys]


# User User Stats
def load_user_stats(keys: List[str]):
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys)\
        .order_by().values('user_id')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
            total_swipe_time=models.Sum('total_time'),
            total_project=models.Count('project_id'),
        )
    user_group_result_qs = UserGroupResult.objects\
        .filter(user_id__in=keys)\
        .order_by().values('user_id')\
        .annotate(count=models.Count('user_group_id', distinct=True))
    user_user_group_count = {
        user_id: count
        for user_id, count in user_group_result_qs.values_list('user_id', 'count')
    }
    _map = {
        user_id: UserSwipeStatType(
            total_swipe=round(total_swipe_count or 0) or 0,
            total_swipe_time=round(total_time or 0 / 60) or 0,  # swipe time in minutes
            total_mapping_projects=round(total_project or 0) or 0,
            total_user_group=round(user_user_group_count.get(user_id, 0)) or 0,
        )
        for (
            user_id,
            total_swipe_count,
            total_time,
            total_project,
        ) in aggregate_results.values_list(
            'user_id',
            'total_swipe_count',
            'total_swipe_time',
            'total_project',
        )
    }
    return [_map.get(key) for key in keys]


def load_user_contribution_stats(keys: List[str]):
    date_threshold = timezone.now() - datetime.timedelta(days=30)
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys, timestamp_date__gte=date_threshold)\
        .order_by().values('user_id', 'timestamp_date')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        ).order_by('timestamp_date')
    _map = defaultdict(list)
    for user_id, task_date, swipe_count in aggregate_results.values_list(
        'user_id', 'timestamp_date', 'total_swipe_count',
    ):
        _map[user_id].append(
            ContributorType(
                total_swipe=swipe_count or 0,
                task_date=task_date,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_time_spending(keys: List[str]):
    date_threshold = timezone.now() - datetime.timedelta(days=30)
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys, timestamp_date__gte=date_threshold)\
        .order_by().values('user_id', 'timestamp_date')\
        .annotate(
            total_swipe_time=models.Sum('total_time'),
        ).order_by('timestamp_date')
    _map = defaultdict(list)
    for user_id, task_date, total_time in aggregate_results.values_list(
        'user_id',
        'timestamp_date',
        'total_swipe_time',
    ):
        _map[user_id].append(
            ContributorTimeType(
                date=task_date,
                total=round(total_time or 0 / 60),
            )
        )
    return [_map.get(key) for key in keys]


def load_user_stats_project_type(keys: List[str]):
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys)\
        .order_by().values('user_id', 'project__project_type')\
        .annotate(
            total_area_swiped=models.Sum('area_swiped'),
        )
    _map = defaultdict(list)
    for user_id, project_type, area_sum in aggregate_results.values_list(
        'user_id',
        'project__project_type',
        'total_area_swiped',
    ):
        _map[user_id].append(
            ProjectTypeStats(
                area=area_sum or 0,
                project_type=project_type,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_stats_project_swipe_type(keys: List[str]):
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys)\
        .order_by().values('user_id', 'project__project_type')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        )
    _map = defaultdict(list)
    for user_id, project_type, total_swipe in aggregate_results.values_list(
        'user_id',
        'project__project_type',
        'total_swipe_count',
    ):
        _map[user_id].append(
            ProjectSwipeTypeStats(
                total_swipe=total_swipe or 0,
                project_type=project_type,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_organization_swipe_type(keys: List[str]):
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys, project__organization_name__isnull=False)\
        .order_by().values('user_id', 'project__organization_name')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        )
    _map = defaultdict(list)
    for user_id, organization_name, total_swipe in aggregate_results.values_list(
        'user_id',
        'project__organization_name',
        'total_swipe_count',
    ):
        _map[user_id].append(
            OrganizationTypeStats(
                total_swipe=total_swipe or 0,
                organization_name=organization_name,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_latest_stats_query(keys: List[str]):
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys)\
        .order_by().values('user_id')\
        .annotate(
            total_swipe_time=models.Sum('total_time'),
            total_group_count=ArrayLength('user_group_ids'),
            total_swipe_count=models.Sum('task_count'),
        )
    _map = {
        user_id: UserLatestStatusTypeStats(
            total_user_group=round(total_group or 0),
            total_swipe=round(total_swipe or 0),
            total_swipe_time=round(total_time or 0 / 60),
        )
        for (
            user_id,
            total_time,
            total_group,
            total_swipe,
        ) in aggregate_results.values_list(
            'user_id',
            'total_swipe_time',
            'total_group_count',
            'total_swipe_count',
        )
    }
    return [_map.get(key) for key in keys]


def load_user_geo_contribution(keys: List[str]):
    # FIXME: Different results
    aggregate_results = AggregatedUserStatData.objects\
        .filter(user_id__in=keys, project__geom__isnull=False)\
        .order_by().values('user_id', 'project_id')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        )
    _map = defaultdict(list)
    for user_id, geom, total_swipes in aggregate_results.values_list(
        'user_id',
        AsGeoJSON(Centroid('project__geom')),
        'total_swipe_count',
    ):
        if geom is None:
            continue
        _map[user_id].append(
            MapContributionTypeStats(
                geojson=json.loads(geom),
                total_contribution=total_swipes
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_geo_contributions(keys: List[str]):
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys, project__geom__isnull=False)\
        .order_by().values('user_group_id', 'project_id')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        )
    _map = defaultdict(list)
    for user_group_id, geom, total_swipes in aggregate_results.values_list(
        'user_group_id',
        AsGeoJSON(Centroid('project__geom')),
        'total_swipe_count',
    ):
        _map[user_group_id].append(
            MapContributionTypeStats(
                geojson=json.loads(geom),
                total_contribution=total_swipes or 0,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_group_stats_project_swipe_type(keys: List[str]):
    aggregate_results = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=keys)\
        .order_by().values('user_group_id', 'project__project_type')\
        .annotate(
            total_swipe_count=models.Sum('task_count'),
        )
    _map = defaultdict(list)
    for user_group_id, project_type, total_swipe in aggregate_results.values_list(
        'user_group_id',
        'project__project_type',
        'total_swipe_count',
    ):
        _map[user_group_id].append(
            ProjectSwipeTypeStats(
                total_swipe=total_swipe or 0,
                project_type=project_type,
            )
        )
    return [_map.get(key) for key in keys]


def load_user_usergroup_stats(keys: List[str]):
    # Fetch user and user_group set
    user_user_groups_qs = UserGroupUserMembership.objects\
        .filter(user_id__in=keys)\
        .values_list('user_id', 'user_group_id')
    user_user_groups_map = {
        user_id: user_group_id
        for user_id, user_group_id in user_user_groups_qs
    }
    # Fetch user_group from above set
    user_group_qs = AggregatedUserGroupStatData.objects\
        .filter(user_group_id__in=user_user_groups_map.values())\
        .order_by().values('user_group_id')\
        .annotate(
            members_count=models.Count('user_id')
        ).values_list('user_group_id', 'user_group__name', 'members_count')
    user_groups_map = {
        user_group_id: {
            'user_group_id': user_group_id,
            'user_group_name': user_group_name,
            'members_count': members_count,
        }
        for user_group_id, user_group_name, members_count in user_group_qs
    }
    _map = defaultdict(list)
    for user_id, user_group_id in user_user_groups_map.items():
        _map[user_id].append(
            UserUserGroupTypeStats(
                **user_groups_map[user_group_id],
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

    # @cached_property
    # def load_user_group_user_contributors_stats(self):
    #     return DataLoader(
    #         load_fn=sync_to_async(load_user_group_user_contributors_stats)
    #     )

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
        return DataLoader(
            load_fn=sync_to_async(load_user_group_stats_project_swipe_type)
        )

    @cached_property
    def load_user_group_organization_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_organization_stats))

    @cached_property
    def load_user_usergroup_stats(self):
        return DataLoader(load_fn=sync_to_async(load_user_usergroup_stats))

    @cached_property
    def load_user_group_contribution_time(self):
        return DataLoader(load_fn=sync_to_async(load_user_group_contribution_time))
