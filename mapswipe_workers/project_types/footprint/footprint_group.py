from mapswipe_workers.project_types.footprint.footprint_task import FootprintTask
from mapswipe_workers.base.base_group import BaseGroup


class FootprintGroup(BaseGroup):
    """
        The subclass of BaseGroup to specify groups of the footprint project type.
    """

    type = 2

    def __init__(self, project,  groupId):
        """
           The Constructor Method for a group instance of the footprint project type.

        Parameters
        ----------
        project: FootprintProject object
            The project the group is associated with
        group_id:
            The id of the group
        feature_ids: int
            The id of the feature
        feature_geometries: dict
            The geometry of the feature as geojson. Consisting of two keys: coordinates and type. Coordinates
            consists of four two pair coordinates representing the footprint of an object
        """
        super().__init__(project, groupId)

    def create_tasks(self, feature_ids, feature_geometries):
        """
        The Function to create tasks for the group of the footprint project type

        Parameters
        ----------
        feature_ids: list
            THe list of the ids of the features
        feature_geometries: list
            A list of geometries oor feature in geojson format. These consist two keys: coordinates and type.
            Coordinates of four two pair coordinates. Every coordinate pair is a vertex, representing the footprint
            of an object.

        Returns
        -------
        tasks: list
        """

        tasks = {}
        for i in range(0, len(feature_ids)):
            task = FootprintTask(self, feature_ids[i], feature_geometries[i])
            self.tasks.append(task)
        self.numberOfTasks = len(tasks)
