from mapswipe_workers.basic.BaseTask import *


class FootprintTask(BaseTask):
    def __init__(self, group, project, feature_id, feature_geometry):
        # super() executes fine now
        task_id = '{}_{}_{}'.format(
            project.id, group.id, feature_id
        )

        super(FootprintTask, self).__init__(task_id)
        self.featureId = feature_id
        self.geojson = feature_geometry