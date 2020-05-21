from mapswipe_workers.base.base_task import BaseTask
from mapswipe_workers.utils import tile_functions as t


class TMSGridTask(BaseTask):
    """
        The subclass of BaseTask to specify tasks of the arbitrary_geometries \
                project type.

        Attributes
        ----------
        task_id: str
            The id of the task
        projectId: str
            The id of the associated BuildAreaProject
        taskX: int
            X coordinate of the respective imagery of the task
        taskY: int
            Y coordinate of the respective imagery of the task
        taskZ: int
            Zoom level of the respective imagery of the task
        url: str
            URL pointing to the respective imagery of the specified \
                    tiled imagery server
    """

    def __init__(self, group, project, TileX, TileY):
        """
            The Constructor method for a group instance of the \
                    arbitrary_geometries project type.

        Parameters
        ----------
        group: BuildAreaGroup object
            The group the task is associated with
        project: BuildAreaProject object
            The project the task is associated with
        TileX: str
            X coordinate of the imagery tile
        TileY: str
            Y coordinate of the imagery tile
        """
        # the task id is composed of TileZ-TileX-TileY
        taskId = "{}-{}-{}".format(project.zoomLevel, TileX, TileY)
        super().__init__(group, taskId)
        self.taskX = str(TileX)
        self.taskY = str(TileY)
        self.geometry = t.geometry_from_tile_coords(TileX, TileY, project.zoomLevel)

        # get TileServer for all project types
        self.url = t.tile_coords_zoom_and_tileserver_to_url(
            TileX, TileY, project.zoomLevel, project.tileServer
        )

        # get TileServer B only for change_detection or completeness type
        if project.project_type in [3, 4]:
            self.urlB = t.tile_coords_zoom_and_tileserver_to_url(
                TileX, TileY, project.zoomLevel, project.tileServerB
            )
