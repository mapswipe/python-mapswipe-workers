#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################
import json
import os
import logging
import time

from mapswipe_workers.cfg import auth


def get_all_users(firebase):
    # connect to firebase
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

def export_users_and_stats(modus, output_path):

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

    print('start users and stats export')
    logging.warning('start users and stats export')

    # check if output path for projects is correct and existing
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    # get users from firebase
    all_users = get_all_users(firebase)

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