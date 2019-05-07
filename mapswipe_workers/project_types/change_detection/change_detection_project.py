import os
import ogr

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import logger
from mapswipe_workers import auth
from mapswipe_workers.base.base_project import BaseProject
from mapswipe_workers.project_types.change_detection.change_detection_group \
        import ChangeDetectionGroup
from mapswipe_workers.project_types.change_detection \
        import grouping_functions


class ChangeDetectionProject(BaseProject):
    """
    The subclass for an import of the type Footprint
    """

    projectType = 1

    def __init__(self, project_draft):
        # this will create the basis attributes
        super().__init__(project_draft)

        # set group size
        self.groupSize = 50
        self.kml = project_draft['kml']
        self.zoomLevel = int(project_draft.get('zoomLevel', 18))
        self.validate_geometries()

        # set configuration for tile servers

        self.tileServerA = vars(auth.tileServer(
            project_draft['tileServerA'].get('name', 'bing'),
            project_draft['tileServerA'].get('url', auth.get_tileserver_url(project_draft['tileServerA'].get('name', 'bing'))),
            project_draft['tileServerA'].get('apiKeyRequired'),
            project_draft['tileServerA'].get('apiKey', auth.get_api_key(project_draft['tileServerA'].get('name', 'bing'))),
            project_draft['tileServerA'].get('wmtsLayerName', None),
            project_draft['tileServerA'].get('caption', None),
            project_draft['tileServerA'].get('date', None)
        ))

        self.tileServerB = vars(auth.tileServer(
            project_draft['tileServerB'].get('name', 'bing'),
            project_draft['tileServerB'].get('url', auth.get_tileserver_url(project_draft['tileServerA'].get('name', 'bing'))),
            project_draft['tileServerB'].get('apiKeyRequired'),
            project_draft['tileServerB'].get('apiKey', auth.get_api_key(project_draft['tileServerA'].get('name', 'bing'))),
            project_draft['tileServerB'].get('wmtsLayerName', None),
            project_draft['tileServerB'].get('caption', None),
            project_draft['tileServerB'].get('date', None)
        ))

    def validate_geometries(self):
        raw_input_file = (
                f'{DATA_PATH}/input_geometries/'
                f'raw_input_{self.projectId}.kml'
                )
        # check if a 'data' folder exists and create one if not
        if not os.path.isdir('{}/input_geometries'.format(DATA_PATH)):
            os.mkdir('{}/input_geometries'.format(DATA_PATH))

        # write string to geom file
        with open(raw_input_file, 'w') as geom_file:
            geom_file.write(self.kml)

        driver = ogr.GetDriverByName('KML')
        datasource = driver.Open(raw_input_file, 0)
        layer = datasource.GetLayer()

        # check if layer is empty
        if layer.GetFeatureCount() < 1:
            logger.warning(
                    f'{self.projectId}'
                    f' - validate geometry - '
                    f'Empty file. '
                    f'No geometry is provided.'
                    )
            return False
            # check if more than 1 geometry is provided
        elif layer.GetFeatureCount() > 1:
            logger.warning(
                    f'{self.projectId}'
                    f' - validate geometry - '
                    f'Input file contains more than one geometry. '
                    f'Make sure to provide exact one input geometry.'
                    )
            return False

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                logger.warning(
                        f'{self.projectId}'
                        f' - validate geometry - '
                        f'Geometry is not valid: {geom_name}. '
                        f'Tested with IsValid() ogr method. '
                        f'Probably self-intersections.'
                        )
                return False

            # we accept only POLYGON or MULTIPOLYGON geometries
            if geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                logger.warning(
                        f'{self.projectId}'
                        f' - validate geometry - '
                        f'Invalid geometry type: {geom_name}. '
                        f'Please provide "POLYGON" or "MULTIPOLYGON"'
                        )
                return False

        del datasource
        del layer

        self.validInputGeometries = raw_input_file

        logger.info(
                f'{self.projectId}'
                f' - validate geometry - '
                f'input geometry is correct.'
                )
        return True

    def create_groups(self):
        """
        The function to create groups from the project extent
        """
        # first step get properties of each group from extent
        raw_groups = grouping_functions.extent_to_slices(
                self.validInputGeometries,
                self.zoomLevel
                )

        for group_id, slice in raw_groups.items():
            group = ChangeDetectionGroup(self, group_id, slice)
            group.create_tasks(self)
            self.groups.append(group)

        logger.info(
                f'{self.projectId}'
                f' - create_groups - '
                f'created groups dictionary'
            )
