from mapswipe_workers.auth import firebaseDB, postgresDB
from mapswipe_workers.definitions import logger


def update_task_contribution_count(uid):
    """Set user's taskContributionCount in Firebase DB based on items_count in Postgres mapping_sessions."""
    p_con = postgresDB()
    fb_db = firebaseDB()

    query = """
        SELECT COALESCE(SUM(items_count), 0)
        FROM public.mapping_sessions
        WHERE user_id = %(uid)s
        ;
    """

    try:
        data = p_con.retr_query(query, {"uid": uid})
        task_contribution_count = data[0][0]
        ref = fb_db.reference(f"v2/users/{uid}/taskContributionCount")
        ref.set(task_contribution_count)
        logger.info(
            f"Updated task contribution count to {task_contribution_count} for user {uid} in Firebase."
        )
    except Exception as e:
        logger.exception(e)
        logger.warning(
            f"Could NOT update task contribution count for user {uid} in Firebase."
        )


def get_all_affected_users():
    """Get the user ids from all users in Firebase DB."""
    p_con = postgresDB()

    query = """
        select 
            user_id
        from users u 
        where 1=1
            and username = ''
            and user_id not LIKE 'osm:%'
        ;
    """

    try:
        data = p_con.retr_query(query)
        uid_list = [item[0] for item in data]
        logger.info(f"Got all {len(uid_list)} users from postgres DB.")
    except Exception as e:
        logger.exception(e)
        logger.warning(
            f"Could NOT update task contribution count for user in Firebase."
        )

    return uid_list


if __name__ == "__main__":
    """Get all user ids from Firebase and update taskContributionCount based on Postgres mapping_sessions."""
    uid_list = get_all_affected_users()

    for uid in uid_list:
        update_task_contribution_count(uid)
