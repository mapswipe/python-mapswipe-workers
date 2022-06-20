import strawberry

from .models import Project


@strawberry.django.filters.filter(Project, lookups=True)
class ProjectFilter:
    project_id: strawberry.auto
    search: str | None

    def filter_search(self, queryset):
        if self.search:
            queryset = queryset.filter(
                name__icontains=self.search,
            )
        return queryset
