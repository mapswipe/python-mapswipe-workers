from collections import defaultdict

from apps.aggregated.models import AggregatedUserGroupStatData
from asgiref.sync import sync_to_async
from django.db import models
from django.utils.functional import cached_property
from strawberry.dataloader import DataLoader

from .models import UserGroupUserMembership
from .types import UserGroupUserStatsType, UserUserGroupType


def load_user_group_user_stats(keys: list[str]) -> list[list[UserGroupUserStatsType]]:
    """
    Load user stats under user_group
    """
    aggregate_results = (
        AggregatedUserGroupStatData.objects.filter(user_group_id__in=keys)
        .order_by()
        .values("user_group_id", "user_id")
        .annotate(
            total_project=models.Count("project", distinct=True),
            total_swipe_count=models.Sum("task_count"),
            total_swipe_time=models.Sum("total_time"),
        )
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
        "user_group_id",
        "user_id",
        "user__username",
        "total_project",
        "total_swipe_count",
        "total_swipe_time",
    ):
        _map[user_group_id].append(
            UserGroupUserStatsType(
                user_id=user_id,
                user_name=username,
                total_swipes=total_swipe_count or 0,
                total_swipe_time=total_time,
                total_mapping_projects=mapped_project_count or 0,
            )
        )
    return [_map.get(key, []) for key in keys]


def load_user_usergroup_stats(keys: list[str]) -> list[list[UserUserGroupType]]:
    # Fetch user and user_group set
    user_user_groups_qs = UserGroupUserMembership.objects.filter(
        user_id__in=keys
    ).values_list("user_id", "user_group_id")
    user_user_groups_map = {
        user_id: user_group_id for user_id, user_group_id in user_user_groups_qs
    }
    # Fetch user_group from above set
    user_group_qs = (
        AggregatedUserGroupStatData.objects.filter(
            user_group_id__in=user_user_groups_map.values()
        )
        .order_by()
        .values("user_group_id")
        .annotate(members_count=models.Count("user_id"))
        .values_list("user_group_id", "user_group__name", "members_count")
    )
    user_groups_map = {
        user_group_id: {
            "user_group_id": user_group_id,
            "user_group_name": user_group_name,
            "members_count": members_count,
        }
        for user_group_id, user_group_name, members_count in user_group_qs
    }
    _map = defaultdict(list)
    for user_id, user_group_id in user_user_groups_map.items():
        _map[user_id].append(
            UserUserGroupType(
                **user_groups_map[user_group_id],
            )
        )
    return [_map.get(key, []) for key in keys]


class ExistingDatabaseDataLoader:
    @cached_property
    def load_user_group_user_stats(self) -> list[list[UserGroupUserStatsType]]:
        return DataLoader(load_fn=sync_to_async(load_user_group_user_stats))

    @cached_property
    def load_user_usergroup_stats(self) -> list[list[UserUserGroupType]]:
        return DataLoader(load_fn=sync_to_async(load_user_usergroup_stats))
