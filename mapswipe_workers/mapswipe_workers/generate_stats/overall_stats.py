import os
import pandas as pd
from mapswipe_workers import auth
from mapswipe_workers.definitions import logger
from mapswipe_workers.utils import geojson_functions


def get_project_static_info(filename):

    pg_db = auth.postgresDB()
    sql_query = """
        COPY (
            SELECT 
                project_id
                ,name
                ,project_details
                ,look_for
                ,project_type
                ,status
                ,ST_Area(geom::geography)/1000000 as area_sqkm
                ,ST_AsText(geom) as geom
                ,ST_AsText(ST_Centroid(geom)) as centroid
            FROM projects
        ) TO STDOUT WITH CSV HEADER"""

    with open(filename, "w") as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db
    logger.info("got projects from postgres.")

    df = pd.read_csv(filename)
    return df


def load_project_info_dynamic(filename):
    if os.path.isfile(filename):
        logger.info(f"file {filename} exists. Init from this file.")
        df = pd.read_csv(filename, index_col="idx")
    else:
        columns = [
            "project_id",
            "progress",
            "number_of_users",
            "number_of_results",
            "number_of_results_progress",
            "day",
        ]
        df = pd.DataFrame(index=[], columns=columns)
        df["project_id"].astype("str")

    return df


def save_projects(filename, df, df_dynamic):
    projects_df = df.merge(
        df_dynamic, left_on="project_id", right_on="project_id", how="left"
    )
    projects_df.to_csv(filename, index_label="idx")
    logger.info(f"saved projects: {filename}")
    geojson_functions.csv_to_geojson(filename, "geom")
    geojson_functions.csv_to_geojson(filename, "centroid")
