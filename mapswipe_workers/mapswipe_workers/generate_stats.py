import sys
from psycopg2 import sql

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def get_aggregated_results(filename):
    '''
    Export the aggregated results statistics as csv file.

    Parameters
    ----------
    filename: str
    -------

    '''
    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_results) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results to %s' % filename)


def get_aggregated_results_by_task_id(filename, project_id):
    '''
    Export aggregated results on a task_id basis per project.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        "COPY (SELECT * FROM aggregated_results_by_task_id WHERE project_id = {}) TO STDOUT WITH CSV HEADER").format(
        sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by task_id for project %s to %s' % (project_id, filename))


def get_aggregated_results_by_user_id(filename):
    '''
    Export aggregated results on a user_id basis as csv file.
    Parameters
    ----------
    filename: str

    Returns
    -------

    '''

    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_results_by_user_id) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by user_id to %s' % filename)


def get_aggregated_results_by_user_id_and_date(filename, user_id):
    '''
    Export results aggregated on user_id and daily basis as csv file.

    Parameters
    ----------
    filename: str
    user_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        "COPY (SELECT * FROM aggregated_results_by_user_id_and_date WHERE user_id = {}) TO STDOUT WITH CSV HEADER").format(
        sql.Literal(user_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by user_id and date for user %s to %s' % (user_id, filename))


def get_aggregated_results_by_project_id(filename):
    '''
    Export results aggregated on project_id basis as csv file.

    Parameters
    ----------
    filename: str
    '''

    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_results_by_project_id) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by project_id to %s' % filename)


def get_aggregated_results_by_project_id_and_date(filename, project_id):
    '''
    Export results aggregated on project_id and daily basis as csv file.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        "COPY (SELECT * FROM aggregated_results_by_project_id_and_date WHERE project_id = {}) TO STDOUT WITH CSV HEADER").format(
        sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by project_id and date for project %s to %s' % (project_id, filename))


def get_aggregated_projects(filename):
    '''
    Export aggregated projects as csv file.

    Parameters
    ----------
    filename: str
    '''

    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_projects) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by project_id and date to %s' % filename)


def get_aggregated_projects_by_project_type(filename):
    '''
    Export projects aggregated on a project_type basis as csv file.

    Parameters
    ----------
    filename: str
    '''

    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_projects_by_project_type) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated projects by project_type to %s' % filename)


def get_aggregated_users(filename):
    '''
    Export aggregated users as csv file.

    Parameters
    ----------
    filename: str
    '''

    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_users) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated users to %s' % filename)


def get_aggregated_progress_by_project_id(filename):
    '''
    Export aggregated progress on a project_id basis as csv file.

    Parameters
    ----------
    filename: str
    '''

    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_progress_by_project_id) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated progress by project_id to %s' % filename)


def get_aggregated_progress_by_project_id_and_date(filename, project_id):
    '''
    Export aggregated progress on a project_id and daily basis as csv file.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        "COPY (SELECT * FROM aggregated_progress_by_project_id_and_date WHERE project_id = {}) TO STDOUT WITH CSV HEADER").format(
        sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated progress by project_id and date for project %s to %s' % (project_id, filename))
