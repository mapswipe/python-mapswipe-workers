from firebase_admin import auth

from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import logger


def remove_unused_user_attributes(uid):
    """Set username in Firebase DB based on auth.display_name for user id."""
    fb_db = firebaseDB()
    try:
        ref = fb_db.reference(f"v2/users/{uid}/")
        ref.update({
            "projectContributionCount": None,
            "groupContributionCount": None
        })

        user_projects = fb_db.reference(f"v2/users/{uid}/contributions/").get(shallow=True)
        if user_projects:
            for project_id in user_projects.keys():
                ref = fb_db.reference(f"v2/users/{uid}/contributions/{project_id}")
                ref.update({
                    "groupContributionCount": None
                })

        logger.info(f"removed attributes for user {uid}")
    except:
        logger.info(f"could NOT remove attributes for user {uid}.")


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
        remove_unused_user_attributes(uid)