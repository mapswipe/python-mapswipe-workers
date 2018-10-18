class BaseGroup(object):
    def __init__(self, project, group_id):
        # set basic group information
        self.project_id = project.id
        self.id = group_id