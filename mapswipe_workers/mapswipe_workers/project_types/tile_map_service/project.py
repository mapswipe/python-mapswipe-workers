from abc import abstractmethod
from dataclasses import dataclass

from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.base.project import BaseGroup, BaseProject, BaseTask
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.utils import tile_functions, tile_grouping_functions
from mapswipe_workers.utils.validate_input import (
    save_geojson_to_file,
    validate_geometries,
)


@dataclass
class TileMapServiceBaseTask(BaseTask):
    taskX: int
    taskY: int
    geometry: str
    url: str


@dataclass
class TileMapServiceBaseGroup(BaseGroup):
    xMax: int
    xMin: int
    yMax: int
    yMin: int


class TileMapServiceBaseProject(BaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        # Note: this will be overwritten by validate_geometry in mapswipe_workers.py
        self.groups: dict[str, TileMapServiceBaseGroup] = {}
        self.tasks: dict[
            str, list[TileMapServiceBaseTask]
        ] = {}  # dict keys are group ids

        self.geometry = project_draft["geometry"]
        self.zoomLevel = int(project_draft.get("zoomLevel", 18))
        self.tileServer = vars(BaseTileServer(project_draft["tileServer"]))

    def validate_geometries(self):
        # TODO rename attribute validInputGeometries, it is a path to a geojson.
        self.validInputGeometries = save_geojson_to_file(self.projectId, self.geometry)
        wkt_geometry = validate_geometries(
            self.projectId, self.zoomLevel, self.validInputGeometries
        )
        return wkt_geometry

    def save_to_firebase(self, project, groups, tasks):
        self.save_project_to_firebase(project)
        self.save_groups_to_firebase(project["projectId"], groups)
        self.save_tasks_to_firebase(project["projectId"], tasks)

    def save_project_to_firebase(self, project):
        project.pop("geometry")
        firebase = Firebase()
        firebase.save_project_to_firebase(project)

    def save_groups_to_firebase(self, projectId: str, groups: list):
        firebase = Firebase()
        firebase.save_groups_to_firebase(projectId, groups)

    @abstractmethod
    def save_tasks_to_firebase(self, projectId: str, tasks: list):
        pass

    def create_groups(self):
        """Create groups for project extent."""
        # first step get properties of each group from extent
        raw_groups = tile_grouping_functions.extent_to_groups(
            self.validInputGeometries,
            self.zoomLevel,
            self.groupSize,
        )
        for group_id, raw_group in raw_groups.items():
            self.groups[group_id] = TileMapServiceBaseGroup(
                projectId=self.projectId,
                groupId=group_id,
                numberOfTasks=0,
                progress=0,
                finishedCount=0,
                requiredCount=0,
                xMax=raw_group["xMax"],
                xMin=raw_group["xMin"],
                yMax=raw_group["yMax"],
                yMin=raw_group["yMin"],
            )

    def create_tasks(self):
        if len(self.groups) == 0:
            raise ValueError("Groups needs to be created before tasks can be created.")
        for group_id, group in self.groups.items():
            self.tasks[group_id] = []
            for TileX in range(group.xMin, group.xMax + 1):
                for TileY in range(group.yMin, group.yMax + 1):
                    geometry = tile_functions.geometry_from_tile_coords(
                        TileX,
                        TileY,
                        self.zoomLevel,
                    )

                    url = tile_functions.tile_coords_zoom_and_tileserver_to_url(
                        TileX,
                        TileY,
                        self.zoomLevel,
                        self.tileServer,
                    )
                    self.tasks[group_id].append(
                        TileMapServiceBaseTask(
                            projectId=self.projectId,
                            groupId=group_id,
                            taskId="{}-{}-{}".format(self.zoomLevel, TileX, TileY),
                            taskX=TileX,
                            taskY=TileY,
                            geometry=geometry,
                            url=url,
                        )
                    )
            self.groups[group_id].numberOfTasks = len(self.tasks[group_id])