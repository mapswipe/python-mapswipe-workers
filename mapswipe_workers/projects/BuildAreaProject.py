from mapswipe_workers.projects.BaseProject import BaseProject
from mapswipe_workers.groups import BuildAreaGroup

########################################################################################################################
# A Build Area Project
class BuildAreaProject(BaseProject):
    type = 1

    def __init__(self, project_id):
        # super() executes fine now
        super(BuildAreaProject, self).__init__(project_id)

    def set_project_info(self, info):
        super(BuildAreaProject, self).set_project_info(info)
        self.info = {
            "tileserver": info['tileserver'],
            "zoomlevel": info['zoomlevel'],
            "extent": info['extent']
        }

    def create_groups(self):
        groups = {}
        for i in range(0,3):
            groups[i] = BuildAreaGroup.BuildAreaGroup(self, i)
        self.groups = groups