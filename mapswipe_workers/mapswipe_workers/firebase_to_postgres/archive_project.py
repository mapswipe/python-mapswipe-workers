"""
Archive a project.
"""

from firebase_admin import exceptions

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def chunks(data, size=250):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(data), size):
        yield data[i : i + size]


def archive_project(project_ids: list) -> None:
    """
    Archive a project.

    Deletes groups, tasks and results from Firebase.
    Set status = archived for project in Firebase and Postgres.
    """
    for project_id in project_ids:
        logger.info(f"Archive project with the id {project_id}")

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/results/{project_id}")
        try:
            ref.delete()
        except exceptions.InvalidArgumentError:
            # Data to write exceeds the maximum size that can be modified
            # with a single request. Delete chunks of data instead.
            childs = ref.get(shallow=True)
            for chunk in chunks(list(childs.keys())):
                ref.update({key: None for key in chunk})
            ref.delete()

        ref = fb_db.reference(f"v2/results/{project_id}")
        try:
            ref.delete()
        except exceptions.InvalidArgumentError:
            # Data to write exceeds the maximum size that can be modified
            # with a single request. Delete chunks of data instead.
            childs = ref.get(shallow=True)
            for chunk in chunks(list(childs.keys())):
                ref.update({key: None for key in chunk})
            ref.delete()

        fb_db.reference(f"v2/groups/{project_id}").delete()
        fb_db.reference(f"v2/projects/{project_id}/status").set("archived")

        pg_db = auth.postgresDB()
        sql_query = """
            UPDATE projects SET status = 'archived'
            WHERE project_id = %(project_id)s;
        """
        pg_db.query(sql_query, {"project_id": project_id})

    return True
