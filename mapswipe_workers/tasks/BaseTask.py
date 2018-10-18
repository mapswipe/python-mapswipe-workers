class BaseTask(object):
    def __init__(self, group, task_id):
        # set basic group information
        # most of this information is redundant. what to do about it?
        self.project_id = group.project_id
        self.group_id = group.id
        self.type = group.type
        self.id = task_id

        # this will be the place for project type specific settings
        self.info = {}

    def print_task_info(self):
        attrs = vars(self)
        print(attrs)