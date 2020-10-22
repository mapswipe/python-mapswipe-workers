from osgeo import ogr

from mapswipe_workers.project_types.base.task import BaseTask
from typing import List


class Task(BaseTask):
    def __init__(
        self, group: object, featureId: int, featureGeometry: dict, center: List
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
        self.center = center

        # Remove projectId and groupId for tasks of Footprint project type
        del self.projectId
        del self.groupId

        # create wkt geometry from geojson
        poly = ogr.CreateGeometryFromJson(str(featureGeometry))
        wkt_geometry = poly.ExportToWkt()
        self.geometry = wkt_geometry
