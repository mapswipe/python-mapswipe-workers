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

    def __init__(self, project, group_id):
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
        self.project_id = project.projectId
        self.group_id = group_id
        self.neededCount = project.verificationCount
        self.completedCount = 0
        self.verificationCount = project.verificationCount
        self.tasks = list()
        self.numberOfTasks = 0


    @abstractmethod
    def create_tasks():
        '''
        Returns
        -------
        tasks: list
        '''
        pass
