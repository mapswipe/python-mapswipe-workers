from abc import ABCMeta, abstractmethod

from mapswipe_workers.definitions import logger


class BaseGroup(metaclass=ABCMeta):
    """
    The basic class for a group

    Attributes
    ----------
    projectId : int
        The id of the project the group is associated with
    id: int
        The id of the group
    completedCount: int
        Number of users who finished the group
    neededCount: int
        Required number of users left to finish the group.
        Decreases with the increase of completedCount.
    count: int
         Number of tasks associated with the group
    """

    def __init__(self, project, groupId):
        """
        The Constructor Method for a group instance

        Parameters
        ----------
        project: BaseProject object
            The project the group is associated with

        group_id: int
            The id of the group

        Returns
        -------
        object
        """
        self.groupId = groupId
        self.numberOfTasks = 0
        self.progress = 0
        self.projectId = project.projectId
        self.finishedCount = 0
        self.requiredCount = 0
        self.tasks = list()

    @abstractmethod
    def create_tasks():
        """
        Create tasks as task object for one group
        and appends those to a tasks list of the group object.

        The number of tasks has to be calculated
        and saved to the numberOfTasks attribute of the group object.
        """
        pass

    def is_valid(self):
        """Check if a group contains any tasks"""
        if self.numberOfTasks > 0:
            return True
        else:
            logger.info(f"group is not valid: {self.groupId}")
            return False
