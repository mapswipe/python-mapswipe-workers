from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaTask import *
from mapswipe_workers.basic.BaseGroup import *


class BuildAreaGroup(BaseGroup):
    type = 1

    def __init__(self, project, group_id, slice):
        # super() executes fine now
        super(BuildAreaGroup, self).__init__(project, group_id)

        # add the type specific attributes
        self.zoomlevel = project.info['zoomlevel']
        self.xMax = slice['xMax']
        self.xMin = slice['xMin']
        self.yMax = slice['yMax']
        self.yMin = slice['yMin']

        # we need to add the tasks then, is this happening during init?
        self.create_tasks(project)

    def create_tasks(self, project):
        tasks = {}
        for TileX in range(int(self.xMin), int(self.xMax) + 1):
            for TileY in range(int(self.yMin), int(self.yMax) + 1):

                task = BuildAreaTask(self, project, TileX, TileY)
                tasks[task.id] = task

        self.tasks = tasks
        self.count = len(tasks)