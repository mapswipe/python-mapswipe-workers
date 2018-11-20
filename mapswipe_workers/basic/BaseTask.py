class BaseTask(object):
    def __init__(self, task_id):
        # set basic group information
        self.id = task_id

    def print_task_info(self):
        attrs = vars(self)
        print(attrs)