from mapswipe_workers.base.base_task import BaseTask


class FootprintTask(BaseTask):
    """
        The subclass of BaseTask to specify tasks of
        the footprint project type.

        Attributes
        ----------
        geojson: dict
            Geojson object containing the representation of the footprint.
            Coordinates consists of four two pair coordinates representing
            the footprint of an object.
    """

    def __init__(self, group, featureId, featureGeometry):
        """
            The constructor method for a group instance of the
            footprint project type.

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
            Every coordinate pair is a vertex, representing the footprint
            of an object.
        """
        super().__init__(group, taskId=featureId)
        self.geojson = featureGeometry
