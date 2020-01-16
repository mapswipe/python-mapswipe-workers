"""
Archive a project.
"""

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def archive_project(project_ids: list) -> None:
    """
    Archive a project.

    Deletes groups, tasks and results from Firebase.
    Set status = archived for project in Firebase and Postgres.
    """
    for project_id in project_ids:

        if not project_id:
            # Empty string or None would delete all results, groups and tasks.
            logger.warning("Project id is an empty string or None.")
            continue

        logger.info("Archive project with the id {0}".format(project_id))
        logger.info(
            "Delete results, groups and tasks of project with the id {0}".format(
                project_id
            )
        )
        fb_db = auth.firebaseDB()
        fb_db.reference("v2/results/{0}".format(project_id)).set({})
        fb_db.reference("v2/groups/{0}".format(project_id)).set({})
        fb_db.reference("v2/tasks/{0}".format(project_id)).set({})

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/projects/{0}/status".format(project_id))
        ref.set({"archived"})

        pg_db = auth.postgresDB()
        sql_query = (
            "UPDATE projects SET status = 'archived' "
            + "WHERE project_id = {0}".format(project_id)
        )
        pg_db.query(sql_query)
