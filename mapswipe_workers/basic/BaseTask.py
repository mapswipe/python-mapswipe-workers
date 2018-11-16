class BaseTask(object):
    def __init__(self, group, task_id):
        # set basic group information
        self.projectId = group.projectId
        self.id = task_id

        # this will be the place for project type specific settings
        self.info = {}

    def print_task_info(self):
        attrs = vars(self)
        print(attrs)