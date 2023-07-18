import csv
import datetime as dt
import hashlib
import os
import shutil
from typing import List, Optional

from mapswipe_workers import auth
from mapswipe_workers.definitions import DATA_PATH, ProjectType, logger
from mapswipe_workers.generate_stats import overall_stats


def generate_data_for_mapswipe_website():
    """
    Generate data for website
    """
    website_data_dest = f"{DATA_PATH}/api/website-data"

    # TODO: Move to utils
    def _compute_md5(file_name):
        hash_md5 = hashlib.md5()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _project_history_zip():
        project_history_file = f"{website_data_dest}/project-history"
        zip_file_name = shutil.make_archive(
            project_history_file,
            "zip",
            f"{DATA_PATH}/api/history/",
        )
        logger.info("finished generate project-history zip")
        return zip_file_name

    def _manifest_file():
        endpoints_dir = f"{DATA_PATH}/api/"
        manifest_file = f"{website_data_dest}/overall-endpoints.csv"
        with open(manifest_file, "w") as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerow(["endpoints", "size_bytes"])
            for path, _, files in os.walk(endpoints_dir):
                for name in files:
                    file_path = os.path.join(path, name)
                    csv_writer.writerow(
                        [
                            "/api/" + file_path.split("/api/")[1],
                            os.path.getsize(file_path),
                        ]
                    )
        logger.info("finished generate endpoints manifest for existing stats")
        return manifest_file

    def _generate_file_hash(files):
        for file in files:
            md5_hash = _compute_md5(file)
            with open(f"{file}.md5", "w") as fp:
                fp.write(md5_hash)

    files_to_track_for_checksum = [
        f"{DATA_PATH}/api/projects/projects_centroid.geojson",
        f"{DATA_PATH}/api/projects/projects_geom.geojson",
    ]
    files_to_track_for_checksum.extend([_project_history_zip(), _manifest_file()])
    _generate_file_hash(files_to_track_for_checksum)


def get_recent_projects(hours: int = 3):
    """Get ids for projects when results have been submitted within the last x hours."""
    pg_db = auth.postgresDB()
    query_insert_results = """
        select project_id
        from mapping_sessions
        where start_time >= %(timestamp)s
        group by project_id
    """
    timestamp = (dt.datetime.utcnow() - dt.timedelta(hours=hours)).isoformat()[
        0:-3
    ] + "Z"
    project_info = pg_db.retr_query(query_insert_results, {"timestamp": timestamp})

    project_ids = []
    for project_id in project_info:
        project_ids.append(project_id[0])
    logger.info(f"Got {len(project_ids)} projects from postgres with recent results.")

    return project_ids


def generate_stats(project_id_list: Optional[List[str]] = None):
    """
    Query attributes for all projects from postgres projects table
    Write information on status (e.g. active, inactive, finished) and further attributes
    for all projects to projects_static.csv.
    Computationally more expensive tasks are only performed for projects specified in
    project_id_list.
    Write information on progress and contributors and further attributes
    only for projects specified in project_id_list to projects_dynamic.csv.
    Write information on project progress history and aggregated results
    only for projects specified in project_id_list to csv and geojson files.
    Merge projects_static.csv and projects_dynamic.csv into projects.csv.
    Convert projects.csv file into GeoJSON format using project geometry and project
    centroid.

    Parameters
    ----------
    project_id_list: list
    """

    projects_info_filename = f"{DATA_PATH}/api/projects/projects_static.csv"
    projects_df = overall_stats.get_project_static_info(projects_info_filename)
    project_id_list_postgres = projects_df["project_id"].to_list()

    projects_info_dynamic_filename = f"{DATA_PATH}/api/projects/projects_dynamic.csv"
    projects_dynamic_df = overall_stats.load_project_info_dynamic(
        projects_info_dynamic_filename
    )

    # Check if an empty project id list has been passed.
    # This means the user did not specify for which projects
    # the generate stats workflow should be performed.
    # In this case, project ids are queried from postgres for projects
    # for which results have been submitted within the last three hours.
    if project_id_list is None or len(project_id_list) == 0:
        project_id_list = get_recent_projects(hours=3)

    logger.info(f"will generate stats for: {project_id_list}")

    # get per project stats and aggregate based on task_id
    for project_id in project_id_list:

        # check if project id is existing
        if project_id not in project_id_list_postgres:
            logger.info(f"project {project_id} does not exist. skip this one.")
            continue

        project_info = projects_df.loc[projects_df["project_id"] == project_id]

        logger.info(f"start generate stats for project: {project_id}")
        idx = projects_dynamic_df.index[
            projects_dynamic_df["project_id"] == project_id
        ].tolist()
        if len(idx) > 0:
            projects_dynamic_df.drop([idx[0]], inplace=True)

        # aggregate results and get per project statistics
        project = ProjectType(project_info["project_type"].item()).constructor

        project_stats_dict = project.get_per_project_statistics(
            project_id, project_info
        )
        if project_stats_dict:
            projects_dynamic_df = projects_dynamic_df.append(
                project_stats_dict, ignore_index=True
            )
            projects_dynamic_df.to_csv(
                projects_info_dynamic_filename, index_label="idx"
            )

    if len(project_id_list) > 0:
        # merge static info and dynamic info and save
        projects_filename = f"{DATA_PATH}/api/projects/projects.csv"
        projects_df = overall_stats.save_projects(
            projects_filename, projects_df, projects_dynamic_df
        )

        # generate overall stats for active, inactive, finished projects
        overall_stats_filename = f"{DATA_PATH}/api/stats.csv"
        overall_stats.get_overall_stats(projects_df, overall_stats_filename)

    logger.info(f"finished generate stats for: {project_id_list}")
    generate_data_for_mapswipe_website()


def generate_stats_all_projects():
    """
    queries all existing project ids from postgres projects table
    saves them into a csv file and returns a list of all project ids
    then generates project statistics using the derived list of project ids
    """

    logger.info("will generate stats for all projects.")

    # get all project ids from postgres database
    projects_info_filename = f"{DATA_PATH}/api/projects/projects_static.csv"
    projects_df = overall_stats.get_project_static_info(projects_info_filename)
    project_id_list = projects_df["project_id"].to_list()

    # generate stats for the derived project ids
    generate_stats(project_id_list)
