"""
Delete projects.
"""

from firebase_admin import exceptions

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def chunks(data, size=250):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(data), size):
        yield data[i : i + size]


def delete_project(project_ids: list) -> None:
    """
    Deletes project, groups, tasks and results from Firebase and Postgres.
    """
    for project_id in project_ids:
        logger.info(
            f"Delete project, groups, tasks and results of project: {project_id}"
        )

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

        ref = fb_db.reference(f"v2/tasks/{project_id}")
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

    return True
