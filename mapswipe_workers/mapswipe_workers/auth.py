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
        if tileserver == "custom":
            return None
        else:
            return CONFIG["imagery"][tileserver]["api_key"]
    except KeyError:
        print(
            f"Could not find the API key for imagery tileserver "
            f"{tileserver} in {CONFIG_PATH}."
        )
        raise


def get_tileserver_url(tileserver):
    CONFIG = load_config()
    try:
        if tileserver == "custom":
            return None
        else:
            return CONFIG["imagery"][tileserver]["url"]
    except KeyError:
        print(
            "Could not find the url for imagery tileserver {} in {}.".format(
                tileserver, CONFIG_PATH
            )
        )
        raise


def init_firebase():
    try:
        # Is an App instance already initialized?
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred)


def firebaseDB():
    try:
        # Is an App instance already initialized?
        firebase_admin.get_app()
        # Return the imported Firebase Realtime Database module
        return db
    except ValueError:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        config = load_config()
        databaseName = config["firebase"]["database_name"]
        databaseURL = f"https://{databaseName}.firebaseio.com"

        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {"databaseURL": databaseURL})

        # Return the imported Firebase Realtime Database module
        return db


class postgresDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        CONFIG = load_config()
        try:
            host = CONFIG["postgres"]["host"]
            port = CONFIG["postgres"]["port"]
            dbname = CONFIG["postgres"]["database"]
            user = CONFIG["postgres"]["username"]
            password = CONFIG["postgres"]["password"]
        except KeyError:
            raise Exception(
                f"Could not load postgres credentials " f"from the configuration file"
            )

        self._db_connection = psycopg2.connect(
            database=dbname, user=user, password=password, host=host, port=port
        )

    def query(self, query, data=None):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        self._db_connection.commit()
        self._db_cur.close()

    def copy_from(self, f, table, columns):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.copy_from(f, table, columns=columns)
        self._db_connection.commit()
        self._db_cur.close()

    def copy_expert(
        self, sql, file,
    ):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.copy_expert(
            sql, file,
        )
        self._db_connection.commit()
        self._db_cur.close()

    def retr_query(self, query, data=None):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        content = self._db_cur.fetchall()
        self._db_connection.commit()
        self._db_cur.close()
        return content

    def __del__(self):
        self._db_connection.close()
