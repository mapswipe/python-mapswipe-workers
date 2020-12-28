from typing import Dict, List, Optional, Union

from osgeo import ogr

from mapswipe_workers.project_types.base.task import BaseTask


class Task(BaseTask):
    def __init__(
        self,
        group: object,
        featureId: Union[int, str],
        featureGeometry: Dict,
        center: Optional[List[float]],
        reference: Optional[int],
        screen: Optional[int],
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

        # only tasks that use Google tile map service need this
        if center:
            self.center = center

        # only tasks that are part of a tutorial need this
        if screen:
            self.screen = screen
            self.reference = reference

        # Remove projectId and groupId for tasks of Footprint project type
        del self.projectId
        del self.groupId

        # create wkt geometry from geojson
        # this geometry will be stored in postgres
        # it will be remove before storing the data in firebase
        poly = ogr.CreateGeometryFromJson(str(featureGeometry))
        wkt_geometry = poly.ExportToWkt()
        self.geometry = wkt_geometry
