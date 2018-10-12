#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################

import time
import logging

from mapswipe_workers.cfg import auth
from mapswipe_workers.export import export_projects
from mapswipe_workers.export import export_project_results
from mapswipe_workers.export import export_users_and_stats
####################################################################################################


def get_projects(firebase):
    # connect to firebase
    fb_db = firebase.database()

    project_dict = {}
    project_dict['all'] = []
    project_dict['active'] = []
    project_dict['not_finished'] = []

    # get the projects from firebase
    all_projects = fb_db.child("projects").get().val()

    for project in all_projects:
        try:
            # some project miss critical information, they will be skipped
            project_id = all_projects[project]['id']
            project_active = all_projects[project]['state']
            project_progress = all_projects[project]['progress']
        except:
            continue

        project_dict['all'].append(int(project_id))
        # projects with state=0 are active, state=3 means inactive
        if project_active == 0:
            project_dict['active'].append(project_id)
        if project_progress < 100:
            project_dict['not_finished'].append(project_id)

    return project_dict


def run_export(modus, project_selection, user_project_list, output_path):

    if modus == 'development':
        # we use the dev instance for testing
        firebase = auth.dev_firebase_admin_auth()
        print('We are using the development instance')
    elif modus == 'production':
        # we use the dev instance for testing
        firebase = auth.firebase_admin_auth()
        print('We are using the production instance')

    # get projects based on type, e.g. "all", "active", "not_finished"
    projects = get_projects(firebase)
    if project_selection == 'user_list':
        projects = user_project_list
    else:
        projects = projects[project_selection]

    export_project_results.export_project_results(modus, projects, output_path)
    export_projects.export_projects(modus, output_path)
    export_users_and_stats.export_users_and_stats(modus, output_path)