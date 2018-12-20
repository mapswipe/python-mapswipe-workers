#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
from mapswipe_workers.basic import auth

def create_projects_table(postgres):

    p_con = postgres()

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
    p_con.query(sql_string, None)

    print('created projects table')

    del p_con

def create_tasks_table(postgres):

    p_con = postgres()

    sql_string = """
        CREATE TABLE IF NOT EXISTS tasks (
        task_id varchar
        ,group_id int
        ,project_id int
        ,info json
        ,CONSTRAINT tasks_pkey PRIMARY KEY(task_id, group_id, project_id)
        );
        """

    p_con.query(sql_string, None)

    print('created tasks table')

    del p_con

def create_results_table(postgres):

    p_con = postgres()

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
    p_con.query(sql_string, None)

    print('created results table')

    del p_con

def setup_database_tables():
    postgres = auth.dev_psqlDB

    # create projects table
    create_projects_table(postgres)

    # create tasks table
    create_tasks_table(postgres)

    # create results table
    create_results_table(postgres)

    # close db connection
    del postgres

####################################################################################################

if __name__ == '__main__':
    setup_database_tables()
