import datetime
import json
from typing import List, Union
from dataclasses import InitVar

import strawberry
import strawberry_django
from django_cte import With
from django.db import models
from django.utils import timezone
from django.contrib.gis.db.models.functions import Centroid

from mapswipe.paginations import CountList, StrawberryDjangoCountList
from mapswipe.types import AreaSqKm

from apps.aggregated.models import AggregatedUserGroupStatData, AggregatedUserStatData

from .filters import ProjectFilter, UserFilter, UserGroupFilter
from .models import Project
from .ordering import UserGroupOrder
from .types import (
    CommunityStatsType,
    ContributorTimeStatType,
    DateRangeInput,
    MapContributionStatsType,
    OrganizationSwipeStatsType,
    ProjectTypeSwipeStatsType,
    ProjectType,
    ProjectTypeAreaStatsType,
    UserGroupType,
    UserType,
    UserStats,
    UserGroupStats,
)


def get_community_stats() -> CommunityStatsType:
    user_agg_data = AggregatedUserStatData.objects.aggregate(
        swipes_sum=models.Sum("swipes"),
        total_users=models.Count("user", distinct=True),
    )
    user_group_agg_data = AggregatedUserGroupStatData.objects.aggregate(
        total_user_groups=models.Count("user_group", distinct=True),
    )
    return CommunityStatsType(
        total_contributors=user_agg_data["total_users"] or 0,
        total_user_groups=user_group_agg_data["total_user_groups"] or 0,
        total_swipes=user_agg_data["swipes_sum"] or 0,
    )


def get_community_stats_latest() -> CommunityStatsType:
    """
    Stats from last 30 days
    """
    date_threshold = timezone.now() - datetime.timedelta(days=30)
    user_agg_data = AggregatedUserStatData.objects.filter(
        timestamp_date__gte=date_threshold
    ).aggregate(
        swipes_sum=models.Sum("swipes"),
        total_users=models.Count("user", distinct=True),
    )
    user_group_agg_data = AggregatedUserGroupStatData.objects.filter(
        timestamp_date__gte=date_threshold
    ).aggregate(
        total_user_groups=models.Count("user_group", distinct=True),
    )
    return CommunityStatsType(
        total_contributors=user_agg_data["total_users"] or 0,
        total_user_groups=user_group_agg_data["total_user_groups"] or 0,
        total_swipes=user_agg_data["swipes_sum"] or 0,
    )


@strawberry.type
class FilteredStats:
    date_range: InitVar[Union[DateRangeInput, None]]

    def __post_init__(self, date_range):
        filters = {}
        if date_range:
            filters.update(
                timestamp_date__gte=date_range.from_date,
                timestamp_date__lte=date_range.to_date,
            )
        self.qs = AggregatedUserStatData.objects.filter(**filters)
        self.qs_cte = AggregatedUserStatData.cte_objects.filter(**filters)

    @strawberry.field
    async def contributor_time_stats(self) -> List[ContributorTimeStatType]:
        qs = self.qs\
            .filter(total_time__isnull=False)\
            .order_by("timestamp_date").values("timestamp_date")\
            .annotate(total_time_sum=models.Sum("total_time"))\
            .values_list(
                "timestamp_date",
                "total_time_sum",
            )
        return [
            ContributorTimeStatType(
                date=date,
                total_swipe_time=total_time_sum,
            )
            async for date, total_time_sum in qs
        ]

    @strawberry.field
    async def project_swipe_type(self) -> List[ProjectTypeSwipeStatsType]:
        qs = self.qs\
            .order_by().values("project__project_type")\
            .annotate(swipes_sum=models.Sum("swipes"))\
            .values_list(
                "project__project_type",
                "swipes_sum",
            )
        return [
            ProjectTypeSwipeStatsType(
                project_type=project_type,
                total_swipes=swipes_sum or 0,
            )
            async for project_type, swipes_sum in qs
        ]

    @strawberry.field
    async def project_type_stats(self) -> List[ProjectTypeAreaStatsType]:
        qs = self.qs\
            .filter(area_swiped__isnull=False)\
            .order_by().values("project__project_type")\
            .annotate(total_area_swiped=models.Sum("area_swiped"))\
            .values_list(
                "project__project_type",
                "total_area_swiped",
            )
        return [
            ProjectTypeAreaStatsType(
                project_type=project_type,
                total_area=AreaSqKm(area),
            )
            async for project_type, area in qs
        ]

    @strawberry.field
    async def organization_type_stats(self) -> List[OrganizationSwipeStatsType]:
        qs = self.qs\
            .order_by().values("project__organization_name")\
            .annotate(swipes_sum=models.Sum("swipes"))\
            .values_list(
                "project__organization_name",
                "swipes_sum",
            )
        return [
            OrganizationSwipeStatsType(
                organization_name=organization or 'N/A',
                total_swipes=swipes_sum,
            )
            async for organization, swipes_sum in qs
        ]

    @strawberry.field
    async def project_geo_contribution(self) -> List[MapContributionStatsType]:
        project_qs = Project.cte_objects\
            .filter(geom__isnull=False)\
            .annotate(centroid=Centroid("geom"))\
            .values("project_id", "centroid")
        agg_data_qs = self.qs_cte\
            .order_by().values('project')\
            .annotate(
                swipes_sum=models.Sum("swipes")
            ).values_list(
                "project_id",
                "swipes_sum",
            )

        project_qs_with = With(project_qs, name='project_data')
        agg_data_qs_with = With(agg_data_qs, name='aggregated_data')
        qs = (
            project_qs_with.join(
                agg_data_qs_with.queryset(),
                project_id=project_qs_with.col.project_id,
            )
            .with_cte(project_qs_with)
            .with_cte(agg_data_qs_with)
            .values_list(
                project_qs_with.col.centroid,
                "swipes_sum",
            )
        )
        return [
            MapContributionStatsType(
                geojson=json.loads(geojson.json),
                total_contribution=total_contribution,
            )
            async for geojson, total_contribution in qs
        ]


@strawberry.type
class UserFilterdStats:
    user_id: InitVar[str]
    date_range: InitVar[Union[DateRangeInput, None]]

    def __post_init__(self, user_id, date_range):
        filters = {
            'user_id': user_id,
        }
        if date_range:
            filters.update(
                timestamp_date__gte=date_range.from_date,
                timestamp_date__lte=date_range.to_date,
            )
        self.qs = AggregatedUserStatData.objects.filter(**filters)


@strawberry.type
class Query:
    community_stats: CommunityStatsType = strawberry_django.field(get_community_stats)
    community_stats_latest: CommunityStatsType = strawberry_django.field(
        get_community_stats_latest,
        description=get_community_stats_latest.__doc__,
    )

    projects: CountList[ProjectType] = StrawberryDjangoCountList(
        pagination=True,
        filters=ProjectFilter,
    )

    users: CountList[UserType] = StrawberryDjangoCountList(
        pagination=True,
        filters=UserFilter
    )
    user: UserType = strawberry_django.field()

    user_groups: CountList[UserGroupType] = StrawberryDjangoCountList(
        pagination=True,
        filters=UserGroupFilter,
        order=UserGroupOrder,
    )
    user_group: UserGroupType = strawberry_django.field()

    @strawberry.field
    async def filtered_stats(
        self,
        date_range: Union[DateRangeInput, None] = None,
    ) -> FilteredStats:
        return FilteredStats(date_range=date_range)

    @strawberry.field
    async def user_stats(
        self,
        user_id: strawberry.ID,
    ) -> UserStats:
        return UserStats(user_id=user_id)

    @strawberry.field
    async def user_group_stats(
        self,
        user_group_id: strawberry.ID,
    ) -> UserGroupStats:
        return UserGroupStats(user_group_id=user_group_id)
