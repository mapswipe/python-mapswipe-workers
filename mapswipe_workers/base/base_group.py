from abc import ABCMeta, abstractmethod


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
            Required number of users left to finish the group. Decreases with the increase of completedCount
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
        self.completedCount = 0
        self.groupId = groupId
        self.neededCount = project.verificationCount
        self.numberOfTasks = 0
        self.progress = 0
        self.projectId = project.projectId
        self.tasks = list()
        self.verificationCount = project.verificationCount


    @abstractmethod
    def create_tasks():
        '''
        Returns
        -------
        tasks: list
        '''
        pass
