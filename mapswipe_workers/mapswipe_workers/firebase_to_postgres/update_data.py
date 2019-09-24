import datetime as dt

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def update_user_data(user_ids=None):
    '''
    Copies new users from Firebase to Postgres
    '''
    # TODO: On Conflict
    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    fb_ref = fb_db.reference('v2/users')

    pg_query = '''
        SELECT created
        FROM users
        ORDER BY created DESC
        LIMIT 1
        '''
    last_updated = pg_db.retr_query(pg_query)
    if not last_updated:
        # No users in the Postgres database yet.
        # Get all users from Firebase.
        users = fb_ref.get()
        print(users)
    else:
        # Get only new users from Firebase.
        last_updated = last_updated[0][0]
        last_updated = last_updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        fb_query = fb_ref.order_by_child('created').start_at(last_updated)
        users = fb_query.get()
        # Delete first user in ordered dict.
        # This user is already in the database (user.created = last_updated).
        if len(users) == 0:
            logger.info(f"there are no new users in firebase based on created timestamp")
        else:
            users.popitem(last=False)

    # update users specified in user_ids list
    if user_ids:
        logger.info(f"will add users to copy_new_users based on user_ids provided")
        for user_id in user_ids:
            user = fb_ref.child(user_id).get()
            users[user_id] = user
            logger.info(f"added user {user_id}")

    for user_id, user in users.items():
        # Convert timestamp (ISO 8601) from string to a datetime object.
        try:
            created = dt.datetime.strptime(
                    user['created'].replace('Z', ''),
                    '%Y-%m-%dT%H:%M:%S.%f'
                    )
        except KeyError:
            # if user has no "created" attribute, we set it to current time
            created = dt.datetime.utcnow().isoformat()[0:-3]+'Z'
            logger.info(f"user {user_id} didn't have a created attribute set it to {created}")

        try:
            username = user['username']
        except KeyError:
            # if user has no "username" attribute, we set it to None
            username = None
            logger.info(f"user {user_id} didn't have a created attribute set it to {username}")

        query_update_user = '''
            INSERT INTO users (user_id, username, created)
            VALUES(%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET username=%s,
            created=%s;
        '''
        data_update_user = [
                user_id,
                username,
                created,
                username,
                created,
                ]
        pg_db.query(query_update_user, data_update_user)

    del(pg_db)

    logger.info('Updated user data in Potgres')


def update_project_data(project_ids=None):
    """
    Gets status of projects
    from Firebase and updates them in Postgres.
    Default behavior is to update all projects.
    If called with a list of project ids as parameter
    only those projects will be updated.

    Parameters
    ----------
    project_ids: list
    """

    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    if project_ids:
        logger.info(f"update project data in postgres for selected projects")
        projects = dict()
        for project_id in project_ids:
            project_ref = fb_db.reference(f'v2/projects/{project_id}')
            projects[project_id] = project_ref.get()
    else:
        logger.info(f"update project data in postgres for all firebase projects")
        projects_ref = fb_db.reference('v2/projects/')
        projects = projects_ref.get()

    for project_id, project in projects.items():
        query_update_project = '''
            UPDATE projects
            SET status=%s
            WHERE project_id=%s;
        '''
        # TODO: Is there need for fallback to ''
        # if project.status is not existent
        data_update_project = [project.get('status', ''), project_id]
        pg_db.query(query_update_project, data_update_project)
        logger.info(f"updated status for project {project_id} in postgres")

    del(pg_db)

    logger.info('Updated project data in Postgres')
