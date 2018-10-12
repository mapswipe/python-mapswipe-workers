#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import os
import logging


from mapswipe_workers.cfg import auth
from mapswipe_workers.importer import groups_a
from mapswipe_workers.importer import check_geometries
from mapswipe_workers.utils import error_handling
from mapswipe_workers.utils import slack

########################################################################################################################


def get_projects_to_import(firebase):
    # this functions looks for new entries in the firebase importer table
    # the output is a dictionary with all information for newly imported projects

    new_imports = {}
    fb_db = firebase.database()

    # iterate over all the keys in the importer, add the ones to the importer cache that are not yet complete
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


def check_imports(firebase, new_imports):

    corrupt_imports = []

    submission_key = auth.get_submission_key()

    for import_key, project in new_imports.items():
        check_result = check_geometries.check_project_geometry(project)
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
        head = 'google-mapswipe-workers: import_projects.py: project %s (%s) not imported' % (import_key, project_name)
        slack.send_slack_message(head + '\n' + msg)

        # delete project from dict
        del new_imports[import_key]
        print('removed corrupt importer %s from new imports' % import_key)
        print('check result: %s' % check_result)

        # delete corrupt importer in firebase
        fb_db = firebase.database()
        fb_db.child("imports").child(import_key).remove()

    return new_imports

def upload_groups_firebase(firebase, project_id, groups):

    try:
        fb_db = firebase.database()
        fb_db.child("groups").child(project_id).set(groups)
        logging.warning('uploaded groups in firebase for project %s' % project_id)
        return True
    except:
        return False


def delete_groups_firebase(firebase, project_id):
    fb_db = firebase.database()

    fb_db.child("groups").child(project_id).remove()
    logging.warning('deleted groups in firebase for project %s' % project_id)


def upload_project_firebase(firebase, project):

    try:
        fb_db = firebase.database()
        fb_db.child("projects").child(project['id']).set(project)
        logging.warning('uploaded project in firebase for project %s' % project['id'])
        return True
    except:
        return False


def delete_project_firebase(firebase, project_id):
    fb_db = firebase.database()

    fb_db.child("projects").child(project_id).remove()
    logging.warning('deleted project in firebase for project %s' % project_id)


def insert_project_mysql(mysqlDB, project):
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


def delete_project_mysql(mysqlDB, project_id):
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


def set_import_complete(firebase, project):
    try:
        fb_db = firebase.database()
        fb_db.child("imports").child(project['importKey']).child('complete').set(True)
        logging.warning('set importer complete for importer %s and project %s' % (project['importKey'], project['id']))
        return True
    except:
        return False


def set_project_info(new_imports, import_key, project_id):

    project = new_imports[import_key]['project']
    project["id"] = str(project_id)
    logging.warning('start importer for project %s' % project['id'])

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

    # set the type of the project, default type is 1 (built_area)
    try:
        project["type"] = new_imports[import_key]["type"]
    except:
        project["type"] = 1

    return project


def get_highest_project_id(firebase):
    fb_db = firebase.database()

    project_keys = fb_db.child('projects').shallow().get().val()
    if not project_keys:
        project_keys = [0]

    project_ids = list(map(int, list(project_keys)))
    project_ids.sort()
    highest_project_id = project_ids[-1]

    logging.warning('returned highest project id: %s' % highest_project_id)
    return highest_project_id


def run_import(modus):

    if modus == 'development':
        # we use the dev instance for testing
        firebase = auth.dev_firebase_admin_auth()
        mysqlDB = auth.dev_mysqlDB
        print('We are using the development instance')
    elif modus == 'production':
        # we use the dev instance for testing
        firebase = auth.firebase_admin_auth()
        mysqlDB = auth.mysqlDB
        print('We are using the production instance')

    # get new projects in the importer table, that have not been imported
    new_imports = get_projects_to_import(firebase)
    if new_imports:
        print('there are %s new imports.' % len(new_imports))

        # first step check if imports are valid
        new_imports = check_imports(firebase, new_imports)

        if new_imports:
            print('there are %s valid projects to importer' % len(new_imports))
            logging.warning('there are %s valid projects to importer' % len(new_imports))

            # get highest project id
            highest_project_id = get_highest_project_id(firebase)

            # now loop through all valid projects and importer them step by step
            counter = 0

            for import_key in new_imports:
                counter += 1

                logging.warning('start processing for importer key: %s' % import_key)

                # set project id based on highest existing id and counter
                # increase by 2 to avoid that firebase json is parsed as list due to integers as keys
                project_id = highest_project_id + (2 * counter)
                logging.warning('created project id for importer key %s: %s' % (import_key, project_id))

                # set project id, contributors, progress, state and type
                project = set_project_info(new_imports, import_key, project_id)

                # the following needs to consider the type of a project (e.g. 1=built_area, 2=footprint_validation etc.)

                if project['type'] == 1:
                    # save project geom to file
                    filename = save_project_geom_to_file(new_imports[import_key], project["id"])
                    # create groups and tasks from geometry groups_a corresponds to project type=1
                    groups = groups_a.run_create_groups(
                       filename,
                       project["id"],
                       project["tileserver"],
                       project["custom_tileserver_url"],
                       project["zoom"])


                # upload groups in firebase
                if not upload_groups_firebase(firebase, project['id'], groups):
                    err = 'something went wrong during group upload for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: import_projects.py: error occured during group upload'
                    slack.send_slack_message(head + '\n' + msg)
                    continue


                # upload project info in firebase projects table
                if not upload_project_firebase(firebase, project):
                    err = 'something went wrong during project upload for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: import_projects.py: error occured during project upload'
                    slack.send_slack_message(head + '\n' + msg)

                    # delete groups that have already been imported
                    delete_groups_firebase(project['id'])
                    continue

                # save project info in mysql
                if not insert_project_mysql(mysqlDB, project):
                    err = 'something went wrong during project insert in mysql for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: import_projects.py: error occured during project insert in mysql'
                    slack.send_slack_message(head + '\n' + msg)

                    # delete groups and project that have already been imported in firebase
                    delete_groups_firebase(project['id'])
                    delete_project_firebase(project['id'])
                    continue

                # set complete in firebase imports table
                if not set_import_complete(firebase, project):
                    err = 'something went wrong during set complete in firebase for project %s (%s)' % (project['id'], project['name'])
                    logging.warning(err)
                    msg = err
                    head = 'google-mapswipe-workers: import_projects.py: error occured during project set complete'
                    slack.send_slack_message(head + '\n' + msg)

                    # delete groups and project that have already been imported in firebase
                    delete_groups_firebase(project['id'])
                    delete_project_firebase(project['id'])
                    delete_project_mysql(project['id'])
                    continue

                # send email that project was successfully imported
                msg = 'successfully imported project %s (%s). Currently set to "inactive"' % (project['id'], project['name'])
                head = 'google-mapswipe-workers: import_projects.py: PROJECT IMPORTED'
                slack.send_slack_message(head + '\n' + msg)

        else:
            print("There are no projects to importer.")
            logging.warning("There are no projects to importer.")

    else:
        print("There are no projects to importer.")
        logging.warning("There are no projects to importer.")


