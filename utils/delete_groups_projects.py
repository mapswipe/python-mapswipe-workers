#!/bin/python3
# -*- coding: UTF-8 -*-
########################################################################################################################

import sys
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')
sys.path.insert(0, '../utils/')


import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-mo', '--modus', nargs='?', default='development', choices=['development', 'production'])

########################################################################################################################

def delete_groups_projects_firebase():

    firebase = firebase_admin_auth()
    fb_db = firebase.database()
    
    
    print('Deleting all groups from Firebase...')
    fb_db.child("groups").remove()
    print('Done.')

    print('Deleting all projects from Firebase...')
    fb_db.child("projects").remove()
    print('Done.')



def delete_projects_mysql():
    print('Delete all projects from MySQL...')
    try:
        m_con = mysqlDB()
        sql_insert = "DELETE FROM projects"
        m_con.query(sql_insert, None)
        del(m_con)

        print('Done')
        return True

    except Exception as e:
        print(e)
        return False

if __name__ == '__main__':

    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    if args.modus == 'development':
        # we use the dev instance for testing
        from cfg.auth import dev_firebase_admin_auth as firebase_admin_auth
        from cfg.auth import dev_mysqlDB as mysqlDB
        print('We are using the development instance')
    elif args.modus == 'production':
        # we use the dev instance for testing
        from cfg.auth import firebase_admin_auth as firebase_admin_auth
        from cfg.auth import mysqlDB as mysqlDB
        print('We are using the production instance')

delete_groups_projects_firebase()
delete_projects_mysql()
