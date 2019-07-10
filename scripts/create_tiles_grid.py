#!/bin/python
# -*- coding: UTF-8 -*-
# Author: B. Herfort, 2016
############################################

import os, sys
from math import ceil
import math


class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Tile:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


def lat_long_zoom_to_pixel_coords(lat, lon, zoom):
    p = Point()
    sinLat = math.sin(lat * math.pi / 180.0)
    x = ((lon + 180) / 360) * 256 * math.pow(2, zoom)
    y = (0.5 - math.log((1 + sinLat) / (1 - sinLat)) /
         (4 * math.pi)) * 256 * math.pow(2, zoom)
    p.x = int(math.floor(x))
    p.y = int(math.floor(y))
    # print "\nThe pixel coordinates are x = {} and y = {}".format(p.x, p.y)
    return p


def pixel_coords_to_tile_address(x, y):
    t = Tile()
    t.x = int(math.floor(x / 256))
    t.y = int(math.floor(y / 256))
    # print"\nThe tile coordinates are x = {} and y = {}".format(t.x, t.y)
    return t


def create_tiles_grid(infile, zoomlevel):
    try:
        from osgeo import ogr, osr
    # print 'Import of ogr and osr from osgeo worked.  Hurray!\n'
    except:
        print('############ ERROR ######################################')
        print('## Import of ogr from osgeo failed\n\n')
        print('#########################################################')
        sys.exit()

    # Get filename and extension
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
    # open the data source
    datasource = driver.Open(infile, 0)
    try:
        # Get the data layer
        layer = datasource.GetLayer()
    except:
        print('############ ERROR ######################################')
        print('##')
        print('## Check input file!')
        print('## ' + infile)
        print('##')
        print('#########################################################')
        sys.exit()
    # Get layer definition
    layer_defn = layer.GetLayerDefn()

    # Get layer extent
    extent = layer.GetExtent()
    xmin = extent[0]
    xmax = extent[1]
    ymin = extent[2]
    ymax = extent[3]

    # get feature geometry of all features of the input file
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in layer:
        geomcol.AddGeometry(feature.GetGeometryRef())

    # get Zoomlevel
    zoom = float(zoomlevel)

    # create output file
    outputGridfn = infile_name + '_tiles.' + infile_extension

    outfile = infile_name + '_tiles.csv'
    l = 0
    if os.path.exists(outfile):
        os.remove(outfile)
    fileobj_output = open(outfile, 'w')
    fileobj_output.write('id;wkt;TileX;TileY;TileZ\n')

    outDriver = driver
    if os.path.exists(outputGridfn):
        os.remove(outputGridfn)
    outDataSource = outDriver.CreateDataSource(outputGridfn)
    outLayer = outDataSource.CreateLayer(outputGridfn, geom_type=ogr.wkbPolygon)
    featureDefn = outLayer.GetLayerDefn()

    # create fields for TileX, TileY, TileZ
    TileX_field = ogr.FieldDefn('TileX', ogr.OFTInteger)
    outLayer.CreateField(TileX_field)
    TileY_field = ogr.FieldDefn('TileY', ogr.OFTInteger)
    outLayer.CreateField(TileY_field)
    TileZ_field = ogr.FieldDefn('TileZ', ogr.OFTInteger)
    outLayer.CreateField(TileZ_field)

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

    for TileY in range(TileY_top, TileY_bottom + 1):
        for TileX in range(TileX_left, TileX_right + 1):

            # Calculate lat, lon of upper left corner of tile
            PixelX = TileX * 256
            PixelY = TileY * 256
            MapSize = 256 * math.pow(2, zoom)
            x = (PixelX / MapSize) - 0.5
            y = 0.5 - (PixelY / MapSize)
            lon_left = 360 * x
            lat_top = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi

            # Calculate lat, lon of lower right corner of tile
            PixelX = (TileX + 1) * 256
            PixelY = (TileY + 1) * 256
            MapSize = 256 * math.pow(2, zoom)
            x = (PixelX / MapSize) - 0.5
            y = 0.5 - (PixelY / MapSize)
            lon_right = 360 * x
            lat_bottom = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi

            # Create Geometry
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(lon_left, lat_top)
            ring.AddPoint(lon_right, lat_top)
            ring.AddPoint(lon_right, lat_bottom)
            ring.AddPoint(lon_left, lat_bottom)
            ring.AddPoint(lon_left, lat_top)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            # add new geom to layer

            # angepasst damit alles herunter geladen wird und nicht nur das untersuchungsgebiet

            # intersect = geomcol.Intersect(poly)

            intersect = True
            if intersect == True:
                l = l + 1
                o_line = poly.ExportToWkt()
                fileobj_output.write(
                    str(l) + ';' + o_line + ';' + str(TileX) + ';' + str(TileY) + ';' + str(zoomlevel) + '\n')

                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(poly)
                if infile_extension == 'kml':
                    col_row_zoom = str(TileX) + '_' + str(TileY) + '_' + str(int(zoom))
                    outFeature.SetField('name', col_row_zoom)
                    outFeature.SetField('description', 'TileX_TileY_TileZ')
                else:
                    outFeature.SetField('TileX', TileX)
                    outFeature.SetField('TileY', TileY)
                    outFeature.SetField('TileZ', zoom)
                outLayer.CreateFeature(outFeature)
                outFeature.Destroy

    # Close DataSources
    outDataSource.Destroy()
    fileobj_output.close()

    print('created grid from %s' % infile)


if __name__ == "__main__":

    #
    # example run : $ python create_tiles_grid.py polygon.shp 18
    #

    if len(sys.argv) != 3:
        print("[ ERROR ] you must supply 2 arguments: input-shapefile-name.shp zoomlevel")
        sys.exit(1)

    create_tiles_grid(sys.argv[1], sys.argv[2])
