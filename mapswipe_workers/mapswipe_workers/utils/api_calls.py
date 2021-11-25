import requests

from ..definitions import OHSOME_API_LINK, logger


def geojsonToFeatureCollection(geojson):
    if geojson["type"] != "FeatureCollection":
        collection = {
            "type": "FeatureCollection",
            "features": [{"type": "feature", "geometry": geojson}],
        }
        return collection
    return geojson


def ohsome(request: dict, area: str, properties=None):
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
    response = response
    if response.status_code != 200:
        err = f"ohsome Request failed: {response.status_code}"
        logger.warning(
            f"{err} - check for errors in filter or geometries - {request['filter']}"
        )
        logger.warning(response.json())
        raise Exception(err)
    else:
        logger.info("Query succesfull.")
    return response.json()
