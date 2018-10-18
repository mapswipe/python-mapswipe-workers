#!/usr/bin/env python

from mapswipe_workers.cfg import auth
from mapswipe_workers.projects import projects as p


if __name__ == '__main__':


    firebase = auth.dev_firebase_admin_auth()
    mysqlDB = auth.dev_mysqlDB

    imports = p.get_new_imports(firebase)
    project_id = 0

    for new_import in imports:
        project_id += 1
        # this will be the place, where we distinguish different project types
        proj = p.init_project(new_import['type'], project_id)
        if not proj:
            continue

        proj.import_project(new_import, firebase, mysqlDB)
        print(vars(proj))

        for group in proj.groups:
            print(vars(proj.groups[group]))