import datetime as dt

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def copy_new_users():
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
    else:
        # Get only new users from Firebase.
        last_updated = last_updated[0][0]
        last_updated = last_updated.strftime('%Y-%m-%dT%H:%M:%S.%f')
        fb_query = fb_ref.order_by_child('created').start_at(last_updated)
        users = fb_query.get()
        # Delete first user in ordered dict.
        # This user is already in the database (user.created = last_updated).
        users.popitem(last=False)

    for user_id, user in users.items():
        # Convert timestamp (ISO 8601) from string to a datetime object.
        # TODO: Make sure strptime is working with timestamps written by the app.
        # ('%Y-%m-%dT%H:%M:%S.%f%z'
        user['created'] = dt.datetime.strptime(
                user['created'],
                '%Y-%m-%dT%H:%M:%S.%f'
                )
        query_update_user = '''
            INSERT INTO users (user_id, username, created)
            VALUES(%s, %s, %s)
        '''
        data_update_user = [
                user_id,
                user['username'],
                user['created'],
                ]
        pg_db.query(query_update_user, data_update_user)

    del(pg_db)

    logger.info('Updated user data in Potgres')


def update_user_data(user_ids=None):
    '''
    Gets username and created attributes of users
    from Firebase and updates them in Postgres.
    Default behavior is to update all users.
    If called with a list of user ids as parameter
    only those user will be updated.

    Parameters
    ----------
    user_ids: list
    '''
    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    if user_ids:
        users = dict()
        for user_id in user_ids:
            ref = fb_db.reference(f'v2/users/{user_id}')
            users[user_id] = ref.get()
    else:
        ref = fb_db.reference(f'v2/users/')
        users = ref.get()

    for user_id, user in users.items():
        # Convert timestamp (ISO 8601) from string to a datetime object
        user['created'] = dt.datetime.strptime(
                user['created'],
                '%Y-%m-%dT%H:%M:%S.%f%z'
                )
        query_update_user = '''
            INSERT INTO users (user_id, username, created)
            VALUES(%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET username=%s,
            created=%s;
        '''
        data_update_user = [
                user_id,
                user['username'],
                user['created'],
                user['username'],
                user['created'],
                ]
        pg_db.query(query_update_user, data_update_user)

    del(pg_db)

    logger.info('Updated user data in Postgres')


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
        projects = dict()
        for project_id in project_ids:
            project_ref = fb_db.reference(f'v2/projects/{project_id}')
            projects[project_id] = project_ref.get()
    else:
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
        data_update_project = [project.get('status', '')]
        pg_db.query(query_update_project, data_update_project)

    del(pg_db)

    logger.info('Updated project data in Postgres')
