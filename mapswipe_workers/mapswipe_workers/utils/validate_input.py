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


def validate_geometries(projectId, zoomLevel, input_file_path):
    driver = ogr.GetDriverByName("GeoJSON")
    datasource = driver.Open(input_file_path, 0)

    try:
        layer = datasource.GetLayer()
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

    # check if layer is empty
    if layer.GetFeatureCount() < 1:
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Empty file. "
            f"No geometry is provided."
        )
        raise CustomError("Empty file. ")

    # check if more than 1 geometry is provided
    elif layer.GetFeatureCount() > MAX_INPUT_GEOMETRIES:
        logger.warning(
            f"{projectId}"
            f" - validate geometry - "
            f"Input file contains more than {MAX_INPUT_GEOMETRIES} geometries. "
            f"Make sure to provide less than {MAX_INPUT_GEOMETRIES} geometries."
        )
        raise CustomError(
            f"Input file contains more than {MAX_INPUT_GEOMETRIES} geometries. "
            "You can split up your project into two or more projects. "
            "This can reduce the number of input geometries. "
        )

    project_area = 0
    geometry_collection = ogr.Geometry(ogr.wkbMultiPolygon)
    # check if the input geometry is a valid polygon
    for feature in layer:

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
        # add geometry to geometry collection
        if geom_name == "MULTIPOLYGON":
            for singlepart_polygon in feat_geom:
                geometry_collection.AddGeometry(singlepart_polygon)
        if geom_name == "POLYGON":
            geometry_collection.AddGeometry(feat_geom)
        if not feat_geom.IsValid():
            logger.warning(
                f"{projectId}"
                f" - validate geometry - "
                f"Geometry is not valid: {geom_name}. "
                f"Tested with IsValid() ogr method. "
                f"Probably self-intersections."
            )
            raise CustomError(f"Geometry is not valid: {geom_name}. ")

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

        # check size of project make sure its smaller than  5,000 sqkm
        # for doing this we transform the geometry
        # into Mollweide projection (EPSG Code 54009)
        source = feat_geom.GetSpatialReference()
        target = osr.SpatialReference()
        target.ImportFromProj4(
            "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
        )

        transform = osr.CoordinateTransformation(source, target)
        feat_geom.Transform(transform)
        project_area = +feat_geom.GetArea() / 1000000

    # max zoom level is 22
    if zoomLevel > 22:
        raise CustomError(f"zoom level is too large (max: 22): {zoomLevel}.")

    # We calculate the max area based on zoom level.
    # This is an approximation to restrict the project size
    # in respect to the number of tasks.
    # At zoom level 22 the max area is set to 20 square kilometers.
    # For zoom level 18 this will result in an max area of 5,120 square kilometers.
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

    del datasource
    del layer

    logger.info(f"{projectId}" f" - validate geometry - " f"input geometry is correct.")

    dissolved_geometry = geometry_collection.UnionCascaded()
    wkt_geometry_collection = dissolved_geometry.ExportToWkt()

    return wkt_geometry_collection
