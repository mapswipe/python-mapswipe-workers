import argparse
import os
import warnings

import geopandas as gpd
import pandas as pd
import rasterio
import requests
from exactextract import exact_extract
from tqdm import tqdm

warnings.filterwarnings("ignore")


def project_list(id_file):
    """Reads Mapswipe project IDs from the user input file"""

    with open(id_file, "r") as file:
        ids = file.read().strip()

    project_list = ids.split(",")
    project_list = [id.strip() for id in project_list]

    return project_list


def population_raster_download():
    """Downloads 1km resolution global population raster for 2020 from WorldPop to the current working directory."""

    url = "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/0_Mosaicked/ppp_2020_1km_Aggregated.tif"

    output_file = "ppp_2020_1km_Aggregated.tif"

    output_file_path = os.path.join(os.getcwd(), output_file)

    if os.path.exists(output_file_path):

        print("Population raster already exists. Moving to next steps......")
        return output_file_path

    else:

        response = requests.get(url, stream=True)
        size = int(response.headers.get("content-length", 0))
        block_size = 1024
        try:
            with open(output_file, "wb") as file, tqdm(
                desc="Downloading population raster",
                total=size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(block_size):
                    if chunk:
                        file.write(chunk)
                        bar.update(len(chunk))

            print("Download complete:", output_file_path)
            return output_file_path

        except requests.RequestException as e:
            print(f"Error downloading data: {e}")


def population_count(list, dir, raster):
    """Gets boundary data for projects from Mapswipe API and calculates zonal statistics
    with global population raster and individual project boundaries."""

    dict = {}
    worldpop = rasterio.open(raster)

    for id in list:
        url = f"https://apps.mapswipe.org/api/project_geometries/project_geom_{id}.geojson"
        response = requests.get(url)

        try:
            geojson = response.json()
            for feature in geojson["features"]:
                geometry = feature.get("geometry", {})
                if "coordinates" in geometry:
                    if geometry["type"] == "Polygon":
                        geometry["coordinates"] = [
                            [[coord[0], coord[1]] for coord in polygon]
                            for polygon in geometry["coordinates"]
                        ]
                    elif geometry["type"] == "MultiPolygon":
                        geometry["coordinates"] = [
                            [
                                [[coord[0], coord[1]] for coord in polygon]
                                for polygon in multipolygon
                            ]
                            for multipolygon in geometry["coordinates"]
                        ]
            gdf = gpd.GeoDataFrame.from_features(geojson["features"])
            gdf.set_crs("EPSG:4326", inplace=True)
            no_of_people = exact_extract(worldpop, gdf, "sum")
            no_of_people = round(no_of_people[0]["properties"]["sum"])

            dict[id] = no_of_people

        except requests.RequestException as e:
            print(f"Error in retrieval of project boundary from Mapswipe: {e}")

    df = pd.DataFrame(
        dict.items(), columns=["Project_IDs", "Number of people impacted"]
    )

    df["Project_IDs"] = "https://mapswipe.org/en/projects/" + df["Project_IDs"]

    df.to_csv(f"{dir}/projects_population.csv")

    print(f"CSV file successfully created at {dir}/number_of_people_impacted.csv")


if __name__ == "__main__":
    """Generates population stats for individual Mapswipe projects"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--text_file",
        help=(
            "Path to the text file containing project IDs from Mapswipe. The file should contain IDs in this manner: "
            "-O8kulfxD4zRYQ2T1aXf, -O8kyOCreRGklW15n8RU, -O8kzSy9105axIPOAJjO, -OAwWv9rnJqPXTpWxO8-, "
            "-OB-tettI2np7t3Gpu-k"
        ),
        type=str,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_directory",
        help="Path to the directory to store the output",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    population_count(
        project_list(args.text_file),
        args.output_directory,
        population_raster_download(),
    )
