class BaseTask(object):
    """
        The basic class for a task

        Attributes
        ----------
        id : int
            The id of the task


    """
    def __init__(self, task_id: int):
        """
            The Constructor Method for a task instance

        Parameters
        ----------
        task_id: int
            The id of the task
        """
        # set basic group information
        self.id = task_id

    def print_task_info(self):
        """
            The function to print the attributes of a task

        """
        attrs = vars(self)
        print(attrs)
