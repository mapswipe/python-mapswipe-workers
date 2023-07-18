import time

from apps.existing_database.models import Project
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from .update_aggregated_data import UPDATE_PROJECT_GROUP_DATA_USING_PROJECT_ID


class Command(BaseCommand):
    def handle(self, **_):
        project_qs = Project.objects.all()
        total_projects = project_qs.count()
        self.stdout.write(f"Total projects: {total_projects}")
        for index, project_id in enumerate(
            project_qs.values_list("project_id", flat=True),
            start=1,
        ):
            self.stdout.write(
                "Running calculation for project ID "
                f"({index}/{total_projects}): {project_id}"
            )
            with transaction.atomic():
                start_time = time.time()
                with connection.cursor() as cursor:
                    cursor.execute(
                        UPDATE_PROJECT_GROUP_DATA_USING_PROJECT_ID,
                        dict(project_id=project_id),
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"- Successfull. Runtime: {time.time() - start_time} seconds"
                    )
                )
