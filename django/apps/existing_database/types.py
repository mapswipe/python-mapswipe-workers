import strawberry

from .models import Project


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
