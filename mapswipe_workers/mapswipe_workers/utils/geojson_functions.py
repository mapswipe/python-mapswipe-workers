import json
import os
import subprocess
import osr
import ogr
from mapswipe_workers.definitions import logger


def csv_to_geojson(filename: str, geometry_field: str = "geom"):
    """
    Use ogr2ogr to convert csv file to GeoJSON
    """

    outfile = filename.replace(".csv", f"_{geometry_field}.geojson")
    # need to remove file here because ogr2ogr can't overwrite when choosing GeoJSON
    if os.path.isfile(outfile):
        os.remove(outfile)
    filename_without_path = filename.split("/")[-1].replace(".csv", "")
    # TODO: remove geom column from normal attributes in sql query
    subprocess.run(
        [
            "ogr2ogr",
            "-f",
            "GeoJSON",
            outfile,
            filename,
            "-sql",
            f'SELECT *, CAST({geometry_field} as geometry) FROM "{filename_without_path}"',
        ],
        check=True,
    )
    logger.info(f"converted {filename} to {outfile}.")

    cast_datatypes_for_geojson(outfile)


def cast_datatypes_for_geojson(filename: str):
    """
    Go through geojson file and try to cast all values as float, except project_id
    remove redundant geometry property
    """

    filename = filename.replace("csv", "geojson")
    with open(filename) as f:
        geojson_data = json.load(f)

    if len(geojson_data["features"]) < 1:
        logger.info(f"there are no features for this file: {filename}")

    else:
        properties = list(geojson_data["features"][0]["properties"].keys())
        for i in range(0, len(geojson_data["features"])):
            for property in properties:
                if property in [
                    "project_id",
                    "name",
                    "project_details",
                    "task_id",
                    "group_id",
                ]:
                    # don't try to cast project_id
                    pass
                elif property in ["geom"]:
                    # remove redundant geometry property
                    del geojson_data["features"][i]["properties"][property]
                elif geojson_data["features"][i]["properties"][property] == "":
                    del geojson_data["features"][i]["properties"][property]
                else:
                    try:
                        geojson_data["features"][i]["properties"][property] = float(
                            geojson_data["features"][i]["properties"][property]
                        )
                    except ValueError:
                        pass

        with open(filename, "w") as f:
            json.dump(geojson_data, f)
        logger.info(f"converted datatypes for {filename}.")


def add_metadata_to_geojson(filename: str, geometry_field: str = "geom"):
    """
    Add a metadata attribute to the geojson file about intended data usage.
    """

    filename = filename.replace(".csv", f"_{geometry_field}.geojson")
    with open(filename) as f:
        geojson_data = json.load(f)

    if len(geojson_data["features"]) < 1:
        logger.info(f"there are no features for this file: {filename}")

    geojson_data["metadata"] = {
        "usage": "This data can only be used for editing in OpenStreetMap."
    }

    with open(filename, "w") as f:
        json.dump(geojson_data, f)
    logger.info(f"added metadata to {filename}.")


def create_group_geom(group_data):
    result_geom_collection = ogr.Geometry(ogr.wkbMultiPolygon)
    for result, data in group_data.items():
        result_geom = ogr.CreateGeometryFromWkt(data["wkt"])
        result_geom_collection.AddGeometry(result_geom)

    group_geom = result_geom_collection.ConvexHull()
    return group_geom


def create_geojson_file_from_dict(final_groups_dict, outfile):
    # TODO: adapt input name

    driver = ogr.GetDriverByName("GeoJSON")
    # define spatial Reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)
    dataSource = driver.CreateDataSource(outfile)
    # create layer
    layer = dataSource.CreateLayer(outfile, srs, geom_type=ogr.wkbPolygon)

    # create fields
    field_id = ogr.FieldDefn("group_id", ogr.OFTInteger)
    layer.CreateField(field_id)

    if len(final_groups_dict) < 1:
        logger.info("there are no geometries to save")
    else:
        for group_id in final_groups_dict.keys():
            group_data = final_groups_dict[group_id]
            group_geom = create_group_geom(group_data)
            final_groups_dict[group_id]["group_geom"] = group_geom
            # init feature

            if group_geom.GetGeometryName() == "POLYGON":
                featureDefn = layer.GetLayerDefn()
                feature = ogr.Feature(featureDefn)
                # create polygon from wkt and set geometry
                feature.SetGeometry(group_geom)
                # set other attributes
                feature.SetField("group_id", group_id)
                # add feature to layer
                layer.CreateFeature(feature)
                feature.Destroy
            elif group_geom.GetGeometryName() == "MULTIPOLYGON":
                for geom_part in group_geom:
                    featureDefn = layer.GetLayerDefn()
                    feature = ogr.Feature(featureDefn)
                    # create polygon from wkt and set geometry
                    feature.SetGeometry(group_geom)
                    # set other attributes
                    feature.SetField("group_id", group_id)
                    # add feature to layer
                    layer.CreateFeature(feature)
                    feature.Destroy
            else:
                print("other geometry type: %s" % group_geom.GetGeometryName())
                print(group_geom)
                continue

    layer = None
    logger.info("created outfile: %s." % outfile)


def create_geojson_file(geometries, outfile):

    driver = ogr.GetDriverByName("GeoJSON")
    # define spatial Reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)
    dataSource = driver.CreateDataSource(outfile)
    # create layer
    layer = dataSource.CreateLayer(outfile, srs, geom_type=ogr.wkbPolygon)

    # create fields
    field_id = ogr.FieldDefn("id", ogr.OFTInteger)
    layer.CreateField(field_id)

    if not geometries:
        logger.info("there are no geometries to save")
    else:
        for counter, geom in enumerate(geometries):
            # init feature
            featureDefn = layer.GetLayerDefn()
            feature = ogr.Feature(featureDefn)
            # create polygon from wkt and set geometry
            feature.SetGeometry(geom)
            # set other attributes
            # set first id to 1 instead of 0
            feature.SetField("id", counter + 1)
            # add feature to layer
            layer.CreateFeature(feature)

    layer = None
    logger.info("created outfile: %s." % outfile)
