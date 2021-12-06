import requests

from mapswipe_workers.definitions import (
    OHSOME_API_LINK,
    OSM_API_LINK,
    CustomError,
    logger,
)


def geojsonToFeatureCollection(geojson: dict) -> dict:
    if geojson["type"] != "FeatureCollection":
        collection = {
            "type": "FeatureCollection",
            "features": [{"type": "feature", "geometry": geojson}],
        }
        return collection
    return geojson


def query_osm(changeset_id: int):
    """Get data from changesetId."""
    url = OSM_API_LINK + f"changeset/{changeset_id}.json"
    valid_response = False
    times_timed_out = 0
    while not valid_response:
        try:
            response = requests.get(url, timeout=3)
            valid_response = True
        except requests.exceptions.Timeout:
            if times_timed_out > 4:
                raise requests.exceptions.Timeout("timed out 5 times")
            logger.warn(url)
            logger.warn("connection timed out")
            times_timed_out += 1

    if response.status_code != 200:
        err = f"osm request failed: {response.status_code}"
        logger.warning(f"{err}")
        logger.warning(response.json())
        raise CustomError(err)
    response = response.json()["elements"][0]
    return response


def remove_noise_and_add_user_info(json: dict) -> dict:
    """Delete unwanted information from properties."""
    logger.info("starting filtering and adding extra info")

    wanted_rows = ["@changesetId", "@lastEdit", "@osmId", "@version", "source"]
    changeset_results = {}
    missing_rows = {
        "@changesetId": 0,
        "@lastEdit": 0,
        "@osmId": 0,
        "@version": 0,
        "source": 0,
        "comment": 0,
    }

    for feature in json["features"]:
        new_properties = {}
        for attribute in wanted_rows:
            try:
                if attribute != "comment":
                    new_properties[attribute.replace("@", "")] = feature["properties"][
                        attribute
                    ]
                else:
                    new_properties[attribute.replace("@", "")] = feature["properties"][
                        "tags"
                    ][attribute]
            except KeyError:
                missing_rows[attribute] += 1
        changeset_id = new_properties["changesetId"]
        if changeset_id not in changeset_results.keys():
            changeset_results[changeset_id] = query_osm(changeset_id)
        new_properties["username"] = changeset_results[changeset_id]["user"]
        new_properties["userid"] = changeset_results[changeset_id]["uid"]
        feature["properties"] = new_properties
    logger.info("finished filtering and adding extra info")
    if any(x > 0 for x in missing_rows.values()):
        logger.warning(f"features missing values:\n{missing_rows}")

    return json


def ohsome(request: dict, area: str, properties=None) -> dict:
    """
    Request data from Ohsome API.
    """
    url = OHSOME_API_LINK + request["endpoint"]
    data = {"bpolys": area, "filter": request["filter"]}
    if properties:
        data["properties"] = properties
    logger.info("Target: " + url)
    logger.info("Filter: " + request["filter"])
    response = requests.post(url, data=data)
    if response.status_code != 200:
        err = f"ohsome request failed: {response.status_code}"
        logger.warning(
            f"{err} - check for errors in filter or geometries - {request['filter']}"
        )
        logger.warning(response.json())
        raise CustomError(err)
    else:
        logger.info("Query succesfull.")

    response = response.json()

    if properties:
        remove_noise_and_add_user_info(response)
    return response
