#!/usr/bin/python
####################################################################################################
import argparse
import ogr
import math


parser = argparse.ArgumentParser(description="Let's get some inputs.")
parser.add_argument('-x', '--tile_x', required=True, default=0, type=int,
                    help='The x coordinate of the tile in a TMS.')
parser.add_argument('-y', '--tile_y', required=True, default=0, type=int,
                    help='The y coordinate of the tile in a TMS.')
parser.add_argument('-z', '--tile_z', required=True, default=0, type=int,
                    help='The z coordinate of the tile in a TMS.')

####################################################################################################


def geometry_from_tile_coords(TileX, TileY, TileZ):

    # Calculate lat, lon of upper left corner of tile
    PixelX = TileX * 256
    PixelY = TileY * 256
    MapSize = 256 * math.pow(2, TileZ)
    x = (PixelX / MapSize) - 0.5
    y = 0.5 - (PixelY / MapSize)
    lon_left = 360 * x
    lat_top = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi

    # Calculate lat, lon of lower right corner of tile
    PixelX = (TileX + 1) * 256
    PixelY = (TileY + 1) * 256
    MapSize = 256 * math.pow(2, TileZ)
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

    wkt_geom = poly.ExportToWkt()
    return wkt_geom

####################################################################################################


if __name__ == '__main__':

    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    wkt_geom = geometry_from_tile_coords(args.tile_x, args.tile_y, args.tile_z)
