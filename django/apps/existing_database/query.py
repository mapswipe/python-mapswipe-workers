import strawberry
import strawberry_django
from mapswipe.paginations import CountList, StrawberryDjangoCountList

from .filters import ProjectFilter, UserGroupFilter
from .ordering import UserGroupOrder
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
        order=UserGroupOrder,
    )

    user_group: UserGroupType = strawberry_django.field()
