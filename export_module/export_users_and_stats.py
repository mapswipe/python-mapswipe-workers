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


def get_all_users():
    # connect to firebase
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # get all projects
    all_users = fb_db.child("users").get().val()

    print('got user information from firebase.')
    logging.warning('got user information from firebase.')

    return all_users

def get_stats(all_users):

    stats_dict = {}
    stats_dict['users'] = len(all_users)
    stats_dict['totalDistanceMappedInSqKm'] = 0
    stats_dict['totalContributionsByUsers'] = 0

    for user in all_users:
        stats_dict['totalDistanceMappedInSqKm'] += all_users[user]['distance']
        stats_dict['totalContributionsByUsers'] += all_users[user]['contributions']

    print('computed stats based on user information from firebase.')
    logging.warning('computed stats based on user information from firebase.')
    return stats_dict

########################################################################################################################

def export_users_and_stats(output_path):

    logging.basicConfig(filename='run_export.log',
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # record time
    starttime = time.time()

    print('start users and stats export')
    logging.warning('start users and stats export')

    # check if output path for projects is correct and existing
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    # get users from firebase
    all_users = get_all_users()

    # save users as json
    # we need to adjust to the nginx output path on the server
    output_json_file = '{}/users.json'.format(output_path)
    with open(output_json_file, 'w') as outfile:
        json.dump(all_users, outfile)
    print('exported users.json file: %s' % output_json_file)
    logging.warning('exported users.json file: %s' % output_json_file)


    # calculate stats from users
    stats = get_stats(all_users)

    # save stats as json file
    # we need to adjust to the nginx output path on the server
    output_json_file = '{}/stats.json'.format(output_path)
    with open(output_json_file, 'w') as outfile:
        json.dump(stats, outfile)
    print('exported stats.json file: %s' % output_json_file)
    logging.warning('exported stats.json file: %s' % output_json_file)

    # calc process time
    endtime = time.time() - starttime
    print('finished users and stats export, %f sec.' % endtime)
    logging.warning('finished users and stats export, %f sec.' % endtime)
    return

########################################################################################################################
if __name__ == '__main__':
    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')


    export_users_and_stats(args.output_path)
