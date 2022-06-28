import strawberry
from strawberry.types import Info

from mapswipe.paginations import CountList, StrawberryDjangoCountList

from .filters import UserFilter
from .models import (
    Project,
    User,
    UserGroup,
    UserGroupUserMembership,
)


@strawberry.django.type(User)
class UserType:
    user_id: strawberry.ID
    username: strawberry.auto


@strawberry.django.type(Project)
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


@strawberry.type
class SwipeStatType:
    total_swipe: int
    total_swipe_time: float


@strawberry.django.type(UserGroupUserMembership)
class UserGroupUserMembershipType:
    user: UserType
    is_active: strawberry.auto

    @strawberry.field
    async def stats(self, info: Info, root: UserGroupUserMembership) -> SwipeStatType:
        return await info.context[
            "dl"
        ].existing_database.load_user_group_user_stats.load(
            (root.user_group_id, root.user_id)
        )


@strawberry.django.type(UserGroup)
class UserGroupType:
    user_group_id: strawberry.ID
    name: strawberry.auto
    description: strawberry.auto

    # XXX: N+1
    user_memberships: CountList[
        UserGroupUserMembershipType
    ] = StrawberryDjangoCountList(
        pagination=True,
        filters=UserFilter,
    )

    @strawberry.field
    async def stats(self, info: Info, root: UserGroup) -> SwipeStatType:
        return await info.context["dl"].existing_database.load_user_group_stats.load(
            root.user_group_id
        )
