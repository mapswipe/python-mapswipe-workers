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

    def __init__(self, imp: object, project_id: int, group_id: int):
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
        # set basic group information, make sure to spell exactly as represented in firebase and consumed by the app
        # projectId is a string in firebase
        self.projectId = project_id
        self.id = group_id
        self.completedCount = 0
        #self.reportCount = 0 # not sure for what the reportCount is used
        self.neededCount = imp.verification_count
        self.verificationCount = imp.verification_count
        #self.distributedCount = 0 # not sure for what the distributedCount is used
        self.count = 0

    def to_dict(self) -> dict:
        """
        The Function to convert the group object to a dictionary

        Returns
        -------
        group: dict
            Returns group attributes in a dictionary

        """
        group = vars(self)
        for task_id, task in group['tasks'].items():
            group['tasks'][task_id] = vars(task)
        return group
    
    @abstractmethod
    def create_tasks(self, imp: object):
        pass
