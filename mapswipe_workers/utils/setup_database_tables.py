#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
from mapswipe_workers.basic import auth

def create_projects_table(mysqlDB):

    m_con = mysqlDB()

    sql_string = """
    CREATE TABLE IF NOT EXISTS projects (
    project_id int
    ,name varchar
    ,objective varchar
    ,project_type int
    ,CONSTRAINT projects_pkey PRIMARY KEY(project_id)
    );
    """

    # create table
    m_con.query(sql_string, None)

    print('created projects table')

    del m_con

def create_tasks_table(mysqlDB):

    m_con = mysqlDB()

    sql_string = """
        CREATE TABLE IF NOT EXISTS tasks (
        task_id varchar
        ,group_id int
        ,project_id int
        ,info json
        ,CONSTRAINT tasks_pkey PRIMARY KEY(task_id, group_id, project_id)
        );
        """

    m_con.query(sql_string, None)

    print('created tasks table')

    del m_con

def create_results_table(mysqlDB):

    m_con = mysqlDB()

    sql_string = """
    CREATE TABLE IF NOT EXISTS results (
    task_id character varying NOT NULL
    ,project_id integer NOT NULL
    ,user_id character varying NOT NULL
    ,"timestamp" bigint
    ,info json
    ,duplicates integer
    ,CONSTRAINT results_pkey PRIMARY KEY (task_id, user_id, project_id)
    );
    """

    # create table
    m_con.query(sql_string, None)

    print('created results table')

    del m_con

def setup_database_tables():
    mysqlDB = auth.dev_psqlDB

    # create projects table
    create_projects_table(mysqlDB)

    # create tasks table
    create_tasks_table(mysqlDB)

    # create results table
    create_results_table(mysqlDB)

    # close db connection
    del mysqlDB

####################################################################################################

if __name__ == '__main__':
    setup_database_tables()
