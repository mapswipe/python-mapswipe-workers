#!/usr/bin/python3
#
# Author: B. Herfort, M. Reinmuth, 2017
############################################

import pyrebase
import pymysql #handle mysql
import json
import sys


# Configuration of the firebase database
def firebase_admin_auth():
    try:
        with open('../cfg/config.cfg') as json_data_file:
            data = json.load(json_data_file)
            api_key = data['firebase']['api_key']
            auth_domain = data['firebase']['auth_domain']
            database_url = data['firebase']['database_url']
            storage_bucket = data['firebase']['storage_bucket']
            service_account = data['firebase']['service_account']
            # print('use configuration for psql as provided by config.json')
    except:
        # Default Configuration
        print('could not get firebase informtaion from config file')
        sys.exit()

    # adapt this to your firebase setting
    config = {
        "apiKey": api_key,
        "authDomain": auth_domain,
        "databaseURL": database_url,
        "storageBucket": storage_bucket,
        # this is important if you want to login as admin
        "serviceAccount": service_account
    }
    firebase = pyrebase.initialize_app(config)
    return firebase

def dev_firebase_admin_auth():
    try:
        with open('../cfg/config.cfg') as json_data_file:
            data = json.load(json_data_file)
            api_key = data['dev_firebase']['api_key']
            auth_domain = data['dev_firebase']['auth_domain']
            database_url = data['dev_firebase']['database_url']
            storage_bucket = data['dev_firebase']['storage_bucket']
            service_account = data['dev_firebase']['service_account']
    except:
        # Default Configuration
        print('could not get firebase dev information from config file')
        sys.exit()

    # adapt this to your firebase setting
    config = {
        "apiKey": api_key,
        "authDomain": auth_domain,
        "databaseURL": database_url,
        "storageBucket": storage_bucket,
        # this is important if you want to login as admin
        "serviceAccount": service_account
    }

    print('use dev configuration: %s' % config)

    firebase = pyrebase.initialize_app(config)
    return firebase


# get the api_key
def get_api_key(tileserver):
    try:
        with open('../cfg/config.cfg') as json_data_file:
            data = json.load(json_data_file)
            api_key = data['imagery'][tileserver]
            return api_key
    except:
        print("Something is wrong with your API key."
              "Do you even have an API key?")
        sys.exit()


# get the import submission_key
def get_submission_key():
    try:
        with open('../cfg/config.cfg') as json_data_file:
            data = json.load(json_data_file)
            submission_key = data['import']['submission_key']
            return submission_key
    except:
        print('we could not load submission key info the config file')
        sys.exit()


class mysqlDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        # try to load configuration from config file
        try:
            with open('../cfg/config.cfg') as json_data_file:
                data = json.load(json_data_file)
                dbname = data['mysql']['database']
                user = data['mysql']['username']
                password = data['mysql']['password']
                host = data['mysql']['host']
                #print('use configuration for mysql as provided by config.json')
        except:
            print('we could not load mysql info the config file')
            sys.exit()

        self._db_connection = pymysql.connect(
            database=dbname,
            user=user,
            password=password,
            host=host)

    def query(self, query, data):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        self._db_connection.commit()
        self._db_cur.close()
        return

    def retr_query(self, query, data):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        content = self._db_cur.fetchall()
        self._db_connection.commit()
        self._db_cur.close()
        return content

    def __del__(self):
        #self._db_cur.close()
        self._db_connection.close()


class dev_mysqlDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        # try to load configuration from config file
        try:
            with open('../cfg/config.cfg') as json_data_file:
                data = json.load(json_data_file)
                dbname = data['dev_mysql']['database']
                user = data['dev_mysql']['username']
                password = data['dev_mysql']['password']
                host = data['dev_mysql']['host']
                #print('use configuration for mysql as provided by config.json')
        except:
            # Default configuration
            print('we could not load mysql dev info from the config file')
            sys.exit()


        self._db_connection = pymysql.connect(
            database=dbname,
            user=user,
            password=password,
            host=host)

    def query(self, query, data):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        self._db_connection.commit()
        self._db_cur.close()
        return

    def retr_query(self, query, data):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        content = self._db_cur.fetchall()
        self._db_connection.commit()
        self._db_cur.close()
        return content

    def __del__(self):
        #self._db_cur.close()
        self._db_connection.close()
