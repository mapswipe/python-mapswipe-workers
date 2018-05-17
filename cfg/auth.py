#!/usr/bin/python3
#
# Author: B. Herfort, M. Reinmuth, 2017
############################################

import pyrebase
import pymysql  # handle mysql
import json
import sys

CONFIG_PATH = '../cfg/config.cfg'

try:
    with open(CONFIG_PATH) as f:
        config_data = f.read()
except IOError:
    print('Unable to load configuration file at {}. Exiting.'.format(CONFIG_PATH))
    raise

try:
    CONFIG = json.loads(config_data)
except ValueError:
    print("Unable to parse configuration file at {}, likely because of malformed JSON. Exiting.".format(CONFIG_PATH))
    raise

# Configuration of the firebase database
def firebase_admin_auth():
    try:
        api_key = CONFIG['firebase']['api_key']
        auth_domain = CONFIG['firebase']['auth_domain']
        database_url = CONFIG['firebase']['database_url']
        storage_bucket = CONFIG['firebase']['storage_bucket']
        service_account = CONFIG['firebase']['service_account']
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
        api_key = CONFIG['dev_firebase']['api_key']
        auth_domain = CONFIG['dev_firebase']['auth_domain']
        database_url = CONFIG['dev_firebase']['database_url']
        storage_bucket = CONFIG['dev_firebase']['storage_bucket']
        service_account = CONFIG['dev_firebase']['service_account']
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
        return CONFIG['imagery'][tileserver]
    except KeyError:
        print("Couldn't find the API key for imagery tileserver {} in {}".format(tileserver, CONFIG_PATH))
        raise


# get the import submission_key
def get_submission_key():
    try:
        return CONFIG['import']['submission_key']
    except KeyError:
        print("Couldn't find the submission key in {}".format(CONFIG_PATH))
        raise


class mysqlDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        # try to load configuration from config file
        try:
            dbname = CONFIG['mysql']['database']
            user = CONFIG['mysql']['username']
            password = CONFIG['mysql']['password']
            host = CONFIG['mysql']['host']
            # print('use configuration for mysql as provided by config.json')
        except:
            print('we could not load mysql info the config file')
            sys.exit()

        self._db_connection = pymysql.connect(
            database=dbname,
            user=user,
            password=password,
            host=host,
            # we need to enable this to upload files to mysql
            local_infile=True)

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
        # self._db_cur.close()
        self._db_connection.close()


class dev_mysqlDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        # try to load configuration from config file
        try:
            dbname = CONFIG['dev_mysql']['database']
            user = CONFIG['dev_mysql']['username']
            password = CONFIG['dev_mysql']['password']
            host = CONFIG['dev_mysql']['host']
            # print('use configuration for mysql as provided by config.json')
        except:
            # Default configuration
            print('we could not load mysql dev info from the config file')
            sys.exit()

        self._db_connection = pymysql.connect(
            database=dbname,
            user=user,
            password=password,
            host=host,
            # we need to enable this to upload files to mysql
            local_infile=True)

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
        # self._db_cur.close()
        self._db_connection.close()
