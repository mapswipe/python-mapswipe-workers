from firebase_admin import auth
from mapswipe_workers.auth import firebaseDB
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


def get_all_users():
    """Get the user ids from all users in Firebase DB."""
    fb_db = firebaseDB()
    users = fb_db.reference("v2/users/").get(shallow=True)
    uid_list = users.keys()
    return uid_list


if __name__ == "__main__":
    """Get all user ids from Firebase and update username based on auth.display_name."""
    uid_list = get_all_users()
    for uid in uid_list:
        update_username(uid)
