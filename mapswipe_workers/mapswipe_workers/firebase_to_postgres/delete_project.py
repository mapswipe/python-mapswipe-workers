"""
Delete projects.
"""
import re
import time
from typing import Iterable

from firebase_admin import exceptions

from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError, logger


def chunks(data: list, size: int = 250) -> Iterable[list]:
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(data), size):
        yield data[i : i + size]  # noqa E203


def delete_project(project_ids: list) -> bool:
    """
    Deletes project, groups, tasks and results from Firebase and Postgres.
    """
    for project_id in project_ids:
        if project_id is None:
            logger.info("Will not delete Null project_id.")
            continue

        logger.info(
            f"Delete project, groups, tasks and results of project: {project_id}"
        )

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/results/{project_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                "Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
                f"{ref.path}"
            )
        try:
            ref.delete()
        except exceptions.InvalidArgumentError:
            # Data to write exceeds the maximum size that can be modified
            # with a single request. Delete chunks of data instead.
            childs = ref.get(shallow=True)
            for chunk in chunks(list(childs.keys())):
                ref.update({key: None for key in chunk})
            ref.delete()

        ref = fb_db.reference(f"v2/tasks/{project_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                f"Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
                f"{ref.path}"
            )
        try:
            ref.delete()
        except exceptions.InvalidArgumentError:
            # Data to write exceeds the maximum size that can be modified
            # with a single request. Delete chunks of data instead.
            childs = ref.get(shallow=True)
            for chunk in chunks(list(childs.keys())):
                ref.update({key: None for key in chunk})
            ref.delete()

        ref = fb_db.reference(f"v2/groupsUsers/{project_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                "Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
                f"{ref.path}"
            )
        ref.delete()
        time.sleep(5)  # Wait for Firebase Functions to complete

        ref = fb_db.reference(f"v2/groups/{project_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                "Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
                f"{ref.path}"
            )
        ref.delete()
        ref = fb_db.reference(f"v2/projects/{project_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                "Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
                f"{ref.path}"
                ""
            )
        ref.delete()

        pg_db = auth.postgresDB()
        sql_query = """
            DELETE FROM mapping_sessions_results msr
            USING mapping_sessions ms
            WHERE ms.mapping_session_id = msr.mapping_session_id
                AND ms.project_id = %(project_id)s;
        """
        pg_db.query(sql_query, {"project_id": project_id})

        pg_db = auth.postgresDB()
        sql_query = """
            DELETE FROM mapping_sessions_results_geometry msr
            USING mapping_sessions ms
            WHERE ms.mapping_session_id = msr.mapping_session_id
                AND ms.project_id = %(project_id)s;
        """
        pg_db.query(sql_query, {"project_id": project_id})

        sql_query = """
            DELETE
            FROM mapping_sessions
            WHERE project_id = %(project_id)s ;
        """
        pg_db.query(sql_query, {"project_id": project_id})
        sql_query = "DELETE FROM tasks WHERE project_id = %(project_id)s;"
        pg_db.query(sql_query, {"project_id": project_id})
        sql_query = "DELETE FROM groups WHERE project_id = %(project_id)s;"
        pg_db.query(sql_query, {"project_id": project_id})
        # -- Table from django/apps/aggregated/models.py. Used to cache stats data
        # NOTE: Django doesn't support database-level CASCADE delete
        #  https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.ForeignKey.on_delete
        for aggregated_table_name in [
            "aggregated_aggregateduserstatdata",
            "aggregated_aggregatedusergroupstatdata",
        ]:
            if pg_db.table_exists(aggregated_table_name):
                sql_query = f"""
                    DELETE FROM {aggregated_table_name}
                    WHERE project_id = %(project_id)s;
                """
                pg_db.query(sql_query, {"project_id": project_id})
        # Finally delete the project
        sql_query = "DELETE FROM projects WHERE project_id = %(project_id)s;"
        pg_db.query(sql_query, {"project_id": project_id})

    return True
