import strawberry
import strawberry_django
from mapswipe.paginations import CountList, StrawberryDjangoCountList

from .filters import ProjectFilter, UserGroupFilter
from .types import ProjectType, UserGroupType


@strawberry.type
class Query:
    projects: CountList[ProjectType] = StrawberryDjangoCountList(
        pagination=True,
        filters=ProjectFilter,
    )

    user_groups: CountList[UserGroupType] = StrawberryDjangoCountList(
        pagination=True,
        filters=UserGroupFilter,
    )

    user_group: UserGroupType = strawberry_django.field()
