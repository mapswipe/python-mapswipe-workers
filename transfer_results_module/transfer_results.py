#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import sys
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')
sys.path.insert(0, '../utils/')

import error_handling
import logging
import json
import os
import time
import requests
from auth import firebase_admin_auth
from auth import mysqlDB
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


def delete_firebase_results(all_results):
    firebase = firebase_admin_auth()
    fb_db = firebase.database()

    # we will use multilocation update to delete the entries, therefore we crate an dict with the items we want to delete
    data = {
    }

    for task_id, results in all_results.items():
        for child_id, result in results.items():
            key = 'results/{task_id}/{child_id}'.format(
                task_id=task_id,
                child_id=child_id)

            data[key] = None
            #q.put([fb_db, task_id, child_id])


    print('start deleting/ update with None')
    print(data)
    fb_db.child('results').child('test').set('this is a test')
    fb_db.update(data)
    print('finished deleting results')
    logging.warning('deleted results in firebase')

    del fb_db


def results_to_txt(all_results):
    results_txt_filename = 'raw_results.txt'
    results_txt_file = open(results_txt_filename, 'w')

    number_of_results = 0
    for task_id, results in all_results.items():
        for child_id, result in results.items():
            number_of_results += 1
            outline = '{task_id}\t{user_id}\t{project_id}\t{timestamp}\t{result}\t{wkt}\t{task_x}\t{task_y}\t{task_z}\t{duplicates}\n'.format(
                task_id = task_id,
                user_id = result['data']['user'],
                project_id = result['data']['projectId'],
                result = result['data']['result'],
                timestamp = result['data']['timestamp'],
                wkt = result['data']['wkt'],
                task_x = task_id.split('-')[1],
                task_y = task_id.split('-')[2],
                task_z = task_id.split('-')[0],
                duplicates = 0
            )

            results_txt_file.write(outline)

    results_txt_file.close()
    logging.warning('there are %s results to import' % number_of_results)
    print('there are %s results to import' % number_of_results)

    return results_txt_filename


def save_results_mysql(results_filename):
    ### this function saves the results from firebase to the mysql database

    # first import to a table where we store the geom as text
    m_con = mysqlDB()
    sql_insert = '''
        DROP TABLE IF EXISTS raw_results CASCADE;
        CREATE TABLE raw_results (
            task_id varchar(45) 
            ,user_id varchar(45) 
            ,project_id int(5) 
            ,timestamp bigint(32) 
            ,result int(1) 
            ,wkt varchar(256) 
            ,task_x varchar(45) 
            ,task_y varchar(45) 
            ,task_z varchar(45) 
            ,duplicates int(5)
        );
        '''

    m_con.query(sql_insert, None)
    print('Created new table for raw results')

    # copy data to the new table
    # we should use LOAD DATA LOCAL INFILE Syntax
    sql_insert = '''
            LOAD DATA LOCAL INFILE 'raw_results.txt' INTO TABLE raw_results
            '''
    m_con.query(sql_insert, None)
    os.remove(results_filename)
    print('copied results information to mysql')

    # second import all entries into the task table and convert into psql geometry
    sql_insert = '''
        INSERT INTO
          results
        SELECT
          *
        FROM
          raw_results
        ON DUPLICATE KEY
          UPDATE results.duplicates = results.duplicates + 1
        ;
        DROP TABLE IF EXISTS raw_results CASCADE;
    '''

    m_con.query(sql_insert, None)
    print('inserted raw results into results table and updated duplicates count')

    del m_con
    return


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
        # start to import the old results first
        with open(results_filename) as results_file:
            results = json.load(results_file)
            results_txt_filename = results_to_txt(results)
            logging.warning("there are results in %s that we didnt't insert. do it now!" % results_filename)
            save_results_mysql(results_txt_filename)
            delete_firebase_results(results)

        os.remove(results_filename)
        print('removed "results.json" file')
        logging.warning('removed "results.json" file')

    firebase = firebase_admin_auth()
    fb_db = firebase.database()
    print('opened connection to firebase')

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

        results_txt_filename = results_to_txt(all_results)

        save_results_mysql(results_txt_filename)

        delete_firebase_results(all_results)

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