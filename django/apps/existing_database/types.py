import datetime
from dataclasses import InitVar

import strawberry
import strawberry_django
from apps.aggregated.models import AggregatedUserGroupStatData, AggregatedUserStatData
from django.contrib.gis.db.models.functions import Centroid
from django.db import models
from django.utils import timezone
from mapswipe.paginations import CountList, apply_pagination
from mapswipe.types import AreaSqKm, GenericJSON, TimeInSeconds
from strawberry.types import Info

from .enums import ProjectTypeEnum
from .models import Project, User, UserGroup, UserGroupResult, UserGroupUserMembership


@strawberry.input
class DateRangeInput:
    from_date: datetime.datetime
    to_date: datetime.datetime


@strawberry.type
class CommunityStatsType:
    total_swipes: int
    total_contributors: int
    total_user_groups: int


@strawberry.type
class ProjectTypeAreaStatsType:
    project_type: ProjectTypeEnum
    total_area: AreaSqKm

    @strawberry.field
    def project_type_display(self) -> str:
        return ProjectTypeEnum(self.project_type).label


@strawberry.type
class ProjectTypeSwipeStatsType:
    project_type: ProjectTypeEnum
    total_swipes: int

    @strawberry.field
    def project_type_display(self) -> str:
        return ProjectTypeEnum(self.project_type).label


@strawberry.type
class UserGroupStatsType:
    total_swipes: int
    total_swipe_time: TimeInSeconds
    total_mapping_projects: int
    total_contributors: int
    total_area_swiped: AreaSqKm
    total_organization: int


@strawberry.type
class UserGroupLatestStatsType:
    total_swipes: int
    total_swipe_time: TimeInSeconds
    total_mapping_projects: int
    total_contributors: int


@strawberry.type
class UserGroupUserStatsType:
    user_id: str
    username: str
    total_mapping_projects: int
    total_swipes: int
    total_swipe_time: TimeInSeconds


@strawberry.type
class UserStatType:
    total_swipes: int
    total_swipe_time: TimeInSeconds
    total_mapping_projects: int
    total_user_groups: int
    total_area_swiped: AreaSqKm
    total_organization: int


@strawberry.type
class ContributorSwipeStatType:
    task_date: datetime.date
    total_swipes: int


@strawberry.type
class ContributorTimeStatType:
    date: datetime.date
    total_swipe_time: TimeInSeconds


@strawberry.type
class OrganizationSwipeStatsType:
    organization_name: str
    total_swipes: int


@strawberry.type
class MapContributionStatsType:
    geojson: GenericJSON
    total_contribution: int


@strawberry.type
class UserLatestStatsType:
    total_swipes: int
    total_swipe_time: TimeInSeconds
    total_user_groups: int


@strawberry.interface
class UserUserGroupBaseFilterStatsQuery:
    @property
    def qs(self):
        self._qs: strawberry.Private[models.QuerySet]
        if self._qs is None:
            raise Exception("qs should be defined")
        return self._qs

    @strawberry.field
    async def swipe_by_date(self) -> list[ContributorSwipeStatType]:
        qs = (
            self.qs.filter(task_count__isnull=False)
            .order_by("timestamp_date")
            .values("timestamp_date")
            .annotate(total_swipes=models.Sum("swipes"))
            .values_list(
                "timestamp_date",
                "total_swipes",
            )
        )
        return [
            ContributorSwipeStatType(
                task_date=task_date,
                total_swipes=swipe_count,
            )
            async for task_date, swipe_count in qs
        ]

    @strawberry.field
    async def swipe_time_by_date(self) -> list[ContributorTimeStatType]:
        qs = (
            self.qs.filter(total_time__isnull=False)
            .order_by("timestamp_date")
            .values("timestamp_date")
            .annotate(
                total_time_sum=models.Sum("total_time"),
            )
            .values_list(
                "timestamp_date",
                "total_time_sum",
            )
        )
        return [
            ContributorTimeStatType(
                date=date,
                total_swipe_time=total_time_sum,
            )
            async for date, total_time_sum in qs
        ]

    @strawberry.field
    async def area_swiped_by_project_type(self) -> list[ProjectTypeAreaStatsType]:
        qs = (
            self.qs.filter(area_swiped__isnull=False)
            .order_by()
            .values("project__project_type")
            .annotate(
                total_area_swiped=models.Sum("area_swiped"),
            )
            .values_list(
                "project__project_type",
                "total_area_swiped",
            )
        )
        return [
            ProjectTypeAreaStatsType(
                project_type=project_type,
                total_area=area_sum,
            )
            async for project_type, area_sum in qs
        ]

    @strawberry.field
    async def swipe_by_project_type(self) -> list[ProjectTypeSwipeStatsType]:
        qs = (
            self.qs.filter(task_count__isnull=False)
            .order_by()
            .values("project__project_type")
            .annotate(
                total_swipes=models.Sum("swipes"),
            )
            .values_list(
                "project__project_type",
                "total_swipes",
            )
        )
        return [
            ProjectTypeSwipeStatsType(
                project_type=project_type,
                total_swipes=total_swipes,
            )
            async for project_type, total_swipes in qs
        ]

    @strawberry_django.field
    async def swipe_by_organization_name(self) -> list[OrganizationSwipeStatsType]:
        qs = (
            self.qs.order_by()
            .values("project__organization_name")
            .annotate(
                total_swipes=models.Sum("swipes"),
            )
            .values_list(
                "project__organization_name",
                "total_swipes",
            )
        )
        return [
            OrganizationSwipeStatsType(
                organization_name=organization_name or "N/A",
                total_swipes=total_swipes,
            )
            async for organization_name, total_swipes in qs
        ]

    @strawberry.field
    async def contribution_by_geo(self) -> list[MapContributionStatsType]:
        qs = (
            self.qs.order_by()
            .values("project_id")
            .annotate(
                total_swipes=models.Sum("swipes"),
            )
            .values_list(
                Centroid("project__geom"),
                "total_swipes",
            )
        )
        return [
            MapContributionStatsType(
                geojson=geom.json,
                total_contribution=total_swipes,
            )
            async for geom, total_swipes in qs
            if geom is not None
        ]


@strawberry.type
class UserFilteredStats(UserUserGroupBaseFilterStatsQuery):
    date_range: InitVar[DateRangeInput | None]
    user_id: InitVar[str]

    def __post_init__(self, date_range, user_id):
        filters = {
            "user_id": user_id,
        }
        if date_range:
            filters.update(
                timestamp_date__gte=date_range.from_date,
                timestamp_date__lte=date_range.to_date,
            )
        self._qs = AggregatedUserStatData.objects.filter(**filters)


@strawberry.type
class UserStats:
    user_id: InitVar[str]

    def __post_init__(self, user_id):
        self._user_id = user_id
        self.qs = AggregatedUserStatData.objects.filter(user_id=user_id)
        self.ug_qs = AggregatedUserGroupStatData.objects.filter(user_id=user_id)

    @strawberry.field
    async def stats(self) -> UserStatType:
        agg_data = await self.qs.aaggregate(
            total_swipes=models.Sum("swipes"),
            total_time_sum=models.Sum("total_time"),
            total_project=models.Count("project_id"),
            total_area_swiped=models.Sum("area_swiped"),
            total_organization=models.Count(
                "project__organization_name",
                distinct=True,
            ),
        )
        user_group_count = (
            await UserGroupResult.objects.filter(user_id=self._user_id).aaggregate(
                count=models.Count("user_group_id", distinct=True)
            )
        )["count"]
        return UserStatType(
            total_swipes=agg_data["total_swipes"] or 0,
            total_swipe_time=TimeInSeconds(agg_data["total_time_sum"] or 0),
            total_mapping_projects=agg_data["total_project"] or 0,
            total_area_swiped=AreaSqKm(agg_data["total_area_swiped"] or 0),
            total_organization=agg_data["total_organization"] or 0,
            total_user_groups=user_group_count or 0,
        )

    @strawberry.field(description="Stats from last 30 days")
    async def stats_latest(self) -> UserLatestStatsType:
        date_threshold = timezone.now() - datetime.timedelta(days=30)
        agg_data = await self.qs.filter(timestamp_date__gte=date_threshold).aaggregate(
            total_swipes=models.Sum("swipes"),
            total_time_sum=models.Sum("total_time"),
        )
        total_group_count = (
            await self.ug_qs.aaggregate(
                count=models.Count(
                    "user_group_id",
                    distinct=True,
                    filter=models.Q(user_group_id__isnull=False),
                )
            )
        )["count"]
        return UserLatestStatsType(
            total_swipes=agg_data["total_swipes"] or 0,
            total_swipe_time=TimeInSeconds(agg_data["total_time_sum"] or 0),
            total_user_groups=total_group_count or 0,
        )

    @strawberry.field
    async def filtered_stats(
        self,
        date_range: DateRangeInput | None = None,
    ) -> UserFilteredStats:
        return UserFilteredStats(user_id=self._user_id, date_range=date_range)


@strawberry.type
class UserGroupFilteredStats(UserUserGroupBaseFilterStatsQuery):
    date_range: InitVar[DateRangeInput | None]
    user_group_id: InitVar[str]

    def __post_init__(self, date_range, user_group_id):
        filters = {
            "user_group_id": user_group_id,
        }
        if date_range:
            filters.update(
                timestamp_date__gte=date_range.from_date,
                timestamp_date__lte=date_range.to_date,
            )
        self._qs = AggregatedUserGroupStatData.objects.filter(**filters)

    # Additional fields
    @strawberry.field
    async def user_stats(self) -> list[UserGroupUserStatsType]:
        qs = (
            self.qs.order_by()
            .values("user_id")
            .annotate(
                total_project=models.Count("project", distinct=True),
                total_swipes=models.Sum("swipes"),
                total_time_sum=models.Sum("total_time"),
            )
            .values_list(
                "user_id",
                "user__username",
                "total_project",
                "total_swipes",
                "total_time_sum",
            )
        )
        return [
            UserGroupUserStatsType(
                user_id=user_id,
                username=username,
                total_swipes=total_swipes,
                total_swipe_time=total_time_sum,
                total_mapping_projects=total_project,
            )
            async for (
                user_id,
                username,
                total_project,
                total_swipes,
                total_time_sum,
            ) in qs
        ]


@strawberry.type
class UserGroupStats:
    user_group_id: InitVar[str]

    def __post_init__(self, user_group_id):
        self._user_group_id = user_group_id
        self.qs = AggregatedUserGroupStatData.objects.filter(
            user_group_id=user_group_id
        )

    @strawberry.field
    async def stats(self) -> UserGroupStatsType:
        agg_data = await self.qs.aaggregate(
            total_swipes=models.Sum("swipes"),
            total_time_sum=models.Sum("total_time"),
            total_contributors=models.Count("user_id", distinct=True),
            total_project=models.Count("project_id", distinct=True),
            total_area_swiped=models.Sum("area_swiped"),
            total_organization=models.Count(
                "project__organization_name",
                distinct=True,
            ),
        )
        return UserGroupStatsType(
            total_swipes=agg_data["total_swipes"] or 0,
            total_swipe_time=TimeInSeconds(agg_data["total_time_sum"] or 0),
            total_contributors=agg_data["total_contributors"] or 0,
            total_mapping_projects=agg_data["total_project"] or 0,
            total_area_swiped=AreaSqKm(agg_data["total_area_swiped"] or 0),
            total_organization=agg_data["total_organization"] or 0,
        )

    @strawberry.field(description="Stats from last 30 days")
    async def stats_latest(self) -> UserGroupLatestStatsType:
        date_threshold = timezone.now() - datetime.timedelta(days=30)
        agg_data = await self.qs.filter(timestamp_date__gte=date_threshold).aaggregate(
            total_swipes=models.Sum("swipes"),
            total_time_sum=models.Sum("total_time"),
            total_contributors=models.Count("user_id", distinct=True),
            total_project=models.Count("project_id", distinct=True),
        )
        return UserGroupLatestStatsType(
            total_swipes=agg_data["total_swipes"] or 0,
            total_swipe_time=TimeInSeconds(agg_data["total_time_sum"] or 0),
            total_contributors=agg_data["total_contributors"] or 0,
            total_mapping_projects=agg_data["total_project"] or 0,
        )

    @strawberry.field
    async def filtered_stats(
        self,
        date_range: DateRangeInput | None = None,
    ) -> UserGroupFilteredStats:
        return UserGroupFilteredStats(
            user_group_id=self._user_group_id,
            date_range=date_range,
        )


@strawberry.type
class UserUserGroupMembershipType:
    user_group_id: strawberry.ID
    user_group_name: str
    members_count: int


@strawberry_django.type(User)
class UserType:
    user_id: strawberry.ID
    username: strawberry.auto

    @strawberry.field
    async def user_in_user_groups(
        self,
        info: Info,
        root: User,
        pagination: strawberry_django.pagination.OffsetPaginationInput,
    ) -> CountList[UserUserGroupMembershipType]:
        qs = (
            UserGroup.objects.filter(
                user_group_id__in=UserGroupUserMembership.objects.filter(
                    user_id=root.user_id
                ).values("user_group_id")
            )
            .annotate(
                members_count=models.functions.Coalesce(
                    models.Subquery(
                        UserGroupUserMembership.objects.filter(
                            user_group_id=models.OuterRef("user_group_id"),
                        )
                        .order_by()
                        .values("user_group_id")
                        .annotate(c=models.Count("user_id"))
                        .values("c")[:1],
                        output_field=models.IntegerField(),
                    ),
                    0,
                ),
            )
            .order_by("user_group_id")
        )
        paginated_qs = apply_pagination(pagination, qs)
        return CountList[UserUserGroupMembershipType](
            node=dict(
                count_callback=lambda: qs.acount(),
                queryset=[
                    UserUserGroupMembershipType(
                        **data,
                    )
                    async for data in paginated_qs.values(
                        "user_group_id",
                        "members_count",
                        user_group_name=models.F("name"),
                    )
                ],
            )
        )


@strawberry_django.type(Project)
class ProjectType:
    project_id: strawberry.ID
    created: strawberry.auto
    name: strawberry.auto
    created_by: strawberry.auto
    progress: strawberry.auto
    project_details: strawberry.auto
    project_type: ProjectTypeEnum
    required_results: strawberry.auto
    result_count: strawberry.auto
    status: strawberry.auto
    geom: str
    organization_name: str


@strawberry.type
class UserGroupUserMembershipType:
    user_id: str
    username: str
    is_active: bool
    # Stats
    total_mapping_projects: int
    total_swipes: int
    total_swipe_time: TimeInSeconds


@strawberry_django.type(UserGroup)
class UserGroupType:
    user_group_id: strawberry.ID
    name: strawberry.auto
    description: strawberry.auto
    created_by: UserType
    archived_by: UserType
    created_at: strawberry.auto
    archived_at: strawberry.auto
    is_archived: strawberry.auto

    # TODO: Make this a generic module
    @strawberry.field
    async def user_memberships(
        self,
        info: Info,
        root: UserGroup,
        pagination: strawberry_django.pagination.OffsetPaginationInput,
    ) -> CountList[UserGroupUserMembershipType]:
        def _subquery_generator(agg_func):
            return models.functions.Coalesce(
                models.Subquery(
                    AggregatedUserGroupStatData.objects.filter(
                        user_id=models.OuterRef("user_id"),
                        user_group_id=models.OuterRef("user_group_id"),
                    )
                    .order_by()
                    .values("user_id")
                    .annotate(c=agg_func)
                    .values("c")[:1],
                    output_field=models.IntegerField(),
                ),
                0,
            )

        qs = (
            UserGroupUserMembership.objects.filter(user_group_id=root.user_group_id)
            .annotate(
                username=models.F("user__username"),
                # Stats Data
                total_mapping_projects=_subquery_generator(
                    models.Count("project", distinct=True)
                ),
                total_swipes=_subquery_generator(models.Sum("task_count")),
                total_swipe_time=_subquery_generator(models.Sum("total_time")),
            )
            .order_by("user_id")
        )
        paginated_qs = apply_pagination(pagination, qs)
        return CountList[UserGroupUserMembershipType](
            node=dict(
                count_callback=lambda: qs.acount(),
                queryset=[
                    UserGroupUserMembershipType(
                        **data,
                    )
                    async for data in paginated_qs.values(
                        "user_id",
                        "is_active",
                        # Annotate fields
                        "username",
                        "total_mapping_projects",
                        "total_swipes",
                        "total_swipe_time",
                    )
                ],
            )
        )

    def get_queryset(self, queryset, info, **kwargs):
        # Filter out user group without name. They aren't sync yet.
        return UserGroup.objects.exclude(name__isnull=True).all()
