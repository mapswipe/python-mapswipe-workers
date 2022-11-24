import os
import unittest

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from mapswipe_workers import auth
from mapswipe_workers.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDbTransactionMixin:
    test_db_name = None
    db_con = None
    db = None
    db_patcher = None
    postgresDB = None

    @classmethod
    def no_op(cls, *args, **kwargs):
        pass

    @classmethod
    def __db_query(cls, query):
        if cls.db_con is None:
            raise Exception("cls.db_con needs to be set.")
        assert cls.db_con.info.dbname == cls.test_db_name
        with cls.db_con.cursor() as cursor:
            cursor.execute(query)
        cls.db_con.commit()
        cursor.close()

    @classmethod
    def __db_rollback(cls):
        if cls.db_con is None:
            raise Exception("cls.db_con needs to be set.")
        assert cls.db_con.info.dbname == cls.test_db_name
        cls.db_con.rollback()

    @classmethod
    def _clear_all_data(cls):
        try:
            cls.__db_query(
                """
                -- temp tables
                TRUNCATE TABLE results_temp;
                TRUNCATE TABLE results_user_groups_temp;
                TRUNCATE TABLE user_groups_temp;
                TRUNCATE TABLE user_groups_user_memberships_temp;
                TRUNCATE TABLE users_temp;
                TRUNCATE TABLE user_groups_membership_logs_temp;
                -- normal tables
                TRUNCATE TABLE results CASCADE;
                TRUNCATE TABLE results_user_groups CASCADE;
                TRUNCATE TABLE tasks CASCADE;
                TRUNCATE TABLE user_groups_user_memberships CASCADE;
                TRUNCATE TABLE user_groups CASCADE;
                TRUNCATE TABLE groups CASCADE;
                TRUNCATE TABLE projects CASCADE;
                TRUNCATE TABLE users CASCADE;
                TRUNCATE TABLE user_groups_membership_logs;
            """
            )
        except psycopg2.errors.InFailedSqlTransaction:
            # Retry with rollback
            cls.__db_rollback()
            return cls._clear_all_data()

    @classmethod
    def _create_new_test_db(cls):
        cls.test_db_name = f"{POSTGRES_DB}_testdb".lower()

        # Connect with database
        # NOTE: Not using context manager because it will start a transaction.
        # https://stackoverflow.com/a/68112827/3436502
        con = psycopg2.connect(
            database=POSTGRES_DB,
            host=POSTGRES_HOST,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
        )
        # Create a new db. Drop if already exists.
        # TODO: Don't drop here, just clear the data.
        #   and DROP after all TestClass are done.
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with con.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {cls.test_db_name};")
            cursor.execute(f"CREATE DATABASE {cls.test_db_name};")
        con.commit()
        con.close()

        # Connect to newly created DB
        cls.db_con = psycopg2.connect(
            database=cls.test_db_name,
            host=POSTGRES_HOST,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
        )

        # Setup newly created DB
        with open(os.path.join(BASE_DIR, "set_up_db.sql")) as fp:
            cls.__db_query(fp.read())

        # XXX: Force overwrite main postgres DB helper methods.
        #   (To use newly creatd test db)
        cls.original_auth_db_connection = auth.postgresDB._db_connection
        cls.original_auth__del__ = auth.postgresDB.__del__
        auth.postgresDB._db_connection = cls.db_con
        auth.postgresDB.__del__ = cls.no_op
        cls.db = auth.postgresDB()

    @classmethod
    def _drop_test_db(cls):
        # Revert auth.postgresDB overwrite
        auth.postgresDB._db_connection = cls.original_auth_db_connection
        auth.postgresDB.__del__ = cls.original_auth__del__
        # Close and Drop test db.
        del cls.db
        if cls.db_con:
            cls.db_con.close()
        # Connect without db and drop
        # NOTE: Not using context manager because it will start a transaction.
        # https://stackoverflow.com/a/68112827/3436502
        con = psycopg2.connect(
            database=POSTGRES_DB,
            host=POSTGRES_HOST,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with con.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {cls.test_db_name};")
        con.commit()
        con.close()


class BaseTestCase(TestDbTransactionMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run at start of each TestCaseClass
        super().setUpClass()
        cls._create_new_test_db()

    def setUp(self):
        super().setUp()
        # Clear all data for next test*
        self._clear_all_data()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._drop_test_db()
