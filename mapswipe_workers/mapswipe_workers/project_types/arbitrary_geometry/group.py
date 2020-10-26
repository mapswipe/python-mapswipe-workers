from typing import List

from mapswipe_workers.project_types.arbitrary_geometry.task import Task
from mapswipe_workers.project_types.base.group import BaseGroup


class Group(BaseGroup):
    def __init__(self, project: object, groupId: int) -> None:
        super().__init__(project, groupId)

    def create_tasks(
        self, feature_ids: List, feature_geometries: List, center_points: List
    ) -> None:
        """Create tasks for a group

        feature_geometries is a list of geometries or feature in geojson format.
        These consist two keys: Coordinates and type.
        Coordinates of four two pair coordinates.
        Every coordinate pair is a vertex.
        """
        for i in range(0, len(feature_ids)):
            task = Task(self, feature_ids[i], feature_geometries[i], center_points[i])
            self.tasks.append(task)
        self.numberOfTasks = len(self.tasks)
