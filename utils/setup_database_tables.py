#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import sys
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')

from auth import mysqlDB as mysqlDB

def create_projects_table():
    m_con = mysqlDB()

    sql_string = """
    CREATE TABLE IF NOT EXISTS projects (
    project_id int(11)
    ,objective varchar(20) 
    ,name varchar(45)
    );
    ALTER TABLE projects ADD PRIMARY KEY (project_id)
    """

    # create table
    m_con.query(sql_string, None)
    del m_con

    print('created projects table')

def create_results_table():
    m_con = mysqlDB()

    sql_string = """
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
    ALTER TABLE results ADD PRIMARY KEY (task_id, user_id, project_id)
    """

    # create table
    m_con.query(sql_string, None)
    del m_con

    print('created results table')


def setup_database_tables():
    # create projects table
    create_projects_table()

    # create results table
    create_results_table()



########################################################################################################################

if __name__ == '__main__':

    setup_database_tables()