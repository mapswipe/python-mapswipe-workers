class BaseGroup(object):
    def __init__(self, project, group_id):
        # set basic group information, make sure to spell exactly as represented in firebase and consumed by the app
        # projectId is a string in firebase
        self.projectId = project.id
        self.id = group_id
        self.completedCount = 0
        #self.reportCount = 0 # not sure for what the reportCount is used
        self.neededCount = project.verification_count
        #self.distributedCount = 0 # not sure for what the distributedCount is used
        self.count = 0
        self.users = []

    def to_dict(self):
        group = vars(self)
        for task_id, task in group['tasks'].items():
            group['tasks'][task_id] = vars(task)
        return group
