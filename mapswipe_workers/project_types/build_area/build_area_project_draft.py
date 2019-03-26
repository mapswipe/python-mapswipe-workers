import os
import logging
import ogr

from mapswipe_workers import auth
from mapswipe_workers.definitions import DATA_PATH
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
        self.tileServer = project_draft['tileServer']
        self.zoomLevel = int(project_draft.get('zoomLevel', 18))
        self.layerName = project_draft.get('layerName', None)
        try:
            self.tileServerUrl = project_draft.get(
                'tileSeverUrl',
                auth.get_tileserver_url(self.tileServer),
                )
        except KeyError:
            logging.warning(
                    f'{self.project_draft_id}'
                    f' - __init__ - no tileServerUrl is given '
                    f'and tileServer ({self.info["tileServer"]} '
                    f'is not preconfigured)'
                    )
            raise KeyError(
                    'Attribute "tileServerUrl" not provided in project_draft and '
                    'not in "auth.get_tileserver_url" function.'
                    )

        # TODO: Is every case of tileserverurl in the above statement?
        # # we need to get the tileserver_url if the tileserver is not custom
        # if ('tileServerUrl' not in self.info.keys() and
        #         self.info['tileServer'] != 'custom'):
        #     try:
        #         self.info["tileServerUrl"] = auth.get_tileserver_url(
        #                 self.info['tileServer']
        #                 )
        #     except:
        #         logging.warning(
        #                 f'{self.project_draft_id}'
        #                 f' - __init__ - no tileServerUrl is given '
        #                 f'and tileServer ({self.info["tileServer"]} '
        #                 f'is not preconfigured)'
        #                 )
        #         raise Exception(
        #                 'Attribute "tileServerUrl" not provided in project_draft and '
        #                 'not in "auth.get_tileserver_url" function.'
        #                 )

        # # we need to get the tileserver_url from the attributes
        # # if the tileserver is custom
        # elif ('tileServerUrl' not in self.info.keys() and
        #         self.info['tileServer'] == 'custom'):
        #     logging.warning(
        #             f'{self.project_draft_id}'
        #             f' - __init__ - we need a tilserver_url for the tileserver: '
        #             f'{self.infp["tileServer"]}'
        #             )
        #     raise Exception(
        #             'Attribute "tileServerUrl" not '
        #             'provided in project_draft for custom tileserver'
        #     )
        try: 
            if self.tileServer != 'custom':
                self.apiKey = auth.get_api_key(self.tileServer)
            else:
                self.apiKey = ''
        except KeyError: 
            logging.warning(
                    f'{self.project_draft_id}'
                    f' - __init__ - we need an api key for the tileserver: '
                    f'{self.info["tileServer"]}'
                    )
            raise Exception(
                    'Attribute "api_key" not provided in project_draft '
                    'and not in "auth.get_api_key" function.'
                    )

        self.validate_geometries()
        # --------------------------

        # if 'kml' not in self.info.keys():
        #     logging.warning(
        #             f'{self.project_draft_id}'
        #             f'- __init__ -  a kml geometry needs to be provided'
        #             )
        #     raise Exception('Attribute "kml" not provided in project_draft.')

        # if 'tileServer' not in self.info.keys():
        #     logging.warning(
        #             f'{self.project_draft_id}'
        #             f'- __init__ - a tilesever name needs to be provided'
        #             )
        #     raise Exception('Attribute "tileServer" not provided in project_draft.')

        # if 'zoomLevel' not in self.info.keys():
        #     logging.warning(
        #             f'{self.project_draft_id}'
        #             f'- __init__ - a zoom level needs to be provided'
        #             )
        #     self.info['zoomLevel'] = 18
        #     logging.warning(
        #             f'{self.project_draft_id}'
        #             f'- __init__ - zoom level is set to 18'
        #             )
        # else:
        #     self.info['zoomLevel'] = int(self.info['zoomLevel'])

        # # we need to get the tileserver_url if the tileserver is not custom
        # if ('tileServerUrl' not in self.info.keys() and
        #         self.info['tileServer'] != 'custom'):
        #     try:
        #         self.info["tileServerUrl"] = auth.get_tileserver_url(
        #                 self.info['tileServer']
        #                 )
        #     except:
        #         logging.warning(
        #                 f'{self.project_draft_id}'
        #                 f' - __init__ - no tileServerUrl is given '
        #                 f'and tileServer ({self.info["tileServer"]} '
        #                 f'is not preconfigured)'
        #                 )
        #         raise Exception(
        #                 'Attribute "tileServerUrl" not provided in project_draft and '
        #                 'not in "auth.get_tileserver_url" function.'
        #                 )

        # # we need to get the tileserver_url from the attributes
        # # if the tileserver is custom
        # elif ('tileServerUrl' not in self.info.keys() and
        #         self.info['tileServer'] == 'custom'):
        #     logging.warning(
        #             f'{self.project_draft_id}'
        #             f' - __init__ - we need a tilserver_url for the tileserver: '
        #             f'{self.infp["tileServer"]}'
        #             )
        #     raise Exception(
        #             'Attribute "tileServerUrl" not '
        #             'provided in project_draft for custom tileserver'
        #     )

        # if ('apiKey' not in self.info.keys() and
        #         self.info['tileServer'] != 'custom'):
        #     try:
        #         self.info['apiKey'] = auth.get_api_key(self.info['tileServer'])
        #     except:
        #         logging.warning(
        #                 f'{self.project_draft_id}'
        #                 f' - __init__ - we need an api key for the tileserver: '
        #                 f'{self.info["tileServer"]}'
        #                 )
        #         raise Exception(
        #                 'Attribute "api_key" not provided in project_draft '
        #                 'and not in "auth.get_api_key" function.'
        #                 )

        # elif ('apiKey' not in self.info.keys() and
        #         self.info['tileServer'] == 'custom'):
        #     self.info['apiKey'] = ''

        # if 'layerName' not in self.info.keys():
        #     self.info['layerName'] = None
        # self.validate_geometries()

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
            logging.warning(
                    f'{self.projectId}'
                    f' - check_input_geometry - '
                    f'Empty file. '
                    f'No geometries are provided'
                    )
            return False
            # check if more than 1 geometry is provided
        elif layer.GetFeatureCount() > 1:
            logging.warning(
                    f'{self.projectId}'
                    f' - check_input_geometry - '
                    f'Input file contains more than one geometry.'
                    f'Make sure to provide exact one input geometry.'
                    )
            return False

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                logging.warning(
                        f'{self.projectId}'
                        f' - check_input_geometry - '
                        f'Geometry is not valid: {geom_name}. '
                        f'Tested with IsValid() ogr method. '
                        f'Probably self-intersections.'
                        )
                return False

            # we accept only POLYGON or MULTIPOLYGON geometries
            if geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                logging.warning(
                        f'{self.projectId}'
                        f' - check_input_geometry - '
                        f'Invalid geometry type: {geom_name}. '
                        f'Please provide "POLYGON" or "MULTIPOLYGON"'
                        )
                return False

        del datasource
        del layer

        self.validInputGeometries = raw_input_file

        logging.warning(
                f'{self.projectId}'
                f' - check_input_geometry - '
                f'input geometry is correct.'
                )
        return True

    def create_groups(self, projectId):
        """
        The function to create groups from the project extent

        Returns
        -------
        groups : dict
            The group information containing task information
        """
        # first step get properties of each group from extent
        raw_groups = grouping_functions.extent_to_slices(
                self.validInputGeometries,
                self.zoomLevel
                )

        groups = dict()
        for group_id, slice in raw_groups.items():
            group = BuildAreaGroup(self, projectId, group_id, slice)
            groups[group.id] = group.to_dict()

        logging.warning(
                f'{self.projectId}'
                f' - create_groups - '
                f'created groups dictionary'
            )
        return groups
