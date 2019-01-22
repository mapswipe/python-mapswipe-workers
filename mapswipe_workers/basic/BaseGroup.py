class BaseGroup(object):
    """
        The basic class for a group

        Attributes
        ----------
        projectId : int
            The id of the project the group is associated with
        completedCount: int
            Number of users who finished the group
        neededCount: int
            Required number of users left to finish the group. Decreases with the increase of completedCount
        count: int
             Number of tasks associated with the group

    """
    def __init__(self, project, group_id):
        # set basic group information, make sure to spell exactly as represented in firebase and consumed by the app
        # projectId is a string in firebase
        self.projectId = project.id
        self.id = group_id
        self.completedCount = 0
        #self.reportCount = 0 # not sure for what the reportCount is used
        self.neededCount = project.verification_count
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
