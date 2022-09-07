import strawberry
import strawberry_django

from .models import User, UserGroup, UserGroupUserMembership


@strawberry_django.ordering.order(User)
class UserOrder:
    user_id: strawberry.auto
    username: strawberry.auto


@strawberry_django.ordering.order(UserGroup)
class UserGroupOrder:
    user_group_id: strawberry.auto
    name: strawberry.auto


@strawberry_django.ordering.order(UserGroupUserMembership)
class UserGroupUserMembershipOrder:
    user: UserOrder
    user_group: UserGroupOrder
