#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################

import os, sys
import logging
import time
import argparse
import json
import threading
from queue import Queue
import requests
import ogr

from mapswipe_workers.basic import BaseFunctions as b
from psycopg2 import sql
####################################################################################################
parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('-op', '--operation', nargs='?', required=True,
                    choices=['download', 'import'])

parser.add_argument('-mo', '--modus', nargs='?', default='development',
                    choices=['development', 'production'])


####################################################################################################
def imports_to_postgres(firebase):
    logging.info('Imports import started')

    fb_db = firebase.database()
    # get a dict with all imports
    imports = fb_db.child("imports").get().val()
    raw_geom = 'data/check_kml.kml'

    # loop over imports
    for import_key, import_dict in imports.items():
        # let's have a look at the project type
        try:
            project_type = import_dict['projectType']
        except:
            project_type = 1

        if not 'tileServer' in import_dict.keys():
            import_dict['tileServer'] = 'bing'

        if len(import_dict['project'].keys()) < 4:
            continue

        if 'projectDescription' in import_dict['project'].keys():
            import_dict['project']['projectDetails'] = import_dict['project']['projectDescription']

        with open(raw_geom, 'w') as geom_file:
            geom_file.write(import_dict['kml'])

        try:
            driver = ogr.GetDriverByName('KML')
            datasource = driver.Open(raw_geom, 0)
            layer = datasource.GetLayer()
            if not layer.GetFeatureCount() > 0:
                continue
            else:
                pass
        except:
            continue

        # now let's init the import
        imp = b.init_import(project_type, import_key, import_dict)

        # set import in postgres
        imp.set_import_postgres(postgres)
        os.remove(raw_geom)

    del fb_db


def projects_to_postgres(firebase, postgres):
    logging.info('Projects import started')
    ### this functions gets the IDs of all projects in firebase
    ### and returns a list

    fb_db = firebase.database()
    p_con = postgres()


    all_projects = fb_db.child("projects").get().val()

    proj_left = len(all_projects)
    logging.info('%i projects available.' % proj_left)

    for key, project_dict in all_projects.items():

        info = {}

        if len(project_dict.keys()) < 4:
            logging.info('project %s. got less than 4 attributes. will be skipped' % key)
            proj_left = proj_left - 1
            logging.info('.. %i projects left' % proj_left)
            continue

        for project_dict_key, val in project_dict.items():
            if not project_dict_key in ['contributors', 'groupAverage', 'id', 'image',
                                        'importKey', 'isFeatured', 'lookFor', 'name',
                                        'progress', 'projectDetails', 'state',
                                        'verificationCount', 'project_type']:
                info[project_dict_key]=val

        project_dict['info'] = info

        # dont no
        try:
            project_dict['project_type']
        except:
            project_dict['project_type'] = 1

        sql_insert = '''
                INSERT INTO public.projects Values(
                  %s -- contributors,
                  ,%s -- groupAverage,
                  ,%s -- id,
                  ,%s -- image,
                  ,%s -- importKey,
                  ,%s -- isFeatured,
                  ,%s -- lookFor,
                  ,%s -- name,
                  ,%s -- progress,
                  ,%s -- projectDetails,
                  ,%s -- state,
                  ,%s -- verificationCount,
                  ,%s -- projectType,
                  ,%s -- info
                  ) 
            '''

        data = [int(project_dict['contributors']),
                float(project_dict['groupAverage']),
                int(project_dict['id']),
                project_dict['image'],
                project_dict['importKey'],
                project_dict['isFeatured'],
                project_dict['lookFor'],
                project_dict['name'],
                int(project_dict['progress']),
                project_dict['projectDetails'],
                project_dict['state'],
                int(project_dict['verificationCount']),
                project_dict['project_type'],
                json.dumps(project_dict['info'])]

        p_con.query(sql_insert, data)
        proj_left = proj_left - 1
        logging.info('%i project imported, %i projects left' % (int(project_dict['id']), proj_left))

    del fb_db
    del p_con


def download_groups_tasks_per_project(q):
    while not q.empty():

        project_id, group_id, task_file, group_file = q.get()

        fb_db = firebase.database()

        group = fb_db.child("groups").child(project_id).child(group_id).get().val()
        group_tasks = group['tasks']


        if len(group_tasks) > 0:
            for task_id, keys in group_tasks.items():

                info = {}

                for task_key, vals in keys.items():
                        if not task_key in ['id', 'projectId']:
                            info[task_key]=vals

                outline = '%s;%i;%i;%s\n' % (group_tasks[task_id]['id'],
                                             int(group_id),
                                             int(group['projectId']),
                                             json.dumps(info))
                task_file.write(outline)

        group_info = {}

        for group_key, group_vals in group.items():

            if not group_key in ['projectId', 'id', 'count', 'completedCount']:
                group_info.update(group_key=group_vals)

        group_outline = '%i;%i;%i;%i;%s\n' % (int(group['projectId']),
                                              int(group['id']),
                                              int(group['count']),
                                              int(group['completedCount']),
                                              json.dumps(group_info))
        group_file.write(group_outline)

        q.task_done()


def import_all_groups_tasks(postgres):
    logging.info('Groups + tasks import started')

    p_con = postgres()

    # list all group csv's
    os.chdir('data')
    for file in os.listdir():

        if file.endswith('_groups.csv'):
            group_file = open(file, 'r')
            import_groups_table_name = 'import_groups'
            project = file.split('_')[0]
            import_groups_table_name = import_groups_table_name + '_{}'.format(project)
            group_columns = ('project_id', 'group_id', 'count', 'completedCount', 'info')
            sql_insert = '''
                        DROP TABLE IF EXISTS {};
                        CREATE TABLE {} (
                            project_id int
                            ,group_id int
                            ,count int
                            ,completedCount int
                            ,info json
                        );
                        '''
            sql_insert = sql.SQL(sql_insert).format(sql.Identifier(import_groups_table_name),
                                                    sql.Identifier(import_groups_table_name))
            p_con.query(sql_insert, None)

            p_con.copy_from(group_file, import_groups_table_name, sep=';', columns=group_columns)

            group_file.close()

            sql_insert = '''
                    INSERT INTO groups
                    SELECT
                      *
                    FROM
                       {}
                      ;
                     DROP TABLE IF EXISTS {};
                '''
            sql_insert = sql.SQL(sql_insert).format(sql.Identifier(import_groups_table_name),
                                                    sql.Identifier(import_groups_table_name))

            p_con.query(sql_insert, None)

            logging.info('Project: %s, groups imported' % project)

        elif (file.endswith('_tasks.csv')):
            task_file = open(file, 'r')
            import_tasks_table_name = 'import_tasks'
            project = file.split('_')[0]
            import_tasks_table_name = import_tasks_table_name + '_{}'.format(project)

            task_columns = ('task_id', 'group_id', 'project_id', 'info')
            sql_insert = '''
                        DROP TABLE IF EXISTS {};
                            CREATE TABLE {} (
                                task_id varchar NOT NULL
                                ,group_id int
                                ,project_id int
                                ,info json
                             );
                        '''
            sql_insert = sql.SQL(sql_insert).format(sql.Identifier(import_tasks_table_name),
                                                    sql.Identifier(import_tasks_table_name))
            p_con.query(sql_insert, None)

            p_con.copy_from(task_file, import_tasks_table_name, sep=';', columns=task_columns)

            task_file.close()

            sql_insert = '''
                    INSERT INTO tasks
                    SELECT
                      *
                    FROM
                       {}
                      ;
                    DROP TABLE IF EXISTS {};
                '''
            sql_insert = sql.SQL(sql_insert).format(sql.Identifier(import_tasks_table_name),
                                                    sql.Identifier(import_tasks_table_name))

            p_con.query(sql_insert, None)

            logging.info('Project: %s, tasks imported' % project)
        else:
            continue

    del p_con


def download_all_groups_tasks(firebase):
    logging.info('Groups + tasks download started')

    fb_db = firebase.database()

    all_projects = fb_db.child("projects").get().val()

    for project in all_projects.keys():

        group_ids = fb_db.child("groups").child(project).shallow().get().val()

        # this tries to set the max pool connections to 100
        adapter = requests.adapters.HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
        for scheme in ('http://', 'https://'):
            fb_db.requests.mount(scheme, adapter)

        # we will use a queue to limit the number of threads running in parallel
        q = Queue(maxsize=0)
        num_threads = 8
        if group_ids:

            task_filename = 'data/%s_tasks.csv' % project
            group_filename = 'data/%s_groups.csv' % project

            if not os.path.exists('data'):
                os.makedirs('data')

            task_file = open(task_filename, 'w')
            group_file = open(group_filename, 'w')

            for group_id in group_ids:
                q.put([project, group_id, task_file, group_file])

            for i in range(num_threads):
                worker = threading.Thread(
                    target=download_groups_tasks_per_project,
                    args=(q,))
                # worker.setDaemon(True)
                worker.start()

            q.join()
            task_file.close()
            group_file.close()

        else:
            logging.info('No groups for project: %s ..skippin it' % project)

        logging.info('Groups + tasks for project: %s downloaded' % project)

    del fb_db


def download_users(firebase):
    logging.info('Users import started')

    fb_db = firebase.database()

    users = fb_db.child("users").get().val()

    user_dict = {}

    for key, val in users.items():
        user_dict['user_id'] = key
        try:
            user_dict['contributions'] = val['contributions']
            user_dict['distance'] = val['distance']
            user_dict['username'] = val['username']
        except KeyError:
            user_dict['contributions'] = 0
            user_dict['distance'] = 0
            user_dict['username'] = 'None'

    users_filename = 'data/users.csv'

    if not os.path.exists('data'):
        os.makedirs('data')

    users_file = open(users_filename, 'w')

    users_outline = '%s;%i;%f;%s\n' % (user_dict['user_id'],
                                       int(user_dict['contributions']),
                                       float(user_dict['distance']),
                                       user_dict['username'])
    users_file.write(users_outline)

    users_file.close()

    logging.info('Downloaded all Users')
    del fb_db


def import_users(postgres):
    logging.info('Users import started')
    p_con = postgres()
    users_file = open('data/users.csv')
    users_columns = ('user_id', 'contributions', 'distance', 'username')
    p_con.copy_from(users_file, 'users', sep=';', columns=users_columns)
    users_file.close()
    logging.info('Imported all users')

####################################################################################################


if __name__ == '__main__':
    start_time = time.time()
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename='./logs/utils_{}.log'.format(args.operation),
                        filemode="a",
                        level=logging.INFO)

    logger = logging.getLogger(name="utils_{}".format(args.operation))

    firebase, postgres = b.get_environment(args.modus)

    logging.info("Operation: %s started." % args.operation)

    cwd = os.getcwd()

    if args.operation == 'download':
        download_all_groups_tasks(firebase)
        download_users(firebase)
    elif args.operation == 'import':
        imports_to_postgres(firebase)
        projects_to_postgres(firebase, postgres)
        import_all_groups_tasks(postgres)
        os.chdir(cwd)
        import_users(postgres)
    else:
        pass

    end_time = time.time() - start_time

    logging.info("Operation: %s done. Duration: %s" % (args.operation, end_time))
