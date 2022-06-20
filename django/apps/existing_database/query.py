import strawberry
from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from mapswipe.paginations import CountList, StrawberryDjangoCountList

from .types import ProjectType
from .filters import ProjectFilter
from .models import Project


@sync_to_async
def load_projects() -> QuerySet:
    return Project.objects.all()


@strawberry.type
class Query:
    projects: CountList[ProjectType] = StrawberryDjangoCountList(
        pagination=True, filters=ProjectFilter,
    )
