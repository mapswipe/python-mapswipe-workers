import strawberry

from .models import Project

ProjectTypeEnum = strawberry.enum(Project.Type, name="ProjectTypeEnum")
