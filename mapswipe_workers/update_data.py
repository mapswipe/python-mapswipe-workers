import csv
import io

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger

# TODO: Retrieve only data from firebase which recently changed
# and therefor needs to be updated in postgres.
# How can this be achived?


def update_project_data(projectIds=None):
    """
    Gets all attributes (progress, contributors, status)
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
            SET contributors=%s, progress=%s, status=%s
            WHERE project_id=%s; 
        '''
        data_update_project = [
                project['contributors'],
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
            user_ref = fb_db.reference(f'users/{userId}')
            users.append(user_ref.get())
    else:
        users_ref = fb_db.reference('users/')
        users = users_ref.get()

    for userId, user in users.items():
        query_update_user = '''
            INSERT INTO users (username, contribution_count, distance, user_id)
            VALUES(%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET username=%s,
            contribution_count=%s,
            distance=%s;
        '''
        data_update_user = [
                user['username'],
                user['contributionCount'],
                user['distance'],
                userId,
                user['username'],
                user['contributionCount'],
                user['distance'],
                ]
        pg_db.query(query_update_user, data_update_user)

    del(pg_db)

    logger.info('Updated user data in Postgres')


def update_group_data():
    pass
