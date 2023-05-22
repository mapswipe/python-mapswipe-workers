from typing import Dict

from mapswipe_workers.project_types.base.group import BaseGroup
from mapswipe_workers.project_types.tile_classification.task import (
    TileClassificationTask,
)


class TileClassificationGroup(BaseGroup):
    """
    Attributes
    ----------
    xMax: int
        The maximum x coordinate of the extent of the group
    xMin: int
        The minimum x coordinate of the extent of the group
    yMax: int
        The maximum y coordinate of the extent of the group
    yMin: int
        The minimum y coordinate of the extent of the group
    """

    def __init__(self, project: object, groupId: int, _slice: Dict):
        """
        Parameters
        ----------
        _slice: dict
            The dictionary containing the spatial representation \
            of the group as extent consisting of 4 values
        """
        super().__init__(project, groupId)
        self.xMax = _slice["xMax"]
        self.xMin = _slice["xMin"]
        self.yMax = _slice["yMax"]
        self.yMin = _slice["yMin"]

    def create_tasks(self, project):
        for TileX in range(int(self.xMin), int(self.xMax) + 1):
            for TileY in range(int(self.yMin), int(self.yMax) + 1):
                task = TileClassificationTask(self, project, TileX, TileY)
                self.tasks.append(task)
        self.numberOfTasks = len(self.tasks)
