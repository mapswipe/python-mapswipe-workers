from mapswipe_workers.basic.BaseProject import BaseProject
from mapswipe_workers.ProjectTypes.Footprint.FootprintGroup import FootprintGroup


########################################################################################################################
# A Footprint Project
class FootprintProject(BaseProject):
    project_type = 2

    def __init__(self, project_id):
        # super() executes fine now
        super().__init__(project_id)

    def set_project_info(self, import_key, import_dict):
        super().set_project_info(import_key, import_dict)
        self.info = {
            "tileserver_url": import_dict['tileserver_url'],
            "input_geometries": import_dict['input_geometries']
        }

    def create_groups(self):
        groups = {}
        # here we create the groups according to the workflow of the project type
        for i in range(0,3):
            groups[i] = FootprintGroup(self, i)
        self.groups = groups
