from mapswipe_workers.generate_stats import project_stats
from mapswipe_workers.definitions import DATA_PATH
import pandas as pd
import numpy as np
from psycopg2 import sql
from mapswipe_workers import auth
import datetime

def get_results_by_project_id(filename, project_id):
    '''
    Export raw results on project_id basis.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        'COPY (SELECT * FROM results_test WHERE project_id = {}) TO STDOUT WITH CSV HEADER'
    ).format(sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)
    del pg_db

    df = pd.read_csv(filename)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day'] = df['timestamp'].apply(
        lambda df: datetime.datetime(year=df.year, month=df.month, day=df.day))
    df.set_index(df["day"], inplace=True)

    print(df)
    return df


def get_tasks_by_project_id(filename, project_id):
    '''
    Export raw results on project_id basis.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        'COPY (SELECT * FROM tasks_test WHERE project_id = {}) TO STDOUT WITH CSV HEADER'
    ).format(sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db


def get_groups_by_project_id(filename, project_id):
    '''
    Export raw results on project_id basis.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        'COPY (SELECT * FROM groups_test WHERE project_id = {}) TO STDOUT WITH CSV HEADER'
    ).format(sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db


def calc_agreement(total, no, yes, maybe, bad):

    if total == 1:
        agreement = 1
    else:
        agreement = 1 / (total * (total - 1)) * (
                        (no*(no - 1)) +
                        (yes * (yes - 1)) +
                        (maybe * (maybe - 1)) +
                        (bad * (bad - 1))
                    )

    return agreement


def agg_results_by_task_id(df):

    results_by_task_id_df = df.groupby(['project_id', 'group_id', 'task_id', 'result']).size().unstack(fill_value=0)
    results_by_task_id_df['total_count'] = results_by_task_id_df[0] + results_by_task_id_df[1] + results_by_task_id_df[2] + results_by_task_id_df[3]
    results_by_task_id_df['0_share'] = results_by_task_id_df[0] / results_by_task_id_df['total_count']
    results_by_task_id_df['1_share'] = results_by_task_id_df[1] / results_by_task_id_df['total_count']
    results_by_task_id_df['2_share'] = results_by_task_id_df[2] / results_by_task_id_df['total_count']
    results_by_task_id_df['3_share'] = results_by_task_id_df[3] / results_by_task_id_df['total_count']
    results_by_task_id_df['agreement'] = results_by_task_id_df.apply(lambda row: calc_agreement(row['total_count'], row[0], row[1], row[2], row[3]), axis=1)

    print(results_by_task_id_df)
    return results_by_task_id_df


project_id = '6'
results_filename = f'{DATA_PATH}/api-data/raw_results_{project_id}.csv'
tasks_filename = f'{DATA_PATH}/api-data/tasks_{project_id}.csv'
groups_filename = f'{DATA_PATH}/api-data/groups_{project_id}.csv'

results_df = get_results_by_project_id(results_filename, project_id)
# tasks_df = get_tasks_by_project_id(tasks_filename, project_id)
# groups_df = get_groups_by_project_id(groups_filename, project_id)


# results_df = pd.read_csv(results_filename)
# results_by_task_id_df = agg_results_by_task_id(results_df)




print(results_df.resample('D').count())

#results_by_date_df = results_df.groupy



'''
results_df[]

results_by_task_id_df = df.groupby(['project_id', 'group_id', 'task_id', 'result']).size().unstack(fill_value=0)

'''

#results_by_user_id_df = raw_results_df.groupby(['project_id', 'user_id', 'result']).size().unstack(fill_value=0)
#print(results_by_user_id_df)