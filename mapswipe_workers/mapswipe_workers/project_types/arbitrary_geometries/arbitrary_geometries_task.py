from osgeo import ogr

from mapswipe_workers.base.base_task import BaseTask


class FootprintTask(BaseTask):
    """
        The subclass of BaseTask to specify tasks of
        the arbitrary_geometries project type.

        Attributes
        ----------
        geojson: dict
            Geojson object containing the representation of the arbitrary_geometries.
            Coordinates consists of four two pair coordinates representing
            the arbitrary_geometries of an object.
    """

    def __init__(self, group, featureId, featureGeometry):
        """
            The constructor method for a group instance of the
            arbitrary_geometries project type.

        Parameters
        ----------
        group: FootprintGroup object
            The group the task is associated with
        feature_id: int
            The feature id
        feature_geometry: dict
            The geometries or feature in geojson format.
            It consist of two keys: Coordinates and type.
            Coordinates of four two pair coordinates.
            Every coordinate pair is a vertex, representing the arbitrary_geometries
            of an object.
        """
        task_id = f"t{featureId}"
        super().__init__(group, taskId=task_id)
        self.geojson = featureGeometry

        # create wkt geometry from geojson
        poly = ogr.CreateGeometryFromJson(str(featureGeometry))
        wkt_geometry = poly.ExportToWkt()
        self.geometry = wkt_geometry
