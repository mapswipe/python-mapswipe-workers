from mapswipe_workers.projects.BaseProject import *


########################################################################################################################
# A Footprint Project
class FootprintProject(BaseProject):
    type = 2

    def __init__(self, project_id):
        # super() executes fine now
        super(FootprintProject, self).__init__(project_id)

    def set_project_info(self, info):
        super(FootprintProject, self).set_project_info(info)
        self.info = {
            "tileserver_url": info['tileserver_url'],
            "input_geometries": info['input_geometries']
        }

    def create_groups(self):
        groups = {}
        # here we create the groups according to the workflow of the project type
        for i in range(0,3):
            groups[i] = FootprintGroup(self, i)
        self.groups = groups
