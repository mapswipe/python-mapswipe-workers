import json
import os

from osgeo import ogr, osr

from mapswipe_workers.definitions import (
    DATA_PATH,
    MAX_INPUT_GEOMETRIES,
    CustomError,
    logger,
)


def save_geojson_to_file(project_id, geometry):
    output_file_path = (
        f"{DATA_PATH}/input_geometries/" f"raw_input_{project_id}.geojson"
    )
    # check if a 'data' folder exists and create one if not
    if not os.path.isdir("{}/input_geometries".format(DATA_PATH)):
        os.mkdir("{}/input_geometries".format(DATA_PATH))

    # write string to geom file
    with open(output_file_path, "w") as geom_file:
        json.dump(geometry, geom_file)
    return output_file_path


def check_if_layer_is_empty(projectId, layer):
    if layer.GetFeatureCount() < 1:
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Empty file. "
            f"No geometry is provided."
        )
        raise CustomError("Empty file. ")


def check_if_layer_has_too_many_geometries(projectId, multi_polygon: ogr.Geometry):
    if multi_polygon.GetGeometryCount() > MAX_INPUT_GEOMETRIES:
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Input file contains more than {MAX_INPUT_GEOMETRIES} individuals polygons."
            f"Make sure to provide less than {MAX_INPUT_GEOMETRIES} polygons."
        )
        raise CustomError(
            f"Input file contains more than {MAX_INPUT_GEOMETRIES} geometries. "
            "You can split up your project into two or more projects. "
            "This can reduce the number of input geometries. "
        )


def check_if_zoom_level_is_too_high(zoomLevel):
    if zoomLevel > 22:
        raise CustomError(f"zoom level is too large (max: 22): {zoomLevel}.")


def check_if_geom_type_is_valid(projectId, geom_name):
    # we accept only POLYGON or MULTIPOLYGON geometries
    if geom_name != "POLYGON" and geom_name != "MULTIPOLYGON":
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Invalid geometry type: {geom_name}. "
            f'Please provide "POLYGON" or "MULTIPOLYGON"'
        )
        raise CustomError(
            f"Invalid geometry type: {geom_name}. "
            "Make sure that all features in your dataset"
            "are of type POLYGON or MULTIPOLYGON. "
        )


def check_if_geom_is_valid(projectId, feat_geom):
    if not feat_geom.IsValid():
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Geometry is not valid:"
            f"Tested with IsValid() ogr method. "
            f"Probably self-intersections."
        )

        raise CustomError("Geometry is not valid.")


def check_if_project_area_is_too_big(projectId, project_area, zoomLevel):
    """We calculate the max area based on zoom level.
    This is an approximation to restrict the project size
    in respect to the number of tasks.
    At zoom level 22 the max area is set to 20 square kilometers.
    For zoom level 18 this will result in a max area of 5,120 square kilometers.
    """

    max_area = 5 * 4 ** (23 - zoomLevel)

    if project_area > max_area:
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Project is too large: {project_area} sqkm. "
            f"Please split your projects into smaller sub-projects and resubmit"
        )
        raise CustomError(
            f"Project is too large: {project_area} sqkm. "
            f"Max area for zoom level {zoomLevel} = {max_area} sqkm. "
            "You can split your project into smaller projects and resubmit."
        )


def load_geojson_to_ogr(projectId, input_file_path):
    driver = ogr.GetDriverByName("GeoJSON")
    datasource = driver.Open(input_file_path, 0)

    try:
        return datasource.GetLayer(), datasource
    except AttributeError:
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Could not get layer for datasource"
        )
        raise CustomError(
            "Could not get layer for datasource."
            "Your geojson file is not correctly defined."
            "Check if you can open the file e.g. in QGIS. "
        )


def get_feature_geometry(projectId, feature):
    try:
        feat_geom = feature.GetGeometryRef()
        geom_name = feat_geom.GetGeometryName()
    except AttributeError:
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"feature geometry is not defined. "
        )
        raise CustomError(
            "At least one feature geometry is not defined."
            "Check in your input file if all geometries are defined "
            "and no NULL geometries exist. "
        )
    return feat_geom, geom_name


def add_geom_to_multipolygon(multi_polygon, feat_geom, geom_name):
    if geom_name == "MULTIPOLYGON":
        for singlepart_polygon in feat_geom:
            multi_polygon.AddGeometry(singlepart_polygon)
    if geom_name == "POLYGON":
        multi_polygon.AddGeometry(feat_geom)
    return multi_polygon


def calculate_polygon_area_in_km(geometry):
    """Calculate the area of a polygon in Mollweide projection (EPSG Code: 54009)."""
    source = geometry.GetSpatialReference()
    target = osr.SpatialReference()
    target.ImportFromProj4(
        "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
    )

    transform = osr.CoordinateTransformation(source, target)
    geometry.Transform(transform)
    return geometry.GetArea() / 1000000


def build_multipolygon_from_layer_geometries(projectId, layer):
    """
    Collect all geometries from input collection into one Multipolygon,
    additionally get the total area covered by all polygons.
    """
    project_area = 0
    multi_polygon = ogr.Geometry(ogr.wkbMultiPolygon)

    # check if the input geometry is a valid polygon
    for feature in layer:
        feat_geom, geom_name = get_feature_geometry(projectId, feature)

        check_if_geom_type_is_valid(projectId, geom_name)
        check_if_geom_is_valid(projectId, feat_geom)

        multi_polygon = add_geom_to_multipolygon(multi_polygon, feat_geom, geom_name)
        project_area += calculate_polygon_area_in_km(feat_geom)

    return multi_polygon, project_area


def validate_and_collect_geometries_to_multipolyon(
    projectId, zoomLevel, input_file_path
):
    """Validate all geometries contained in input file and collect them to a single multi polygon."""
    layer, datasource = load_geojson_to_ogr(projectId, input_file_path)

    # check if inputs fit constraints
    check_if_layer_is_empty(projectId, layer)
    check_if_zoom_level_is_too_high(zoomLevel)

    multi_polygon, project_area = build_multipolygon_from_layer_geometries(
        projectId, layer
    )

    check_if_layer_has_too_many_geometries(projectId, multi_polygon)
    check_if_project_area_is_too_big(projectId, project_area, zoomLevel)

    del datasource
    del layer

    logger.info(f"{projectId}" f" - validate geometry - " f"input geometry is correct.")
    return multi_polygon


def multipolygon_to_wkt(multi_polygon):
    dissolved_geometry = multi_polygon.UnionCascaded()
    return dissolved_geometry.ExportToWkt()
