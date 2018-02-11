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
import numpy as np
import os
import threading
import time
from queue import Queue

import requests

from auth import firebase_admin_auth



import argparse
# define arguments that can be passed by the user
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-p', '--projects', nargs='+', required=True, default=None, type=int,
                    help='project id of the project to process. You can add multiple project ids.')


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
    # projects neeed to have at least 12 attributes in firebase, otherwise something went wrong during the import
    elif len(project_data) < 12:
        print('project missed critical information: %s' % project_id)
        logging.warning('project missed critical information in firebase: %s' % project_id)
        return False
    else:
        print('project is in firebase projects table and has all attributes: %s' % project_id)
        logging.warning('project is in firebase projects table and has all attributes: %s' % project_id)
        return True

def get_verification_count(project_id):
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # get the verification count for this project from firebase
    verification_count = float(fb_db.child("projects").child(project_id).child("verificationCount").shallow().get().val())

    return verification_count

def get_group_progress(q):

    while not q.empty():
        # get the values from the q object
        fb_db, group_progress_list, project_id, group_id, verification_count = q.get()

        #this functions downloads only the completed count per group from firebase
        try:
            # establish a new connection to firebase
            completed_count = fb_db.child("groups").child(project_id).child(group_id).child("completedCount").get().val()
        except:
            # add a catch, if something with the connection to firebase goes wrong and log potential errors
            tb = sys.exc_info()
            logging.warning(str(tb))
            completed_count = None



        # we check whether the completed_count is defined. if the connection fails etc. we don't write None
        # writing None would cause an error during the upload to mysql
        if completed_count is None:
            print(completed_count)
            print('completed count for group %s of project %s is not defined' % (group_id, project_id))

            # if we can't get the completed count for a group, we will set it to 0.0
            completed_count = 0.0
            progress = 0.0
            # all variables are converted to float to avoid errors when computing the mean later
            group_progress_list.append(
                [float(project_id), float(group_id), float(completed_count), float(verification_count),
                 float(progress)])
        else:

            progress = 100.0 * float(completed_count) / float(verification_count)
            if progress > 100:
                progress = 100.0
            # all variables are converted to float to avoid errors when computing the mean later
            group_progress_list.append(
                [float(project_id), float(group_id), float(completed_count), float(verification_count),
                 float(progress)])

        q.task_done()

def download_group_progress(project_id, verification_count):
    # this functions uses threading to get the completed counts of all groups per project




    # create a list where we store the progress and other information for each group
    group_progress_list = []

    # we will use a queue to limit the number of threads running in parallel
    q = Queue(maxsize=0)
    num_threads = 24

    # it is important to use the shallow option, only keys will be loaded and not the complete json
    firebase = firebase_admin_auth()
    fb_db = firebase.database()
    # this tries to set the max pool connections to 100
    adapter = requests.adapters.HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
    for scheme in ('http://', 'https://'):
        fb_db.requests.mount(scheme, adapter)


    all_groups = fb_db.child("groups").child(project_id).shallow().get().val()

    print('downloaded all groups of project %s from firebase' % project_id)
    logging.warning('downloaded all groups of project %s from firebase' % project_id)
    for group_id in all_groups:
        q.put([fb_db, group_progress_list, project_id, group_id, verification_count])

    print('added all groups of project %s to queue' % project_id)
    logging.warning('added all groups of project %s to queue' % project_id)
    for i in range(num_threads):
        worker = threading.Thread(
            target=get_group_progress,
            args=(q,))
        worker.start()

    q.join()

    del fb_db

    print('downloaded progress for all groups of project %s from firebase' % project_id)
    logging.warning('downloaded progress for all groups of project %s from firebase' % project_id)

    return group_progress_list

def calculate_project_progress(project_id, group_progress_list):

    data = np.array(group_progress_list)
    project_progress = np.average(data, axis=0)[-1]
    print('calculated progress for project %s. progress = %s' % (project_id, project_progress))
    logging.warning('calculated progress for project %s. progress = %s' % (project_id, project_progress))
    return project_progress

def set_project_progress_firebase(project_id, progress):
    # connect to firebase
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # update progress value for firebase project
    # progress in firebase is stored as integer
    progress = int(progress)
    fb_db.child("projects").child(project_id).update({"progress": progress})

    # check if progress has been updated
    new_progress = fb_db.child("projects").child(project_id).child("progress").shallow().get().val()

    if progress == new_progress:
        print('update progress for project %s successful' % project_id)
        logging.warning('update progress in firebase for project %s successful' % project_id)
        return True
    else:
        print('update progress in firebase for project %s FAILED' % project_id)
        logging.warning('update progress for project %s FAILED' % project_id)
        return False


########################################################################################################################

def update_project_progress(projects):

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
            print('start project progress update for project: %s' % project_id)
            logging.warning('start project progress update for project: %s' % project_id)

            # check if project exists in firebase
            if project_exists(project_id):
                print('project exists in firebase: %s' % project_id)
                logging.warning('project exists in firebase: %s' % project_id)
                pass
            else:
                print('project does not exist in firebase: %s. Skip it.' % project_id)
                logging.warning('project does not exist in firebase: %s. Skip it.' % project_id)
                continue

            # get verification count and check if it is valid
            verification_count = get_verification_count(project_id)
            if verification_count is None:
                print('verification count is not defined. Skip the project: %s' % project_id)
                logging.warning('verification count is not defined. Skip the project: %s' % project_id)
                continue
            elif verification_count < 1:
                print('something is wrong with the verification count: %s. Skip the project: %s' % (verification_count, project_id))
                logging.warning('something is wrong with the verification count: %s. Skip the project: %s' % (verification_count, project_id))
                continue

            # download group completed count data from firebase
            group_progress_list = download_group_progress(project_id, verification_count)

            # calculate project progress
            project_progress = calculate_project_progress(project_id, group_progress_list)

            # save project progress in firebase
            set_project_progress_firebase(project_id, project_progress)

    # calc process time
    endtime = time.time() - starttime
    print('finished project progress update for projects: %s, %f sec.' % (projects, endtime))
    logging.warning('finished project progress update for projects: %s, %f sec.' % (projects, endtime))
    return

########################################################################################################################
if __name__ == '__main__':
    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    update_project_progress(args.projects)
