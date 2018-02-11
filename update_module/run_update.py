#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import sys
import json
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')
sys.path.insert(0, '../utils/')

import logging
from update_project_contributors import update_project_contributors
from update_project_progress import update_project_progress
from auth import firebase_admin_auth
from send_slack_message import send_slack_message

import time
import argparse

# define arguments that can be passed by the user
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-l', '--loop', dest='loop', action='store_true',
                    help='if loop is set, the import will be repeated several times. You can specify the behaviour using --sleep_time and/or --max_iterations.')
parser.add_argument('-s', '--sleep_time', required=False, default=None, type=int,
                    help='the time in seconds for which the script will pause in beetween two imports')
parser.add_argument('-m', '--max_iterations', required=False, default=None, type=int,
                    help='the maximum number of imports that should be performed')

parser.add_argument('-mo', '--modus', nargs='?', default='active',
                    choices=['all', 'not_finished', 'active', 'user_list'])

parser.add_argument('-p', '--user_project_list', nargs='+', required=None, default=None, type=int,
                    help='project id of the project to process. You can add multiple project ids.')

########################################################################################################################

def get_projects():
    # connect to firebase
    firebase = firebase_admin_auth()
    fb_db = firebase.database()


    project_dict = {}
    project_dict['all'] = []
    project_dict['active'] = []
    project_dict['not_finished'] = []

    # get the projects from firebase
    all_projects = fb_db.child("projects").get().val()

    for project in all_projects:
        try:
            # some project miss critical information, they will be skipped
            project_id = all_projects[project]['id']
            project_active = all_projects[project]['state']
            project_progress = all_projects[project]['progress']
        except:
            continue

        project_dict['all'].append(int(project_id))
        # projects with state=0 are active, state=3 means inactive
        if project_active == 0:
            project_dict['active'].append(project_id)
        if project_progress < 100:
            project_dict['not_finished'].append(project_id)

    return project_dict

def run_update(project_selection, user_project_list):

    logging.basicConfig(filename='run_update.log',
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # get projects based on type, e.g. "all", "active", "not_finished"
    project_groups = get_projects()
    if project_selection == 'user_list':
        projects = user_project_list
        print('use project ids provided by user: %s' % user_project_list)
        logging.warning('use project ids provided by user: %s' % user_project_list)
    else:
        projects = project_groups[project_selection]
        print('use project ids provided by user for %s projects: %s' % (project_selection, projects))
        logging.warning('use project ids provided by user for %s projects: %s' % (project_selection, projects))

    update_project_contributors(projects)
    update_project_progress(projects)


########################################################################################################################

if __name__ == '__main__':
    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')


    logging.basicConfig(filename='run_update.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

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

        logging.warning('### START run_update.py workflow ###')

        # this runs the script and sends an email if an error happens within the execution
        try:
            run_update(args.modus, args.user_project_list)
        except:
            tb = sys.exc_info()
            # log error
            logging.warning(str(tb))
            # send mail to mapswipe google group with
            print(tb)
            msg = str(tb)
            head = 'google-mapswipe-workers: run_update.py: error occured'
            send_slack_message(head + '\n' + msg)

        # check if the script should be looped
        if args.loop:
            if args.max_iterations > counter:
                counter = counter + 1
                print('update finished. will pause for %s seconds' % args.sleep_time)
                logging.warning('update finished. will pause for %s seconds' % args.sleep_time)
                x = 1
                time.sleep(args.sleep_time)
            else:
                x = 0
                # print('import finished and max iterations reached. stop here.')
                print('update finished and max iterations reached. sleeping now for %s sec.' % args.sleep_time)
                logging.warning('update finished and max iterations reached. sleeping now for %s sec.' % args.sleep_time)
                time.sleep(args.sleep_time)
        # the script should run only once
        else:
            print("Don't loop. Stop after the first run.")
            logging.warning("<<< Don't loop. Stop after the first run. >>>")
            x = 0
