#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import sys
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')
sys.path.insert(0, '../utils/')

from math import ceil
import logging
import math
import json
import numpy as np
import os
import time
import ogr, osr
import gdal

from auth import get_api_key

import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-i', '--input_file', required=False, default=None, type=str,
                    help='the input file containning the geometry as kml, shp or geojson')
parser.add_argument('-t', '--tileserver', nargs='?', default='bing',
                    choices=['bing', 'digital_globe', 'google', 'custom'])
parser.add_argument('-z', '--zoomlevel', required=False, default=18, type=int,
                    help='the zoom level.')
parser.add_argument('-p', '--project_id', required=False, default=None, type=int,
                    help='the project id.')
parser.add_argument('-c', '--custom_tileserver_url', required=False, default=None, type=str,
                    help='the custom url with {z}, {x}, {y} placeholders')

########################################################################################################################

class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Tile:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

def lat_long_zoom_to_pixel_coords(lat, lon, zoom):
    """Create pixel coordinates from lat-long point at a given zoom level"""
    p = Point()
    sinLat = math.sin(lat * math.pi / 180.0)
    x = ((lon + 180) / 360) * 256 * math.pow(2, zoom)
    y = (0.5 - math.log((1 + sinLat) / (1 - sinLat)) /
         (4 * math.pi)) * 256 * math.pow(2, zoom)
    p.x = int(math.floor(x))
    p.y = int(math.floor(y))
    return p

def pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom):
    MapSize = 256 * math.pow(2, zoom)
    x = (PixelX / MapSize) - 0.5
    y = 0.5 - (PixelY / MapSize)
    lon = 360 * x
    lat = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi

    return lon, lat


def pixel_coords_to_tile_address(x, y):
    """Create a tile address from pixel coordinates of point within tile."""
    t = Tile()
    t.x = int(math.floor(x / 256))
    t.y = int(math.floor(y / 256))
    return t

def geometry_from_tile_coords(TileX, TileY, zoom):

    # Calculate lat, lon of upper left corner of tile
    PixelX = TileX * 256
    PixelY = TileY * 256
    lon_left, lat_top = pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)

    # Calculate lat, lon of lower right corner of tile
    PixelX = (TileX + 1) * 256
    PixelY = (TileY + 1) * 256
    lon_right, lat_bottom = pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)

    # Create Geometry
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(lon_left, lat_top)
    ring.AddPoint(lon_right, lat_top)
    ring.AddPoint(lon_right, lat_bottom)
    ring.AddPoint(lon_left, lat_bottom)
    ring.AddPoint(lon_left, lat_top)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    wkt_geom = poly.ExportToWkt()
    return wkt_geom


def get_geometry_from_file(infile):

    try:
        infile_name = infile.split('.')[0]
        infile_extension = infile.split('.')[-1]
    except:
        print("check input file")
        sys.exit()

    # Get the driver --> supported formats: Shapefiles, GeoJSON, kml
    if infile_extension == 'shp':
        driver = ogr.GetDriverByName('ESRI Shapefile')
    elif infile_extension == 'geojson':
        driver = ogr.GetDriverByName('GeoJSON')
    elif infile_extension == 'kml':
        driver = ogr.GetDriverByName('KML')
    else:
        print('Check input file format for ' + infile)
        print('Supported formats .shp .geojson .kml')
        sys.exit()

    datasource = driver.Open(infile, 0)
    try:
        # Get the data layer
        layer = datasource.GetLayer()
    except:
        print('Error, please check input file!')
        print('## ' + infile)
        sys.exit()

    # get feature geometry of all features of the input file
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in layer:
        geomcol.AddGeometry(feature.GetGeometryRef())

    extent = layer.GetExtent()
    logging.info('got geometry and extent from file')
    return extent, geomcol


def get_horizontal_slice(extent, geomcol, zoom):
    logging.info('geomcol: %s' % geomcol)
    slice_collection = ogr.Geometry(ogr.wkbGeometryCollection)

    xmin = extent[0]
    xmax = extent[1]
    ymin = extent[2]
    ymax = extent[3]

    # we only use the first geometry
    polygon_to_slice = geomcol.GetGeometryRef(0)
    #logging.info('polygon to slice: %s' % polygon_to_slice)

    # get upper left left tile coordinates
    pixel = lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
    tile = pixel_coords_to_tile_address(pixel.x, pixel.y)

    TileX_left = tile.x
    TileY_top = tile.y

    # get lower right tile coordinates
    pixel = lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
    tile = pixel_coords_to_tile_address(pixel.x, pixel.y)

    TileX_right = tile.x
    TileY_bottom = tile.y


    TileWidth = abs(TileX_right - TileX_left)
    TileHeight = abs(TileY_top - TileY_bottom)

    TileY = TileY_top
    TileX = TileX_left

    # get rows
    rows = int(ceil(TileHeight / 3))
    # get columns
    cols = int(ceil(TileWidth / 3))

    ############################################################

    for i in range(0, rows+1):
        # Calculate lat, lon of upper left corner of tile
        PixelX = TileX_left * 256
        PixelY = TileY * 256
        lon_left, lat_top = pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)


        PixelX = (TileX_right) * 256
        PixelY = (TileY+3) * 256
        lon_right, lat_bottom = pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)

        # Create Geometry
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(lon_left, lat_top)
        ring.AddPoint(lon_right, lat_top)
        ring.AddPoint(lon_right, lat_bottom)
        ring.AddPoint(lon_left, lat_bottom)
        ring.AddPoint(lon_left, lat_top)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        sliced_poly = poly.Intersection(polygon_to_slice)

        if sliced_poly:
            if sliced_poly.GetGeometryName() == 'POLYGON':
                slice_collection.AddGeometry(sliced_poly)
                #logging.info('sliced poly: %s' % sliced_poly)
            elif sliced_poly.GetGeometryName() == 'MULTIPOLYGON':
                for geom_part in sliced_poly:
                    slice_collection.AddGeometry(geom_part)
                    #logging.info('sliced poly: %s' % sliced_poly)
            else:
                #logging.info('sliced poly: %s' % sliced_poly)
                pass
        else:
            #logging.info('sliced poly: %s' % sliced_poly)
            pass


        #####################
        TileY = TileY + 3

    return slice_collection


def get_vertical_slice(geomcol, zoom):
    # this functions slices the horizontal stripes vertically
    # each stripe has a height of three tiles
    # the width depends on the width threshold set below
    # the final group polygon is calculated from TileX_min, TileX_max, TileY_min, TileY_max

    # the width threshold defines how "long" the groups are
    width_threshold = 70
    # create an empty dict for the group ids and TileY_min, TileY_may, TileX_min, TileX_max
    raw_groups = {}
    group_id = 100

    # add these variables to test, if groups are created correctly
    TileY_top = -1

    # process each polygon individually
    for p in range(0, geomcol.GetGeometryCount()):
        horizontal_slice = geomcol.GetGeometryRef(p)

        # sometimes we get really really small polygones, skip these
        if horizontal_slice.GetArea() < 0.0000001:
            continue
            logging.info('polygon area: %s' % horizontal_slice.GetArea())
            logging.info('skipped this polygon')

        extent = horizontal_slice.GetEnvelope()
        xmin = extent[0]
        xmax = extent[1]
        ymin = extent[2]
        ymax = extent[3]

        # get upper left left tile coordinates
        pixel = lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
        tile = pixel_coords_to_tile_address(pixel.x, pixel.y)
        TileX_left = tile.x

        # this is a fix for incorrect groups height
        # this is caused by a wrong calculation of the tile coordinates, probably because of float precision
        # previously we started with tile x and tiley -->
        # then calculated correspondinglat, lon -->
        # finally we calculated corresponding tilex and tile y again,
        # however in some rare occassion the tileY from the beginning and from the end were different
        # thats why we now don't calculate tile.y coordinates from lat, lon but use the coordinates of the upper group
        # this assumes that horizontal slices are ordered north to south
        if TileY_top < 0:
            TileY_top = tile.y
            TileY_bottom = TileY_top + 3
        else:
            TileY_top += 3
            TileY_bottom += 3

        # get lower right tile coordinates
        pixel = lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
        tile = pixel_coords_to_tile_address(pixel.x, pixel.y)
        TileX_right = tile.x

        TileWidth = abs(TileX_right - TileX_left)
        TileHeight = abs(TileY_top - TileY_bottom)

        TileX = TileX_left

        # get rows
        rows = int(ceil(TileHeight / 3))

        # get columns
        cols = int(ceil(TileWidth / width_threshold))
        # how wide should the group be, calculate from total width and do equally for all slices
        step_size = ceil(TileWidth/cols)

        for i in range(0, cols):
            # we need to make sure that geometries are not clipped at the edge
            if i == (cols-1):
                step_size = TileX_right - TileX + 1

            # Calculate lat, lon of upper left corner of tile
            PixelX = TileX * 256
            PixelY = TileY_top * 256
            lon_left, lat_top = pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)
            #logging.info('lon_left: %s, lat_top: %s' % (lon_left, lat_top))

            PixelX = (TileX + step_size) * 256
            PixelY = TileY_bottom * 256
            lon_right, lat_bottom = pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)
            #logging.info('lon_right: %s, lat_bottom: %s' % (lon_right, lat_bottom))

            # Create Geometry
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(lon_left, lat_top)
            ring.AddPoint(lon_right, lat_top)
            ring.AddPoint(lon_right, lat_bottom)
            ring.AddPoint(lon_left, lat_bottom)
            ring.AddPoint(lon_left, lat_top)
            group_poly = ogr.Geometry(ogr.wkbPolygon)
            group_poly.AddGeometry(ring)

            # add info to groups_dict
            group_id += 1
            raw_groups[group_id] = {
                "xMin": str(TileX),
                "xMax": str(TileX + step_size - 1),
                "yMin": str(TileY_top),
                "yMax": str(TileY_bottom - 1),
                "group_polygon": group_poly
            }

            #####################
            TileX = TileX + step_size

    logging.warning('created vertical_slice')
    return raw_groups


def save_geom_as_geojson(geomcol, outfile):
    wgs = osr.SpatialReference()
    wgs.ImportFromEPSG(4326)

    driver = ogr.GetDriverByName('GeoJSON')
    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)
    data_final = driver.CreateDataSource(outfile)
    layer_final = data_final.CreateLayer(outfile, wgs, geom_type=ogr.wkbPolygon)
    fdef_final = layer_final.GetLayerDefn()

    # save each polygon as feature in layer
    for p in range(0, geomcol.GetGeometryCount()):
        da = geomcol.GetGeometryRef(p)
        da.FlattenTo2D()
        if da.GetGeometryName() == 'POLYGON':
            feature_final = ogr.Feature(fdef_final)
            feature_final.SetGeometry(da)
            layer_final.CreateFeature(feature_final)
            feature_final.Destroy

        elif da.GetGeometryName() == 'MULTIPOLYGON':
            for geom_part in da:
                feature_final = ogr.Feature(fdef_final)
                feature_final.SetGeometry(geom_part)
                layer_final.CreateFeature(feature_final)
                feature_final.Destroy
        else:
            print('other geometry type: %s' % da.GetGeometryName())
            print(da)
            continue

    geomcol = None
    data_final.Destroy()


def tile_coords_zoom_and_tileserver_to_URL(TileX, TileY, zoomlevel, tileserver,
                                           api_key, custom_tileserver_url):
    """Create a URL for a tile based on tile coordinates and zoom"""
    URL = ''
    if tileserver == 'bing':
        quadKey = tile_coords_and_zoom_to_quadKey(
            int(TileX), int(TileY), int(zoomlevel))
        URL = quadKey_to_Bing_URL(quadKey, api_key)
    elif tileserver == 'digital_globe':
        URL = ("https://api.mapbox.com/v4/digitalglobe.nal0g75k/"
               "{}/{}/{}.png?access_token={}"
               .format(zoomlevel, TileX, TileY, api_key))
    elif tileserver == 'google':
        URL = ("https://mt0.google.com/vt/lyrs=s&hl=en&x={}&y={}&z={}"
               .format(TileX, TileY, zoomlevel))
    elif tileserver == 'custom':
        # don't forget the linebreak!
        URL = custom_tileserver_url.format(z=zoomlevel, x=TileX, y=TileY)
    return URL


def tile_coords_and_zoom_to_quadKey(x, y, zoom):
    """Create a quadkey for use with certain tileservers that use them."""
    quadKey = ''
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey


def quadKey_to_Bing_URL(quadKey, api_key):
    """Create a URL linking to a Bing tile server"""
    tile_url = ("http://t0.tiles.virtualearth.net/tiles/a{}.jpeg?"
                "g=854&mkt=en-US&token={}".format(quadKey, api_key))
    #print "\nThe tile URL is: {}".format(tile_url)

    return tile_url


def create_tasks(xmin, xmax, ymin, ymax, config):
    # be aware that input is tile coordinates not lat, lon
    # create dict for tasks
    tasks = {}

    for TileX in range(int(xmin), int(xmax)+1):
        for TileY in range(int(ymin), int(ymax)+1):
            task = {}
            task['id'] = '{zoom}-{taskx}-{tasky}'.format(
                zoom = config['zoom'],
                taskx = TileX,
                tasky = TileY
            )
            task['projectId'] = str(config['project_id'])
            task['taskX'] = str(TileX)
            task['taskY'] = str(TileY)
            task['taskZ'] = str(config['zoom'])

            task['url'] = tile_coords_zoom_and_tileserver_to_URL(
                    TileX, TileY, config['zoom'],
                    config['tileserver'],
                    config['api_key'],
                    config['custom_tileserver_url'])
            # we no longer provide wkt geometry, you can calc using some python scripts
            #task['wkt'] = geometry_from_tile_coords(TileX, TileY, zoom)
            task['wkt'] = ''

            tasks[task['id']] = task

    logging.info('created tasks for a group for project %s' % config['project_id'])
    return tasks


def create_groups(groups, config):
    # this function will create a json file to upload in firebase groups table

    # Create the output Driver
    outDriver = ogr.GetDriverByName('GeoJSON')
    # Create the output GeoJSON
    outfile = 'data/groups_{}.geojson'.format(config["project_id"])
    outDataSource = outDriver.CreateDataSource(outfile)
    outLayer = outDataSource.CreateLayer(outfile, geom_type=ogr.wkbPolygon)

    outLayer.CreateField(ogr.FieldDefn('project_id', ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn('group_id', ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn('xmin', ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn('xmax', ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn('ymin', ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn('ymax', ogr.OFTInteger))

    for group_id, group in groups.items():

        group_geometry = group['group_polygon']
        del group['group_polygon']

        group['zoomLevel'] = config['zoom']
        group['projectId'] = str(config['project_id'])
        group['distributedCount'] = 0
        group['completedCount'] = 0
        group['reportCount'] = 0
        group['id'] = group_id

        # get tasks for this group
        group['tasks'] = create_tasks(
            group['xMin'], group['xMax'], group['yMin'], group['yMax'], config)

        group['count'] = len(group['tasks'])

        # write to geojson file
        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(group_geometry)
        outFeature.SetField('project_id', group['projectId'])
        outFeature.SetField('group_id', group['id'])
        outFeature.SetField('xmin', group['xMin'])
        outFeature.SetField('xmax', group['xMax'])
        outFeature.SetField('ymin', group['yMin'])
        outFeature.SetField('ymax', group['yMax'])
        outLayer.CreateFeature(outFeature)
        outFeature = None

    outDataSource = None
    logging.warning('created all groups for project %s' % config['project_id'])
    return groups


def run_create_groups(input_file, project_id, tileserver, custom_tileserver_url, zoom):
    logging.basicConfig(filename='run_import.log',
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # Enable GDAL/OGR exceptions
    gdal.UseExceptions()

    # get api key for tileserver
    if tileserver != 'custom':
        api_key = get_api_key(tileserver)
    else:
        api_key = ''

    config = {
        "project_id": project_id,
        "tileserver": tileserver,
        "custom_tileserver_url": custom_tileserver_url,
        "api_key": api_key,
        "zoom": zoom
    }
    logging.warning('will use the following config: %s' % config)

    extent, geomcol = get_geometry_from_file(input_file)

    horizontal_slice = get_horizontal_slice(extent, geomcol, config['zoom'])
    #outfile = 'data/horizontally_sliced_groups_{}.geojson'.format(config["project_id"])
    #save_geom_as_geojson(horizontal_slice, outfile)

    raw_groups = get_vertical_slice(horizontal_slice, config['zoom'])

    groups = create_groups(raw_groups, config)
    outfile = 'data/groups_{}.json'.format(config["project_id"])
    # save groups as json file
    with open(outfile, 'w') as fp:
        json.dump(groups, fp)
        logging.warning('saved groups as json file for project %s' % config["project_id"])

    logging.warning('returned groups for project %s' % config["project_id"])
    return groups


########################################################################################################################

if __name__ == '__main__':

    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    run_create_groups(args.input_file, args.project_id, args.tileserver, args.custom_tileserver_url, args.zoomlevel)

