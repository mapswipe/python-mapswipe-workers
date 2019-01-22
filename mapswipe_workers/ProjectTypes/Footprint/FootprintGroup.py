from mapswipe_workers.ProjectTypes.Footprint.FootprintTask import *
from mapswipe_workers.basic.BaseGroup import *


class FootprintGroup(BaseGroup):
    """
        The subclass of BaseGroup to specify groups of the footprint project type.
    """

    type = 2

    def __init__(self, project, group_id, feature_ids, feature_geometries):
        """
           The Constructor Method for a group instance of the footprint project type.

        Parameters
        ----------
        project: BaseProject object
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
        super(FootprintGroup, self).__init__(project, group_id)
        self.create_tasks(project, feature_ids, feature_geometries)

    def create_tasks(self, project, feature_ids, feature_geometries):
        """
        The Function to create tasks for the group of the footprint project type

        Parameters
        ----------
        project: BaseProject object
            The project the group is associated with
        feature_ids: int
            The id of the feature
        feature_geometries: dict
            The geometry of the feature as geojson. Consisting of two keys: coordinates and type. Coordinates
            consists of four two pair coordinates representing the footprint of an object
        """

        tasks = {}
        for i in range(0, len(feature_ids)):
            task = FootprintTask(self, project, feature_ids[i], feature_geometries[i])
            tasks[task.id] = task

        self.tasks = tasks
        self.count = len(tasks)
