#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################
import json
import os
import logging
import time

from mapswipe_workers.cfg import auth


def project_exists(firebase, project_id):
    # check if a project corresponding to the provided id exists in firebase and has all information required
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


def get_project_results(mysqlDB, project_id):
    # establish mysql connection
    m_con = mysqlDB()
    # sql command
    sql_query = '''
        select
          task_id as id
          -- ,results.user_id
          ,project_id as project
          -- ,results.timestamp
          ,task_x
          ,task_y
          ,task_z
          ,avg(result) as decision
          ,SUM(CASE
            WHEN result = 1 THEN 1
            ELSE 0
           END) AS yes_count
           ,SUM(CASE
            WHEN result = 2 THEN 1
            ELSE 0
           END) AS maybe_count
           ,SUM(CASE
            WHEN result = 3 THEN 1
            ELSE 0
           END) AS bad_imagery_count
           ,wkt
        from
          results
        where
          project_id = %s and result > 0
        group by
          task_id, wkt'''

    data = [project_id]

    project_results = m_con.retr_query(sql_query, data)
    # delete/close db connection
    del m_con

    print('got results information from mysql for project: %s. rows = %s' % (project_id, len(project_results)))
    logging.warning('got results information from mysql for project: %s. rows = %s' % (project_id, len(project_results)))

    return project_results

def rows_to_json(project_id, project_results, output_json_file):

    result_list = []
    for row in project_results:

        row_dict = {}
        row_dict['id'] = row[0]
        row_dict['project'] = row[1]
        row_dict['task_x'] = row[2]
        row_dict['task_y'] = row[3]
        row_dict['task_z'] = row[4]
        # we need to avoid json decimal error and convert to string and then to float
        # Object of type 'Decimal' is not JSON serializable
        row_dict['decision'] = float(str(row[5]))
        row_dict['yes_count'] = float(str(row[6]))
        row_dict['maybe_count'] = float(str(row[7]))
        row_dict['bad_imagery_count'] = float(str(row[8]))
        row_dict['wkt'] = row[9]
        result_list.append(row_dict)

    with open(output_json_file, 'w') as outfile:
        json.dump(result_list, outfile)

    print('wrote results to json file for project: %s. outfile = %s' % (project_id, output_json_file))
    logging.warning('wrote results to json file for project: %s. outfile = %s' % (project_id, output_json_file))
    return output_json_file


def export_project_results(modus, projects, output_path):

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

    # record time
    starttime = time.time()

    # check if output path for projects is correct and existing
    if not os.path.isdir(output_path + '/projects'):
        os.mkdir(output_path + '/projects')

    # check if a non-empty list with project ids is provided
    if len(projects) == 0:
        print('no projects to process')
        logging.warning('no projects to process')
    else:
        for project_id in projects:
            print('start project results export for project: %s' % project_id)
            logging.warning('start project results export for project: %s' % project_id)

            # check if project exists in firebase
            if project_exists(firebase, project_id):
                print('project exists in firebase: %s' % project_id)
                logging.warning('project exists in firebase: %s' % project_id)
                pass
            else:
                print('project does not exist in firebase: %s. Skip it.' % project_id)
                logging.warning('project does not exist in firebase: %s. Skip it.' % project_id)
                continue

            # get contributors data from mysql
            project_results = get_project_results(mysqlDB, project_id)

            # save project progress in firebase
            # we need to adjust to the nginx output path on the server
            output_json_file = '{}/projects/{}.json'.format(output_path, project_id)
            json_output_file = rows_to_json(project_id, project_results, output_json_file)

    # calc process time
    endtime = time.time() - starttime
    print('finished project results export for projects: %s, %f sec.' % (projects, endtime))
    logging.warning('finished project results export for projects: %s, %f sec.' % (projects, endtime))
    return