#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
import logging
import time
import os
import json
from mapswipe_workers.basic import BaseFunctions as b
from psycopg2 import sql
import argparse


####################################################################################################
parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('-mo', '--modus', nargs='?', default='development',
                    choices=['development', 'production'])
####################################################################################################


def check_firebase_psql(firebase, postgres):
    logging.info('Checking imports')

    fb_db = firebase.database()
    p_con = postgres()
    fb_imports = list(fb_db.child("imports").shallow().get().val())
    sql_imports = '''SELECT import_id FROM imports '''

    psql_imports = [r[0] for r in p_con.retr_query(sql_imports, None)]

    diff_imports = set(fb_imports).difference(set(psql_imports))
    if diff_imports:
        logging.info('Following imports are missing in postgres:')
        for imp in diff_imports:
            logging.info('Import missing in postgresql: %s' % imp)

    fb_projects = list(fb_db.child("projects").shallow().get().val())
    sql_projects = '''SELECT project_id FROM projects'''
    psql_projects = [str(r[0]) for r in p_con.retr_query(sql_projects, None)]
    diff_projects = set(fb_projects).difference(set(psql_projects))
    if diff_projects:
        logging.info('Following projects are missing in postgres:')
        for prj in diff_projects:
            logging.info('Project missing in postgresql: %s' % prj)
    else:
        logging.info('No projects are missing in postgresql')

    fb_users = list(fb_db.child("users").shallow().get().val())
    sql_users = '''SELECT user_id FROM users'''
    psql_users = [str(r[0]) for r in p_con.retr_query(sql_users, None)]
    diff_users = set(fb_users).difference(set(psql_users))
    if diff_users:
        logging.info('Following users are missing in postgres:')
        for usr in diff_users:
            logging.info('User missing in postgresql: %s' % usr)
    else:
        logging.info('No users are missing in postgresql')

    logging.info('Starting check for groups\n Groups for projects which are not present in postgres will be skipped..')

    missing_groups = {}
    for project in psql_projects:
        logging.info('Checking project: %s/%s' %(psql_projects.index(project), len(psql_projects)))
        fb_groups = list(fb_db.child("groups").child(project).shallow().get().val())
        sql_groups = '''SELECT group_id FROM groups WHERE project_id = %s'''
        data = [int(project)]
        psql_groups = [str(r[0]) for r in p_con.retr_query(sql_groups, data)]
        diff_groups = set(fb_groups).difference(set(psql_groups))
        if diff_groups:
            logging.info('found missing group')
            missing_groups[project] = diff_groups
    if missing_groups:
        if not os.path.exists('data'):
            os.makedirs('data')
            with open('data/missing_groups.json', 'w') as mg:
                json.dumps(missing_groups, mg)

        for group_prj in missing_groups.keys():
            logging.info('One or group for project %s us is missing in postgresql' % group_prj)
        logging.info('For detailed information on which group, please have look at the .json'
                     ' in data/missing_groups.json')
    else:
        logging.info('No groups are missing in postgresql')

####################################################################################################


if __name__ == '__main__':
    start_time = time.time()
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename='./logs/utils_report.log',
                        filemode="a",
                        level=logging.INFO)
    logger = logging.getLogger(name="utils_report")

    logging.info("Operation started in mode %s." % args.modus)

    firebase, postgres = b.get_environment(args.modus)

    check_firebase_psql(firebase, postgres)
    end_time = time.time() - start_time

    logging.info("Operation done. Duration: %s" % end_time)
