from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.base.project import BaseProject
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.tile_classification.group import (
    TileClassificationGroup,
)
from mapswipe_workers.utils import tile_grouping_functions
from mapswipe_workers.utils.validate_input import (
    save_geojson_to_file,
    validate_geometries,
)


class TileClassificationProject(BaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        # Note: this will be overwritten by validate_geometry in mapswipe_workers.py
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

    def save_project_to_firebase(self, project):
        firebase = Firebase()
        firebase.save_project_to_firebase(project)

    def save_groups_to_firebase(self, projectId: str, groups: list):
        firebase = Firebase()
        firebase.save_groups_to_firebase(projectId, groups)

    def save_tasks_to_firebase(self, projectId: str, tasks: list):
        pass

    def create_groups(self):
        """
        The function to create groups from the project extent
        """
        # first step get properties of each group from extent
        raw_groups = tile_grouping_functions.extent_to_groups(
            self.validInputGeometries, self.zoomLevel, self.groupSize
        )

        for group_id, slice in raw_groups.items():
            group = TileClassificationGroup(self, group_id, slice)
            group.create_tasks(self)

            # only append valid groups
            if group.is_valid():
                self.groups.append(group)
