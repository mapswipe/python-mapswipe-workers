import sys
from psycopg2 import sql

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger
from mapswipe_workers.definitions import DATA_PATH


def generate_stats(only_new_results=None):

    # get project_ids and user_ids of results in result_temp
    # we will generate stats only for these if flag is set
    if only_new_results:
        logger.info('will generate stats only for projects and users with new results')
        project_id_list = get_new_project_id_list()
        user_id_list = get_new_user_id_list()
    else:
        logger.info('will generate stats for all projects and users')
        project_id_list = get_project_id_list()
        user_id_list = get_user_id_list()

    filename = f'{DATA_PATH}/aggregated_results.csv'
    get_aggregated_results(filename)

    filename = f'{DATA_PATH}/aggregated_results_by_user_id.csv'
    get_aggregated_results_by_user_id(filename)

    filename = f'{DATA_PATH}/aggregated_results_by_project_id.csv'
    get_aggregated_results_by_project_id(filename)

    filename = f'{DATA_PATH}/aggregated_projects.csv'
    get_aggregated_projects(filename)

    filename = f'{DATA_PATH}/aggregated_projects_by_project_type.csv'
    get_aggregated_projects_by_project_type(filename)

    filename = f'{DATA_PATH}/aggregated_users.csv'
    get_aggregated_users(filename)

    filename = f'{DATA_PATH}/aggregated_progress_by_project_id.csv'
    get_aggregated_progress_by_project_id(filename)

    logger.info('start to export csv file for %s projects based on given project_id_list' % len(project_id_list))
    for project_id in project_id_list:
        filename = f'{DATA_PATH}/aggregated_results_by_task_id/aggregated_results_by_task_id_{project_id}.csv'
        get_aggregated_results_by_task_id(filename, project_id)

        filename = f'{DATA_PATH}/aggregated_results_by_project_id_and_date/aggregated_results_by_project_id_and_date_{project_id}.csv'
        get_aggregated_results_by_project_id_and_date(filename, project_id)

        filename = f'{DATA_PATH}/aggregated_progress_by_project_id_and_date/aggregated_progress_by_project_id_and_date_{project_id}.csv'
        get_aggregated_progress_by_project_id_and_date(filename, project_id)

    logger.info('start to export csv file for %s users based on given user_id_list' % len(user_id_list))
    for user_id in user_id_list:
        filename = f'{DATA_PATH}/aggregated_results_by_user_id_and_date/aggregated_results_by_user_id_and_date_{user_id}.csv'
        get_aggregated_results_by_user_id_and_date(filename, user_id)

    logger.info('exported statistics based on results, projects and users tables in postgres')


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


def get_new_project_id_list():
    '''
    Get the project_ids for all results which have been uploaded to result_temp
    '''

    p_con = auth.postgresDB()
    query_get_project_ids = '''
                SELECT distinct(project_id) FROM results_temp
            '''
    project_ids = p_con.retr_query(query_get_project_ids)
    del p_con

    project_id_list = set([])
    for i in range(0, len(project_ids)):
        project_id_list.add(project_ids[i][0])

    return project_id_list


def get_new_user_id_list():
    '''
    Get the user_ids for all results which have been uploaded to result_temp
    '''

    p_con = auth.postgresDB()
    query_get_user_ids = '''
                    SELECT distinct(user_id) FROM results_temp
                '''
    user_ids = p_con.retr_query(query_get_user_ids)
    del p_con

    user_id_list = set([])
    for i in range(0, len(user_ids)):
        user_id_list.add(user_ids[i][0])

    return user_id_list


def get_project_id_list():
    '''
    Get the project_ids for all results in results table
    '''

    p_con = auth.postgresDB()
    query_get_project_ids = '''
                SELECT distinct(project_id) FROM results
            '''
    project_ids = p_con.retr_query(query_get_project_ids)
    del p_con

    project_id_list = set([])
    for i in range(0, len(project_ids)):
        project_id_list.add(project_ids[i][0])

    return project_id_list


def get_user_id_list():
    '''
    Get the user_ids for all results in results table
    '''

    p_con = auth.postgresDB()
    query_get_user_ids = '''
                    SELECT distinct(user_id) FROM results
                '''
    user_ids = p_con.retr_query(query_get_user_ids)
    del p_con

    user_id_list = set([])
    for i in range(0, len(user_ids)):
        user_id_list.add(user_ids[i][0])

    return user_id_list