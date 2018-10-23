from mapswipe_workers.basic.BaseTask import *
from mapswipe_workers.ProjectTypes.BuildArea import TileFunctions as t


class BuildAreaTask(BaseTask):
    def __init__(self, group, project, TileX, TileY):
        # the task id is composed of TileZ-TileX-TileY
        task_id = '{}-{}-{}'.format(
            project.info['zoomlevel'],
            TileX,
            TileY
        )
        super(BuildAreaTask, self).__init__(group, task_id)

        self.taskX = str(TileX)
        self.taskY = str(TileY)
        self.taskZ = str(project.info['zoomlevel'])
        self.url = t.tile_coords_zoom_and_tileserver_to_URL(
            TileX,
            TileY,
            project.info['zoomlevel'],
            project.info['tileserver'],
            project.info['api_key'],
            project.info['custom_tileserver_url']
        )

        # we no longer provide wkt geometry, you can calc using some python scripts
        # self.wkt = geometry_from_tile_coords(TileX, TileY, group.zoomlevel)
        self.wkt = ''


