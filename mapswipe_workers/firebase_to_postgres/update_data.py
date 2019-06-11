import csv
import io

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger

# TODO: Retrieve only data from firebase which recently changed
# and therefor needs to be updated in postgres.
# How can this be achived?

# TODO: are all data repressented?


def update_project_data(projectIds=None):
    """
    Gets all attributes (progress, contributorCount, status)
    of projects, which are subject to changes,
    from Firebase and updates them in Postgres.
    Default behavior is to update all projects.
    If called with a list of project ids as parameter
    only those projects will be updated.

    Parameters
    ----------
    projectIds: list
    """

    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    if projectIds:
        projects = list()
        for projectId in projectIds:
            project_ref = fb_db.reference(f'projects/{projectId}')
            projects.append(project_ref.get())
    else:
        projects_ref = fb_db.reference('projects/')
        projects = projects_ref.get()

    for projectId, project in projects.items():
        query_update_project = '''
            UPDATE projects
            SET contributor_count=%s, progress=%s, status=%s
            WHERE project_id=%s; 
        '''
        data_update_project = [
                project['contributorCount'],
                project['progress'],
                project.get('status', ''),
                projectId
                ]
        pg_db.query(query_update_project, data_update_project)

    del(pg_db)

    logger.info('Updated project data in Postgres')


def update_user_data(userIds=None):
    """
    Gets all attributes of users
    from Firebase and updates them in Postgres.
    Default behavior is to update all users.
    If called with a list of user ids as parameter
    only those user will be updated.

    Parameters
    ----------
    userIds: list
    """

    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    if userIds:
        users = list()
        for userId in userIds:
            ref = fb_db.reference(f'users/{userId}')
            users.append(ref.get())
    else:
        pg_query = '''
            SELECT created
            FROM users
            ORDER BY created LIMIT 1
            '''
        last_updated = retr_query(pg_query)

        ref = fb_db.reference('users/')
        fb_query = ref.order_by_child(f'{userId}/created').end_at(last_updated)
        users = fb_query.get

    for userId, user in users.items():
        query_update_user = '''
            INSERT INTO users (user_id, username, created)
            VALUES(%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET username=%s,
            created=%s;
        '''
        data_update_user = [
                userId,
                user['username'],
                user['created'],
                user['username'],
                user['created'],
                ]
        pg_db.query(query_update_user, data_update_user)

    del(pg_db)

    logger.info('Updated user data in Postgres')


def update_group_data():
    pass
