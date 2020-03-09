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
        logger.info("Archive project with the id {0}".format(project_id))
        logger.info("Delete results of project with the id {0}".format(project_id))

        fb_db = auth.firebaseDB()
        fb_db.reference("v2/results/{0}".format(project_id)).set({})

        # get group keys for this project to estimate size in firebase
        groups = fb_db.reference("v2/groups/{0}/".format(project_id)).get(shallow=True)

        if not groups:
            logger.info("no groups to delete in firebase")
        else:
            group_keys = list(groups.keys())
            chunk_size = 250
            chunks = int(len(group_keys) / chunk_size) + 1

            # delete groups, tasks in firebase for each chunk using the update function
            for i in range(0, chunks):
                logger.info(
                    "Delete max {1} groups and tasks of project with the id {0}".format(
                        project_id, chunk_size
                    )
                )
                update_dict = {}
                for group_id in group_keys[:chunk_size]:
                    update_dict[group_id] = None
                fb_db.reference("v2/groups/{0}".format(project_id)).update(update_dict)
                fb_db.reference("v2/tasks/{0}".format(project_id)).update(update_dict)
                group_keys = group_keys[chunk_size:]

        logger.info(
            "Set status=archived in Firebase for project with the id {0}".format(
                project_id
            )
        )
        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/projects/{0}/status".format(project_id))
        ref.set("archived")

        logger.info(
            "Set status=archived in Postgres for project with the id {0}".format(
                project_id
            )
        )
        pg_db = auth.postgresDB()
        sql_query = """
            UPDATE projects SET status = 'archived'
            WHERE project_id = '{0}';
        """.format(
            project_id
        )
        pg_db.query(sql_query)
