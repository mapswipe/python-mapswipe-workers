import firebase_admin
import psycopg2
from firebase_admin import credentials, db

from mapswipe_workers.definitions import CONFIG, SERVICE_ACCOUNT_KEY_PATH


def get_api_key(tileserver: str) -> str:
    if tileserver == "custom":
        return None
    else:
        return CONFIG["imagery"][tileserver]["api_key"]


def get_tileserver_url(tileserver: str) -> str:
    if tileserver == "custom":
        return None
    else:
        return CONFIG["imagery"][tileserver]["url"]


def firebaseDB() -> object:
    try:
        # Is an App instance already initialized?
        firebase_admin.get_app()
        # Return the imported Firebase Realtime Database module
        return db
    except ValueError:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        databaseName = CONFIG["firebase"]["database_name"]
        databaseURL = f"https://{databaseName}.firebaseio.com"

        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {"databaseURL": databaseURL})

        # Return the imported Firebase Realtime Database module
        return db


class postgresDB(object):
    """Helper calss for Postgres interactions"""

    _db_connection = None
    _db_cur = None

    def __init__(self):
        host = CONFIG["postgres"]["host"]
        port = CONFIG["postgres"]["port"]
        dbname = CONFIG["postgres"]["database"]
        user = CONFIG["postgres"]["username"]
        password = CONFIG["postgres"]["password"]

        self._db_connection = psycopg2.connect(
            database=dbname, user=user, password=password, host=host, port=port,
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
        self._db_connection.close()
