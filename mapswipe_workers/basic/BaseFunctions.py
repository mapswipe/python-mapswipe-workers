#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    Documentation Test
"""

import logging
import json
import os
import csv
import requests
from typing import Union

from mapswipe_workers.utils import error_handling
from mapswipe_workers.utils import slack
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import CustomError
from mapswipe_workers.basic import auth
# Make sure to import all project types here
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaImport import BuildAreaImport
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaProject import BuildAreaProject


from mapswipe_workers.ProjectTypes.Footprint.FootprintImport import FootprintImport
from mapswipe_workers.ProjectTypes.Footprint.FootprintProject import FootprintProject



########################################################################################################################
# INIT                                                                                                                 #
########################################################################################################################
class myRequestsSession(requests.Session):
    """
    The class to replace the get function to allow a timeout parameter to be set.
    """

    def __init__(self):
        super(myRequestsSession, self).__init__()

    def get(self, request_ref, headers, timeout=30):
        print('Using customized get request with a timeout of 30 seconds.')
        return super(myRequestsSession, self).get(request_ref, headers=headers, timeout=timeout)


def get_environment(modus='development'):
    """
    The function to get the firebase and postgres configuration

    Parameters
    ----------
    modus : str
        either `development` or `production to decide which firebase configuration to use

    Returns
    -------
    firebase : pyrebase firebase object
            initialized firebase app with admin authentication
    postgres : database connection class
        The database connection to postgres database
    """
    if modus == 'development':
        # we use the dev instance for testing
        firebase = auth.dev_firebase_admin_auth()
        postgres = auth.dev_psqlDB
        logging.warning('ALL - get_environment - use development instance')
    elif modus == 'production':
        # we use the dev instance for testing
        firebase = auth.firebase_admin_auth()
        postgres = auth.psqlDB
        logging.warning('ALL - get_environment - use production instance')
    else:
        firebase = None
        postgres = None

    return firebase, postgres


def init_import(project_type, import_key, import_dict):
    """
    The function to init an import in regard to its type

    Parameters
    ----------
    project_type : int
        the type of the project
    import_key : str
        the key for the import as depicted in firebase
    import_dict : dict
        a dictionary with the attributes for the import

    Returns
    -------
    imp :
        the import instance
    """

    class_to_type = {
        # Make sure to import all project types here
        1: BuildAreaImport,
        2: FootprintImport
    }

    imp = class_to_type[int(project_type)](import_key, import_dict)
    return imp


def init_project(project_type, project_id, firebase, postgres):
    """
    The function to init a project in regard to its type

    Parameters
    ----------
    project_type : int
        the type of the project
    project_id : int
        the id of the project
    firebase : pyrebase firebase object
            initialized firebase app with admin authentication
    postgres : database connection class
        The database connection to postgres database

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

    proj = class_to_type[project_type](project_id, firebase, postgres)
    return proj


def get_projects(firebase, postgres, filter='all'):
    """
    The function to download project information from firebase and init the projects
    Parameters
    ----------
    firebase : pyrebase firebase object
            initialized firebase app with admin authentication
    postgres : database connection class
        The database connection to postgres database
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
    fb_db.requests.get = myRequestsSession().get
    all_projects = fb_db.child("projects").get().val()
    
    # return empty list if there are no projects in firebase
    if all_projects == None:
        logging.warning('All - get_projects - no projects in firebase')
        projects_list = []
        return projects_list

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
            proj = init_project(project_type, project_id, firebase, postgres)
            projects_list.append(proj)

    return projects_list

def project_exists(project_id, firebase, postgres):
    """
    The function to check if all project information exists in firebase and postgres database.

    Parameters
    ----------
    project_id : int
        the id of the project
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication
    postgres : database connection class
        The database connection to postgres database

    Returns
    -------
    bool
        True if project exists, False it not
    """
    in_firebase = project_exists_firebase(project_id, firebase)
    in_postgres = project_exists_postgres(project_id, postgres)

    if in_firebase is True and in_postgres is True:
        return True
    else:
        return False


def project_exists_firebase(project_id, firebase):
    """
    The function to check whether a project exists in firebase.

    Parameters
    ----------
    project_id : int
        the id of the project
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    bool
        True if project info and group info exist in firebase, false otherwise
    """

    fb_db = firebase.database()
    fb_db.requests.get = myRequestsSession().get
    project_data = fb_db.child("projects").child(project_id).get().val()

    if not project_data:
        logging.warning('%s - project_exists_firebase - project info NOT in firebase' % project_id)
    else:
        logging.warning('%s - project_exists_firebase - project info in firebase' % project_id)

    groups_data = fb_db.child("groups").child(project_id).shallow().get().val()
    if not groups_data:
        logging.warning('%s - project_exists_firebase - groups info NOT in firebase' % project_id)
    else:
        logging.warning('%s - project_exists_firebase - groups info in firebase' % project_id)

    if project_data and groups_data:
        return True
    else:
        return False


def project_exists_postgres(project_id, postgres):
    """
    The function to check whether a project exists in postgres.

    Parameters
    ----------
    project_id : int
        the id of the project
    postgres : database connection class
        The database connection to postgres database

    Returns
    -------
    bool
        True is project info, group info and task info exist in postgres database. False otherwise.
    """

    p_con = postgres()
    data = [project_id]

    sql_query = 'SELECT * FROM projects WHERE project_id = %s'
    project_data = p_con.retr_query(sql_query, data)
    if not project_data:
        logging.warning('%s - project_exists_postgres - project info NOT in postgres' % project_id)
    else:
        logging.warning('%s - project_exists_postgres - project info in postgres' % project_id)

    sql_query = 'SELECT * FROM groups WHERE project_id = %s LIMIT 1'
    groups_data = p_con.retr_query(sql_query, data)
    if not groups_data:
        logging.warning('%s - project_exists_postgres - groups info NOT in postgres' % project_id)
    else:
        logging.warning('%s - project_exists_postgres - groups info in postgres' % project_id)

    sql_query = 'SELECT * FROM tasks WHERE project_id = %s LIMIT 1'
    tasks_data = p_con.retr_query(sql_query, data)
    if not tasks_data:
        logging.warning('%s - project_exists_postgres - tasks info NOT in postgres' % project_id)
    else:
        logging.warning('%s - project_exists_postgres - tasks info in postgres' % project_id)

    del p_con

    if project_data and groups_data and tasks_data:
        return True
    else:
        return False


########################################################################################################################
# IMPORT                                                                                                               #
########################################################################################################################



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
    fb_db.requests.get = myRequestsSession().get
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
        list of tuple with import_key, project_id and project_type of imported projects
    """

    # get dev or production environment for firebase and postgres
    firebase, postgres = get_environment(modus)

    # this will return a list of imports
    imported_projects = []

    # check for new imports in firebase
    imports = get_new_imports(firebase)

    for import_key, import_dict in imports.items():
        # let's have a look at the project type
        try:
            project_type = import_dict['projectType']
        except:
            project_type = 1

        # now let's init the import
        try:
            imp = init_import(project_type, import_key, import_dict)
            # and now let's finally create a project
            project_id, project_type = imp.create_project(firebase, postgres)
            imported_projects.append((imp.import_key, project_id, project_type))
            try:
                msg = "### IMPORT SUCCESSFUL ### \nproject-name: %s \nimport-key: %s \nproject-id: %s \nproject-type: %s \nMake sure to activate the project in firebase. \nHappy Swiping. :)" % (imp.name, import_key, project_id, project_type)

                slack.send_slack_message(msg)
            except:
                logging.exception('could not send slack message.')

        except CustomError as error:
            error_handling.send_error(error, import_key)
            logging.exception('%s - get_new_imports - import failed' % import_key)
            continue

    return imported_projects


########################################################################################################################
# UPDATE                                                                                                               #
########################################################################################################################
def run_update(modus, filter):
    """
    The function to update project progress and contributors in firebase

    Parameters
    ----------
    modus : str
        The environment to use for firebase and postgres
        Can be either 'development' or 'production'
    filter : str or list
        The filter for the projects.
        Can be either 'all', 'active', 'not_finished' or a list of project ids as integer

    Returns
    -------
    updated_projects : list
        The list of all projects ids for projects which have been updated
    """

    # get dev or production environment for firebase and postgres
    firebase, postgres = get_environment(modus)

    project_list = get_projects(firebase, postgres, filter)
    updated_projects = []
    for proj in project_list:
        proj.update_project(firebase, postgres)
        updated_projects.append(proj.id)

    # update users
    update_users_postgres(firebase, postgres)

    return updated_projects


def update_users_postgres(firebase, postgres, users_txt_filename='raw_users.txt')-> bool:
    """
    The fucntion to replace the users table in postgres with the current information from firebase

    Parameters
    ----------
    firebase :  pyrebase firebase object
        initialized firebase app with admin authentication
    postgres : database connection class
        the database connection to postgres database
    users_txt_filename : string
        the path for the textfile which temporally stores the raw information

    Returns
    -------
    bool
        True if successful, False otherwise
    """

    # open new txt file and write header
    users_txt_file = open(users_txt_filename, 'w', newline='')
    fieldnames = ('user_id', 'contributions', 'distance', 'username')
    w = csv.DictWriter(users_txt_file, fieldnames=fieldnames, delimiter=';', quotechar="'")

    #query users from fdb
    users = firebase.database().child("users").get().val()

    # check that there are users in firebase
    if not users:
        logging.warning('ALL - update_users - there are no users in firebase')
    else:
        for user in users:
            try:
                #check for missing info, add dummy values
                if not 'username' in users[user]:
                    users[user]['username'] = 'unknown'
                if not 'contributions' in users[user]:
                    users[user]['contributions'] = 0
                if not 'distance' in users[user]:
                    users[user]['distance'] = 0

                output_dict = {
                    "user_id": user,
                    "contributions": users[user]['contributions'],
                    "distance": users[user]['distance'],
                    "username": users[user]['username']
                }

                w.writerow(output_dict)

            except Exception as e:
                logging.warning('ALL - update_users - users missed critical information: %s' % e)

    users_txt_file.close()

    # create new table in postgres for raw_users
    p_con = postgres()
    sql_insert = '''
        DROP TABLE IF EXISTS raw_users CASCADE;
        CREATE TABLE raw_users (
            user_id varchar
            ,contributions int
            ,distance double precision
            ,username varchar
        );
        '''
    p_con.query(sql_insert, None)

    # insert user data from text file into new table in postgres
    f = open(users_txt_filename, 'r')
    columns = ['user_id', 'contributions', 'distance', 'username']
    p_con.copy_from(f, 'raw_users', sep=';', columns=columns)
    logging.warning('ALL - update_users - inserted raw users into table raw_users')
    f.close()
    os.remove(users_txt_filename)
    logging.warning('ALL - update_users - deleted file: %s' % users_txt_filename)

    # update users in postgres, update contributions and distance and handle conflicts
    sql_insert = '''
        INSERT INTO
          users
        SELECT
          *
          -- duplicates is set to zero by default, this will be updated on conflict only
          --0
        FROM
          raw_users a

        ON CONFLICT ON CONSTRAINT "users_pkey"
          DO UPDATE SET contributions = excluded.contributions
          ,distance = excluded.distance;
        DROP TABLE IF EXISTS raw_users CASCADE;
        '''  # conflict action https://www.postgresql.org/docs/current/sql-insert.html
    p_con.query(sql_insert, None)
    logging.warning('ALL - update_users - inserted results into users table and updated contributions and/or distance')

    del p_con
    return True


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
    fb_db.requests.get = myRequestsSession().get
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
    fb_db.requests.get = myRequestsSession().get
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

                # the info column should have json format for uploading to postgres
                output_dict['info'] = json.dumps(output_dict['info'])

                w.writerow(output_dict)

            except Exception as e:
                logging.warning('ALL - results_to_txt - result missed critical information: %s' % e)

    results_txt_file.close()
    logging.warning('ALL - results_to_txt - there are %s results to import' % number_of_results)
    logging.warning('ALL - results_to_txt - created file: %s' % results_txt_filename)
    return results_txt_filename


def save_results_postgres(postgres, results_filename):
    """
    The function to save results in the postgres database

    Parameters
    ----------
    postgres : database connection class
            The database connection to postgres database
    results_filename : str
        The name of the file with the results

    Returns
    -------
    bool
        True if successful, False otherwise
    """

    ### this function saves the results from firebase to the postgres database

    # pre step delete table if exist
    p_con = postgres()

    # first importer to a table where we store the geom as text
    sql_insert = '''
        DROP TABLE IF EXISTS raw_results CASCADE;
        CREATE TABLE raw_results (
            task_id varchar,
            project_id int,
            user_id varchar,
            timestamp bigint,
            info json
        );
        '''

    p_con.query(sql_insert, None)

    # copy data to the new table
    # old: postgres we should use LOAD DATA LOCAL INFILE Syntax

    f = open(results_filename, 'r')
    columns = ['task_id', 'project_id', 'user_id', 'timestamp', 'info']
    p_con.copy_from(f, 'raw_results', sep='\t', columns=columns)
    logging.warning('ALL - save_results_postgres - inserted raw results into table raw_results')
    f.close()

    os.remove(results_filename)
    logging.warning('ALL - save_results_postgres - deleted file: %s' % results_filename)

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
          DO UPDATE SET duplicates = results.duplicates + 1;
        DROP TABLE IF EXISTS raw_results CASCADE;
    '''

    p_con.query(sql_insert, None)
    logging.warning('ALL - save_results_postgres - inserted results into results table and updated duplicates count')

    del p_con
    return True


def run_transfer_results(modus):
    """
    The function to download results from firebase, upload them to postgres and then delete the transfered results in firebase.

    Parameters
    ----------
    modus : str
        The environment to use for firebase and postgres
        Can be either 'development' or 'production'

    Returns
    -------
    bool
        True if successful, False otherwise

    """

    results_filename = '{}/tmp/results.json'.format(DATA_PATH)
    if not os.path.isdir(DATA_PATH+'/tmp'):
        os.mkdir(DATA_PATH+'/tmp')

    # get dev or production environment for firebase and postgres
    firebase, postgres = get_environment(modus)

    # first check if we have results stored locally, that have not been inserted in postgres
    if os.path.isfile(results_filename):
        # start to import the old results first
        with open(results_filename) as results_file:
            results = json.load(results_file)
            results_txt_filename = results_to_txt(results)
            logging.warning("ALL - run_transfer_results - there are results in %s that we didnt't insert. do it now!" % results_filename)
            save_results_postgres(postgres, results_txt_filename)
            delete_firebase_results(firebase, results)

        os.remove(results_filename)
        logging.warning('ALL - run_transfer_results - removed "results.json" file')

    fb_db = firebase.database()
    fb_db.requests.get = myRequestsSession().get

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
        save_results_postgres(postgres, results_txt_filename)
        delete_firebase_results(firebase, all_results)
        os.remove(results_filename)
        logging.warning('ALL - run_transfer_results - removed %s' % results_filename)
    else:
        logging.warning('ALL - run_transfer_results - there are no results to transfer in firebase')

    return True


########################################################################################################################
# EXPORT                                                                                                               #
########################################################################################################################
def export_all_projects(firebase):
    """
    The function to export all projects in a json file

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # check if output path for projects is correct and existing
    if not os.path.isdir(DATA_PATH):
        os.mkdir(DATA_PATH)

    fb_db = firebase.database()
    fb_db.requests.get = myRequestsSession().get
    all_projects = fb_db.child("projects").get().val()

    if not all_projects:
        logging.warning("ALL - export_all_projects - no projects in firebase. Can't export")
        return False
    else:
        # save projects as json
        output_json_file = '{}/projects.json'.format(DATA_PATH)

        # don't export api key
        for project_id in all_projects.keys():
            try:
                del all_projects[project_id]['info']['apiKey']
            except:
                pass

        with open(output_json_file, 'w') as outfile:
            json.dump(all_projects, outfile, indent=4)
        logging.warning('ALL - export_all_projects - exported projects file: %s' % output_json_file)
        return True


def export_users_and_stats(firebase):
    """
    The function to save users and stats as a json file

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # check if output path for projects is correct and existing
    if not os.path.isdir(DATA_PATH):
        os.mkdir(DATA_PATH)

    fb_db = firebase.database()
    fb_db.requests.get = myRequestsSession().get
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
        output_json_file = '{}/users.json'.format(DATA_PATH)
        with open(output_json_file, 'w') as outfile:
            json.dump(all_users, outfile, indent=4)
        logging.warning('ALL - export_users_and_stats - exported users file: %s' % output_json_file)

        # export stats as json file
        output_json_file = '{}/stats.json'.format(DATA_PATH)
        with open(output_json_file, 'w') as outfile:
            json.dump(stats, outfile, indent=4)
        logging.warning('ALL - export_users_and_stats - exported stats file: %s' % output_json_file)
        return True


def run_export(modus: str, filter: Union[str, list])-> list:
    """
    The function to export general statistics along with progress and results per
    projects as well as all users in json format for to use in the mapswipe api.

    Examples
    ----------
    Output structure:
        progress_<project_id>.json
            {
                "timestamps": [
                    int,
                    int,
                    ..
                ],
                "progress": [
                    int,
                    int,
                    ..
                ],
                "contributors": [
                    int,
                    int
                ]
            }
        stats.json
            {
                "users": int,
                "totalDistanceMappedInSqKm": float,
                "totalContributionsByUsers": int
            }
        results_<project_id>.json
             {
                "task_id": {
                    "project_id": int,
                    "decision": float,
                    "yes_count": int,
                    "maybe_count": int,
                    "bad_imagery_count": int,
            }
        users.json
            {
                "user_id": {
                    "contribution": int,
                    "distance": int,
                    "username": str
                }
            }

    Parameters
    ----------
    modus : str
        The environment to use for firebase and postgres
        Can be either 'development' or 'production'
    filter : str or list
        The filter for the projects.
        Can be either 'all', 'active', 'not_finished' or a list of project ids as integer

    Returns
    -------
    exported_projects : list
        The list of all projects ids for projects which have been updated
    """

    firebase, postgres = get_environment(modus)

    project_list = get_projects(firebase, postgres, filter)
    logging.warning('ALL - run_export - got %s projects to export. Filter is set for %s projects' % (len(project_list),
                                                                                                     filter))
    exported_projects = []
    for project in project_list:
        project.export_progress()
        logging.warning('%s - run_export - progress successfully exported' % project.id)
        project.export_results(postgres)
        logging.warning('%s - run_export - results successfully exported' % project.id)
        exported_projects.append(project.id)


    export_all_projects(firebase)
    export_users_and_stats(firebase)

    return exported_projects


########################################################################################################################
# DELETE PROJECTS                                                                                                      #
########################################################################################################################

def delete_project_firebase(project_id, import_key, firebase):
    """
    The function to delete the project and groups in firebase

    Parameters
    ----------
    project_id : int
        the id of the project
    import_key : str
        the key for the import as depicted in firebase
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    bool
        True if successful. False otherwise
    """

    fb_db = firebase.database()
    fb_db.requests.get = myRequestsSession().get
    # we create this element to do a multi location update
    data = {
        "projects/{}/".format(project_id): None,
        "groups/{}/".format(project_id): None,
        "imports/{}/".format(import_key): None
    }

    fb_db.update(data)
    logging.warning('%s - delete_project_firebase - deleted project and groups and import in firebase' % project_id)

    return True


def delete_project_postgres(project_id, import_key, postgres):
    """
    The function to delete results, tasks, groups, import of project in postgres.

    Parameters
    ----------
    project_id : int
        the id of the project
    import_key : str
        the key for the import as depicted in firebase
    postgres : database connection class
        The database connection to postgres database

    Returns
    -------
    bool
        True is successful. False otherwise.

    TODO:
    -----
    Handle exception:
        pypostgres.err.InternalError: (1205, 'Lock wait timeout exceeded; try restarting transaction')
    """

    p_con = postgres()
    sql_insert = """
        BEGIN TRANSACTION;
        DELETE FROM projects WHERE project_id = %s;
        DELETE FROM results WHERE project_id = %s;
        DELETE FROM tasks WHERE project_id = %s;
        DELETE FROM groups WHERE project_id = %s;
        DELETE FROM imports WHERE import_id = %s
        END TRANSACTION;
    """
    data = [int(project_id), int(project_id), int(project_id), int(project_id), str(import_key)]
    p_con.query(sql_insert, data)
    del p_con

    logging.warning('%s - delete_results_postgres - deleted all results, tasks, groups and import and project in postgres' % project_id)
    return True

def delete_local_files(project_id, import_key):
    """
    The function to delete all local files of this project at the server.

    Parameters
    ----------
    project_id : int
        the id of the project
    import_key : str
        the key for the import as depicted in firebase

    Returns
    -------
    deleted_files : list
        a list with the names of the deleted files
    """


    deleted_files = []

    file_list = [
        '{}/results/results_{}.json'.format(DATA_PATH, project_id),
        '{}/input_geometries/raw_input_{}.geojson'.format(DATA_PATH, import_key),
        '{}/input_geometries/raw_input_{}.kml'.format(DATA_PATH, import_key),
        '{}/input_geometries/valid_input_{}.geojson'.format(DATA_PATH, import_key),
        '{}/input_geometries/valid_input_{}.kml'.format(DATA_PATH, import_key),
        '{}/progress/progress_{}.json'.format(DATA_PATH, project_id),
    ]

    for filepath in file_list:
        if os.path.isfile(filepath):
            os.remove(filepath)
            deleted_files.append(filepath)

    logging.warning('%s - delete_project_firebase - deleted local files: %s' % (project_id, deleted_files))
    return deleted_files


def run_delete(modus, list):
    """
    The function to delete a list of projects and all corresponding information (results, tasks, groups) in firebase and postgres

    Parameters
    ----------
    modus : str
        The environment to use for firebase and postgres
        Can be either 'development' or 'production'
    list : list
        The ids of the projects to delete

    Returns
    -------
    deleted_projects : list
        The list of all projects ids for projects which have been deleted
    """

    # get dev or production environment for firebase and postgres
    firebase, postgres = get_environment(modus)
    deleted_projects = []

    if not list:
        logging.warning('ALL - run_delete - no input list provided.')
    else:
        project_list = get_projects(firebase, postgres, list)
        for proj in project_list:
            proj.delete_project(firebase, postgres)
            deleted_projects.append(proj.id)

    return deleted_projects


########################################################################################################################
# ARCHIVE PROJECTS                                                                                                      #
########################################################################################################################
def run_archive(modus, list):
    """
    The function to archive a list of projects and its corresponding information (groups) to reduce storage in firebase

    Parameters
    ----------
    modus : str
        The environment to use for firebase and postgres
        Can be either 'development' or 'production'
    list : list
        The ids of the projects to archive

    Returns
    -------
    archived_projects : list
        The list of all projects ids for projects which have been archived
    """

    # get dev or production environment for firebase and postgres
    firebase, postgres = get_environment(modus)

    if not list:
        logging.warning('ALL - run_archive - no input list provided.')
        return False
    else:
        project_list = get_projects(firebase, postgres, list)
        archived_projects = []
        for proj in project_list:
            logging.warning('ALL - run_archive - currently not implemented.')
            pass
            # TODO implement archive function on project level
            # proj.archive_project(firebase, postgres)
            # archived_projects.append(proj.id)

        return archived_projects

if __name__ == '__main__':
    pass
