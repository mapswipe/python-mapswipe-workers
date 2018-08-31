#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
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

def delete_groups_projects():

    firebase = firebase_admin_auth()
    fb_db = firebase.database()
    
    
    print('Deleting all groups...')
    fb_db.child("groups").remove()
    print('Done.')

    print('Deleting all projects...')
    fb_db.child("projects").remove()
    print('Done.')


if __name__ == '__main__':

    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    if args.modus == 'development':
        # we use the dev instance for testing
        from cfg.auth import dev_firebase_admin_auth as firebase_admin_auth
        print('We are using the development instance')
    elif args.modus == 'production':
        # we use the dev instance for testing
        from cfg.auth import firebase_admin_auth as firebase_admin_auth
        print('We are using the production instance')

delete_groups_projects()
