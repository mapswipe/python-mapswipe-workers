class BaseTask(object):
    """
        The basic class for a task

        Attributes
        ----------
        id : int
            The id of the task
    """

    def __init__(self, group, taskId):
        """
            The Constructor Method for a task instance

        Parameters
        ----------
        task_id: int
            The id of the task
        """
        # set basic group information
        self.projectId = group.projectId
        self.groupId = group.groupId
        self.taskId = taskId
