#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import sys
import json
import os
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')
sys.path.insert(0, '../utils/')

import logging
import time
from auth import firebase_admin_auth

import argparse
# define arguments that can be passed by the user
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-o', '--output_path', required=None, default='/var/www/html', type=str,
                    help='output path. please provide a location where the exported files should be stored.')

def get_all_projects():
    # connect to firebase
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # get all projects
    all_projects = fb_db.child("projects").get().val()

    print('got project information from firebase.')
    logging.warning('got project information from firebase.')

    return all_projects

########################################################################################################################

def export_projects(output_path):

    logging.basicConfig(filename='run_export.log',
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # record time
    starttime = time.time()

    print('start projects export')
    logging.warning('start projects export')

    # check if output path for projects is correct and existing
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    # get projects from firebase
    all_projects = get_all_projects()

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

########################################################################################################################
if __name__ == '__main__':
    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    export_projects(args.output_path)
