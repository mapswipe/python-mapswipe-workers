from mapswipe_workers.basic import auth
from mapswipe_workers.basic import BaseFunctions as b
from mapswipe_workers.definitions import DATA_PATH

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.WARNING)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

modus = 'development'
firebase, mysqlDB = b.get_environment(modus)


#project_type = 1
#project_id = 13531
#proj = b.init_project(project_type, project_id, firebase, mysqlDB)

#proj.update_project(firebase, mysqlDB)


filter = 'active'
#filter = [13523, 13531]
project_list = b.get_projects(firebase, mysqlDB, filter)
print(len(project_list))

for proj in project_list:
    if int(proj.id) < 13520:
        proj.delete_project(firebase, mysqlDB)

'''

#for proj in project_list:
#    proj.update_project(firebase, mysqlDB)


b.run_transfer_results('development')

project_type = 1
project_id = 13547

proj = b.init_project(project_type, project_id, firebase, mysqlDB)

print(proj)

print(vars(proj))


proj.update_project(firebase, mysqlDB)
'''
'''
for project_id in [13533]:
    project_type = 1
    proj = b.init_project(project_type, project_id, firebase, mysqlDB)
    proj.delete_project(firebase, mysqlDB)
'''
