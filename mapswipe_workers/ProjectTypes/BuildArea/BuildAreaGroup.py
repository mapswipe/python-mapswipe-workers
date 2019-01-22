from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaTask import *
from mapswipe_workers.basic.BaseGroup import *


class BuildAreaGroup(BaseGroup):
    """
        The subclass of BaseGroup to specify groups of the build area
        project type.

        Attributes
        ----------
        zoomLevel: int
            The zoom level of the defined tiled imagery server used for the project
        xMax: int
            The maximum x coordinate of the extent of the group
        xMin: int
            The minimum x coordinate of the extent of the group
        yMax: int
            The maximum y coordinate of the extent of the group
        yMin: int
            The minimum y coordinate of the extent of the group
    """
    type = 1

    def __init__(self, project, group_id, slice: dict):
        """
            The Constructor Method for a group instance of the build area project type

        Parameters
        ----------
        project: BaseProject object
            The project the group is associated with
        group_id: int
            The id of the group
        slice: dict
            The dictionary containing the spatial representation of the group as extent
            consisting of 4 values
        """
        # super() executes fine now
        super(BuildAreaGroup, self).__init__(project, group_id)

        # add the type specific attributes
        self.zoomLevel = project.info['zoomlevel']
        self.xMax = slice['xMax']
        self.xMin = slice['xMin']
        self.yMax = slice['yMax']
        self.yMin = slice['yMin']

        # we need to add the tasks then, is this happening during init?
        self.create_tasks(project)

    def create_tasks(self, project: object):
        """
        The Function to create tasks for the group of the build area project type

        Parameters
        ----------
        project: BaseProject object
            The project the group is associated with
        """
        tasks = {}
        for TileX in range(int(self.xMin), int(self.xMax) + 1):
            for TileY in range(int(self.yMin), int(self.yMax) + 1):

                task = BuildAreaTask(self, project, TileX, TileY)
                tasks[task.id] = task

        self.tasks = tasks
        self.count = len(tasks)