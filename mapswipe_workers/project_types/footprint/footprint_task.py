from mapswipe_workers.base.base_task import BaseTask


class FootprintTask(BaseTask):
    """
        The subclass of BaseTask to specify tasks of
        the footprint project type.

        Attributes
        ----------
        task_id: int
            The id of the task
        featureId: int
            The id of the feature
        geojson: dict
            Geojson object containing the representation of the footprint.
            Coordinates consists of four two pair coordinates representing
            the footprint of an object.
    """

    def __init__(self, group, feature_id, feature_geometry):
        """
            The constructor method for a group instance of the
            footprint project type.

        Parameters
        ----------
        group: FootprintGroup object
            The group the task is associated with
        project: FootprintProject object
            The project the task is associated with
        feature_id: int
            The feature id
        feature_geometry: dict
            The geometries or feature in geojson format.
            It consist of two keys: Coordinates and type.
            Coordinates of four two pair coordinates.
            Every coordinate pair is a vertex, representing the footprint
            of an object.
        """
        taskId = '{}_{}_{}'.format(
            group.projectId, group.groupId, feature_id
        )

        super().__init__(group, task_id)
        self.featureId = feature_id
        self.geojson = feature_geometry
