from typing import List

from mapswipe_workers.project_types.base.task import BaseTask


class Task(BaseTask):
    def __init__(self, group: object, task_id: int, media_list: List):
        task_id_unique = "t{}-{}".format(task_id, group.groupId)
        super().__init__(group, taskId=task_id_unique)
        self.media = media_list.pop(0)
        self.geometry = None  # Needed for postgres schema
