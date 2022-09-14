import datetime
import json
from typing import List

import strawberry
import strawberry_django
from django.conf import settings
from django.contrib.gis.db.models.functions import Area
from django.db import connections, models
from django.utils import timezone
from mapswipe.paginations import CountList, StrawberryDjangoCountList

from .filters import ProjectFilter, UserFilter, UserGroupFilter
from .models import AggregatedUserGroupStatData, AggregatedUserStatData, Project
from .ordering import UserGroupOrder
from .types import (
    CommunityStatsLatestType,
    CommunityStatsType,
    ContributorTimeType,
    MapContributionTypeStats,
    OrganizationTypeStats,
    ProjectSwipeTypeStats,
    ProjectType,
    ProjectTypeStats,
    UserGroupType,
    UserType,
)


def get_community_stats() -> CommunityStatsType:
    user_agg_data = AggregatedUserStatData.objects.aggregate(
        total_swipe=models.Sum("task_count"),
        total_users=models.Count("user", distinct=True),
    )
    user_group_agg_data = AggregatedUserGroupStatData.objects.aggregate(
        total_user_groups=models.Count("user_group", distinct=True),
    )
    return CommunityStatsType(
        total_contributors=user_agg_data["total_users"],
        total_groups=user_group_agg_data["total_user_groups"],
        total_swipes=user_agg_data["total_swipe"],
    )


def get_community_stats_latest() -> CommunityStatsLatestType:
    date_threshold = timezone.now() - datetime.timedelta(days=30)
    user_agg_data = AggregatedUserStatData.objects.filter(
        timestamp_date__gte=date_threshold
    ).aggregate(
        total_swipe=models.Sum("task_count"),
        total_users=models.Count("user", distinct=True),
    )
    user_group_agg_data = AggregatedUserGroupStatData.objects.filter(
        timestamp_date__gte=date_threshold
    ).aggregate(
        total_user_groups=models.Count("user_group", distinct=True),
    )
    return CommunityStatsLatestType(
        total_contributors_last_month=user_agg_data["total_users"],
        total_groups_last_month=user_group_agg_data["total_user_groups"],
        total_swipes_last_month=user_agg_data["total_swipe"],
    )


def get_project_type_query() -> List[ProjectTypeStats]:
    aggregate_results = (
        Project.objects.filter(project_type=1, geom__isnull=False)
        .order_by()
        .values("project_type")
        .annotate(
            # FIXME: This was used before SUM(st_area(P.geom::geography))
            area_sum=models.Sum(Area("geom"))
        )
        .values_list(
            "project_type",
            "area_sum",
        )
    )
    return [
        ProjectTypeStats(
            area=area_sum.sq_m,
            project_type=project_type,
        )
        for project_type, area_sum in aggregate_results
    ]


def get_project_swipe_type() -> List[ProjectSwipeTypeStats]:
    aggregate_results = (
        AggregatedUserStatData.objects.order_by()
        .values("project__project_type")
        .annotate(
            total_swipe=models.Sum("task_count"),
        )
        .values_list("project__project_type", "total_swipe")
    )
    return [
        ProjectSwipeTypeStats(
            total_swipe=total_swipe or 0,
            project_type=project_type,
        )
        for project_type, total_swipe in aggregate_results
    ]


def get_project_geo_area_type() -> List[MapContributionTypeStats]:
    # TODO: Use django-cte
    sql = f"""
        WITH project_data AS (
          SELECT
            project_id,
            -- AsGeoJSON(Centroid('project__geom')
            ST_AsGeoJSON(ST_Centroid(geom), 8) as centroid
          FROM {Project._meta.db_table}
          WHERE geom IS NOT NULL
        )
        SELECT
          project_data.centroid,
          SUM(agg_data.task_count) AS total_swipe_count
        FROM
          aggregated_project_user_timestamp__task_count_total_time as agg_data
              INNER JOIN project_data USING (project_id)
        GROUP BY
          project_data.centroid;
    """
    with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
        cursor.execute(sql, [])
        return [
            MapContributionTypeStats(
                total_contribution=swipe_count or 0,
                geojson=json.loads(geom),
            )
            for geom, swipe_count in cursor.fetchall()
        ]


def get_organization_stats() -> List[OrganizationTypeStats]:
    aggregate_results = (
        AggregatedUserStatData.objects.order_by()
        .values("project__organization_name")
        .annotate(total_swipe_count=models.Sum("task_count"))
        .values_list("project__organization_name", "total_swipe_count")
    )
    return [
        OrganizationTypeStats(
            organization_name=organization,
            total_swipe=count,
        )
        for organization, count in aggregate_results
    ]


@strawberry.type
class Query:
    users: CountList[UserType] = StrawberryDjangoCountList(
        pagination=True, filters=UserFilter
    )
    projects: CountList[ProjectType] = StrawberryDjangoCountList(
        pagination=True,
        filters=ProjectFilter,
    )

    user_groups: CountList[UserGroupType] = StrawberryDjangoCountList(
        pagination=True,
        filters=UserGroupFilter,
        order=UserGroupOrder,
    )
    user_group: UserGroupType = strawberry_django.field()
    user: UserType = strawberry_django.field()
    community_stats: CommunityStatsType = strawberry_django.field(get_community_stats)
    community_stast_lastest: CommunityStatsLatestType = strawberry_django.field(
        get_community_stats_latest
    )
    project_type_stats: ProjectTypeStats = strawberry_django.field(
        get_project_type_query
    )
    organization_type_stats: List[OrganizationTypeStats] = strawberry_django.field(
        get_organization_stats
    )
    project_swipe_type: List[ProjectSwipeTypeStats] = strawberry_django.field(
        get_project_swipe_type
    )
    project_geo_contribution: List[MapContributionTypeStats] = strawberry_django.field(
        get_project_geo_area_type
    )

    @strawberry.field
    async def contributor_time_stats(
        self,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
    ) -> List[ContributorTimeType]:
        qs = AggregatedUserStatData.objects.filter(
            timestamp_date__gte=from_date,
            timestamp_date__lte=to_date,
            total_time__isnull=False,
        )
        _qs = (
            qs.order_by("timestamp_date")
            .values("timestamp_date")
            .annotate(total_swipe_time=models.Sum("total_time"))
            .values_list(
                "timestamp_date",
                "total_swipe_time",
            )
        )
        return [
            ContributorTimeType(
                date=date,
                total=round(total or 0),
            )
            async for date, total in _qs
        ]
