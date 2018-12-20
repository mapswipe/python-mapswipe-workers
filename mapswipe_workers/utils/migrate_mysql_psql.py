#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
from mapswipe_workers.basic import auth
from psycopg2 import sql


def setup_mysql_fdw(postgres):
    p_con = postgres()

    mysql_properties = auth.CONFIG['mysql']
    mysql_properties['port'] = '3306'
    mysql_properties = [mysql_properties['host'], mysql_properties['port'], mysql_properties['username'],
                        mysql_properties['password']]

    sql_string = '''
    CREATE EXTENSION IF NOT EXISTS mysql_fdw;
    
    --remote connection
    CREATE SERVER mysql_server FOREIGN DATA WRAPPER mysql_fdw
    OPTIONS (host '%s', port '%s');
    
    --mapping of local user to remote user
    CREATE USER MAPPING FOR "%s" SERVER mysql_server OPTIONS (username '%s', password '%s');
    
    --schema for remote tables
    CREATE SCHEMA mysql;
    -- import of schema + tables tables
    IMPORT FOREIGN SCHEMA "mapswipe" from server mysql_server into mysql;
    
    --show search_path;
    -- otherwise schema has to be called when querying tabls like: FROM mysql.results
    --set search_path= 'mapswipe';
    ''' % (mysql_properties[0], mysql_properties[1], mysql_properties[2], mysql_properties[2], mysql_properties[3])
    print(sql_string)

    # create table
    p_con.query(sql_string, None)

    print('established mysql fdw on our postgres db')

    del p_con


def check_mysql_schema(postgres) -> bool:
    p_con = postgres()

    sql_string = '''
    SELECT
        schema_name
    FROM
        information_schema.schemata
    '''

    schemas = p_con.retr_query(sql_string, None)

    del p_con

    return 'mysql' in schemas[-1][0]


def get_projects(postgres):
    p_con = postgres()

    sql_string = '''
        SELECT
            count(*)
        FROM
            {}.projects
        '''
    msql_string = sql.SQL(sql_string).format(sql.Identifier('mysql'))
    psql_string = sql.SQL(sql_string).format(sql.Identifier('public'))

    msql_projects_count = p_con.retr_query(msql_string, None)
    psql_projects_count = p_con.retr_query(psql_string, None)

    del p_con
    return msql_projects_count, psql_projects_count


def create_materialized_views(postgres):
    p_con = postgres()

    sql_string = '''
        CREATE MATERIALIZED VIEW IF NOT EXISTS public.msql_projects as (
            SELECT
                project_id
                ,1 as project_type
                ,name
                ,objective
            FROM
                mysql.projects
        );
        CREATE MATERIALIZED VIEW IF NOT EXISTS public.msql_results as (
            SELECT 
                task_id
                ,project_id
                ,user_id
                ,timestamp
                ,json_build_object('device', '', 'item', '', 'result', result, 'wkt', wkt) as info
                ,duplicates
            FROM mysql.results 
            LIMIT
                1000
        );
        '''
    p_con.query(sql_string, None)
    del p_con


def import_projects(postgres):
    p_con = postgres()

    sql_string = '''
        INSERT INTO public.projects
        SELECT
          *
          -- duplicates is set to zero by default, this will be updated on conflict only
          --,0
        FROM
          public.msql_projects;
    '''
    del p_con


def import_results(postgres):
    p_con = postgres()

    sql_string = '''
        INSERT INTO public.results
        SELECT
          *
          -- duplicates is set to zero by default, this will be updated on conflict only
          --,0
        FROM
          public.msql_results;
    '''
    del p_con


####################################################################################################
if __name__ == '__main__':

    postgres = auth.dev_psqlDB

    if not check_mysql_schema(postgres):
        setup_mysql_fdw(postgres)

    print('Projects: \nmysql: %i \npsql: %i ' % (get_projects(postgres)[0][0][0], get_projects(postgres)[1][0][0]))

    create_materialized_views(postgres)

    print('Materialized views created')
