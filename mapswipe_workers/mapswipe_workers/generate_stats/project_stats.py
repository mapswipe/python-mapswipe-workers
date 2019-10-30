import os
from psycopg2 import sql
import pandas as pd
import datetime
from mapswipe_workers import auth
from mapswipe_workers.definitions import logger
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.utils import geojson_functions


def id_to_string(x):
    try:
        x = str(int(x))
    except:
        x = str(x)

    return x


def get_results_by_project_id(filename, project_id):
    '''
    Export results for the given project id.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        'COPY (SELECT * FROM results WHERE project_id = {}) TO STDOUT WITH CSV HEADER'
    ).format(sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)
    del pg_db
    logger.info(f'got results from postgres for {project_id}')

    df = pd.read_csv(filename)

    if len(df) > 0:
        df['group_id'] = df.apply(lambda row: id_to_string(row['group_id']), axis=1)
        df['group_id'] = df['group_id'].astype(str)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['day'] = df['timestamp'].apply(
            lambda df: datetime.datetime(year=df.year, month=df.month, day=df.day))
        logger.info(f'created pandas results df for {project_id}')
        return df
    else:
        logger.info(f'there are no results for this project {project_id}')
        return None


def get_tasks_by_project_id(filename, project_id):
    '''
    Export tasks for the given project id.  Only export if not already downloaded before.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    if os.path.isfile(filename):
        logger.info(f'file {filename} already exists for {project_id}. skip download.')
        pass
    else:
        pg_db = auth.postgresDB()
        sql_query = sql.SQL(
            'COPY (SELECT project_id, group_id, task_id, ST_AsText(geom) as geom FROM tasks WHERE project_id = {}) TO STDOUT WITH CSV HEADER'
        ).format(sql.Literal(project_id))

        with open(filename, 'w') as f:
            pg_db.copy_expert(sql_query, f)

        del pg_db
        logger.info(f'got tasks from postgres for {project_id}')

    df = pd.read_csv(filename)
    df['group_id'] = df.apply(lambda row: id_to_string(row['group_id']), axis=1)
    df['group_id'] = df['group_id'].astype(str)

    logger.info(f'created pandas tasks df for {project_id}')
    return df


def get_groups_by_project_id(filename, project_id):
    '''
    Export groups based on given project id. Only export if not already downloaded before.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    if os.path.isfile(filename):
        logger.info(f'file {filename} already exists for {project_id}. skip download.')
        pass
    else:
        pg_db = auth.postgresDB()
        sql_query = sql.SQL(
            'COPY (SELECT * FROM groups WHERE project_id = {}) TO STDOUT WITH CSV HEADER'
        ).format(sql.Literal(project_id))

        with open(filename, 'w') as f:
            pg_db.copy_expert(sql_query, f)

        del pg_db
        logger.info(f'got groups from postgres for {project_id}')

    df = pd.read_csv(filename)
    df['group_id'] = df.apply(lambda row: id_to_string(row['group_id']), axis=1)
    df['group_id'] = df['group_id'].astype(str)
    df['number_of_users_required'] = df['required_count'] + df['finished_count']

    logger.info(f'created pandas groups df for {project_id}')
    return df


def calc_agreement(total, no, yes, maybe, bad):
    '''
    for each task the "agreement" is computed as defined by Scott's Pi to give a measure for inter-rater reliability
    https://en.wikipedia.org/wiki/Scott%27s_Pi
    '''

    if total == 1:
        agreement = 1
    else:
        agreement = 1 / (total * (total - 1)) * (
                        (no*(no - 1)) +
                        (yes * (yes - 1)) +
                        (maybe * (maybe - 1)) +
                        (bad * (bad - 1)))

    return agreement


def calc_results_progress(number_of_users, number_of_users_required, cum_number_of_users, number_of_tasks, number_of_results):
    '''
    for each project the progress is calculated
    not all results are considered when calculating the progress
    if the required number of users has been reached for a task
    all further results will not contribute to increase the progress
    '''

    if cum_number_of_users <= number_of_users_required:
        # this is the simplest case, the number of users is less than the required number of users
        # all results contribute to progress
        number_of_results_progress = number_of_results
    elif (cum_number_of_users - number_of_users) < number_of_users_required:
        # the number of users is bigger than the number of users required
        # but the previous number of users was below the required number
        # some results contribute to progress
        number_of_results_progress = (number_of_users_required - (cum_number_of_users - number_of_users)) * number_of_tasks
    else:
        # for all other cases: already more users than required
        # all results do not contribute to progress
        number_of_results_progress = 0

    return number_of_results_progress


def agg_results_by_task_id(results_df, tasks_df):
    '''
    for each task several users contribute results
    this functions aggregates using task id
    the following values are calculated:
    total_count, 0_count, 1_count, 2_count, 3_count
    0_share, 1_share, 2_share, 3_share, agreement
    '''


    results_by_task_id_df = results_df.groupby(['project_id', 'group_id', 'task_id', 'result']).size().unstack(fill_value=0)

    if 0 not in results_by_task_id_df.columns:
        results_by_task_id_df[0] = 0

    if 1 not in results_by_task_id_df.columns:
        results_by_task_id_df[1] = 0

    if 2 not in results_by_task_id_df.columns:
        results_by_task_id_df[2] = 0

    if 3 not in results_by_task_id_df.columns:
        results_by_task_id_df[3] = 0

    results_by_task_id_df['total_count'] = results_by_task_id_df[0] + results_by_task_id_df[1] + results_by_task_id_df[2] + results_by_task_id_df[3]
    results_by_task_id_df['0_share'] = results_by_task_id_df[0] / results_by_task_id_df['total_count']
    results_by_task_id_df['1_share'] = results_by_task_id_df[1] / results_by_task_id_df['total_count']
    results_by_task_id_df['2_share'] = results_by_task_id_df[2] / results_by_task_id_df['total_count']
    results_by_task_id_df['3_share'] = results_by_task_id_df[3] / results_by_task_id_df['total_count']
    results_by_task_id_df['agreement'] = results_by_task_id_df.apply(lambda row: calc_agreement(row['total_count'], row[0], row[1], row[2], row[3]), axis=1)
    # rename columns, ogr2ogr will fail otherwise
    results_by_task_id_df.rename(columns={
        0: '0_count',
        1: '1_count',
        2: '2_count',
        3: '3_count'

    }, inplace=True)

    logger.info(f'aggregated results by task id and computed agreement')

    agg_results_df = results_by_task_id_df.merge(tasks_df[['geom', 'task_id']], left_on='task_id', right_on='task_id')
    logger.info(f'added geometry to aggregated results')

    return agg_results_df


def get_progress_by_date(results_df, groups_df):
    '''
    for each project we retrospectively generate the following attributes for a given date utilizing the results:
    number_of_results, cum_number_of_results, progress, cum_progress
    '''


    groups_df['required_results'] = groups_df['number_of_tasks'] * groups_df['number_of_users_required']
    required_results = groups_df['required_results'].sum()
    logger.info(f'calcuated required results: {required_results}')

    results_with_groups_df = results_df.merge(groups_df, left_on='group_id', right_on='group_id')
    results_by_group_id_df = results_with_groups_df.groupby(['project_id_x', 'group_id', 'day']).agg(
        number_of_tasks=pd.NamedAgg(column='number_of_tasks', aggfunc='min'),
        number_of_users_required=pd.NamedAgg(column='number_of_users_required', aggfunc='min'),
        number_of_users=pd.NamedAgg(column='user_id', aggfunc=pd.Series.nunique)
    )
    results_by_group_id_df['number_of_results'] = results_by_group_id_df['number_of_users'] * results_by_group_id_df['number_of_tasks']
    results_by_group_id_df['cum_number_of_users'] = results_by_group_id_df['number_of_users'].groupby(['project_id_x', 'group_id']).cumsum()
    results_by_group_id_df['number_of_results_progress'] = results_by_group_id_df.apply(lambda row: calc_results_progress(
        row['number_of_users'],
        row['number_of_users_required'],
        row['cum_number_of_users'],
        row['number_of_tasks'],
        row['number_of_results']
    ), axis=1)

    progress_by_date_df = results_by_group_id_df.reset_index().groupby(['day']).agg(
        number_of_results=pd.NamedAgg(column='number_of_results', aggfunc='sum'),
        number_of_results_progress=pd.NamedAgg(column='number_of_results_progress', aggfunc='sum')
    )
    progress_by_date_df['cum_number_of_results'] = progress_by_date_df['number_of_results'].cumsum()
    progress_by_date_df['cum_number_of_results_progress'] = progress_by_date_df['number_of_results_progress'].cumsum()
    progress_by_date_df['progress'] = progress_by_date_df['number_of_results_progress'] / required_results
    progress_by_date_df['cum_progress'] = progress_by_date_df['cum_number_of_results_progress'] / required_results

    logger.info('calculated progress by date')
    return progress_by_date_df


def get_new_user(day, first_day):
    '''
    Check if user has contributed results to this project before
    '''

    if day == first_day:
        return 1
    else:
        return 0


def get_contributors_by_date(results_df):
    '''
    for each project we retrospectively generate the following attributes for a given date utilizing the results:
    number_of_users, number_of_new_users, cum_number_of_users
    '''

    user_first_day_df = results_df.groupby(['user_id']).agg(
        first_day=pd.NamedAgg(column='day', aggfunc='min')
    )
    logger.info('calculated first day per user')

    results_by_user_id_df = results_df.groupby(['project_id', 'user_id', 'day']).agg(
        number_of_results=pd.NamedAgg(column='user_id', aggfunc='count')
    )
    results_by_user_id_df = results_by_user_id_df.reset_index().merge(user_first_day_df, left_on='user_id', right_on='user_id')
    results_by_user_id_df['new_user'] = results_by_user_id_df.apply(
        lambda row: get_new_user(row['day'], row['first_day']),
        axis=1
    )

    contributors_by_date_df = results_by_user_id_df.reset_index().groupby(['project_id', 'day']).agg(
        number_of_users=pd.NamedAgg(column='user_id', aggfunc=pd.Series.nunique),
        number_of_new_users=pd.NamedAgg(column='new_user', aggfunc='sum')
    )
    contributors_by_date_df['cum_number_of_users'] = contributors_by_date_df['number_of_new_users'].cumsum()

    logger.info('calculated contributors by date')
    return contributors_by_date_df


def get_per_project_statistics(project_id):
    '''
    the function to calculate all project related statistics
    will derive:
    results, groups, tasks, agg_results, history
    '''

    # set filenames
    results_filename = f'{DATA_PATH}/api-data/results/results_{project_id}.csv'
    tasks_filename = f'{DATA_PATH}/api-data/tasks/tasks_{project_id}.csv'
    groups_filename = f'{DATA_PATH}/api-data/groups/groups_{project_id}.csv'
    agg_results_filename = f'{DATA_PATH}/api-data/agg_results/agg_results_{project_id}.csv'
    project_stats_by_date_filename = f'{DATA_PATH}/api-data/history/history_{project_id}.csv'

    # load data from postgres or local storage if already downloaded
    results_df = get_results_by_project_id(results_filename, project_id)

    if results_df is None:
        logger.info(f'no results: skipping per project stats for {project_id}')
        return None
    else:
        groups_df = get_groups_by_project_id(groups_filename, project_id)
        tasks_df = get_tasks_by_project_id(tasks_filename, project_id)

        # aggregate results by task id
        agg_results_df = agg_results_by_task_id(results_df, tasks_df)
        agg_results_df.to_csv(agg_results_filename, index_label='idx')
        logger.info(f'saved agg results for {project_id}: {agg_results_filename}')
        geojson_functions.csv_to_geojson(agg_results_filename, 'geom')

        # calculate progress by date
        progress_by_date_df = get_progress_by_date(results_df, groups_df)

        # calculate contributors by date
        contributors_by_date_df = get_contributors_by_date(results_df)

        # merge contributors and progress
        project_stats_by_date_df = progress_by_date_df.merge(contributors_by_date_df, left_on='day', right_on='day')
        project_stats_by_date_df['project_id'] = project_id
        project_stats_by_date_df.to_csv(project_stats_by_date_filename)
        logger.info(f'saved project stats by date for {project_id}: {project_stats_by_date_filename}')

        project_stats_dict = {
            'project_id': project_id,
            'progress': project_stats_by_date_df['cum_progress'].iloc[-1],
            'number_of_users': project_stats_by_date_df['cum_number_of_users'].iloc[-1],
            'number_of_results': project_stats_by_date_df['cum_number_of_results'].iloc[-1],
            'number_of_results_progress': project_stats_by_date_df['cum_number_of_results_progress'].iloc[-1],
            'day': project_stats_by_date_df.index[-1]
        }

        return project_stats_dict

