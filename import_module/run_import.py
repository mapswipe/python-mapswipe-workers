#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import sys
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')
sys.path.insert(0, '../utils/')

import logging
import os
import time
import ogr

from auth import get_submission_key
from create_groups import run_create_groups

import error_handling

from send_slack_message import send_slack_message

import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-l', '--loop', dest='loop', action='store_true',
                    help='if loop is set, the import will be repeated several times. You can specify the behaviour using --sleep_time and/or --max_iterations.')
parser.add_argument('-s', '--sleep_time', required=False, default=None, type=int,
                    help='the time in seconds for which the script will pause in beetween two imports')
parser.add_argument('-m', '--max_iterations', required=False, default=None, type=int,
                    help='the maximum number of imports that should be performed')
parser.add_argument('-mo', '--modus', nargs='?', default='development',
                    choices=['development', 'production'])

########################################################################################################################

def get_projects_to_import():
    # this functions looks for new entries in the firebase import table
    # the output is a dictionary with all information for newly imported projects

    new_imports = {}

    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # iterate over all the keys in the importer, add the ones to the import cache that are not yet complete
    all_imports = fb_db.child("imports").get().val()

    if all_imports:
        for import_key, project in all_imports.items():
            try:
                # check if project was already imported and "complete" is set
                complete = project['complete']
            except:
                # insert into new projects dict
                new_imports[import_key] = project

    return new_imports


def save_project_geom_to_file(new_import, project_id):
    # check input type

    # check if a 'data' folder exists and craete one if not
    if not os.path.isdir('data'):
        os.mkdir('data')

    if 'kml' in new_import.keys():
        logging.warning('kml geometry provided')
        geometry = new_import['kml']
        geometry_type = 'KML'
        filename = 'data/project_{}.kml'.format(project_id)
        '''
    elif 'geojson' in new_import.keys():
        logging.warning('geojson geometry provided')
        geometry = new_import['geojson']
        geometry_type = 'GeoJSON'
        filename = 'data/project_{}.geojson'.format(project_id)
        '''
    # if geometry is not kml nor geojson we can't import the project
    else:
        print('no kml or geojson geometry provided in imported project')
        return False

    # write string to geom file
    with open(filename, 'w') as geom_file:
        geom_file.write(geometry)

    return filename

def check_project_geometry(project):
    # this function checks whether the project geometry is valid

    if 'kml' in project.keys():
        geometry = project['kml']
        geometry_type = 'KML'
        filename = 'input.kml'
        '''
    elif 'geojson' in project.keys():
        geometry = project['geojson']
        geometry_type = 'GeoJSON'
        filename = 'input.geojson'
        '''
    # if geometry is not kml nor geojson we can't import the project
    else:
        print('no kml or geojson geometry provided in imported project')
        return False

    # try to save the geometry to a file and open it with ogr
    try:
        # write kml string to kml file
        with open(filename, 'w') as geom_file:
            geom_file.write(geometry)

        driver = ogr.GetDriverByName(geometry_type)
        datasource = driver.Open(filename, 0)
        layer = datasource.GetLayer()
    except:
        err = ('%s geometry could not be opened with ogr.' % geometry_type)
        print(err)
        return err

    # check if layer is empty
    if layer.GetFeatureCount() < 1:
        err = 'empty file. No geometries provided'
        print(err)
        return err

    # check if more than 1 geometry is provided
    if layer.GetFeatureCount() > 1:
        err = 'Input file contains more than one geometry. Make sure to provide exact one input geometry.'
        print(err)
        return err

    # check if the input geometry is a valid polygon
    for feature in layer:
        feat_geom = feature.GetGeometryRef()
        geom_name = feat_geom.GetGeometryName()

        if not feat_geom.IsValid():
            err = 'geometry is not valid: %s. Tested with IsValid() ogr method. probably self-intersections.' % geom_name
            return err

        # we accept only POLYGON or MULTIPOLYGON geometries
        if geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
            err = 'invalid geometry type: %s. please provide "POLYGON" or "MULTIPOLYGON"' % geom_name
            print(err)
            return err

    del datasource
    del layer
    os.remove(filename)
    print('geometry is correct')
    return 'correct'

def check_imports(new_imports):

    corrupt_imports = []

    submission_key = get_submission_key()

    for import_key, project in new_imports.items():
        check_result = check_project_geometry(project)
        if check_result != 'correct':
            corrupt_imports.append([import_key, project['project']['name'], check_result])
            print('some error in geometry')
        elif project['key'] != submission_key:
            check_result = 'no/wrong submission key provided'
            corrupt_imports.append([import_key, project['project']['name'], check_result])
            print('no submission key provided')


    for import_key, project_name, check_result in corrupt_imports:
        # send slack message that project was corrupt, maybe project manager could try to reimport
        msg = '%s \n %s \n %s \n %s' % (import_key, project_name, check_result, str(new_imports[import_key]))
        head = 'google-mapswipe-workers: run_import.py: project %s (%s) not imported' % (import_key, project_name)
        send_slack_message(head + '\n' + msg)

        # delete project from dict
        del new_imports[import_key]
        print('removed corrupt import %s from new imports' % import_key)
        print('check result: %s' % check_result)

        # delete corrupt import in firebase
        firebase = firebase_admin_auth()
        fb_db = firebase.database()
        fb_db.child("imports").child(import_key).remove()

    return new_imports

def upload_groups_firebase(project_id, groups):

    try:
        firebase = firebase_admin_auth()
        fb_db = firebase.database()
        fb_db.child("groups").child(project_id).set(groups)
        logging.warning('uploaded groups in firebase for project %s' % project_id)
        return True
    except:
        return False


def delete_groups_firebase(project_id):
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    fb_db.child("groups").child(project_id).remove()
    logging.warning('deleted groups in firebase for project %s' % project_id)


def upload_project_firebase(project):

    try:
        firebase = firebase_admin_auth()
        fb_db = firebase.database()
        fb_db.child("projects").child(project['id']).set(project)
        logging.warning('uploaded project in firebase for project %s' % project['id'])
        return True
    except:
        return False


def delete_project_firebase(project_id):
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    fb_db.child("projects").child(project_id).remove()
    logging.warning('deleted project in firebase for project %s' % project_id)


def insert_project_mysql(project):
    try:
        m_con = mysqlDB()
        sql_insert = "INSERT INTO projects Values(%s,%s,%s)"
        data = [int(project['id']), project['lookFor'], project['name']]
        # insert in table
        m_con.query(sql_insert, data)
        del m_con

        logging.warning('inserted project info in mysql for project %s' % project['id'])
        return True
    except:
        logging.warning('failed to insert project info in mysql for project %s' % project['id'])
        return False


def delete_project_mysql(project_id):
    try:
        m_con = mysqlDB()
        sql_insert = "DELETE FROM projects WHERE project_id = %s"
        data = [int(project_id)]
        # insert in table
        m_con.query(sql_insert, data)
        del m_con

        logging.warning('deleted project info in mysql for project %s' % project_id)
        return True
    except:
        logging.warning('failed to delete project info in mysql for project %s' % project_id)
        return False


def set_import_complete(project):
    try:
        firebase = firebase_admin_auth()
        fb_db = firebase.database()
        fb_db.child("imports").child(project['importKey']).child('complete').set(True)
        logging.warning('set import complete for import %s and project %s' % (project['importKey'], project['id']))
        return True
    except:
        return False


def set_project_info(new_imports, import_key, project_id):

    project = new_imports[import_key]['project']
    project["id"] = str(project_id)
    logging.warning('start import for project %s' % project['id'])

    project["contributors"] = 0
    project["progress"] = 0
    # we set the groupAverage to 0, however it should be calculated from the tasks per group
    project["groupAverage"] = 0.0
    # state = 3 --> inactive, state = 0 --> active
    project["state"] = 3
    project["importKey"] = import_key
    try:
        project["tileserver"] = new_imports[import_key]["tileServer"]
    except:
        project["tileserver"] = 'bing'
    try:
        project["custom_tileserver_url"] = new_imports[import_key]["CustomTileServerUrl"]
    except:
        project["custom_tileserver_url"] = None
    try:
        project["zoom"] = new_imports[import_key]["ZoomLevel"]
    except:
        project["zoom"] = 18

    return project

def get_highest_project_id():
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    project_keys = fb_db.child('projects').shallow().get().val()
    if not project_keys:
        project_keys = [0]

    project_ids = list(map(int, list(project_keys)))
    project_ids.sort()
    highest_project_id = project_ids[-1]

    logging.warning('returned highest project id: %s' % highest_project_id)
    return highest_project_id



########################################################################################################################
def run_import():

    logging.basicConfig(filename='run_import.log',
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # get new projects in the import table, that have not been imported
    new_imports = get_projects_to_import()
    if new_imports:
        print('there are %s new imports.' % len(new_imports))

        # first step check if imports are valid
        new_imports = check_imports(new_imports)

        if new_imports:
            print('there are %s valid projects to import' % len(new_imports))
            logging.warning('there are %s valid projects to import' % len(new_imports))

            # get highest project id
            highest_project_id = get_highest_project_id()

            # now loop through all valid projects and import them step by step
            counter = 0

            for import_key in new_imports:
                counter += 1

                logging.warning('start processing for import key: %s' % import_key)

                # set project id based on highest existing id and counter
                project_id = highest_project_id + counter

                logging.warning('created project id for import key %s: %s' % (import_key, project_id))


                # set project id, contributors, progress, state
                project = set_project_info(new_imports, import_key, project_id)

                # save project geom to file
                filename = save_project_geom_to_file(new_imports[import_key], project["id"])

                # create tiles from geometry
                # create groups from tiles
                groups = run_create_groups(filename, project["id"],
                                           project["tileserver"], project["custom_tileserver_url"],
                                           project["zoom"])

                # upload groups in firebase

                if not upload_groups_firebase(project['id'], groups):
                    err = 'something went wrong during group upload for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: run_import.py: error occured during group upload'
                    send_slack_message(head + '\n' + msg)
                    continue


                # upload project info in firebase projects table
                if not upload_project_firebase(project):
                    err = 'something went wrong during project upload for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: run_import.py: error occured during project upload'
                    send_slack_message(head + '\n' + msg)

                    # delete groups that have already been imported
                    delete_groups_firebase(project['id'])
                    continue

                # save project info in mysql
                if not insert_project_mysql(project):
                    err = 'something went wrong during project insert in mysql for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: run_import.py: error occured during project insert in mysql'
                    send_slack_message(head + '\n' + msg)

                    # delete groups and project that have already been imported in firebase
                    delete_groups_firebase(project['id'])
                    delete_project_firebase(project['id'])
                    continue

                # set complete in firebase imports table
                if not set_import_complete(project):
                    err = 'something went wrong during set complete in firebase for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: run_import.py: error occured during project set complete'
                    send_slack_message(head + '\n' + msg)

                    # delete groups and project that have already been imported in firebase
                    delete_groups_firebase(project['id'])
                    delete_project_firebase(project['id'])
                    delete_project_mysql(project['id'])
                    continue

                # send email that project was successfully imported
                msg = 'successfully imported project %s (%s). Currently set to "inactive"' % (project['id'], project['name'])
                head = 'google-mapswipe-workers: run_import.py: PROJECT IMPORTED'
                send_slack_message(head + '\n' + msg)

        else:
            print("There are no projects to import.")
            logging.warning("There are no projects to import.")

    else:
        print("There are no projects to import.")
        logging.warning("There are no projects to import.")


########################################################################################################################
if __name__ == '__main__':

    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    if args.modus == 'development':
        # we use the dev instance for testing
        from auth import dev_firebase_admin_auth as firebase_admin_auth
        from auth import dev_mysqlDB as mysqlDB
        print('We are using the development instance')
    elif args.modus == 'production':
        # we use the dev instance for testing
        from auth import firebase_admin_auth as firebase_admin_auth
        from auth import mysqlDB as mysqlDB
        print('We are using the production instance')

    # check whether arguments are correct
    if args.loop and (args.max_iterations is None):
        parser.error('if you want to loop the script please provide number of maximum iterations.')
    elif args.loop and (args.sleep_time is None):
        parser.error('if you want to loop the script please provide a sleep interval.')

    # create a variable that counts the number of imports
    counter = 1
    x = 1

    while x > 0:

        print(' ')
        print('###### ###### ###### ######')
        print('###### iteration: %s ######' % counter)
        print('###### ###### ###### ######')

        # this runs the script and sends an email if an error happens within the execution
        try:
            run_import()
        except Exception as error:
            error_handling.send_error(error, 'run_import.py')

        # check if the script should be looped
        if args.loop:
            if args.max_iterations > counter:
                counter = counter + 1
                print('import finished. will pause for %s seconds' % args.sleep_time)
                x = 1
                time.sleep(args.sleep_time)
            else:
                x = 0
                # print('import finished and max iterations reached. stop here.')
                print('import finished and max iterations reached. sleeping now.')
                time.sleep(args.sleep_time)
        # the script should run only once
        else:
            print("Don't loop. Stop after the first run.")
            x = 0
