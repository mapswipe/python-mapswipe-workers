import math

from osgeo import ogr
from Typing import Dict, List

from mapswipe_workers.definitions import logger
from mapswipe_workers.utils import tile_functions as t


def get_geometry_from_file(infile: str):
    """
    The function to load input geometries from an .shp, .kml or .geojson file

    Parameters
    ----------
    infile : str
        the path to the .shp, .kml or .geojson
        file containing the input geometries

    Returns
    -------
    extent : list
        the extent of the layer as [x_min, x_max, y_min, y_max]
    geomcol : ogr.Geometry(ogr.wkbGeometryCollection)
        a geometry collection of all feature geometries for the given file
    """

    infile_extension = infile.split(".")[-1]

    # Get the driver --> supported formats: Shapefiles, GeoJSON, kml
    if infile_extension == "shp":
        driver = ogr.GetDriverByName("ESRI Shapefile")
    elif infile_extension == "geojson":
        driver = ogr.GetDriverByName("GeoJSON")
    elif infile_extension == "kml":
        driver = ogr.GetDriverByName("KML")

    datasource = driver.Open(infile, 0)

    # Get the data layer
    layer = datasource.GetLayer()

    # get feature geometry of all features of the input file
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in layer:
        geomcol.AddGeometry(feature.GetGeometryRef())

    extent = layer.GetExtent()
    logger.info("got geometry and extent from file")
    return extent, geomcol


def get_horizontal_slice(extent: List, geomcol, zoom: int):
    """
    The function slices all input geometries vertically
    using a height of max 3 tiles per geometry.
    The function iterates over all input geometries.
    For each geometry tile coordinates are calculated.
    Then this geometry is split into several geometries using the min
    and max tile coordinates for the geometry.

    Parameters
    ----------
    extent : list
        the extent of the layer as [x_min, x_max, y_min, y_max]
    geomcol : ogr.Geometry(ogr.wkbGeometryCollection)
        a geometry collection of all feature geometries for the given file
    zoom : int
        the tile map service zoom level

    Returns
    -------
    slice_infos : dict
        a dictionary containing a list of "tile_y_top" coordinates,
        a list of "tile_y_bottom" coordinates and a "slice_collection"
        containing a ogr geometry collection
    """

    slice_infos = {
        "tile_y_top": [],
        "tile_y_bottom": [],
        "slice_collection": ogr.Geometry(ogr.wkbGeometryCollection),
    }

    xmin = extent[0]
    xmax = extent[1]
    ymin = extent[2]
    ymax = extent[3]

    for i in range(0, geomcol.GetGeometryCount()):
        polygon_to_slice = geomcol.GetGeometryRef(i)
        # logging.info('polygon to slice: %s' % polygon_to_slice)'''

        # polygon_to_slice = geomcol.GetGeometryRef(0)

        # get upper left left tile coordinates
        pixel = t.lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
        tile = t.pixel_coords_to_tile_address(pixel.x, pixel.y)
        TileX_left = tile.x
        TileY_top = tile.y

        # get lower right tile coordinates
        pixel = t.lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
        tile = t.pixel_coords_to_tile_address(pixel.x, pixel.y)

        TileX_right = tile.x
        TileY_bottom = tile.y
        TileHeight = abs(TileY_top - TileY_bottom)

        TileY = TileY_top

        # get rows
        rows = int(math.ceil(TileHeight / 3))

        ############################################################

        for i in range(0, rows + 1):
            # Calculate lat, lon of upper left corner of tile
            PixelX = TileX_left * 256
            PixelY = TileY * 256
            lon_left, lat_top = t.pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)

            PixelX = TileX_right * 256
            PixelY = (TileY + 3) * 256
            lon_right, lat_bottom = t.pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)

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
                if sliced_poly.GetGeometryName() == "POLYGON":
                    slice_infos["tile_y_top"].append(TileY)
                    slice_infos["tile_y_bottom"].append(TileY + 3)
                    slice_infos["slice_collection"].AddGeometry(sliced_poly)
                elif sliced_poly.GetGeometryName() == "MULTIPOLYGON":
                    for geom_part in sliced_poly:
                        slice_infos["tile_y_top"].append(TileY)
                        slice_infos["tile_y_bottom"].append(TileY + 3)
                        slice_infos["slice_collection"].AddGeometry(geom_part)
                else:
                    pass
            else:
                pass

            TileY = TileY + 3

    return slice_infos


def get_vertical_slice(slice_infos: Dict, zoom: int, width_threshold: int = 40):
    """
    The function slices the horizontal stripes vertically.
    Each input stripe has a height of three tiles
    and will be splitted into vertical parts.
    The width of each part is defined by the width threshold set below.

    Parameters
    ----------
    slice_infos : dict
        a dictionary containing a list of "tile_y_top" coordinates,
        a list of "tile_y_bottom" coordinates
        and a "slice_collection" containing a ogr geometry collection
    zoom : int
        the tile map service zoom level
    width_threshold :  int
        the number of vertical tiles for a group,
        this defines how "long" groups are.

    Returns
    -------
    raw_groups : dict
        a dictionary containing "xMin", "xMax", "yMin", "yMax"
        and a "group_polygon" as ogr.Geometry(ogr.wkbPolygon)
        and the "group_id" as key
    """

    # create an empty dict for the group ids
    # and TileY_min, TileY_may, TileX_min, TileX_max
    raw_groups = {}
    group_id = 100

    # add these variables to test, if groups are created correctly
    TileY_top = -1

    geomcol = slice_infos["slice_collection"]

    # process each polygon individually
    for p in range(0, geomcol.GetGeometryCount()):
        horizontal_slice = geomcol.GetGeometryRef(p)

        # sometimes we get really really small polygones, skip these
        if horizontal_slice.GetArea() < 0.0000001:
            continue

        extent = horizontal_slice.GetEnvelope()
        xmin = extent[0]
        xmax = extent[1]
        ymin = extent[2]
        ymax = extent[3]

        # get upper left left tile coordinates
        pixel = t.lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
        tile = t.pixel_coords_to_tile_address(pixel.x, pixel.y)
        TileX_left = tile.x

        # get lower right tile coordinates
        pixel = t.lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
        tile = t.pixel_coords_to_tile_address(pixel.x, pixel.y)
        TileX_right = tile.x

        # we don't compute tile y top and tile y botton coordinates again,
        # but get the ones from the list
        # doing so we can avoid problems due to rounding errors
        # which result in wrong tile coordinates
        TileY_top = slice_infos["tile_y_top"][p]
        TileY_bottom = slice_infos["tile_y_bottom"][p]

        TileWidth = abs(TileX_right - TileX_left)
        TileX = TileX_left

        # get columns
        cols = int(math.ceil(TileWidth / width_threshold))
        # avoid zero division error and check if cols is smaller than zero
        if cols < 1:
            continue

        # how wide should the group be, calculate from total width
        # and do equally for all slices
        step_size = math.ceil(TileWidth / cols)

        # the step_size should be always and even number
        # this will make sure that there will be always 6 tasks per screen
        if step_size % 2 == 1:
            step_size += 1

        for i in range(0, cols):
            # we need to make sure that geometries are not clipped at the edge
            if i == (cols - 1):
                step_size = TileX_right - TileX + 1
                if step_size % 2 == 1:
                    step_size += 1

            # Calculate lat, lon of upper left corner of tile
            PixelX = TileX * 256
            PixelY = TileY_top * 256
            lon_left, lat_top = t.pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)
            # logging.info('lon_left: %s, lat_top: %s' % (lon_left, lat_top))

            PixelX = (TileX + step_size) * 256
            PixelY = TileY_bottom * 256
            lon_right, lat_bottom = t.pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)

            # TODO line 254-262 does exactly the same as in line 345-352,
            #  maybe put it in a function create_geom_from_group_coords
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
            group_id_string = f"g{group_id}"
            raw_groups[group_id_string] = {
                "xMin": str(TileX),
                "xMax": str(TileX + step_size - 1),
                "yMin": str(TileY_top),
                "yMax": str(TileY_bottom - 1),
                "group_polygon": group_poly,
            }

            TileX = TileX + step_size

    logger.info("created vertical_slice")
    return raw_groups


def groups_intersect(group_a: Dict, group_b: Dict):
    """Check if groups intersect."""
    x_max = int(group_a["xMax"])
    x_min = int(group_a["xMin"])
    y_max = int(group_a["yMax"])
    y_min = int(group_a["yMin"])

    x_maxB = int(group_b["xMax"])
    x_minB = int(group_b["xMin"])
    y_maxB = int(group_b["yMax"])
    y_minB = int(group_b["yMin"])

    return (
        (x_min <= x_maxB)
        and (x_minB <= x_max)
        and (y_min <= y_maxB)
        and (y_minB <= y_max)
    )


def merge_groups(group_a: Dict, group_b: Dict, zoom: int):
    """Merge two overlapping groups into a single group.

    This can result in groups that are "longer" than
    the groups set in the first place and they can be
    longer than the initial groupSize defined by the project
    manager.
    """

    x_max = int(group_a["xMax"])
    x_min = int(group_a["xMin"])
    y_max = int(group_a["yMax"])
    y_min = int(group_a["yMin"])

    x_maxB = int(group_b["xMax"])
    x_minB = int(group_b["xMin"])

    # if two groups overlap, merge into one group
    new_x_min = min([x_min, x_minB])
    new_x_max = max([x_max, x_maxB])

    # check if group_x_size is even and adjust new_x_max
    if (new_x_max - new_x_min + 1) % 2 == 1:
        new_x_max += 1

    # Calculate lat, lon of upper left corner of tile
    PixelX = int(new_x_min) * 256
    PixelY = (int(y_max) + 1) * 256
    lon_left, lat_top = t.pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)
    # logging.info('lon_left: %s, lat_top: %s' % (lon_left, lat_top))

    # Calculate lat, lon of bottom right corner of tile
    PixelX = (int(new_x_max) + 1) * 256
    PixelY = int(y_min) * 256
    lon_right, lat_bottom = t.pixel_coords_zoom_to_lat_lon(PixelX, PixelY, zoom)

    # Create Geometry
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(lon_left, lat_top)
    ring.AddPoint(lon_right, lat_top)
    ring.AddPoint(lon_right, lat_bottom)
    ring.AddPoint(lon_left, lat_bottom)
    ring.AddPoint(lon_left, lat_top)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    new_group = {
        "xMin": str(new_x_min),
        "xMax": str(new_x_max),
        "yMin": str(y_min),
        "yMax": str(y_max),
        "group_polygon": poly,
    }

    return new_group


def adjust_overlapping_groups(groups: Dict, zoom: int):
    """Loop through groups dict and merge overlapping groups."""

    groups_without_overlap = {}
    overlaps_total = 0

    for group_id in list(groups.keys()):

        # skip if groups has been removed already
        if group_id not in groups.keys():
            continue

        overlap_count = 0
        for group_id_b in list(groups.keys()):
            # skip if it is the same group
            if group_id_b == group_id:
                continue

            if groups_intersect(groups[group_id], groups[group_id_b]):
                overlap_count += 1
                new_group = merge_groups(groups[group_id], groups[group_id_b], zoom)
                del groups[group_id_b]
                groups_without_overlap[group_id] = new_group

        if overlap_count == 0:
            groups_without_overlap[group_id] = groups[group_id]

        del groups[group_id]
        overlaps_total += overlap_count

    logger.info(f"overlaps_total: {overlaps_total}")
    return groups_without_overlap, overlaps_total


def extent_to_groups(infile, zoom: int, groupSize):
    """
    The function to polygon geometries of a given input file
    into horizontal slices and then vertical slices.

    Parameters
    ----------
    infile : str
        the path to the .shp, .kml
        or .geojson file containing the input geometries
    zoom : int
        the tile map service zoom level

    Returns
    -------
    raw_groups_dict : dict
        a dictionary containing "xMin", "xMax", "yMin", "yMax"
        and a "group_polygon" as ogr.Geometry(ogr.wkbPolygon)
        and the "group_id" as key
    """
    extent, geomcol = get_geometry_from_file(infile)

    # get horizontal slices --> rows
    horizontal_slice_infos = get_horizontal_slice(extent, geomcol, zoom)

    # then get vertical slices --> columns
    raw_groups_dict = get_vertical_slice(horizontal_slice_infos, zoom, groupSize)

    # finally remove overlapping groups
    groups_dict, overlaps_total = adjust_overlapping_groups(raw_groups_dict, zoom)

    # check if there are still overlaps
    c = 0
    while overlaps_total > 0:
        c += 1
        # avoid that this runs forever
        if c == 5:
            break

        groups_dict, overlaps_total = adjust_overlapping_groups(
            groups_dict.copy(), zoom
        )

    return groups_dict


def vertical_groups_as_geojson(raw_group_infos: Dict, outfile: str):
    """
    The function to create a geojson file from the groups dictionary.

    Parameters
    ----------
    raw_group_infos : dict
        a dictionary containing "xMin", "xMax", "yMin", "yMax"
        and a "group_polygon" as ogr.Geometry(ogr.wkbPolygon)
        and the "group_id" as key
    outfile : str
        the path a .geojson file for storing the output

    Returns
    -------
    bool
        True if successful, False otherwise.
    """

    # Create the output Driver and the output GeoJSON
    outDriver = ogr.GetDriverByName("GeoJSON")
    # Create the output GeoJSON
    outDataSource = outDriver.CreateDataSource(outfile)
    outLayer = outDataSource.CreateLayer(outfile, geom_type=ogr.wkbPolygon)

    outLayer.CreateField(ogr.FieldDefn("group_id", ogr.OFTString))
    outLayer.CreateField(ogr.FieldDefn("xmin", ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn("xmax", ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn("ymin", ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn("ymax", ogr.OFTInteger))

    for group_id, group in raw_group_infos.items():
        # write to geojson file
        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(group["group_polygon"])
        outFeature.SetField("group_id", group_id)
        outFeature.SetField("xmin", group["xMin"])
        outFeature.SetField("xmax", group["xMax"])
        outFeature.SetField("ymin", group["yMin"])
        outFeature.SetField("ymax", group["yMax"])
        outLayer.CreateFeature(outFeature)
        outFeature = None

    outDataSource = None
    logger.info("created all %s." % outfile)

    return True


def horizontal_groups_as_geojson(slices_info: Dict, outfile: str):

    # Create the output Driver and out GeoJson
    outDriver = ogr.GetDriverByName("GeoJSON")
    # Create the output GeoJSON
    outDataSource = outDriver.CreateDataSource(outfile)
    outLayer = outDataSource.CreateLayer(outfile, geom_type=ogr.wkbPolygon)
    slices_geom = slices_info["slice_collection"]

    for group in slices_geom:
        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(group)
        outLayer.CreateFeature(outFeature)
        outFeature = None

    outDataSource = None
    logger.info("created all %s." % outfile)

    return True
