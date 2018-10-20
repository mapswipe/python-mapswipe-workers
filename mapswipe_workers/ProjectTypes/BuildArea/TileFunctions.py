import math
import ogr


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