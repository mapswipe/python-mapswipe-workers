from django.conf import settings
from django.db import connections
from django.core.management.base import BaseCommand

from apps.existing_database.models import Project


class Command(BaseCommand):
    FETCH_ORGANIZATION_DETAILS = f"""
        SELECT project_id, name FROM {Project._meta.db_table}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_organization_name(self, name):
        if name and '\n' in name:
            name_parts = [x.strip() for x in name.split('\n')]
            if name_parts[1] == '':
                return 'null'
            else:
                return name_parts[1]
        return 'null'

    def handle(self, *args, **kwargs):
        with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
            cursor.execute(self.FETCH_ORGANIZATION_DETAILS)
            aggregate_results = cursor.fetchall()
        for project_id, name in aggregate_results:
            organization_name = self.parse_organization_name(name)
            with connections[settings.MAPSWIPE_EXISTING_DB].cursor() as cursor:
                cursor.execute(
                    f"""
                        UPDATE projects set organization_name='{organization_name}'
                        WHERE project_id='{project_id}'
                    """
                )
