import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import mercantile
import pandas as pd
import requests
from shapely import (
    LineString,
    MultiLineString,
    MultiPolygon,
    Point,
    Polygon,
    box,
    unary_union,
)
from shapely.geometry import shape
from vt2geojson import tools as vt2geojson_tools

from mapswipe_workers.definitions import (
    MAPILLARY_API_KEY,
    MAPILLARY_API_LINK,
    CustomError,
    logger,
)
from mapswipe_workers.utils.spatial_sampling import spatial_sampling


def create_tiles(polygon, level):
    if not isinstance(polygon, (Polygon, MultiPolygon)):
        return pd.DataFrame(columns=["x", "y", "z", "geometry"])
    if isinstance(polygon, Polygon):
        polygon = MultiPolygon([polygon])

    tiles = []
    for i, poly in enumerate(polygon.geoms):
        tiles.extend(list(mercantile.tiles(*poly.bounds, level)))

    bbox_list = [mercantile.bounds(tile.x, tile.y, tile.z) for tile in tiles]
    bbox_polygons = [box(*bbox) for bbox in bbox_list]
    tiles = pd.DataFrame(
        {
            "x": [tile.x for tile in tiles],
            "y": [tile.y for tile in tiles],
            "z": [tile.z for tile in tiles],
            "geometry": bbox_polygons,
        }
    )

    return tiles


def download_and_process_tile(row, attempt_limit=3):
    z = row["z"]
    x = row["x"]
    y = row["y"]
    url = f"{MAPILLARY_API_LINK}{z}/{x}/{y}?access_token={MAPILLARY_API_KEY}"

    attempt = 0
    while attempt < attempt_limit:
        try:
            r = requests.get(url)
            assert r.status_code == 200, r.content
            features = vt2geojson_tools.vt_bytes_to_geojson(r.content, x, y, z).get(
                "features", []
            )
            data = []
            for feature in features:
                geometry = feature.get("geometry", {})
                properties = feature.get("properties", {})
                geometry_type = geometry.get("type", None)
                coordinates = geometry.get("coordinates", [])

                element_geometry = None
                if geometry_type == "Point":
                    element_geometry = Point(coordinates)
                elif geometry_type == "LineString":
                    element_geometry = LineString(coordinates)
                elif geometry_type == "MultiLineString":
                    element_geometry = MultiLineString(coordinates)
                elif geometry_type == "Polygon":
                    element_geometry = Polygon(coordinates[0])
                elif geometry_type == "MultiPolygon":
                    element_geometry = MultiPolygon(coordinates)

                # Append the dictionary with geometry and properties
                row = {"geometry": element_geometry, **properties}
                data.append(row)

            data = pd.DataFrame(data)

            if not data.empty:
                return data
        except Exception as e:
            print(f"An exception occurred while requesting a tile: {e}")
            attempt += 1

    print(f"A tile could not be downloaded: {row}")
    return None


def coordinate_download(
    polygon, level, use_concurrency=True, attempt_limit=3, workers=os.cpu_count() * 4
):
    tiles = create_tiles(polygon, level)

    downloaded_metadata = []

    if not tiles.empty:
        if not use_concurrency:
            workers = 1

        futures = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for index, row in tiles.iterrows():
                futures.append(
                    executor.submit(download_and_process_tile, row, attempt_limit)
                )

            for future in as_completed(futures):
                if future is not None:
                    df = future.result()

                    if df is not None and not df.empty:
                        downloaded_metadata.append(df)
        if len(downloaded_metadata):
            downloaded_metadata = pd.concat(downloaded_metadata, ignore_index=True)
        else:
            return pd.DataFrame(downloaded_metadata)

        target_columns = [
            "id",
            "geometry",
            "captured_at",
            "is_pano",
            "compass_angle",
            "sequence",
            "organization_id",
        ]
        for col in target_columns:
            if col not in downloaded_metadata.columns:
                downloaded_metadata[col] = None
        if (
            downloaded_metadata.isna().all().all() is False
            or downloaded_metadata.empty is False
        ):
            downloaded_metadata = downloaded_metadata[
                downloaded_metadata["geometry"].apply(
                    lambda point: point.within(polygon)
                )
            ]
        return downloaded_metadata


def geojson_to_polygon(geojson_data):
    if geojson_data["type"] == "FeatureCollection":
        features = geojson_data["features"]
    elif geojson_data["type"] == "Feature":
        features = [geojson_data]
    else:
        raise ValueError("Unsupported GeoJSON type.")

    polygons = []
    for feature in features:
        geometry = shape(feature["geometry"])
        if isinstance(geometry, (Polygon, MultiPolygon)):
            polygons.append(geometry)
        else:
            raise ValueError(
                "Non-polygon geometries cannot be combined into a MultiPolygon."
            )

    combined_multipolygon = unary_union(polygons)

    return combined_multipolygon


def filter_by_timerange(df: pd.DataFrame, start_time: str, end_time: str = None):
    df["captured_at"] = pd.to_datetime(df["captured_at"], unit="ms")
    start_time = pd.to_datetime(start_time).tz_localize(None)
    if end_time is None:
        end_time = pd.Timestamp.now().tz_localize(None)
    else:
        end_time = pd.to_datetime(end_time).tz_localize(None)
    filtered_df = df[
        (df["captured_at"] >= start_time) & (df["captured_at"] <= end_time)
    ]
    return filtered_df


def filter_results(
    results_df: pd.DataFrame,
    creator_id: int = None,
    is_pano: bool = None,
    organization_id: str = None,
    start_time: str = None,
    end_time: str = None,
):
    df = results_df.copy()
    if creator_id is not None:
        if df["creator_id"].isna().all():
            logger.info("No Mapillary Feature in the AoI has a 'creator_id' value.")
            return None
        df = df[df["creator_id"] == creator_id]

    if is_pano is not None:
        if df["is_pano"].isna().all():
            logger.info("No Mapillary Feature in the AoI has a 'is_pano' value.")
            return None
        df = df[df["is_pano"] == is_pano]

    if organization_id is not None:
        if df["organization_id"].isna().all():
            logger.info(
                "No Mapillary Feature in the AoI has an 'organization_id' value."
            )
            return None
        df = df[df["organization_id"] == organization_id]

    if start_time is not None:
        if df["captured_at"].isna().all():
            logger.info("No Mapillary Feature in the AoI has a 'captured_at' value.")
            return None
        df = filter_by_timerange(df, start_time, end_time)

    return df


def get_image_metadata(
    aoi_geojson,
    level=14,
    attempt_limit=3,
    is_pano: bool = None,
    creator_id: int = None,
    organization_id: str = None,
    start_time: str = None,
    end_time: str = None,
    sampling_threshold=None,
):
    aoi_polygon = geojson_to_polygon(aoi_geojson)
    downloaded_metadata = coordinate_download(aoi_polygon, level, attempt_limit)

    if downloaded_metadata.empty or downloaded_metadata.isna().all().all():
        raise CustomError("No Mapillary Features in the AoI.")

    downloaded_metadata = downloaded_metadata[
        downloaded_metadata["geometry"].apply(lambda geom: isinstance(geom, Point))
    ]

    filtered_metadata = filter_results(
        downloaded_metadata, creator_id, is_pano, organization_id, start_time, end_time
    )

    if (
        filtered_metadata is None
        or filtered_metadata.empty
        or filtered_metadata.isna().all().all()
    ):
        raise CustomError("No Mapillary Features in the AoI match the filter criteria.")

    if sampling_threshold is not None:
        filtered_metadata = spatial_sampling(filtered_metadata, sampling_threshold)

    total_images = len(filtered_metadata)
    if total_images > 100000:
        raise CustomError(
            f"Too many Images with selected filter options for the AoI: {total_images}"
        )

    return {
        "ids": filtered_metadata["id"].tolist(),
        "geometries": filtered_metadata["geometry"].tolist(),
    }
