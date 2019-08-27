from mapswipe_workers import auth
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import logger


# TODO: Should postgres views are defined instead of hardcoded sql queries?
def get_general_stats():

    pg_db = auth.postgresDB()

    query_select_project_total = '''
        SELECT COUNT(*)
        FROM projects;
    '''
    query_select_project_finished = '''
        SELECT COUNT(*)
        FROM projects
        WHERE progress=100;
    '''

    query_select_project_inactive = '''
        SELECT COUNT(*)
        FROM projects
        WHERE status='inactive';
    '''

    query_select_project_active = '''
        SELECT COUNT(*)
        FROM projects
        WHERE status='active';
    '''

    query_select_project_avg_progress = '''
        SELECT AVG(progress)
        FROM projects
        WHERE progress <> 100
        AND status='active';
    '''

    query_select_user_total = '''
        SELECT COUNT(*)
        FROM users;
    '''

    project_total = pg_db.retr_query(query_select_project_total)[0]
    project_finished = pg_db.retr_query(query_select_project_finished)[0]
    project_inactive = pg_db.retr_query(query_select_project_inactive)[0]
    project_active = pg_db.retr_query(query_select_project_active)[0]
    project_avg_progress = pg_db.retr_query(
            query_select_project_avg_progress
            )[0]
    user_total = pg_db.retr_query(query_select_user_total)[0]

    stats = {
            'project_total': project_total,
            'project_finished': project_finished,
            'project_inactive': project_inactive,
            'project_active': project_active,
            'project_avg_progress': project_avg_progress,
            'user_total': user_total,
            }

    del(pg_db)
    logger.info('generated stats')
    return stats


def get_all_active_projects():

    pg_db = auth.postgresDB()
    query_select_project_active = '''
        SELECT *
        FROM projects
        WHERE status='active';
    '''
    active_projects = pg_db.retr_query(query_select_project_active)[0]

    del(pg_db)
    logger.info('generated list of active projects')
    return active_projects


def get_aggregated_results(projects):
    """
    Returns
    -------
    aggregated_results: dict
    """

    # TODO: rewrite this function to work with new data structure
    # TODO: What is decision representing (avg(results))

    pg_db = auth.postgresDB()

    query_select_results = '''
        SELECT
          task_id AS id
          ,project_id AS project
          ,avg(cast(info ->> 'result' AS integer))AS decision
          ,SUM(CASE
            WHEN cast(info ->> 'result' AS integer) = 1 THEN 1
            ELSE 0
           END) AS yes_count
           ,SUM(CASE
            WHEN cast(info ->> 'result' AS integer) = 2 THEN 1
            ELSE 0
           END) AS maybe_count
           ,SUM(CASE
            WHEN cast(info ->> 'result' AS integer) = 3 THEN 1
            ELSE 0
           END) AS bad_imagery_count
        FROM
          results
        WHERE
          project_id = %s AND cast(info ->> 'result' as integer) > 0
        GROUP BY
          task_id
          ,project_id
        '''

    query_select_aggregated_results = '''
        SELECT project_id, COUNT(result) as yes_count
        FROM results
        AND result = 1
        GROUP BY project_id

        UNION

        SELECT project_id, COUNT(result) as maybe_count
        FROM results
        AND result = 2
        GROUP BY project_id

        UNION

        SELECT project_id, COUNT(result) as bad_imagery_count
        FROM results
        AND result = 3
        GROUP BY project_id
        '''

    aggregated_results = pg_db.retr_query(query_select_aggregated_results)
    del pg_db
    return aggregated_results
