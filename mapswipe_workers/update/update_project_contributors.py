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

from cfg.auth import firebase_admin_auth
from cfg.auth import mysqlDB


import argparse
# define arguments that can be passed by the user
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-p', '--projects', nargs='+', required=True, default=None, type=int,
                    help='project id of the project to process. You can add multiple project ids.')
parser.add_argument('-o', '--output_path', required=None, default='/var/www/html', type=str,
                    help='output path. please provide a location where the exported files should be stored.')


def project_exists(project_id):
    # check if a project corresponding to the provided id exists in firebase and has all information required
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # get the headers from firebase
    project_data = fb_db.child("projects").child(project_id).shallow().get().val()

    if project_data is None:
        print('project is not in firebase projects table: %s' % project_id)
        logging.warning('project is not in firebase projects table: %s' % project_id)
        return False
    # projects neeed to have at least 12 attributes in firebase, otherwise something went wrong during the importer
    elif len(project_data) < 12:
        print('project missed critical information: %s' % project_id)
        logging.warning('project missed critical information in firebase: %s' % project_id)
        return False
    else:
        print('project is in firebase projects table and has all attributes: %s' % project_id)
        logging.warning('project is in firebase projects table and has all attributes: %s' % project_id)
        return True


def get_project_contributors(project_id):
    # establish mysql connection
    m_con = mysqlDB()
    # sql command
    sql_query = '''
        SELECT
          count(distinct(user_id))
        FROM
          results
        WHERE
          project_id = %s
    '''
    data = [project_id]
    # one row with one value will be returned
    contributors = m_con.retr_query(sql_query, data)[0][0]
    # delete/close db connection
    del m_con

    print('got contributors from mysql for project: %s. contributors = %s' % (project_id, contributors))
    logging.warning('got contributors from mysql for project: %s. contributors = %s' % (project_id, contributors))

    return contributors


def set_project_contributors_firebase(project_id, contributors):
    # connect to firebase
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # update contributors value for firebase project
    # contributors in firebase is stored as integer
    contributors = int(contributors)
    fb_db.child("projects").child(project_id).update({"contributors": contributors})

    # check if progress has been updated
    new_contributors = fb_db.child("projects").child(project_id).child("contributors").shallow().get().val()

    if contributors == new_contributors:
        print('update contributors for project %s successful' % project_id)
        logging.warning('update contributors in firebase for project %s successful' % project_id)
        return True
    else:
        print('update contributors in firebase for project %s FAILED' % project_id)
        logging.warning('update contributors for project %s FAILED' % project_id)
        return False


def log_project_contributors(project_id, project_contributors, output_path):

    # check if output path for projects is correct and existing
    if not os.path.exists(output_path + '/contributors'):
        os.makedirs(output_path + '/contributors')

    filename = "{}/contributors/contributors_{}.txt".format(output_path, project_id)

    print(project_contributors)

    with open(filename, 'a') as output_file:
        timestamp = int(time.time())
        outline = "{},{}\n".format(timestamp, project_contributors)
        output_file.write(outline)

    print('log contributors to file for project %s successful' % project_id)
    logging.warning('log contributors to file for project %s successful' % project_id)


########################################################################################################################
def update_project_contributors(projects, output_path):

    logging.basicConfig(filename='run_update.log',
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # record time
    starttime = time.time()

    # check if a non-empty list with project ids is provided
    if len(projects) == 0:
        print('no projects to process')
        logging.warning('no projects to process')
    else:
        for project_id in projects:
            print('start project contributors update for project: %s' % project_id)
            logging.warning('start project contributors update for project: %s' % project_id)

            # check if project exists in firebase
            if project_exists(project_id):
                print('project exists in firebase: %s' % project_id)
                logging.warning('project exists in firebase: %s' % project_id)
                pass
            else:
                print('project does not exist in firebase: %s. Skip it.' % project_id)
                logging.warning('project does not exist in firebase: %s. Skip it.' % project_id)
                continue

            # get contributors data from mysql
            project_contributors = get_project_contributors(project_id)

            # save project progress in firebase
            set_project_contributors_firebase(project_id, project_contributors)

            # log project contributors to stats file
            log_project_contributors(project_id, project_contributors, output_path)

    # calc process time
    endtime = time.time() - starttime
    print('finished project contributors update for projects: %s, %f sec.' % (projects, endtime))
    logging.warning('finished project contributors update for projects: %s, %f sec.' % (projects, endtime))
    return


########################################################################################################################
if __name__ == '__main__':
    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    update_project_contributors(args.projects, args.output_path)
