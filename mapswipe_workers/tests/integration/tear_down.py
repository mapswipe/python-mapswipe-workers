"""Helper functions for test tear down"""
import re
import time
from typing import List

from mapswipe_workers import auth


def delete_test_data(project_id: str) -> None:
    """
    Delete test project indluding groups, tasks and results
    from Firebase and Postgres
    """

    if not re.match(r"[-a-zA-Z0-9]+", project_id):
        raise ValueError(
            "Given argument resulted in invalid Firebase Realtime Database reference. "
        )

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"v2/results/{project_id}")
    ref.delete()
    ref = fb_db.reference(f"v2/tasks/{project_id}")
    ref.delete()
    ref = fb_db.reference(f"v2/groupsUsers/{project_id}")
    ref.delete()
    time.sleep(5)  # Wait for Firebase Functions to complete
    ref = fb_db.reference(f"v2/groups/{project_id}")
    ref.delete()
    ref = fb_db.reference(f"v2/projects/{project_id}")
    ref.delete()
    ref = fb_db.reference(f"v2/projectDrafts/{project_id}")
    ref.delete()
    ref = fb_db.reference(f"v2/users/{project_id}")
    ref.delete()

    pg_db = auth.postgresDB()
    sql_query = "DELETE FROM results WHERE project_id = %s"
    pg_db.query(sql_query, [project_id])
    sql_query = "DELETE FROM results_temp WHERE project_id = %s"
    pg_db.query(sql_query, [project_id])
    sql_query = "DELETE FROM tasks WHERE project_id = %s"
    pg_db.query(sql_query, [project_id])
    sql_query = "DELETE FROM groups WHERE project_id = %s"
    pg_db.query(sql_query, [project_id])
    sql_query = "DELETE FROM projects WHERE project_id = %s"
    pg_db.query(sql_query, [project_id])
    sql_query = "DELETE FROM users WHERE user_id = %s"
    pg_db.query(sql_query, [project_id])
    sql_query = "DELETE FROM users_temp WHERE user_id = %s"
    pg_db.query(sql_query, [project_id])


def delete_test_user(user_ids: List) -> None:
    for user_id in user_ids:
        if not re.match(r"[-a-zA-Z0-9]+", user_id):
            raise ValueError(
                "Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
            )

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/users/{user_id}")
        ref.delete()

        pg_db = auth.postgresDB()
        sql_query = "DELETE FROM users WHERE user_id = %s"
        pg_db.query(sql_query, [user_id])
        sql_query = "DELETE FROM users_temp WHERE user_id = %s"
        pg_db.query(sql_query, [user_id])


if __name__ == "__main__":
    delete_test_data("test_build_area")
