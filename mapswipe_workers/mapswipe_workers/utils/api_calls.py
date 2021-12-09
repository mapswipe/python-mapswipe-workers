from xml.etree import ElementTree

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from mapswipe_workers.definitions import (
    OHSOME_API_LINK,
    OSM_API_LINK,
    CustomError,
    logger,
)


def retry_get(url, retries=3, timeout=4):
    retry = Retry(total=retries)
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session.get(url, timeout=timeout)


def geojsonToFeatureCollection(geojson: dict) -> dict:
    if geojson["type"] != "FeatureCollection":
        collection = {
            "type": "FeatureCollection",
            "features": [{"type": "feature", "geometry": geojson}],
        }
        return collection
    return geojson


def chunks(arr, n_objects):
    return [
        arr[i * n_objects : (i + 1) * n_objects]
        for i in range((len(arr) + n_objects - 1) // n_objects)
    ]


def query_osm(changeset_ids: list, changeset_results):
    """Get data from changesetId."""
    id_string = ""
    for id in changeset_ids:
        id_string += f"{id},"

    id_string = id_string[:-1]

    url = OSM_API_LINK + f"changesets?changesets={id_string}"
    response = retry_get(url)
    if response.status_code != 200:
        err = f"osm request failed: {response.status_code}"
        logger.warning(f"{err}")
        logger.warning(response.json())
        raise CustomError(err)
    tree = ElementTree.fromstring(response.content)

    for changeset in tree.iter("changeset"):
        id = changeset.attrib["id"]
        username = changeset.attrib["user"]
        userid = changeset.attrib["uid"]
        comment = created_by = None
        for tag in changeset.iter("tag"):
            if tag.attrib["k"] == "comment":
                try:
                    comment = tag.attrib["v"].replace("\n", " ")
                except AttributeError:
                    pass
            if tag.attrib["k"] == "created_by":
                created_by = tag.attrib["v"]

        changeset_results[int(id)] = {
            "username": username,
            "userid": userid,
            "comment": comment,
            "created_by": created_by,
        }
    return changeset_results


def add_to_properties(attribute: str, feature: dict, new_properties: dict):
    """Adds attribute to new geojson properties if it is needed."""
    if attribute != "comment":
        new_properties[attribute.replace("@", "")] = feature["properties"][attribute]
    else:
        new_properties[attribute.replace("@", "")] = feature["properties"]["tags"][
            attribute
        ]
    return new_properties


def remove_noise_and_add_user_info(json: dict) -> dict:
    """Delete unwanted information from properties."""
    logger.info("starting filtering and adding extra info")
    changeset_results = {}

    missing_rows = {
        "@changesetId": 0,
        "@lastEdit": 0,
        "@osmId": 0,
        "@version": 0,
    }

    for feature in json["features"]:
        new_properties = {}
        for attribute in missing_rows.keys():
            try:
                new_properties[attribute.replace("@", "")] = feature["properties"][
                    attribute
                ]
            except KeyError:
                missing_rows[attribute] += 1
        changeset_results[new_properties["changesetId"]] = None
        feature["properties"] = new_properties

    len_osm = len(changeset_results.keys())
    batches = int(len(changeset_results.keys()) / 100) + 1
    logger.info(
        f"""{len_osm} changesets will be queried in roughly {batches} batches"""
    )
    chunk_list = chunks(list(changeset_results.keys()), 100)
    for i, subset in enumerate(chunk_list):
        changeset_results = query_osm(subset, changeset_results)
        logger.info(
            f"finished query {i}/{len(chunk_list)},{round(i/len(chunk_list), 1)}%"
        )

    for feature in json["features"]:
        changeset = changeset_results[feature["properties"]["changesetId"]]
        feature["properties"]["username"] = changeset["username"]
        feature["properties"]["userid"] = changeset["userid"]
        feature["properties"]["comment"] = changeset["comment"]
        feature["properties"]["created_by"] = changeset["created_by"]

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
        response = remove_noise_and_add_user_info(response)
    return response
