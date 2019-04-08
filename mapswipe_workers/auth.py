#!/usr/bin/python3
#
# Author: B. Herfort, M. Reinmuth, 2017
############################################

import json

import psycopg2
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from mapswipe_workers.definitions import CONFIG_PATH
from mapswipe_workers.definitions import SERVICE_ACCOUNT_KEY_PATH


def load_config():
    """
    Loads the user configuration values.

    Returns
    -------
    dictonary
    """
    with open(CONFIG_PATH) as f:
        CONFIG = json.load(f)
    return CONFIG


def get_api_key(tileserver):
    CONFIG = load_config()
    try:
        return CONFIG['imagery'][tileserver]['api_key']
    except KeyError:
        print(
                f'Could not find the API key for imagery tileserver '
                f'{tileserver} in {CONFIG_PATH}.'
                )
        raise


def get_tileserver_url(tileserver):
    CONFIG = load_config()
    try:
        return CONFIG['imagery'][tileserver]['url']
    except KeyError:
        print('Could not find the url for imagery tileserver {} in {}.'.format(
            tileserver,
            CONFIG_PATH
            ))
        raise


def get_submission_key():
    CONFIG = load_config()
    try:
        return CONFIG['import']['submission_key']
    except KeyError:
        print("Couldn't find the submission key in {}".format(CONFIG_PATH))
        raise


def firebaseDB():
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    config = load_config()
    databaseURL = config['firebase']['database_url']

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': databaseURL
    })

    return db


class postgresDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        # try to load configuration from config file
        CONFIG = load_config()
        try:
            dbname = CONFIG['postgres']['database']
            user = CONFIG['postgres']['username']
            password = CONFIG['postgres']['password']
            host = CONFIG['postgres']['host']
            port = CONFIG['postgres']['port']
        except KeyError:
            # Default configuration
            raise Exception('Could not load psql info from the config file')

        self._db_connection = psycopg2.connect(
                database=dbname,
                user=user,
                password=password,
                host=host,
                port=port
                )

    def query(self, query, data):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        self._db_connection.commit()
        self._db_cur.close()

    def copy_from(
            self,
            f,
            table,
            columns
            ):
        print(f.getvalue())
        print(columns)
        self._db_cur = self._db_connection.cursor()
        self._db_cur.copy_from(
                f,
                table,
                columns=columns
                )
        self._db_connection.commit()
        print('yeah')
        self._db_cur.close()

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
