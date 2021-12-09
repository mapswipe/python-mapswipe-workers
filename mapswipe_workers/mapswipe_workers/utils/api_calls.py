import queue
import threading
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


def add_to_properties(attribute: str, feature: dict, new_properties: dict):
    """Adds attribute to new geojson properties if it is needed."""
    if attribute != "comment":
        new_properties[attribute.replace("@", "")] = feature["properties"][attribute]
    else:
        new_properties[attribute.replace("@", "")] = feature["properties"]["tags"][
            attribute
        ]
    return new_properties


# startblock for osm changesets threading
q = queue.Queue()
osm_results = {}


def chunks(_list, n_objects):
    return [
        _list[i * n_objects : (i + 1) * n_objects]
        for i in range((len(_list) + n_objects - 1) // n_objects)
    ]


def query_osm(changeset_ids: list):
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
    for changeset in tree:
        id = changeset.attrib["id"]
        username = changeset.attrib["user"]
        userid = changeset.attrib["uid"]
        hashtags = None
        for tag in changeset:
            if tag.attrib["k"] == "hashtags":
                hashtags = tag.attrib["v"]
        osm_results[id] = {"username": username, "userid": userid, "hashtags": hashtags}
    return


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        query_osm(item)
        logger.info("worker finished")
        q.task_done()


def start_workers(worker_pool=2):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
    return threads


def stop_workers(threads):
    # stop workers
    for i in threads:
        q.put(None)
    for t in threads:
        t.join()


# endblock for osm changesets threading


def remove_noise_and_add_user_info(json: dict) -> dict:
    """Delete unwanted information from properties."""
    logger.info("starting filtering and adding extra info")

    wanted_attributes = [
        "@changesetId",
        "@lastEdit",
        "@osmId",
        "@version",
        "source",
        "comment",
    ]
    changeset_ids = []
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
        for attribute in wanted_attributes:
            try:
                new_properties = add_to_properties(attribute, feature, new_properties)
            except KeyError:
                missing_rows[attribute] += 1
        changeset_id = new_properties["changesetId"]
        if changeset_id not in changeset_ids:
            changeset_ids.append(changeset_id)
        feature["properties"] = new_properties
    logger.info(
        f"""{len(changeset_ids)} changesets will
         be queried in roughly {int(len(changeset_ids)/99) +1} batches"""
    )
    chunk_list = chunks(changeset_ids, 99)
    for subset in chunk_list:
        q.put(subset)
    q.put([100, 2002])
    assert len(changeset_ids) == sum([len(arr) for arr in chunk_list])
    workers = start_workers(worker_pool=2)  # more could lead to ban from osm api

    q.join()
    stop_workers(workers)
    assert len(changeset_ids) == len(osm_results.keys()) - 2

    for feature in json["features"]:
        try:
            changeset = osm_results[feature["properties"]["changesetId"]]
            feature["properties"]["username"] = changeset["username"]
            feature["properties"]["userid"] = changeset["userid"]
            feature["properties"]["hashtags"] = changeset["hashtags"]
        except KeyError:
            logger.info(feature["properties"]["changesetId"])

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
