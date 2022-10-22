import strawberry

from .models import Project

ProjectTypeEnum = strawberry.enum(Project.ProjectType, name="ProjectTypeEnum")
