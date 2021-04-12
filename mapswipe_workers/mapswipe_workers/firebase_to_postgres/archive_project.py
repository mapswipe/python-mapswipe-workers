"""
Archive a project.
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


def archive_project(project_ids: list) -> bool:
    """
    Archive a project.

    Deletes groups, tasks and results from Firebase.
    Set status = archived for project in Firebase and Postgres.
    """
    for project_id in project_ids:
        logger.info(f"Archive project with the id {project_id}")

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/results/{project_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                f"""Given argument resulted in invalid Firebase Realtime Database reference.
                {ref.path}"""
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
                f"""Given argument resulted in invalid Firebase Realtime Database reference.
                {ref.path}"""
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
                f"""Given argument resulted in invalid Firebase Realtime Database reference.
                        {ref.path}"""
            )
        ref.delete()

        time.sleep(5)  # Wait for Firebase Functions to complete

        ref = fb_db.reference(f"v2/groups/{project_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                f"""Given argument resulted in invalid Firebase Realtime Database reference.
                        {ref.path}"""
            )
        ref.delete()

        fb_db.reference(f"v2/projects/{project_id}/status").set("archived")

        pg_db = auth.postgresDB()
        sql_query = """
            UPDATE projects SET status = 'archived'
            WHERE project_id = %(project_id)s;
        """
        pg_db.query(sql_query, {"project_id": project_id})

    return True
