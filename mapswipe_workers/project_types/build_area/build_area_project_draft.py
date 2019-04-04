import os
import ogr

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import logger
from mapswipe_workers.base.base_project_draft import BaseProjectDraft
from mapswipe_workers.project_types.build_area.build_area_group \
        import BuildAreaGroup
from mapswipe_workers.project_types.build_area \
        import grouping_functions


class BuildAreaProjectDraft(BaseProjectDraft):
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
        self.wmtsLayerName = project_draft.get('wmtsLayerName', None)
        self.zoomLevel = int(project_draft.get('zoomLevel', 18))

        self.validate_geometries()

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

    def create_groups(self, project):
        """
        The function to create groups from the project extent
        """
        # first step get properties of each group from extent
        raw_groups = grouping_functions.extent_to_slices(
                self.validInputGeometries,
                self.zoomLevel
                )

        for group_id, slice in raw_groups.items():
            group = BuildAreaGroup(project, group_id, slice)
            group.create_tasks(project)
            self.groups.append(group)

        logger.info(
                f'{self.projectId}'
                f' - create_groups - '
                f'created groups dictionary'
            )
