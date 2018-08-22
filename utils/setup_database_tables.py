#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
from cfg.auth import mysqlDB as mysqlDB


def create_projects_table():
    m_con = mysqlDB()

    sql_string_create_table = """
    CREATE TABLE IF NOT EXISTS projects (
    project_id int(11)
    ,objective varchar(20)
    ,name varchar(45)
    );
    """

    sql_string_alter_table = 'ALTER TABLE projects ADD PRIMARY KEY (project_id);'


    # create table
    m_con.query(sql_string_create_table, None)
    m_con.query(sql_string_alter_table, None)

    del m_con

    print('created projects table')


def create_results_table():
    m_con = mysqlDB()

    sql_string_create_table = """
    CREATE TABLE IF NOT EXISTS results (
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
    """

    sql_string_alter_table = 'ALTER TABLE results ADD PRIMARY KEY (task_id, user_id, project_id)'

    # create table
    m_con.query(sql_string_create_table, None)
    m_con.query(sql_string_alter_table, None)

    del m_con

    print('created results table')


def setup_database_tables():
    # create projects table
    create_projects_table()

    # create results table
    create_results_table()


####################################################################################################

if __name__ == '__main__':
    setup_database_tables()
