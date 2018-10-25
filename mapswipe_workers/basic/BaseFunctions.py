import logging
import json
import os
import csv
import requests


from mapswipe_workers.cfg import auth
# Make sure to import all project types here
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaProject import BuildAreaProject
from mapswipe_workers.ProjectTypes.Footprint.FootprintProject import FootprintProject


########################################################################################################################
# INIT                                                                                                                 #
########################################################################################################################
def get_environment(modus):

    if modus == 'development':
        # we use the dev instance for testing
        firebase = auth.dev_firebase_admin_auth()
        mysqlDB = auth.dev_mysqlDB
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
        1: BuildAreaProject(project_id, firebase, mysqlDB, import_key, import_dict),
        # 2: FootprintProject(project_id, firebase, import_key, import_dict)
    }

    proj = class_to_type[project_type]
    return proj


def get_projects(firebase, mysqlDB, filter='all'):

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
    fb_db = firebase.database()
    results = fb_db.child("results").get().val()
    return results


def delete_firebase_results(firebase, all_results):
    fb_db = firebase.database()
    # we will use multilocation update to delete the entries
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
    results_txt_filename = 'raw_results.txt'

    # If csv file is a file object, it should be opened with newline=''
    results_txt_file = open(results_txt_filename, 'w', newline='')
    csvwriter = csv.writer(results_txt_file, delimiter='\t')

    number_of_results = 0
    for task_id, results in all_results.items():
        for child_id, result in results.items():
            number_of_results += 1

            try:
                output_list = [
                    task_id,
                    result['data']['user'],
                    int(result['data']['projectId']),
                    int(result['data']['timestamp']),
                    int(result['data']['result']),
                    result['data']['wkt'],
                    task_id.split('-')[1],
                    task_id.split('-')[2],
                    task_id.split('-')[0],
                    0
                ]
                csvwriter.writerow(output_list)
            except Exception as e:
                logging.warning('ALL - results_to_txt - result missed critical information: %s' % e)



    results_txt_file.close()
    logging.warning('ALL - results_to_txt - there are %s results to import' % number_of_results)
    return results_txt_filename


def save_results_mysql(mysqlDB, results_filename):
    ### this function saves the results from firebase to the mysql database

    # pre step delete table if exist
    m_con = mysqlDB()
    sql_insert = 'DROP TABLE IF EXISTS raw_results CASCADE;'
    m_con.query(sql_insert, None)

    # first importer to a table where we store the geom as text
    sql_insert = '''
        CREATE TABLE raw_results (
            task_id varchar(45)
            ,user_id varchar(45)
            ,project_id int(5)
            ,timestamp bigint(32)
            ,result int(1)
            ,wkt varchar(256)
            ,task_x varchar(45)
            ,task_y varchar(45)
            ,task_z varchar(45)
            ,duplicates int(5)
        );
        '''

    m_con.query(sql_insert, None)

    # copy data to the new table
    # we should use LOAD DATA LOCAL INFILE Syntax
    sql_insert = '''
            LOAD DATA LOCAL INFILE 'raw_results.txt' INTO TABLE raw_results
            '''
    m_con.query(sql_insert, None)
    os.remove(results_filename)

    # second importer all entries into the task table and convert into psql geometry
    sql_insert = '''
        INSERT INTO
          results
        SELECT
          *
        FROM
          raw_results
        ON DUPLICATE KEY
          UPDATE results.duplicates = results.duplicates + 1
    '''

    m_con.query(sql_insert, None)
    logging.warning('ALL - save_results_mysql - inserted raw results into results table and updated duplicates count')

    del m_con
    return


def run_transfer_results(modus, results_filename='data/results.json'):

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

########################################################################################################################
# EXPORT                                                                                                               #
########################################################################################################################
def run_export():
    pass