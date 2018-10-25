from mapswipe_workers.cfg import auth
from mapswipe_workers.basic import BaseFunctions as b

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.WARNING)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

firebase = auth.dev_firebase_admin_auth()
mysqlDB = auth.dev_mysqlDB

filter = 'active'
output_path = 'data'

filter = [1010, 1050]
project_list = b.get_projects(firebase, mysqlDB, filter)
print(len(project_list))

for proj in project_list:
    proj.update_project(firebase, mysqlDB, output_path)


'''
project_type = 1
project_id = 1056

proj = b.init_project(project_type, project_id, firebase, mysqlDB)

print(proj)

print(vars(proj))


proj.update_project(firebase, mysqlDB)
'''