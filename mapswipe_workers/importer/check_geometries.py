#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import os
import ogr


def check_project_geometry(project):
    # this function checks whether the project geometry is valid

    if 'kml' in project.keys():
        geometry = project['kml']
        geometry_type = 'KML'
        filename = 'input.kml'
        '''
    elif 'geojson' in project.keys():
        geometry = project['geojson']
        geometry_type = 'GeoJSON'
        filename = 'input.geojson'
        '''
    # if geometry is not kml nor geojson we can't importer the project
    else:
        print('no kml or geojson geometry provided in imported project')
        return False

    # try to save the geometry to a file and open it with ogr
    try:
        # write kml string to kml file
        with open(filename, 'w') as geom_file:
            geom_file.write(geometry)

        driver = ogr.GetDriverByName(geometry_type)
        datasource = driver.Open(filename, 0)
        layer = datasource.GetLayer()
    except:
        err = ('%s geometry could not be opened with ogr.' % geometry_type)
        print(err)
        return err

    # check if layer is empty
    if layer.GetFeatureCount() < 1:
        err = 'empty file. No geometries provided'
        print(err)
        return err

    # check if more than 1 geometry is provided
    if layer.GetFeatureCount() > 1:
        err = 'Input file contains more than one geometry. Make sure to provide exact one input geometry.'
        print(err)
        return err

    # check if the input geometry is a valid polygon
    for feature in layer:
        feat_geom = feature.GetGeometryRef()
        geom_name = feat_geom.GetGeometryName()

        if not feat_geom.IsValid():
            err = 'geometry is not valid: %s. Tested with IsValid() ogr method. probably self-intersections.' % geom_name
            return err

        # we accept only POLYGON or MULTIPOLYGON geometries
        if geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
            err = 'invalid geometry type: %s. please provide "POLYGON" or "MULTIPOLYGON"' % geom_name
            print(err)
            return err

    del datasource
    del layer
    os.remove(filename)
    print('geometry is correct')
    return 'correct'


