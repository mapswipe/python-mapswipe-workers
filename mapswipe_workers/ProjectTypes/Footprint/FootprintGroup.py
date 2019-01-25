from mapswipe_workers.ProjectTypes.Footprint.FootprintTask import *
from mapswipe_workers.basic.BaseGroup import *


class FootprintGroup(BaseGroup):
    """
        The subclass of BaseGroup to specify groups of the footprint project type.
    """

    type = 2

    def __init__(self, imp, project_id,  group_id, feature_ids, feature_geometries):
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
        # super() executes fine now
        super(FootprintGroup, self).__init__(imp, project_id, group_id)
        self.create_tasks(feature_ids, feature_geometries)

    def create_tasks(self, feature_ids, feature_geometries):
        """
        The Function to create tasks for the group of the footprint project type

        Parameters
        ----------
        project: FootprintProject object
            The project the group is associated with
        feature_ids: list
            THe list of the ids of the features
        feature_geometries: list
            A list of geometries oor feature in geojson format. These consist two keys: coordinates and type.
            Coordinates of four two pair coordinates. Every coordinate pair is a vertex, representing the footprint
            of an object.
        """

        tasks = {}
        for i in range(0, len(feature_ids)):
            task = FootprintTask(self, feature_ids[i], feature_geometries[i])
            tasks[task.id] = task

        self.tasks = tasks
        self.count = len(tasks)
