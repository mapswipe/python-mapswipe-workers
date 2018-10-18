from mapswipe_workers.groups.BaseGroup import *
from mapswipe_workers.tasks.FootprintTask import *


class FootprintGroup(BaseGroup):
    type = 2

    def __init__(self, project, group_id):
        # super() executes fine now
        super(FootprintGroup, self).__init__(project, group_id)
        self.create_tasks()

    def create_tasks(self):
        tasks = {}
        for i in range(0,3):
            tasks[i] = FootprintTask(self, i)
        self.tasks = tasks