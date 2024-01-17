"""
Delete projects.
"""
import re
import time
from typing import Iterable

from firebase_admin import exceptions

from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError, ProjectType, logger


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
        try:
            project_type = pg_db.retr_query(
                "Select project_type from projects where project_id = %(project_id)s;",
                {"project_id": project_id},
            )[0][0]
            project = ProjectType(project_type).constructor
            project.delete_from_postgres(project_id)

        except IndexError:
            logger.info(
                f"Tried to delete project which does not exist in postgres: {project_id}"
            )

    return True
