from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import logger


def remove_timestamps(uid):
    """Remove timestamps from user contributions in Firebase."""
    fb_db = firebaseDB()
    try:
        ref = fb_db.reference(f"v2/users/{uid}/contributions")
        user_contributions = ref.get()

        if not user_contributions:
            logger.info(f"user {uid} has no contributions in firebase.")
        else:
            for project_id in user_contributions.keys():
                for group_id in user_contributions[project_id].keys():
                    user_contributions[project_id][group_id] = 1

            ref.update(user_contributions)
            logger.info(
                f"updated user contributions for user {uid}, project {project_id}"
            )
    except ValueError:
        logger.info(f"could not remove timestamps for user {uid} in firebase.")


def get_all_users():
    """Get the user ids from all users in Firebase DB."""
    fb_db = firebaseDB()
    users = fb_db.reference(f"v2/users/").get(shallow=True)
    uid_list = users.keys()
    return uid_list


if __name__ == "__main__":
    """Get all user ids from Firebase and remove timestamps from user contributions."""
    uid_list = get_all_users()
    for uid in uid_list:
        remove_timestamps(uid)
