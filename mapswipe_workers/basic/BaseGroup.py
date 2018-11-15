class BaseGroup(object):
    def __init__(self, project, group_id):
        # set basic group information
        self.project_id = project.id
        self.id = group_id
        self.completedCount = 0
        self.neededCount = project.verification_count
        self.count = 0
        self.users = []

    def to_dict(self):
        group = vars(self)
        for task_id, task in group['tasks'].items():
            group['tasks'][task_id] = vars(task)
        return group
