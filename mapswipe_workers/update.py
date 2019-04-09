import csv
import io

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger

# TODO: Retrieve only data from firebase which recently changed
# and therefor needs to be updated in postgres.
# How can this be achived?


def update_project_data():

    fb_db = auth.firebaseDB()
    projects_ref = db_db.reference('projects/')
    projects = projects_ref.get()

    pg_db = auth.postgresDB()

    for projectId, project in projects.items():
        query_update_project = '''
            UPDATE projects
            SET contributors=%s, progress=%s, status=%s
            WHERE project_id=%s; 
        '''
        data_update_project = [
                project['contributors'],
                project['progress'],
                project['status'],
                project_id
                ]
        pg_db.query(query_update_project, data_update_project)

    del(fb_db)
    del(pg_db)

    logger.info('Updated project data in Postgres')


def update_user_data():
    fb_db = auth.firebaseDB()
    users_ref = fb_db.reference('users/')
    users = users_ref.get()

    pg_db = auth.postgresDB()

    for userId, user in users.items():
        query_update_user = '''
            UPDATE users
            SET contribution_count=%s, distance=%s, username=%s
            WHERE user_id=%s; 
        '''
        data_update_user = [
                user['contributionCount'],
                user['distance'],
                user['username'],
                userId
                ]
        pg_db.query(query_update_user, data_update_user)

    del(fb_db)
    del(pg_db)

    logger.info('Updated user data in Postgres')


def update_group_data():
    pass
