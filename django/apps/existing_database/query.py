import strawberry

from mapswipe.paginations import CountList, StrawberryDjangoCountList

from .types import (
    ProjectType,
    UserGroupType,
)
from .filters import (
    ProjectFilter,
    UserGroupFilter,
)


@strawberry.type
class Query:
    projects: CountList[ProjectType] = StrawberryDjangoCountList(
        pagination=True, filters=ProjectFilter,
    )

    user_groups: CountList[UserGroupType] = StrawberryDjangoCountList(
        pagination=True, filters=UserGroupFilter,
    )
