from mapswipe_workers.tasks.BaseTask import *


class BuildAreaTask(BaseTask):
    def __init__(self, group, task_id):
        # super() executes fine now
        super(BuildAreaTask, self).__init__(group, task_id)
        self.type = 1
        self.info = {
            "url": "123.png"
        }
