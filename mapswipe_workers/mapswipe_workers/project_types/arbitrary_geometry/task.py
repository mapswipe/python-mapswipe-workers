from typing import Dict, Union

from osgeo import ogr

from mapswipe_workers.project_types.base.task import BaseTask


class Task(BaseTask):
    def __init__(
        self,
        group: object,
        featureId: Union[int, str],
        feature: Dict,
    ):
        """
        Parameters
        ----------
        feature: dict
            a Feature in geojson format.
        """
        task_id = f"t{featureId}"
        super().__init__(group, taskId=task_id)
        self.geojson = feature["geometry"]
        self.properties = feature["properties"]
        # only tasks that are part of a tutorial need this
        if "screen" in feature["properties"].keys():
            self.screen = feature["properties"]["screen"]
            self.reference = feature["properties"]["reference"]

        # Remove projectId and groupId for tasks of validate project type
        del self.projectId
        del self.groupId

        # create wkt geometry from geojson
        # this geometry will be stored in postgres
        # it will be removed before storing the data in firebase
        poly = ogr.CreateGeometryFromJson(str(self.geojson))
        wkt_geometry = poly.ExportToWkt()
        self.geometry = wkt_geometry
