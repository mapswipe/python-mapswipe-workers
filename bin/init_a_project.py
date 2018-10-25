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

modus = 'development'
#-firebase, mysqlDB = b.get_environment(modus)


b.run_transfer_results(modus)


'''
filter = 'active'
#filter = [13523, 13531]
output_path = 'data'
project_list = b.get_projects(firebase, mysqlDB, filter)
print(len(project_list))

#for proj in project_list:
#    proj.update_project(firebase, mysqlDB, output_path)


project_type = 1
project_id = 1056

proj = b.init_project(project_type, project_id, firebase, mysqlDB)

print(proj)

print(vars(proj))


proj.update_project(firebase, mysqlDB)
'''