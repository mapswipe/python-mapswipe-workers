#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from mapswipe_workers.definitions import logger
from mapswipe_workers import auth

from mapswipe_workers.project_types.build_area.build_area_project \
        import BuildAreaProject

from mapswipe_workers.project_types.footprint.footprint_project import \
        FootprintProject


# TODO: still needed?
class myRequestsSession(requests.Session):
    """
    The class to replace the get function to allow a timeout parameter to be set.
    """

    def __init__(self):
        super(myRequestsSession, self).__init__()

        adapter = requests.adapters.HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
        for scheme in ('http://', 'https://'):
            self.mount(scheme, adapter)

    def get(self, request_ref, headers, timeout=30):
        # print('Using customized get request with a timeout of 30 seconds.')
        return super(myRequestsSession, self).get(request_ref, headers=headers, timeout=timeout)



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


# TODO: Is this function still in use?
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
    fieldnames = ('user_id', 'contributions', 'username')
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

                output_dict = {
                    "user_id": user,
                    "contributions": users[user]['contributions'],
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
            ,username varchar
        );
        '''
    p_con.query(sql_insert, None)

    # insert user data from text file into new table in postgres
    f = open(users_txt_filename, 'r')
    columns = ['user_id', 'contributions', 'username']
    p_con.copy_from(f, 'raw_users', sep=';', columns=columns)
    logging.warning('ALL - update_users - inserted raw users into table raw_users')
    f.close()
    os.remove(users_txt_filename)
    logging.warning('ALL - update_users - deleted file: %s' % users_txt_filename)

    # update users in postgres, update contributions and handle conflicts
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
          DO UPDATE SET contributions = excluded.contributions;
        DROP TABLE IF EXISTS raw_users CASCADE;
        '''  # conflict action https://www.postgresql.org/docs/current/sql-insert.html
    p_con.query(sql_insert, None)
    logging.warning('ALL - update_users - inserted results into users table and updated contributions')

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


#
#
# --- EXPORT ---
#
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


# TODO: is this function still in use?
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
