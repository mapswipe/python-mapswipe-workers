#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
import os
import time
import json
import threading
from queue import Queue
import requests

from mapswipe_workers.basic import BaseFunctions as b
from psycopg2 import sql

def imports_to_postgres(firebase, postgres):
    fb_db = firebase.database()
    # get a dict with all imports
    imports = fb_db.child("imports").get().val()

    # loop over imports
    for import_key, import_dict in imports.items():
        # let's have a look at the project type
        try:
            project_type = import_dict['projectType']
        except:
            project_type = 1

        # now let's init the import
        imp = b.init_import(project_type, import_key, import_dict)

        # set import in postgres
        imp.set_import_postgres(postgres)

def projects_to_postgres(firebase, postgres):
    ### this functions gets the IDs of all projects in firebase
    ### and returns a list

    fb_db = firebase.database()
    p_con = postgres()


    all_projects = fb_db.child("projects").get().val()

    for key, project_dict in all_projects.items():

        info = {}

        for project_dict_key , val in project_dict.items():
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
                int(project_dict['groupAverage']),
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

def save_groups_tasks_psql(postgres, project, task_filename, group_filename):

    p_con = postgres()

    # Open CSV file
    task_file = open(task_filename, 'r')
    group_file = open(group_filename, 'r')
    import_tasks_table_name = 'import_tasks'
    import_task_table_name = import_tasks_table_name + '_{}'.format(project)

    import_groups_table_name = 'import_groups'
    import_groups_table_name = import_groups_table_name + '_{}'.format(project)

    task_columns = ('task_id', 'group_id', 'project_id', 'info')
    group_columns = ('project_id', 'group_id', 'count', 'completedCount', 'info')

    sql_insert = '''
            DROP TABLE IF EXISTS {};
            CREATE TABLE {} (
                task_id varchar NOT NULL
                ,group_id int
                ,project_id int
                ,info json
            );
            '''

    sql_insert = sql.SQL(sql_insert).format(sql.Identifier(import_task_table_name),
                                            sql.Identifier(import_task_table_name))

    p_con.query(sql_insert, None)

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

    # copy data to the new table
    p_con.copy_from(task_file, import_task_table_name, sep=';', columns=task_columns)
    p_con.copy_from(group_file, import_groups_table_name, sep=';', columns=group_columns)

    task_file.close()
    os.remove(task_filename)
    print('uploaded task + group information to psql')

    sql_insert = '''
        INSERT INTO tasks
        SELECT
          *
        FROM
           {}
          ;
    '''

    sql_insert = sql.SQL(sql_insert).format(sql.Identifier(import_tasks_table_name))
    print(sql_insert)
    p_con.query(sql_insert, None)

    sql_insert = '''
        INSERT INTO groups
        SELECT
          *
        FROM
          {};
        '''

    sql_insert = sql.SQL(sql_insert).format(sql.Identifier(import_groups_table_name))

    p_con.query(sql_insert, None)

    print('inserted into table')

def download_all_groups_tasks(firebase):

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
            print('no groups for project: %s ..skippin it' % project)

        print('project: %s downloaded' % project)

    del fb_db


def download_users(firebase,postgres):
    fb_db = firebase.database()
    p_con = postgres()

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
    del p_con
    del fb_db


####################################################################################################
if __name__ == '__main__':


    starttime = time.time()
    #os.chdir('../..')
    #enable connection to firebase
    firebase, postgres = b.get_environment()

    # imports
    #imports_to_postgres(firebase,postgres)

    # projects
    #projects_to_postgres(firebase,postgres)
    # groups + tasks
    #download_all_groups_tasks(firebase)

    # users
    download_users(firebase,postgres)

    endtime = time.time() - starttime

    print(endtime)
