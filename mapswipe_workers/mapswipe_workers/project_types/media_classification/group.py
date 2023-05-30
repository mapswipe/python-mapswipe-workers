from mapswipe_workers.project_types.base.project import BaseGroup
from mapswipe_workers.project_types.media_classification.task import Task


class Group(BaseGroup):
    def __init__(self, project: object, group_id: int) -> None:
        super().__init__(project, groupId=f"g{group_id}")
        self.numberOfTasks = project.groupSize

    def create_tasks(self, media_list):
        """Create tasks for a group"""
        for i in range(self.numberOfTasks):
            task = Task(self, i, media_list)
            self.tasks.append(task)
            if not media_list:
                self.numberOfTasks = i + 1
                break
