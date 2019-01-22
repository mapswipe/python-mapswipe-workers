from mapswipe_workers.ProjectTypes.Footprint.FootprintTask import *
from mapswipe_workers.basic.BaseGroup import *


class FootprintGroup(BaseGroup):

    type = 2

    def __init__(self, project, group_id, feature_ids, feature_geometries):
        # super() executes fine now
        super(FootprintGroup, self).__init__(project, group_id)
        self.create_tasks(project, feature_ids, feature_geometries)

    def create_tasks(self, project, feature_ids, feature_geometries):

        tasks = {}
        for i in range(0, len(feature_ids)):
            task = FootprintTask(self, project, feature_ids[i], feature_geometries[i])
            tasks[task.id] = task

        self.tasks = tasks
        self.count = len(tasks)
