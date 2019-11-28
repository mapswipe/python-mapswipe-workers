import json
import os
import subprocess
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
                    except KeyError:
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
