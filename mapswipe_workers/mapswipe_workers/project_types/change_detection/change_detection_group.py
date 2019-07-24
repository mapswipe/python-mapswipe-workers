from mapswipe_workers.project_types.change_detection.change_detection_task \
        import ChangeDetectionTask
from mapswipe_workers.base.base_group import BaseGroup


class ChangeDetectionGroup(BaseGroup):
    """
        The subclass of BaseGroup to specify groups of the build area
        project type.

        Attributes
        ----------
        xMax: int
            The maximum x coordinate of the extent of the group
        xMin: int
            The minimum x coordinate of the extent of the group
        yMax: int
            The maximum y coordinate of the extent of the group
        yMin: int
            The minimum y coordinate of the extent of the group
    """

    def __init__(self, project, groupId, slice):
        """
            The constructor method for a group instance of the \
                    build area project type

        Parameters
        ----------
        project: ChangeDetectionProject object
            The project the group is associated with
        group_id: int
            The id of the group
        slice: dict
            The dictionary containing the spatial representation \
            of the group as extent consisting of 4 values
        """
        super().__init__(project, groupId)
        self.xMax = slice['xMax']
        self.xMin = slice['xMin']
        self.yMax = slice['yMax']
        self.yMin = slice['yMin']

    def create_tasks(self, project):
        """
        The Function to create tasks for the group of the build \
                area project type

        Parameters
        ----------
        project: ChangeDetectionProject object
            The project the group is associated with
        """
        for TileX in range(int(self.xMin), int(self.xMax) + 1):
            for TileY in range(int(self.yMin), int(self.yMax) + 1):
                task = ChangeDetectionTask(self, project, TileX, TileY)
                self.tasks.append(task)
        self.numberOfTasks = len(self.tasks)
