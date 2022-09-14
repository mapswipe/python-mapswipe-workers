from apps.existing_database.models import Project
from django.core.management.base import BaseCommand
from django.db import models

EMTPY_TEXT = ""


@staticmethod
def parse_organization_name(name):
    if name and "\n" in name:
        name_parts = [x.strip() for x in name.split("\n")]
        if name_parts[1] != "":
            return name_parts[1]
    return EMTPY_TEXT  # Return empty to track this as proccessed


class Command(BaseCommand):
    def handle(self, **_):
        updated_projects = []
        project_qs = Project.objects.filter(
            models.Q(organization_name__isnull=True)
            & ~models.Q(organization_name=EMTPY_TEXT)
        )
        self.stdout.write(f"Projects to update: {project_qs.count()}")
        for project_id, name in project_qs.values_list("project_id", "name"):
            organization_name = parse_organization_name(name)
            updated_projects.append(
                Project(
                    project_id=project_id,
                    organization_name=organization_name,
                )
            )
        Project.objects.bulk_update(updated_projects, ["organization_name"])
        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated: {len(updated_projects)}")
        )
