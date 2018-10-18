from mapswipe_workers.groups.BaseGroup import *
from mapswipe_workers.tasks.BuildAreaTask import *


class BuildAreaGroup(BaseGroup):
    type = 1

    def __init__(self, project, group_id):
        # super() executes fine now
        super(BuildAreaGroup, self).__init__(project, group_id)
        self.create_tasks()

    def create_tasks(self):
        tasks = {}
        for i in range(0,3):
            tasks[i] = BuildAreaTask(self, i)
        self.tasks = tasks