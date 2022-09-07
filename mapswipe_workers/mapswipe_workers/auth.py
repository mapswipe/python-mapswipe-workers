import firebase_admin
import psycopg2
from firebase_admin import db

from mapswipe_workers.config import (
    FIREBASE_DB,
    IMAGE_API_KEYS,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
from mapswipe_workers.definitions import IMAGE_URLS


def get_api_key(tileserver: str) -> str:
    if tileserver == "custom":
        return None
    else:
        return IMAGE_API_KEYS[tileserver]


def get_tileserver_url(tileserver: str) -> str:
    if tileserver == "custom":
        return None
    else:
        return IMAGE_URLS[tileserver]


def firebaseDB() -> object:
    try:
        # Is an App instance already initialized?
        firebase_admin.get_app()
        # Return the imported Firebase Realtime Database module
        return db
    except ValueError:
        databaseURL = f"https://{FIREBASE_DB}.firebaseio.com"
        # Initialize the app.
        # Credentials will be retrieved from of following environment variable:
        # GOOGLE_APPLICATION_CREDENTIALS (Path to service account key in json format)
        firebase_admin.initialize_app(options={"databaseURL": databaseURL})
        # Return the imported Firebase Realtime Database module
        return db


class postgresDB(object):
    """Helper class for Postgres interactions"""

    __db_connection = None
    _db_cur = None

    @property
    def _db_connection(self):
        if self.__db_connection is None:
            self.__db_connection = psycopg2.connect(
                database=POSTGRES_DB,
                host=POSTGRES_HOST,
                password=POSTGRES_PASSWORD,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
            )
        return self.__db_connection

    def query(self, query, data=None):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        self._db_connection.commit()
        self._db_cur.close()

    def copy_from(self, f, table, columns=None):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.copy_from(f, table, columns=columns)
        self._db_connection.commit()
        self._db_cur.close()

    def copy_expert(self, sql, file):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.copy_expert(sql, file)
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
        if self._db_connection and not self._db_connection.closed:
            self._db_connection.close()
