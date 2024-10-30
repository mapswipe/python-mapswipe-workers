import mercantile
import json
import requests
import os
import time
from shapely import box, Polygon, MultiPolygon, Point, LineString, MultiLineString
import pandas as pd
from vt2geojson import tools as vt2geojson_tools
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_image_ids():
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def create_tiles(polygon, level):
    if not isinstance(polygon, (Polygon, MultiPolygon)):
        return pd.DataFrame(columns=['x', 'y', 'z', 'geometry'])
    if isinstance(polygon, Polygon):
        polygon = MultiPolygon([polygon])

    tiles = []
    for i, poly in enumerate(polygon.geoms):
        tiles.extend(list(mercantile.tiles(*poly.bounds, level)))

    bbox_list = [mercantile.bounds(tile.x, tile.y, tile.z) for tile in tiles]
    bbox_polygons = [box(*bbox) for bbox in bbox_list]
    tiles = pd.DataFrame({
        'x': [tile.x for tile in tiles],
        'y': [tile.y for tile in tiles],
        'z': [tile.z for tile in tiles],
        'geometry': bbox_polygons})

    return tiles


def download_and_process_tile(row, token, attempt_limit=3):
    z = row["z"]
    x = row["x"]
    y = row["y"]
    endpoint = "mly1_computed_public"
    url = f"https://tiles.mapillary.com/maps/vtp/{endpoint}/2/{z}/{x}/{y}?access_token={token}"

    attempt = 0
    while attempt < attempt_limit:
        try:
            r = requests.get(url)
            assert r.status_code == 200, r.content
            features = vt2geojson_tools.vt_bytes_to_geojson(r.content, x, y, z).get('features', [])

            data = []
            for feature in features:
                geometry = feature.get('geometry', {})
                properties = feature.get('properties', {})
                geometry_type = geometry.get('type', None)
                coordinates = geometry.get('coordinates', [])

                element_geometry = None
                if geometry_type == 'Point':
                    element_geometry = Point(coordinates)
                elif geometry_type == 'LineString':
                    element_geometry = LineString(coordinates)
                elif geometry_type == 'MultiLineString':
                    element_geometry = MultiLineString(coordinates)
                elif geometry_type == 'Polygon':
                    element_geometry = Polygon(coordinates[0])
                elif geometry_type == 'MultiPolygon':
                    element_geometry = MultiPolygon(coordinates)

                # Append the dictionary with geometry and properties
                row = {'geometry': element_geometry, **properties}
                data.append(row)

            data = pd.DataFrame(data)

            if not data.empty:
                return data, None
        except Exception as e:
            print(f"An exception occurred while requesting a tile: {e}")
            attempt += 1

    print(f"A tile could not be downloaded: {row}")
    return None, row


def coordinate_download(polygon, level, token, use_concurrency=True, attempt_limit=3, workers=os.cpu_count() * 4):
    tiles = create_tiles(polygon, level)

    downloaded_metadata = []
    failed_tiles = []

    if not tiles.empty:
        if not use_concurrency:
            workers = 1

        futures = []
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for index, row in tiles.iterrows():
                futures.append(executor.submit(download_and_process_tile, row, token, attempt_limit))

            for future in as_completed(futures):
                if future is not None:
                    df, failed_row = future.result()

                    if df is not None and not df.empty:
                        downloaded_metadata.append(df)
                    if failed_row is not None:
                        failed_tiles.append(failed_row)

        end_time = time.time()
        total_time = end_time - start_time

        total_tiles = len(tiles)
        average_time_per_tile = total_time / total_tiles if total_tiles > 0 else 0

        print(f"Total time for downloading {total_tiles} tiles: {total_time:.2f} seconds")
        print(f"Average time per tile: {average_time_per_tile:.2f} seconds")

        if len(downloaded_metadata):
            downloaded_metadata = pd.concat(downloaded_metadata, ignore_index=True)
        else:
            downloaded_metadata = pd.DataFrame(downloaded_metadata)

        failed_tiles = pd.DataFrame(failed_tiles, columns=tiles.columns).reset_index(drop=True)

        return downloaded_metadata, failed_tiles
