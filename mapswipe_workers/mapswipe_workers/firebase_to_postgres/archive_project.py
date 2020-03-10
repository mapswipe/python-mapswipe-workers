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
        logger.info(f"Archive project with the id {project_id}")
        logger.info(f"Delete results of project with the id {project_id}")

        fb_db = auth.firebaseDB()
        fb_db.reference(f"v2/results/{project_id}").set({})

        # get group keys for this project to estimate size in firebase
        groups = fb_db.reference(f"v2/groups/{project_id}").get(shallow=True)

        if not groups:
            logger.info("no groups to delete in firebase")
        else:
            group_keys = list(groups.keys())
            chunk_size = 250
            chunks = int(len(group_keys) / chunk_size) + 1

            # delete groups, tasks in firebase for each chunk using the update function
            for i in range(0, chunks):
                logger.info(
                    f"Delete max {chunk_size} groups and tasks"
                    f"of project with the id {project_id}"
                )
                update_dict = {}
                for group_id in group_keys[:chunk_size]:
                    update_dict[group_id] = None
                fb_db.reference(f"v2/groups/{project_id}").update(update_dict)
                fb_db.reference(f"v2/tasks/{project_id}").update(update_dict)
                group_keys = group_keys[chunk_size:]

        logger.info(
            f"Set status=archived in Firebase for project with the id {project_id}"
        )
        fb_db = auth.firebaseDB()
        fb_db.reference(f"v2/projects/{project_id}/status").set("archived")

        logger.info(
            f"Set status=archived in Postgres for project with the id {project_id}"
        )
        pg_db = auth.postgresDB()
        sql_query = """
            UPDATE projects SET status = 'archived'
            WHERE project_id = %(project_id)s;
        """
        pg_db.query(sql_query, {"project_id": project_id})
