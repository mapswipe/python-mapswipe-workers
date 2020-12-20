from typing import Dict, List

from osgeo import ogr

from mapswipe_workers.project_types.base.task import BaseTask


class Task(BaseTask):
    def __init__(
        self,
        group: object,
        featureId: int,
        featureGeometry: Dict,
        center: List,
        reference: int,
        screen: int,
    ):
        """
        Parameters
        ----------
        feature_geometry: dict
            The geometries or feature in geojson format.
            It consist of two keys: Coordinates and type.
            Coordinates of four two pair coordinates.
            Every coordinate pair is a vertex.
        """
        task_id = f"t{featureId}"
        super().__init__(group, taskId=task_id)
        self.geojson = featureGeometry

        if center is not None:
            self.center = center

        if screen is not None:
            self.screen = screen
            self.reference = reference

        # Remove projectId and groupId for tasks of Footprint project type
        del self.projectId
        del self.groupId

        # create wkt geometry from geojson
        poly = ogr.CreateGeometryFromJson(str(featureGeometry))
        wkt_geometry = poly.ExportToWkt()
        self.geometry = wkt_geometry
