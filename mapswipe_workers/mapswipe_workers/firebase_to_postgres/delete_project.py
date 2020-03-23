"""
Delete projects.
"""

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def delete_project(project_ids: list) -> None:
    """
    Deletes projects.

    Deletes project, groups, tasks and results from Firebase and Postgres
    """
    for project_id in project_ids:
        logger.info(
            f"Delete project, groups, tasks and results of project: {project_id}"
        )

        fb_db = auth.firebaseDB()
        fb_db.reference(f"v2/results/{project_id}").delete()
        fb_db.reference(f"v2/tasks/{project_id}").delete()
        fb_db.reference(f"v2/groups/{project_id}").delete()
        fb_db.reference(f"v2/projects/{project_id}").delete()

        pg_db = auth.postgresDB()
        sql_query = "DELETE FROM results WHERE project_id = {};".format(project_id)
        pg_db.query(sql_query, project_id)
        sql_query = "DELETE FROM tasks WHERE project_id = {};".format(project_id)
        pg_db.query(sql_query, project_id)
        sql_query = "DELETE FROM groups WHERE project_id = {};".format(project_id)
        pg_db.query(sql_query, project_id)
        sql_query = "DELETE FROM projects WHERE project_id = {};".format(project_id)
        pg_db.query(sql_query, project_id)
