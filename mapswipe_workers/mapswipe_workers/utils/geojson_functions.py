import gzip
import json
import os
import shutil
import subprocess
import tempfile

from osgeo import ogr, osr

from mapswipe_workers.definitions import logger


def gzipped_csv_to_gzipped_geojson(
    filename: str, geometry_field: str = "geom", add_metadata: bool = False
):
    """Convert gzipped csv file to gzipped GeoJSON.

    First the gzipped files are unzipped and stored in temporary csv and geojson files.
    Then the unzipped csv file is converted into a geojson file with ogr2ogr.
    Last, the generated geojson file is again compressed using gzip.
    """
    # generate temporary files which will be automatically deleted at the end
    tmp_csv_file = os.path.join(tempfile._get_default_tempdir(), "tmp.csv")
    tmp_geojson_file = os.path.join(tempfile._get_default_tempdir(), "tmp.geojson")

    outfile = filename.replace(".csv", f"_{geometry_field}.geojson")

    # uncompress content of zipped csv file and save to csv file
    with gzip.open(filename, "rb") as f_in:
        with open(tmp_csv_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # use ogr2ogr to transform csv file into geojson file
    # TODO: remove geom column from normal attributes in sql query
    subprocess.run(
        [
            "ogr2ogr",
            "-f",
            "GeoJSON",
            tmp_geojson_file,
            tmp_csv_file,
            "-sql",
            f'SELECT *, CAST({geometry_field} as geometry) FROM "tmp"',  # noqa E501
        ],
        check=True,
    )

    if add_metadata:
        add_metadata_to_geojson(tmp_geojson_file)

    cast_datatypes_for_geojson(tmp_geojson_file)

    # compress geojson file with gzip
    with open(tmp_geojson_file, "r") as f:
        json_data = json.load(f)

    with gzip.open(outfile, "wt") as fout:
        json.dump(json_data, fout)

    logger.info(f"converted {filename} to {outfile} with ogr2ogr.")


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
            f'SELECT *, CAST({geometry_field} as geometry) FROM "{filename_without_path}"',  # noqa E501
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


def create_group_geom(group_data, shape="bounding_box"):
    """Create bounding box or convex hull of input task geometries."""

    result_geom_collection = ogr.Geometry(ogr.wkbMultiPolygon)
    for result, data in group_data.items():
        result_geom = ogr.CreateGeometryFromWkt(data["wkt"])
        result_geom_collection.AddGeometry(result_geom)

    if shape == "convex_hull":
        group_geom = result_geom_collection.ConvexHull()
    elif shape == "bounding_box":
        # Get Envelope
        lon_left, lon_right, lat_top, lat_bottom = result_geom_collection.GetEnvelope()

        # Create Geometry
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(lon_left, lat_top)
        ring.AddPoint(lon_right, lat_top)
        ring.AddPoint(lon_right, lat_bottom)
        ring.AddPoint(lon_left, lat_bottom)
        ring.AddPoint(lon_left, lat_top)
        # TODO: Make sure to return 2D geom, currently 3D with z = 0.0
        group_geom = ogr.Geometry(ogr.wkbPolygon)
        group_geom.AddGeometry(ring)

    return group_geom


def create_geojson_file_from_dict(final_groups_dict, outfile):
    """Take output from generate stats and create TM geometries.

    In order to create a GeoJSON file with a coordinate precision of 7
    we take a small detour.
    First, we create a GeoJSONSeq file.
    This contains only the features.
    Then we add these features to the final GeoJSON file.
    The current shape of the output geometries is set to 'bounding_box'.
    """

    driver = ogr.GetDriverByName("GeoJSONSeq")
    # define spatial Reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    outfile_temp = outfile.replace(".geojson", "_temp.geojson")

    if os.path.exists(outfile_temp):
        driver.DeleteDataSource(outfile_temp)

    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)

    dataSource = driver.CreateDataSource(outfile_temp)
    # create layer
    layer = dataSource.CreateLayer(outfile_temp, srs, geom_type=ogr.wkbPolygon,)

    # create fields
    field_id = ogr.FieldDefn("group_id", ogr.OFTInteger)
    layer.CreateField(field_id)

    if len(final_groups_dict) < 1:
        logger.info("there are no geometries to save")
    else:
        for group_id in final_groups_dict.keys():
            group_data = final_groups_dict[group_id]
            # create the final group geometry
            group_geom = create_group_geom(group_data, "bounding_box")
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

    # make sure to close layer and data source
    layer = None
    dataSource = None

    # load the features from temp file
    feature_collection = []
    with open(outfile_temp, "r") as f:
        for cnt, line in enumerate(f):
            feature_collection.append(json.loads(line))

    # create final geojson structure
    geojson_structure = {
        "type": "FeatureCollection",
        "name": outfile,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": feature_collection,
    }

    # save to geojson
    with open(outfile, "w") as json_file:
        json.dump(geojson_structure, json_file)
        logger.info("created outfile: %s." % outfile)

    # remove temp file
    if os.path.exists(outfile_temp):
        driver.DeleteDataSource(outfile_temp)


def create_geojson_file(geometries, outfile):

    driver = ogr.GetDriverByName("GeoJSONSeq")
    # define spatial Reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    outfile_temp = outfile.replace(".geojson", "_temp.geojson")

    if os.path.exists(outfile_temp):
        driver.DeleteDataSource(outfile_temp)

    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)

    dataSource = driver.CreateDataSource(outfile_temp)
    # create layer
    layer = dataSource.CreateLayer(outfile_temp, srs, geom_type=ogr.wkbPolygon,)

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

    # make sure to close layer and data source
    layer = None
    dataSource = None

    # load the features from temp file
    feature_collection = []
    with open(outfile_temp, "r") as f:
        for cnt, line in enumerate(f):
            feature_collection.append(json.loads(line))

    # create final geojson structure
    geojson_structure = {
        "type": "FeatureCollection",
        "name": outfile,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": feature_collection,
    }
    # save to geojson
    with open(outfile, "w") as json_file:
        json.dump(geojson_structure, json_file)
        logger.info("created outfile: %s." % outfile)

    # remove temp file
    if os.path.exists(outfile_temp):
        driver.DeleteDataSource(outfile_temp)

    logger.info("created outfile: %s." % outfile)
