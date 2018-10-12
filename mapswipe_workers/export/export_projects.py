#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import json
import os
import logging
import time

from mapswipe_workers.cfg import auth
########################################################################################################################


def get_all_projects(firebase):
    # connect to firebase
    fb_db = firebase.database()

    # get all projects
    all_projects = fb_db.child("projects").get().val()

    print('got project information from firebase.')
    logging.warning('got project information from firebase.')

    return all_projects


def export_projects(modus, output_path):

    if modus == 'development':
        # we use the dev instance for testing
        firebase = auth.dev_firebase_admin_auth()
        print('We are using the development instance')
    elif modus == 'production':
        # we use the dev instance for testing
        firebase = auth.firebase_admin_auth()
        print('We are using the production instance')


    # record time
    starttime = time.time()

    print('start projects export')
    logging.warning('start projects export')

    # check if output path for projects is correct and existing
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    # get projects from firebase
    all_projects = get_all_projects(firebase)

    # save users as json
    # we need to adjust to the nginx output path on the server
    output_json_file = '{}/projects.json'.format(output_path)
    with open(output_json_file, 'w') as outfile:
        json.dump(all_projects, outfile)
    print('exported projects.json file: %s' % output_json_file)
    logging.warning('exported projects.json file: %s' % output_json_file)

    # calc process time
    endtime = time.time() - starttime
    print('finished projects export, %f sec.' % endtime)
    logging.warning('finished projects export, %f sec.' % endtime)
    return


