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
import json
import numpy as np
import os
import threading
import time
from queue import Queue

import requests

import pymysql
from auth import firebase_admin_auth
from auth import mysqlDB

import error_handling

from send_slack_message import send_slack_message

import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-l', '--loop', dest='loop', action='store_true',
                    help='if loop is set, the import will be repeated several times. You can specify the behaviour using --sleep_time and/or --max_iterations.')
parser.add_argument('-s', '--sleep_time', required=False, default=None, type=int,
                    help='the time in seconds for which the script will pause in beetween two imports')
parser.add_argument('-m', '--max_iterations', required=False, default=None, type=int,
                    help='the maximum number of imports that should be performed')

########################################################################################################################


def get_results_from_firebase():
    firebase = firebase_admin_auth()
    fb_db = firebase.database()
    results = fb_db.child("results").get().val()
    return results

def delete_results_in_firebase(task_id, child_id):
    firebase = firebase_admin_auth()
    fb_db = firebase.database()
    fb_db.child("results").child(task_id).child(child_id).remove()

def save_to_database(data):
    m_con = mysqlDB()

    task_id = data["id"]
    user_id = data["user"]
    project_id = int(data["projectId"])
    timestamp = int(data["timestamp"])
    result = int(data["result"])
    wkt = data["wkt"]
    task_x = data["id"].split('-')[1]
    task_y = data["id"].split('-')[2]
    task_z = data["id"].split('-')[0]
    duplicates = 0

    sql_insert = "INSERT INTO results Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    data = [str(task_id), str(user_id), int(project_id), int(timestamp), int(result), str(wkt), str(task_x),
            str(task_y), str(task_z), int(duplicates)]
    # insert in table
    m_con.query(sql_insert, data)
    del m_con

def data_transfer(q):

    while not q.empty():
        task_id, child_id, data = q.get()

        try:
            save_to_database(data)
            delete_results_in_firebase(task_id, child_id)
            #print('entry in mysql imported and deleted the following entry already.')
            #print(task_id, child_id, data)
            logging.info('entry in mysql imported and deleted the following entry already.')
            logging.info('task_id: %s, child_id: %s' % (task_id, child_id))
            q.task_done()

        except pymysql.err.IntegrityError as e:
            # we need to catch duplicate entries, 1062 --> "duplicate entry"
            if e.args[0] == 1062:
                print('Duplicate entry in mysql not imported. Will delete the following entry now.')
                print(task_id, child_id, data)
                logging.warning('Duplicate entry in mysql not imported. Will delete the following entry now.')
                logging.warning('task_id: %s, child_id: %s' % (task_id, child_id))
                delete_results_in_firebase(task_id, child_id)
                q.task_done()
        except:
            print('error during data transfer. Do nothing.')
            print(sys.exc_info())
            logging.warning('error during data transfer. Do nothing.')
            logging.warning(sys.exc_info())
            q.task_done()

def transfer_results(results_filename, all_results):
    print('there are %s results to transfer.' % len(all_results))
    logging.warning('there are %s results to transfer.' % len(all_results))


    # we will use a queue to limit the number of threads running in parallel
    q = Queue(maxsize=0)
    num_threads = 8

    for task_id, results in all_results.items():
        # there might be several results for a task_id
        for child_id, result in results.items():
            # each result has a user_id and data
            data = result['data']
            q.put([task_id, child_id, data])

    print('added all results to queue')
    logging.warning('added all results to queue')

    for i in range(num_threads):
        worker = threading.Thread(
            target=data_transfer,
            args=(q,))
        worker.start()

    q.join()

    print('transfered all results from firebase to mysql')
    logging.warning('transfered all results from firebase to mysql')



def run_transfer_results():

    logging.basicConfig(filename='transfer_results.log',
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # first check if we have results stored locally, that have not been inserted in MySQL
    results_filename = 'results.json'
    if os.path.isfile(results_filename):
        logging.warning("there are results in %s that we didnt't insert. do it now!" % results_filename)
        print("there are results in %s, that we didnt't insert. do it now!" % results_filename)
        # start to import the old results first
        with open(results_filename) as results_file:
            results = json.load(results_file)
            transfer_results(results_filename, results)

        os.remove(results_filename)
        print('removed "results.json" file')
        logging.warning('removed "results.json" file')

    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # this tries to set the max pool connections to 100
    adapter = requests.adapters.HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
    for scheme in ('http://', 'https://'):
        fb_db.requests.mount(scheme, adapter)


    # download all results and save as in json file to avoid data loss when script fails
    all_results = fb_db.child("results").get().val()
    del fb_db

    print('downloaded all results from firebase')
    logging.warning('downloaded all results from firebase')
    # test if there are any results to transfer
    if all_results:
        with open(results_filename, 'w') as fp:
            json.dump(all_results, fp)
            logging.warning('wrote results data to %s' % results_filename)
            print('wrote results data to %s' % results_filename)

        transfer_results(results_filename, all_results)
        os.remove(results_filename)
        print('removed "results.json" file')
        logging.warning('removed "results.json" file')
    else:
        logging.warning('there are no results to transfer in firebase')
        print('there are no results to transfer in firebase')


########################################################################################################################
if __name__ == '__main__':

    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

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

        # this runs the script and sends an email if an error happens within the execution
        try:
            run_transfer_results()
        except Exception as error:
            error_handling.send_error(error, 'transfer_results.py')

        # check if the script should be looped
        if args.loop:
            if args.max_iterations > counter:
                counter = counter + 1
                print('import finished. will pause for %s seconds' % args.sleep_time)
                x = 1
                time.sleep(args.sleep_time)
            else:
                x = 0
                # print('import finished and max iterations reached. stop here.')
                print('import finished and max iterations reached. sleeping now.')
                time.sleep(args.sleep_time)
        # the script should run only once
        else:
            print("Don't loop. Stop after the first run.")
            x = 0
