import strawberry
import strawberry_django

from .models import Project, User, UserGroup


@strawberry_django.filters.filter(User, lookups=True)
class UserFilter:
    user_id: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                username__icontains=self.search,
            )
        return queryset


@strawberry_django.filters.filter(Project, lookups=True)
class ProjectFilter:
    project_id: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                name__icontains=self.search,
            )
        return queryset


@strawberry_django.filters.filter(UserGroup, lookups=True)
class UserGroupFilter:
    user_group_id: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                name__icontains=self.search,
            )
        return queryset
