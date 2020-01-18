"""Update users and project information from Firebase in Postgres."""

import datetime as dt

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, sentry


def get_last_updated_timestamp() -> str:
    """Get the timestamp of the latest created user in Postgres."""
    pg_db = auth.postgresDB()
    query = """
        SELECT created
        FROM users
        ORDER BY created DESC
        LIMIT 1
        """
    last_updated = pg_db.retr_query(query)
    try:
        last_updated = last_updated[0][0]
        last_updated = last_updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        logger.info("Last updated users: {0}".format(last_updated))
    except IndexError:
        logger.exception("Could not get last timestamp of users.")
        sentry.capture_exception()
        last_updated = ""
    return last_updated


def update_user_data(user_ids: list = []) -> None:
    """Copies new users from Firebase to Postgres."""
    # TODO: On Conflict
    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    ref = fb_db.reference("v2/users")
    last_updated = get_last_updated_timestamp()

    if user_ids:
        logger.info("Add custom user ids to user list, which will be updated.")
        users = {}
        for user_id in user_ids:
            users[user_id] = ref.child(user_id).get()
    elif last_updated:
        # Get only new users from Firebase.
        query = ref.order_by_child("created").start_at(last_updated)
        users = query.get()
        if len(users) == 0:
            logger.info("there are no new users in Firebase.")
        else:
            # Delete first user in ordered dict (FIFO).
            # This user is already in the database (user.created = last_updated).
            users.popitem(last=False)
    else:
        # Get all users from Firebase.
        users = ref.get()

    for user_id, user in users.items():
        # Convert timestamp (ISO 8601) from string to a datetime object.
        try:
            created = dt.datetime.strptime(
                user["created"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
            )
        except KeyError:
            # If user has no "created" attribute set it to current time.
            created = dt.datetime.utcnow().isoformat()[0:-3] + "Z"
            logger.info(
                "user {0} didn't have a 'created' attribute. ".format(user_id)
                + "Set it to '{0}' now.".format(created)
            )
        username = user.get("username", None)
        query_update_user = """
            INSERT INTO users (user_id, username, created)
            VALUES(%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET username=%s,
            created=%s;
        """
        data_update_user = [
            user_id,
            username,
            created,
            username,
            created,
        ]
        pg_db.query(query_update_user, data_update_user)
    logger.info("Updated user data in Potgres.")


def update_project_data(project_ids: list = []):
    """
    Gets status of projects
    from Firebase and updates them in Postgres.

    Default behavior is to update all projects.
    If called with a list of project ids as parameter
    only those projects will be updated.
    """

    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    if project_ids:
        logger.info(f"update project data in postgres for selected projects")
        projects = dict()
        for project_id in project_ids:
            project_ref = fb_db.reference(f"v2/projects/{project_id}")
            projects[project_id] = project_ref.get()
    else:
        logger.info(f"update project data in postgres for all firebase projects")
        projects_ref = fb_db.reference("v2/projects/")
        projects = projects_ref.get()

    if projects:
        for project_id, project in projects.items():
            query_update_project = """
                UPDATE projects
                SET status=%s
                WHERE project_id=%s;
            """
            # TODO: Is there need for fallback to ''
            # if project.status is not existent
            data_update_project = [project.get("status", ""), project_id]
            pg_db.query(query_update_project, data_update_project)
            logger.info(f"updated status for project {project_id} in postgres")

    del pg_db

    logger.info("Updated project data in Postgres")
