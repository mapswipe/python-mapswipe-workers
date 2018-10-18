from mapswipe_workers.tasks.BaseTask import *


class FootprintTask(BaseTask):
    def __init__(self, group, task_id):
        # super() executes fine now
        super(FootprintTask, self).__init__(group, task_id)
        self.type = 2
        self.info = {
            "geometry": "some polygon"
        }