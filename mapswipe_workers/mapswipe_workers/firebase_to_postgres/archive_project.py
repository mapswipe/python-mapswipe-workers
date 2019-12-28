"""
Archive a project.

Delete groups, tasks and results of a project in Firebase.
Keep all informations in Postgres.
"""

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def archive_project(project_id: str) -> None:
    """
    Archive a project.

    Call a function which deletes groups, tasks and results in Firebase.
    Set archive = true for project in Postgres.
    """
    logger.info("Archive project with the id {0}".format(project_id))
    delete_project_from_firebase(project_id)

    pg_db = auth.postgresDB()
    sql_query = "UPDATE projects SET archived = true WHERE project_id = {0}".format(
        project_id
    )
    pg_db.query(sql_query)


def delete_project_from_firebase(project_id: str) -> None:
    """Delete results, groups and tasks of given project in Firebase."""
    logger.info(
        "Delete results, groups and tasks of project with the id {0}".format(project_id)
    )
    fb_db = auth.firebaseDB()
    fb_db.reference("v2/results/{0}".format(project_id)).set({})
    fb_db.reference("v2/groups/{0}".format(project_id)).set({})
    fb_db.reference("v2/tasks/{0}".format(project_id)).set({})
