from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import logger


def get_all_users():
    """Get the user ids from all users in Firebase DB."""
    fb_db = firebaseDB()
    users = fb_db.reference(f"v2/users/").get(shallow=True)
    uid_list = users.keys()
    return uid_list


def copy_user_contributions(uid):
    """Copy user contributions in Firebase from `users` to `userContributions`."""
    fb_db = firebaseDB()
    try:
        ref = fb_db.reference(f"v2/users/{uid}/contributions")
        user_contributions = ref.get()
        # only set username for users with display_name
        if not user_contributions:
            logger.info(f"user {uid} has no contributions in firebase.")
        else:
            for project_id in user_contributions.keys():
                ref = fb_db.reference(f"v2/userContributions/{uid}/{project_id}/")
                ref.update(user_contributions[project_id])
                logger.info(
                    f"updated user contributions for user {uid}, project {project_id}"
                )

            # TODO: uncomment when we want to delete old contributions from firebase.
            #  This should be done after all mapswipe clients can deal with it.
            # ref = fb_db.reference(f"v2/users/{uid}/contributions/")
            # ref.set(None)

    except ValueError:
        logger.info(f"could copy user contributions in firebase for {uid}.")


if __name__ == "__main__":
    """Get users in Firebase and copy their contributions to `userContributions`."""
    # TODO: add another process to delete all old contributions
    #  once copied to new endpoint.
    #  This might not be needed here immediately, but at some point in time.
    uid_list = get_all_users()
    for uid in uid_list:
        copy_user_contributions(uid)
