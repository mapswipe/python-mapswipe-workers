import os
import subprocess
from psycopg2 import sql
import dateutil
import dateutil.parser
import json

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger
from mapswipe_workers.definitions import DATA_PATH

from mapswipe_workers.generate_stats import project_stats
from mapswipe_workers.generate_stats import overall_stats
from mapswipe_workers.generate_stats import user_stats


def generate_stats(only_new_results):
    filename = f'{DATA_PATH}/api-data/last_update.txt'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            timestamp = f.read()
            last_update = dateutil.parser.parse(timestamp)
            logger.info(f'got last_update timestamp {last_update} from file {filename}')
    else:
        last_update = None

    # we will generate stats only for these if flag is set
    if only_new_results and last_update:
        logger.info('will generate stats only for projects and users with new results')
        # get project_ids and user_ids for results created after last update
        project_id_list = get_new_project_id_list(last_update)
        user_id_list = get_new_user_id_list(last_update)
    else:
        logger.info('will generate stats for all projects and users')
        project_id_list = get_project_id_list()
        user_id_list = get_user_id_list()

    # get new last_update timestamp
    last_update = get_last_result()

    # get project stats
    for project_id in project_id_list:

        # results
        filename = f'{DATA_PATH}/api-data/results/{project_id}_results_by_task_id.csv'
        project_stats.get_results_by_task_id(filename, project_id)
        csv_to_geojson(filename, 'geom')

        # progress
        filename = f'{DATA_PATH}/api-data/progress/{project_id}_progress_by_date.csv'
        project_stats.get_progress_by_date(filename, project_id)

        # contributors
        # project_stats.get_contributors_by_date(filename, project_id)

    # get user stats
    for user_id in user_id_list:
        pass

    # get overall stats
    # overall_stats.get_overall_stats()
    # csv_to_geojson(filename, 'geom')
    # csv_to_geojson(filename, 'centroid')

    '''


    filename = f'{DATA_PATH}/api-data/agg_results.csv'
    get_aggregated_results(filename)

    filename = f'{DATA_PATH}/api-data/agg_res_by_user_id.csv'
    get_aggregated_results_by_user_id(filename)

    filename = f'{DATA_PATH}/api-data/agg_res_by_project_id.csv'
    get_aggregated_results_by_project_id(filename)
    csv_to_geojson(filename, 'geom')
    csv_to_geojson(filename, 'centroid')


    filename = f'{DATA_PATH}/api-data/agg_projects.csv'
    get_aggregated_projects(filename)

    filename = f'{DATA_PATH}/api-data/agg_projects_by_project_type.csv'
    get_aggregated_projects_by_project_type(filename)

    filename = f'{DATA_PATH}/api-data/agg_users.csv'
    get_aggregated_users(filename)

    filename = f'{DATA_PATH}/api-data/agg_progress_by_project_id.csv'
    get_aggregated_progress_by_project_id(filename)
    csv_to_geojson(filename, 'geom')
    csv_to_geojson(filename, 'centroid')

    logger.info('start to export csv file for %s projects based on given project_id_list' % len(project_id_list))
    for project_id in project_id_list:
        filename = f'{DATA_PATH}/api-data/agg_res_by_task_id/agg_res_by_task_id_{project_id}.csv'
        get_aggregated_results_by_task_id(filename, project_id)

        filename = f'{DATA_PATH}/api-data/agg_res_by_task_id/agg_res_by_task_id_geom_{project_id}.csv'
        get_aggregated_results_by_task_id_geom(filename, project_id)
        csv_to_geojson(filename)

        filename = f'{DATA_PATH}/api-data/agg_res_by_project_id_and_date/agg_res_by_project_id_and_date_{project_id}.csv'
        get_aggregated_results_by_project_id_and_date(filename, project_id)

        filename = f'{DATA_PATH}/api-data/agg_progress_by_project_id_and_date/agg_progress_by_project_id_and_date_{project_id}.csv'
        get_aggregated_progress_by_project_id_and_date(filename, project_id)

    logger.info('start to export csv file for %s users based on given user_id_list' % len(user_id_list))
    for user_id in user_id_list:
        filename = f'{DATA_PATH}/api-data/agg_res_by_user_id_and_date/agg_res_by_user_id_and_date_{user_id}.csv'
        get_aggregated_results_by_user_id_and_date(filename, user_id)

    # write new last_update file, if there are any results in postgres
    if last_update:
        filename = f'{DATA_PATH}/api-data/last_update.txt'
        with open(filename, 'w') as f:
            timestamp = last_update.strftime('%Y-%m-%dT%H:%M:%S.%f')
            f.write(timestamp)
            logger.info(f'wrote last_update timestamp {timestamp} to file {filename}')
    '''
    logger.info('exported statistics based on results, projects and users tables in postgres')


def get_new_project_id_list(last_update):
    '''
    Get the project_ids for all results which have been uploaded to result_temp
    '''

    p_con = auth.postgresDB()
    query_get_project_ids = '''
                SELECT distinct(project_id) FROM results WHERE timestamp > %s;
            '''
    data = [last_update]
    project_ids = p_con.retr_query(query_get_project_ids, data)
    del p_con

    project_id_list = set([])
    for i in range(0, len(project_ids)):
        project_id_list.add(project_ids[i][0])

    return project_id_list


def get_new_user_id_list(last_update):
    '''
    Get the user_ids for all results which have been uploaded to result_temp
    '''

    p_con = auth.postgresDB()
    query_get_user_ids = '''
                    SELECT distinct(user_id) FROM results WHERE timestamp > %s;
                '''
    data = [last_update]
    user_ids = p_con.retr_query(query_get_user_ids, data)
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


def get_last_result():
    '''
    Get the user_ids for all results in results table
    '''

    p_con = auth.postgresDB()
    query_get_last_result = '''
                    SELECT timestamp FROM results ORDER BY timestamp DESC LIMIT 1
                '''
    last_updates = p_con.retr_query(query_get_last_result)
    del p_con

    if last_updates:
        last_update = last_updates[0][0]
    else:
        last_update = None

    return last_update


def csv_to_geojson(filename, geometry_field='geom'):
    '''
    Use ogr2ogr to convert csv file to GeoJSON
    '''

    outfile = filename.replace('.csv', f'_{geometry_field}.geojson')
    # need to remove file here because ogr2ogr can't overwrite when choosing GeoJSON
    if os.path.isfile(outfile):
        os.remove(outfile)
    filename_without_path = filename.split('/')[-1].replace('.csv', '')
    # TODO: remove geom column from normal attributes in sql query
    subprocess.run([
        "ogr2ogr",
        "-f",
        "GeoJSON",
        outfile,
        filename,
        "-sql",
        f'SELECT *, CAST({geometry_field} as geometry) FROM "{filename_without_path}"'
    ], check=True)
    logger.info(f'converted {filename} to {outfile}.')

    cast_datatypes_for_geojson(outfile)


def cast_datatypes_for_geojson(filename):
    '''
    Go through geojson file and try to cast all values as float, except project_id
    remove redundant geometry property
    '''
    filename = filename.replace('csv', 'geojson')
    with open(filename) as f:
        geojson_data = json.load(f)

    properties = list(geojson_data['features'][0]['properties'].keys())

    for i in range(0, len(geojson_data['features'])):
        for property in properties:
            if property in ['project_id', 'name', 'project_details', 'task_id', 'group_id']:
                # don't try to cast project_id
                pass
            elif property in ['geom']:
                # remove redundant geometry property
                del geojson_data['features'][i]['properties'][property]
            else:
                try:
                    geojson_data['features'][i]['properties'][property] = float(geojson_data['features'][i]['properties'][property])
                except:
                    pass

    with open(filename, 'w') as f:
        json.dump(geojson_data, f)
    logger.info(f'converted datatypes for {filename}.')
