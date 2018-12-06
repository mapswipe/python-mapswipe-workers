import logging
import json
import os
import csv
import requests

from mapswipe_workers.basic import auth
# Make sure to import all project types here
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaProject import BuildAreaProject
from mapswipe_workers.ProjectTypes.Footprint.FootprintProject import FootprintProject


########################################################################################################################
# INIT                                                                                                                 #
########################################################################################################################
def get_environment(modus='development'):
    """
    The function to get the firebase and mysql configuration

    Parameters
    ----------
    modus : str
        either `development` or `production to decide which firebase configuration to use

    Returns
    -------
    firebase : pyrebase firebase object
            initialized firebase app with admin authentication
    mysqlDB : database connection class
        The database connection to mysql database
    """
    if modus == 'development':
        # we use the dev instance for testing
        firebase = auth.dev_firebase_admin_auth()
        mysqlDB = auth.dev_psqlDB
        logging.warning('ALL - get_environment - use development instance')
    elif modus == 'production':
        # we use the dev instance for testing
        firebase = auth.firebase_admin_auth()
        mysqlDB = auth.mysqlDB
        logging.warning('ALL - get_environment - use production instance')
    else:
        firebase = None
        mysqlDB = None

    return firebase, mysqlDB


def init_project(project_type, project_id, firebase, mysqlDB, import_key=None, import_dict=None):
    """
    The function to init a project in regard to its type

    Parameters
    ----------
    project_type : int
        the type of the project
    project_id: int
        the id of the project

    Returns
    -------
    proj :
        the project instance
    """

    class_to_type = {
        # Make sure to import all project types here
        1: BuildAreaProject,
        2: FootprintProject
    }

    proj = class_to_type[project_type](project_id, firebase, mysqlDB, import_key, import_dict)
    return proj


def get_projects(firebase, mysqlDB, filter='all'):
    """
    The function to download project information from firebase and init the projects
    Parameters
    ----------
    firebase : pyrebase firebase object
            initialized firebase app with admin authentication
    mysqlDB : database connection class
        The database connection to mysql database
    filter : str or list
        The filter for the projects.
        Can be either 'all', 'active', 'not_finished' or a list of project ids as integer

    Returns
    -------
    projects_list : list
        The list containing the projects
    """
    # create a list for projects according to filter
    projects_list = []

    fb_db = firebase.database()
    all_projects = fb_db.child("projects").get().val()

    # we need to check if the user provided a list of project ids to filter
    if type(filter) is list:
        project_ids = filter.copy()
        filter = 'user'
    else:
        project_ids = []

    for project_id in all_projects:

        # a valid project in firebase has at least 12 attributes
        if len(all_projects[project_id]) < 12:
            logging.warning('%s - get_projects - project is in firebase, but misses critical information' % project_id)
            continue

        # we check all conditions for each group of projects
        conditions = {
            'all': True,
            'active': all_projects[project_id]['state'] == 0,
            'not_finished': all_projects[project_id]['progress'] < 100,
            'user': int(project_id) in project_ids
        }

        if conditions[filter]:
            try:
                project_type = all_projects[project_id]['projectType']
            except:
                project_type = 1
            proj = init_project(project_type, project_id, firebase, mysqlDB)
            projects_list.append(proj)

    return projects_list


########################################################################################################################
# IMPORT                                                                                                               #
########################################################################################################################
def get_new_project_id(firebase):
    """
    The function to get a project id which is not used in firebase

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    new_project_id : int
        a new project id which has not been used in firebase

    Notes
    -----
        the new project id needs to be increased by more than 1 to avoid firebase json parsed as an array
        more information here: https://firebase.googleblog.com/2014/04/best-practices-arrays-in-firebase.html
    """

    fb_db = firebase.database()

    project_keys = fb_db.child('projects').shallow().get().val()
    if not project_keys:
        # set mininum project id to 1000, if no project has been imported yet
        project_keys = [1000]

    project_ids = list(map(int, list(project_keys)))
    project_ids.sort()
    highest_project_id = project_ids[-1]

    logging.warning('ALL - get_new_project_id - highest existing project id: %s' % highest_project_id)
    new_project_id = highest_project_id + 2

    logging.warning('ALL - get_new_project_id - returned new project id: %s' % new_project_id)
    return new_project_id


def get_new_imports(firebase):
    """
    The function to get new project imports from firebase which have not been imported

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    new_imports : dict
        a dictionary of imports which have not been imported already
    """

    fb_db = firebase.database()
    all_imports = fb_db.child("imports").get().val()

    new_imports = {}
    if all_imports:
        for import_key, new_import in all_imports.items():
            try:
                # check if project was already imported and "complete" is set
                complete = new_import['complete']
            except:
                # insert into new projects dict
                new_imports[import_key] = new_import

    logging.warning('ALL - get_new_imports - got %s projects which have not been imported' % len(new_imports))
    return new_imports


def run_import(modus):
    """
    A function to create all newly imported projects in firebase

    Parameters
    ----------
    modus : str
        either `development` or `production to decide which firebase configuration to use

    Returns
    -------
    imported_projects : list
        list of project ids of imported projects
    """

    # get dev or production environment for firebase and mysql
    firebase, mysqlDB = get_environment(modus)

    # this will return a list of imports
    imported_projects = []

    # check for new imports in firebase
    imports = get_new_imports(firebase)
    for import_key, new_import in imports.items():

        # let's create a project now
        project_id = get_new_project_id(firebase)
        try:
            project_type = new_import['projectType']
        except:
            project_type = 1

        # this will be the place, where we distinguish different project types
        proj = init_project(project_type, project_id, firebase, mysqlDB, import_key, new_import)
        proj.import_project(firebase, mysqlDB)
        imported_projects.append(proj.id)

    return imported_projects


########################################################################################################################
# UPDATE                                                                                                               #
########################################################################################################################
def run_update(modus, filter, output_path):
    """
    The function to update project progress and contributors in firebase

    Parameters
    ----------
    modus : str
        The environment to use for firebase and mysql
        Can be either 'development' or 'production'
    filter : str or list
        The filter for the projects.
        Can be either 'all', 'active', 'not_finished' or a list of project ids as integer
    output_path: str
        The output path of the logs for progress and contributors

    Returns
    -------
    updated_projects : list
        The list of all projects ids for projects which have been updated
    """

    # get dev or production environment for firebase and mysql
    firebase, mysqlDB = get_environment(modus)

    project_list = get_projects(firebase, filter)
    updated_projects = []
    for proj in project_list:
        proj.update_project(firebase, mysqlDB, output_path)
        updated_projects.append(proj.id)

    return updated_projects


########################################################################################################################
# TRANSFER RESULTS                                                                                                     #
########################################################################################################################
def get_results_from_firebase(firebase):
    """
    The function to download all results from firebase

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    results : dict
        The results in a dictionary with the following format:
        {
        "task_id" {
            "user1_id": {
                "data": {...}
                },
            "user2_id": {
                "data": {...}
                },
            }
        }
    """

    fb_db = firebase.database()
    results = fb_db.child("results").get().val()
    return results


def delete_firebase_results(firebase, all_results):
    """
    The function to delete all results in firebase

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication
    results : dict
        The results in a dictionary with the following format:
        {
        "task_id": {
            "user1_id": {},
            "user2_id": {},
            }
        }

    Returns
    -------
    bool
        True if successful, False otherwise

    Notes
    -----
    We use the update method of firebase instead of delete.
    Update allows to delete items at multiple locations at the same time.
    """

    fb_db = firebase.database()
    # we will use multilocation update to deete the entries
    # therefore we crate an dict with the items we want to delete
    data = {}
    for task_id, results in all_results.items():
        for child_id, result in results.items():
            key = 'results/{task_id}/{child_id}'.format(
                task_id=task_id,
                child_id=child_id)

            data[key] = None

    fb_db.update(data)
    del fb_db

    logging.warning('ALL - delete_firebase_results - deleted all results in firebase')
    return True


def results_to_txt(all_results):
    """
    The function to save results from firebase in csv format

    Parameters
    ----------
    all_results : dict
        The results in a dictionary with the following format:
        {
        "task_id" {
            "user1_id": {
                "data": {...}
                },
            "user2_id": {
                "data": {...}
                },
            }
        }

    Returns
    -------
    results_txt_filename : str
        The name of the file with the results

    """
    results_txt_filename = 'raw_results.txt'

    # If csv file is a file object, it should be opened with newline=''
    results_txt_file = open(results_txt_filename, 'w', newline='')

    fieldnames = ('task_id', 'project_id', 'user_id', 'timestamp', 'info')
    w = csv.DictWriter(results_txt_file, fieldnames=fieldnames, delimiter='\t', quotechar="'")

    number_of_results = 0
    for task_id, results in all_results.items():
        for child_id, result in results.items():
            number_of_results += 1

            try:
                output_dict = {
                    "task_id": result['data']['id'],
                    "project_id": int(result['data']['projectId']),
                    "user_id": result['data']['user'],
                    "timestamp": int(result['data']['timestamp']),
                    "info": {}
                }

                for key in result['data'].keys():
                    # those keys have already been set
                    if not key in ['user', 'projectId', 'timestamp', 'id']:
                        output_dict['info'][key] = result['data'][key]

                # the info column should have json format for uploading to mysql
                output_dict['info'] = json.dumps(output_dict['info'])

                w.writerow(output_dict)

            except Exception as e:
                logging.warning('ALL - results_to_txt - result missed critical information: %s' % e)

    results_txt_file.close()
    logging.warning('ALL - results_to_txt - there are %s results to import' % number_of_results)
    logging.warning('ALL - results_to_txt - created file: %s' % results_txt_filename)
    return results_txt_filename


def save_results_mysql(mysqlDB, results_filename):
    """
    The function to save results in the mysql database

    Parameters
    ----------
    mysqlDB : database connection class
            The database connection to mysql database
    results_filename : str
        The name of the file with the results

    Returns
    -------
    bool
        True if successful, False otherwise
    """


    ### this function saves the results from firebase to the mysql database

    # pre step delete table if exist
    m_con = mysqlDB()
    sql_insert = 'DROP TABLE IF EXISTS raw_results CASCADE;'
    m_con.query(sql_insert, None)

    # first importer to a table where we store the geom as text
    sql_insert = '''
        DROP TABLE IF EXISTS raw_results;
        CREATE TABLE raw_results (
            task_id varchar,
            project_id int,
            user_id varchar,
            timestamp bigint,
            info json
        );
        '''

    m_con.query(sql_insert, None)

    # copy data to the new table
    # old: mysql we should use LOAD DATA LOCAL INFILE Syntax

    f = open(results_filename, 'r')
    columns = ['task_id', 'project_id', 'user_id', 'timestamp', 'info']
    m_con.copy_from(f, 'raw_results', sep='\t', columns=columns)
    logging.warning('ALL - save_results_mysql - inserted raw results into table raw_results')
    f.close()

    os.remove(results_filename)
    logging.warning('ALL - save_results_mysql - deleted file: %s' % results_filename)

    # second import all entries into the task table and convert into psql geometry
    sql_insert = '''
        INSERT INTO
          results
        SELECT
          *,
          -- duplicates is set to zero by default, this will be updated on conflict only
          0
        FROM
          raw_results
        ON CONFLICT ON CONSTRAINT "results_pkey"
          DO UPDATE SET duplicates = results.duplicates + 1
    '''

    m_con.query(sql_insert, None)
    logging.warning('ALL - save_results_mysql - inserted results into results table and updated duplicates count')

    del m_con
    return True


def run_transfer_results(modus, results_filename='data/results.json'):
    """

    Parameters
    ----------
    modus : str
        The environment to use for firebase and mysql
        Can be either 'development' or 'production'
    results_filename : str
        The name of the file with the results

    Returns
    -------
    bool
        True if successful, False otherwise

    TODO
    ----
    How to deal with results from projects with different types?
    Projects might not always return an integer as result.
    """


    # get dev or production environment for firebase and mysql
    firebase, mysqlDB = get_environment(modus)

    # first check if we have results stored locally, that have not been inserted in MySQL
    if os.path.isfile(results_filename):
        # start to import the old results first
        with open(results_filename) as results_file:
            results = json.load(results_file)
            results_txt_filename = results_to_txt(results)
            logging.warning("ALL - run_transfer_results - there are results in %s that we didnt't insert. do it now!" % results_filename)
            save_results_mysql(mysqlDB, results_txt_filename)
            delete_firebase_results(firebase, results)

        os.remove(results_filename)
        logging.warning('ALL - run_transfer_results - removed "results.json" file')

    fb_db = firebase.database()

    # this tries to set the max pool connections to 100
    adapter = requests.adapters.HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
    for scheme in ('http://', 'https://'):
        fb_db.requests.mount(scheme, adapter)


    # download all results and save as in json file to avoid data loss when script fails
    all_results = fb_db.child("results").get().val()
    del fb_db

    logging.warning('ALL - run_transfer_results - downloaded all results from firebase')
    # test if there are any results to transfer
    if all_results:
        with open(results_filename, 'w') as fp:
            json.dump(all_results, fp)
            logging.warning('ALL - run_transfer_results - wrote results data to %s' % results_filename)

        results_txt_filename = results_to_txt(all_results)
        save_results_mysql(mysqlDB, results_txt_filename)
        delete_firebase_results(firebase, all_results)
        os.remove(results_filename)
        logging.warning('ALL - run_transfer_results - removed %s' % results_filename)
    else:
        logging.warning('ALL - run_transfer_results - there are no results to transfer in firebase')

    return True

########################################################################################################################
# EXPORT                                                                                                               #
########################################################################################################################
def export_all_projects(firebase, output_path='data'):
    """
    The function to export all projects in a json file

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication
    output_path: str
        The output path of the json files

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # check if output path for projects is correct and existing
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    fb_db = firebase.database()
    all_projects = fb_db.child("projects").get().val()

    if not all_projects:
        logging.warning("ALL - export_all_projects - no projects in firebase. Can't export")
        return False
    else:
        # save projects as json
        output_json_file = '{}/projects.json'.format(output_path)
        with open(output_json_file, 'w') as outfile:
            json.dump(all_projects, outfile)
        logging.warning('ALL - export_all_projects - exported projects file: %s' % output_json_file)
        return True



def export_users_and_stats(firebase, output_path='data'):
    """
    The function to save users and stats as a json file

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication
    output_path: str
        The output path of the json files

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # check if output path for projects is correct and existing
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    fb_db = firebase.database()
    all_users = fb_db.child("users").get().val()

    if not all_users:
        logging.warning("ALL - export_users_and_stats - no users in firebase. Can't export")
        return False
    else:
        # compute stats from user data and save in dict
        stats = {
            'users': len(all_users),
            'totalDistanceMappedInSqKm': 0,
            'totalContributionsByUsers': 0
        }

        for user in all_users:
            try:
                # for some user there might be no distance attribute, if they didn't map anything etc.
                stats['totalDistanceMappedInSqKm'] += all_users[user]['distance']
                stats['totalContributionsByUsers'] += all_users[user]['contributions']
            except:
                pass

        # export users as json file
        output_json_file = '{}/users.json'.format(output_path)
        with open(output_json_file, 'w') as outfile:
            json.dump(all_users, outfile)
        logging.warning('ALL - export_users_and_stats - exported users file: %s' % output_json_file)

        # export stats as json file
        output_json_file = '{}/stats.json'.format(output_path)
        with open(output_json_file, 'w') as outfile:
            json.dump(stats, outfile)
        logging.warning('ALL - export_users_and_stats - exported stats file: %s' % output_json_file)
        return True


def run_export(modus, filter, output_path='data'):
    pass