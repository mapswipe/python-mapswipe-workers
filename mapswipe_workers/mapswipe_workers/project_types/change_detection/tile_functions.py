import math
import ogr


class Point:
    """
    The basic class point representing a Pixel
    Attributes
    ----------
    x : int
        x coordinate
    y : int
        y coordinate
    """

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Tile:
    """
    The basic class tile representing a TMS tile

    Attributes
    ----------
    x : int
        x coordinate
    y : int
        y coordinate
    """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


def lat_long_zoom_to_pixel_coords(lat, lon, zoom):
    """
    The function to compute pixel coordinates from lat-long point at a given zoom level

    Parameters
    ----------
    lat : float
        latitude in degree
    lon : float
        longitude in degree
    zoom : int
        tile map service zoom level

    Returns
    -------
    p : Point
    """

    p = Point()
    sinLat = math.sin(lat * math.pi / 180.0)
    x = ((lon + 180) / 360) * 256 * math.pow(2, zoom)
    y = (
        (0.5 - math.log((1 + sinLat) / (1 - sinLat)) / (4 * math.pi))
        * 256
        * math.pow(2, zoom)
    )
    p.x = int(math.floor(x))
    p.y = int(math.floor(y))
    return p


def pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom):
    """
    The function to compute latitude, longituted from pixel coordinates at a given zoom level

    Parameters
    ----------
    PixelX : int
        x coordinate
    PixelY : int
        y coordinate
    zoom : int
        tile map service zoom level

    Returns
    -------
    lon : float
        the longitude in degree
    lat : float
        the latitude in degree
    """

    MapSize = 256 * math.pow(2, zoom)
    x = (PixelX / MapSize) - 0.5
    y = 0.5 - (PixelY / MapSize)
    lon = 360 * x
    lat = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi

    return lon, lat


def pixel_coords_to_tile_address(PixelX, PixelY):
    """
    The function to compute a tile address from pixel coordinates of point within tile.

    Parameters
    ----------
    PixelX : int
        x coordinate
    PixelY : int
        y coordinate

    Returns
    -------
    t : Tile
    """

    t = Tile()
    t.x = int(math.floor(PixelX / 256))
    t.y = int(math.floor(PixelY / 256))
    return t


def tile_coords_zoom_and_tileserver_to_url(
    tile_x: int, tile_y: int, tile_z: int, tile_server: dict
) -> str:
    """
    The function to Create a URL for a tile based on tile coordinates, zoom and given tile server

    Parameters
    ----------
    tile_x : int
        x coordinate of tile
    tile_y : int
        y coordinate of tile
    tile_z :  int
        tile map service zoom level
    tile_server :  dict
        the tile server dictionary containing name and url

    Returns
    -------
    URL : string
        the url for the specific tile image
    """

    if tile_server["name"] == "bing":
        quadKey = tile_coords_and_zoom_to_quadKey(tile_x, tile_y, tile_z)
        url = quadKey_to_Bing_URL(quadKey, tile_server["apiKey"])
    elif tile_server["name"] == "sinergise":
        url = tile_server["url"].format(
            key=tile_server["apiKey"],
            x=tile_x,
            y=tile_y,
            z=tile_z,
            layer=tile_server["wmtsLayerName"],
        )
    elif "maxar" in tile_server["name"]:
        # maxar uses not the standard TMS tile y coordinate, but the Google tile y coordinate
        # more information here: https://www.maptiler.com/google-maps-coordinates-tile-bounds-projection/
        tile_y = int(math.pow(2, tile_z) - tile_y)
        url = tile_server["url"].format(
            key=tile_server["apiKey"], x=tile_x, y=tile_y, z=tile_z,
        )
    else:
        url = tile_server["url"].format(
            key=tile_server["apiKey"], x=tile_x, y=tile_y, z=tile_z,
        )

    return url


def tile_coords_and_zoom_to_quadKey(TileX, TileY, zoom):
    """
    The function to create a quadkey for use with certain tileservers that use them, e.g. Bing

    Parameters
    ----------
    TileX : int
         x coordinate of tile
    TileY : int
         y coordinate of tile
    zoom : int
        tile map service zoom level

    Returns
    -------
    quadKey : str
    """

    quadKey = ""
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (TileX & mask) != 0:
            digit += 1
        if (TileY & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey


def quadKey_to_Bing_URL(quadKey, api_key):
    """
    The function to create a tile image URL linking to a Bing tile server

    Parameters
    ----------
    quadKey :  str
        the quad key for Bing for the given tile
    api_key : str
        the Bing maps api key

    Returns
    -------
    tile_url : str
        the url for the specific Bing tile image
    """

    tile_url = "https://ecn.t0.tiles.virtualearth.net/tiles/a{}.jpeg?g=7505&mkt=en-US&token={}".format(
        quadKey, api_key
    )

    return tile_url


def geometry_from_tile_coords(TileX, TileY, zoom):
    """
    The function to compute the polygon geometry of a tile map service tile

    Parameters
    ----------
    TileX : int
         x coordinate of tile
    TileY : int
         y coordinate of tile
    zoom : int
        tile map service zoom level

    Returns
    -------
    wkt_geom : str
        the polygon geometry of the tile in WKT format
    """

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
