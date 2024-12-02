from firebase_admin import auth

from mapswipe_workers.auth import firebaseDB, postgresDB
from mapswipe_workers.definitions import logger


def update_username(uid):
    """Set username in Firebase DB based on auth.display_name for user id."""
    fb_db = firebaseDB()
    try:
        user = auth.get_user(uid)
        username = user.display_name
        # only set username for users with display_name
        if not username:
            logger.info(f"user {uid} has no display_name in firebase.")
        else:
            ref = fb_db.reference(f"v2/users/{user.uid}/username")
            ref.set(username)
            logger.info(f"updated username for user {uid}: {username}")
    except auth.UserNotFoundError:
        logger.info(f"could not find user {uid} in firebase to update username.")


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
            f"Could NOT get affected users from postgres."
        )

    return uid_list


if __name__ == "__main__":
    """Get all user ids from Firebase and update username based on auth.display_name."""
    uid_list = get_all_affected_users()

    for uid in uid_list:
        if len(uid) == 0:
            continue
        else:
            update_username(uid)
