from typing import List, Dict, Optional
import datetime

import strawberry
import strawberry_django
from strawberry.scalars import JSON
from mapswipe.paginations import CountList, StrawberryDjangoCountList
from strawberry.types import Info

from .filters import UserMembershipFilter
from .models import (
    Project,
    User,
    UserGroup,
    UserGroupUserMembership,
    Organization
)
from .ordering import UserGroupUserMembershipOrder


@strawberry.type
class CommunityStatsType:
    total_contributors: int
    total_groups: int
    total_swipes: int


@strawberry.type
class ProjectTypeStats:
    project_type: Optional[str] = None
    area: Optional[float] = None


@strawberry.type
class ProjectSwipeTypeStats:
    total_swipe: int
    project_type: Optional[str] = None


@strawberry.type
class CommunityStatsLatestType:
    total_contributors_last_month: int
    total_groups_last_month: int
    total_swipes_last_month: int


@strawberry.type
class SwipeStatType:
    total_swipe: int
    total_swipe_time: int
    total_mapping_projects: int
    total_contributors: int


@strawberry.type
class UserLatestType:
    total_contributors: int
    total_groups: int
    total_swipes: int


@strawberry.type
class UserGroupLatestType:
    total_contributors: int
    total_swipes: int
    total_swipe_time: int


@strawberry.type
class UserGroupUserType:
    total_mapping_projects: int
    total_swipes: int
    total_swipe_time: int
    user_name: str


@strawberry.type
class UserSwipeStatType:
    total_swipe: int
    total_swipe_time: int
    total_mapping_projects: int
    total_task: int
    total_user_group: int


@ strawberry.type
class ContributorType:
    total_swipe: int
    task_date: datetime.date


@strawberry.type
class ContributorTimeType:
    total_time: int
    task_date: Optional[datetime.date] = None


@strawberry.type
class OrganizationTypeStats:
    total_swipe: int
    organization_name: Optional[str] = None


@strawberry.type
class MapContributionTypeStats:
    geojson: JSON
    total_contribution: int


@strawberry.type
class UserUserGroupTypeStats:
    user_group: str
    members_count: int
    joined_at: Optional[datetime.date] = None


@strawberry.type
class UserLatestStatusTypeStats:
    total_user_group: int
    total_swipe: int
    total_swipe_time: float


@strawberry_django.type(Organization)
class OrganizationType:
    organization_id: strawberry.ID


@strawberry_django.type(User)
class UserType:
    user_id: strawberry.ID
    username: strawberry.auto

    @strawberry.field
    async def stats(self, info: Info, root: User) -> Optional[UserSwipeStatType]:
        return await info.context[
            "dl"
        ].existing_database.load_user_stats.load(root.user_id)

    @strawberry.field
    async def contribution_stats(self, info: Info, root: User) -> Optional[List[ContributorType]]:
        return await info.context[
            "dl"
        ].existing_database.load_user_contribution_stats.load(root.user_id)

    @strawberry.field
    async def contribution_time(self, info: Info, root: User) -> Optional[List[ContributorTimeType]]:
        return await info.context[
            "dl"
        ].existing_database.load_user_time_spending.load(root.user_id)

    @strawberry.field
    async def project_stats(self, info: Info, root: User) -> Optional[List[ProjectTypeStats]]:
        return await info.context[
            "dl"
        ].existing_database.load_user_stats_project_type.load(root.user_id)

    @strawberry.field
    async def project_swipe_stats(self, info: Info, root: User) -> Optional[List[ProjectSwipeTypeStats]]:
        return await info.context[
            "dl"
        ].existing_database.load_user_stats_project_swipe_type.load(root.user_id)

    @strawberry_django.field
    async def organization_swipe_stats(self, info: Info, root: User) -> Optional[List[OrganizationTypeStats]]:
        return await info.context[
            "dl"
        ].existing_database.load_user_organization_swipe_type.load(root.user_id)

    @strawberry.field
    async def stats_latest(self, info: Info, root: User) -> Optional[UserLatestStatusTypeStats]:
        return await info.context[
            "dl"
        ].existing_database.load_user_latest_stats_query.load(root.user_id)

    @strawberry.field
    async def user_geo_contribution(self, info: Info, root: User) -> Optional[List[MapContributionTypeStats]]:
        return await info.context[
            "dl"
        ].existing_database.load_user_geo_contribution.load(root.user_id)

    @strawberry.field
    async def user_in_user_groups(self, info: Info, root: User) -> Optional[List[UserUserGroupTypeStats]]:
        return await info.context[
            'dl'
        ].existing_database.load_user_usergroup_stats.load(root.user_id)


@strawberry_django.type(Project)
class ProjectType:
    project_id: strawberry.ID
    created: strawberry.auto
    name: strawberry.auto
    created_by: strawberry.auto
    progress: strawberry.auto
    project_details: strawberry.auto
    project_type: strawberry.auto
    required_results: strawberry.auto
    result_count: strawberry.auto
    status: strawberry.auto
    organization: OrganizationType
    geom: str
    organization_name: str


@strawberry_django.type(UserGroupUserMembership)
class UserGroupUserMembershipType:
    user: UserType
    is_active: strawberry.auto
    left_at: str
    joined_at: str

    @strawberry.field
    async def stats(self, info: Info, root: UserGroupUserMembership) -> Optional[UserGroupUserType]:
        return await info.context["dl"].existing_database.load_user_group_user_stats.load(root.user_group_id)

    @strawberry.field
    async def contributors_stats(self, info: Info, root: UserGroupUserMembership) -> ContributorType:
        return await info.context[
            "dl"
        ].existing_database.load_user_group_user_contributors_stats.load(
            (root.user_group_id, root.user_id)
        )


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

    # XXX: N+1
    user_memberships: CountList[
        UserGroupUserMembershipType
    ] = StrawberryDjangoCountList(
        pagination=True,
    )

    @strawberry.field
    async def user_stats(self, info: Info, root: UserGroup) -> Optional[List[UserGroupUserType]]:
        return await info.context["dl"].existing_database.load_user_group_user_stats.load(root.user_group_id)

    @strawberry.field
    async def stats(self, info: Info, root: UserGroup) -> SwipeStatType:
        return await info.context["dl"].existing_database.load_user_group_stats.load(
            root.user_group_id
        )

    @strawberry.field
    async def contribution_stats(self, info: Info, root: UserGroup) -> List[ContributorType]:
        return await info.context["dl"].existing_database.load_user_group_contributors_stats.load(
            root.user_group_id
        )

    @strawberry.field
    async def project_type_stats(self, info: Info, root: UserGroup) -> Optional[List[ProjectTypeStats]]:
        return await info.context["dl"].existing_database.load_user_group_project_type_stats.load(
            root.user_group_id
        )

    @strawberry.field
    async def user_group_geo_stats(self, info: Info, root: UserGroup) -> Optional[List[MapContributionTypeStats]]:
        return await info.context["dl"].existing_database.load_user_group_geo_contributions.load(
            root.user_group_id
        )

    @strawberry.field
    async def user_group_organization_stats(self, info: Info, root: UserGroup) -> Optional[List[OrganizationTypeStats]]:
        return await info.context["dl"].existing_database.load_user_group_organization_stats.load(
            root.user_group_id
        )

    @strawberry.field
    async def user_group_latest(self, info: Info, root: UserGroup) -> Optional[UserGroupLatestType]:
        return await info.context["dl"].existing_database.user_group_latest_stats.load(root.user_group_id)

    @strawberry.field
    async def project_swipe_type(self, info: Info, root: UserGroup) -> Optional[List[ProjectSwipeTypeStats]]:
        return await info.context["dl"].existing_database.load_user_group_stats_project_swipe_type.load(root.user_group_id)

    @strawberry.field
    async def contribution_time(self, info: Info, root: UserGroup) -> Optional[List[ContributorTimeType]]:
        return await info.context["dl"].existing_database.load_user_group_contribution_time.load(root.user_group_id)

    def get_queryset(self, queryset, info, **kwargs):
        # Filter out user group without name. They aren't sync yet.
        return UserGroup.objects.exclude(name__isnull=True).all()
