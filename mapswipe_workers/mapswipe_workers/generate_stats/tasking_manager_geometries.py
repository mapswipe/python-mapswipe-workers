import csv
from queue import Queue
import threading
from osgeo import ogr

from mapswipe_workers.definitions import logger
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.utils import tile_functions, geojson_functions


def load_data(project_id: str, csv_file: str) -> list:
    """
    This will load the aggregated results csv file into a list of dictionaries.
    For further steps we currently rely on task_x, task_y, task_z and yes_share and maybe_share and wkt
    """

    project_data = []
    with open(csv_file, "r") as f:
        reader = csv.reader(f, delimiter=",")

        for i, row in enumerate(reader):
            if i == 0:
                # skip header
                continue

            # the last row of the csv might contain a comment about data use
            if row[0].startswith("#"):
                continue

            task_id = row[1]
            task_x = int(task_id.split("-")[1])
            task_y = int(task_id.split("-")[2])
            task_z = int(task_id.split("-")[0])

            # TODO: Add no_count here and use later
            project_data.append(
                {
                    "id": task_id,
                    "project_id": project_id,
                    "task_x": task_x,
                    "task_y": task_y,
                    "task_z": task_z,
                    "no_count": int(row[2]),
                    "yes_count": int(row[3]),
                    "maybe_count": int(row[4]),
                    "bad_imagery_count": int(row[5]),
                    "no_share": float(row[7]),
                    "yes_share": float(row[8]),
                    "maybe_share": float(row[9]),
                    "bad_imagery_share": float(row[10]),
                    "wkt": tile_functions.geometry_from_tile_coords(
                        task_x, task_y, task_z
                    ),
                }
            )

    return project_data


def yes_maybe_condition_true(x: dict) -> bool:
    """
    The yes maybe condition is true if 35% or
    2 (or more) out of 3 users
    2 (or more) out of 4 users
    2 (or more) out of 5 users
    have classified as 'yes' or 'maybe'
    """

    if x["yes_share"] + x["maybe_share"] > 0.35:
        return True
    else:
        return False


def filter_data(project_data: list) -> list:
    """
    Filter results that fulfil the yes_maybe_condition.
    """

    # filter yes and maybe
    filtered_project_data = [x for x in project_data if yes_maybe_condition_true(x)]
    return filtered_project_data


def check_list_sum(x, range_val):
    """
    This checks if a give tile belongs to the defined "star"-shaped neighbourhood
    """

    item_sum = abs(x[0]) + abs(x[1])
    if item_sum <= range_val:
        return True
    else:
        return False


def get_neighbour_list(neighbourhood_shape: str, neighbourhood_size: int) -> list:
    """
    Filters tiles that are neighbours.
    This is based on a given search radius (neighbourhood size) and search window shape (neighbourhood shape=.
    """

    neighbour_list = []
    range_val = int(neighbourhood_size / 2)
    for i in range(-range_val, range_val + 1):
        for j in range(-range_val, range_val + 1):
            if i == 0 and j == 0:
                pass
            else:
                neighbour_list.append([i, j])

    if neighbourhood_shape == "star":
        neighbour_list = [x for x in neighbour_list if check_list_sum(x, range_val)]

    return neighbour_list


def add_group_id_to_neighbours(task_x: int, task_y: int, task_z: int, group_id: int):
    """
    Add a group id to all other tiles that are in the neighbourhood of the given tile,
    which is defined by task_x, task_y and task_z.
    """

    # look for neighbours
    for i, j in neighbour_list:
        new_task_x = int(task_x) + i
        new_task_y = int(task_y) + j
        new_task_id = f"{task_z}-{new_task_x}-{new_task_y}"

        if new_task_id in yes_results_dict:
            yes_results_dict[new_task_id]["my_group_id"] = group_id


def create_duplicates_dict() -> dict:
    """
    Check which tasks belong to multiple groups.
    This will be used as a later stage to put tasks into distinct groups.
    """

    duplicated_groups = {}
    for task_id in yes_results_dict.keys():
        my_group_id = yes_results_dict[task_id]["my_group_id"]
        # check for other results in the neighbourhood
        # look for neighbours
        for i, j in neighbour_list:
            new_task_x = int(yes_results_dict[task_id]["task_x"]) + i
            new_task_y = int(yes_results_dict[task_id]["task_y"]) + j
            new_task_id = (
                f"{yes_results_dict[task_id]['task_z']}-{new_task_x}-{new_task_y}"
            )

            if new_task_id in yes_results_dict:
                neighbours_group_id = yes_results_dict[new_task_id]["my_group_id"]
                if neighbours_group_id != my_group_id:
                    # add the other group to duplicated groups dict
                    try:
                        duplicated_groups[my_group_id].add(neighbours_group_id)
                    except KeyError:
                        duplicated_groups[my_group_id] = set([neighbours_group_id])
                    # add my_group_id to other groupd_id in duplicated dict
                    try:
                        duplicated_groups[neighbours_group_id].add(my_group_id)
                    except KeyError:
                        duplicated_groups[neighbours_group_id] = set([my_group_id])

    return duplicated_groups


def remove_duplicates(duplicated_groups: dict):
    """
    Remove groups ids for tasks which have more than one.
    This is to make sure that every task belongs to a single group only.
    This distinct group id will be the basis for further geometric processing.
    """

    for duplicated_group_id in sorted(duplicated_groups.keys(), reverse=True):
        logger.debug(
            f"{duplicated_group_id}: {list(duplicated_groups[duplicated_group_id])}"
        )
        my_duplicated_group_id = duplicated_group_id
        for other_group_id in duplicated_groups[duplicated_group_id]:
            if other_group_id < my_duplicated_group_id:
                my_duplicated_group_id = other_group_id

        for task_id in yes_results_dict.keys():
            if yes_results_dict[task_id]["my_group_id"] == duplicated_group_id:
                yes_results_dict[task_id]["my_group_id"] = my_duplicated_group_id


def split_groups(q):
    """
    This function will be executed using threading.
    First it checks if there are still processes pending in the queue.
    We are using a clustering algorithm to put tasks together in groups.
    Since it is computationally expensive to check which tiles are neighbours,
    we split our results into chunks (called groups here).
    When we reach a group size below the defined group size we will stop.
    Otherwise, the group will be split into two parts and
    both will be added as new groups to our queue.
    """

    while not q.empty():
        group_id, group_data, group_size = q.get()
        logger.debug(f"the group ({group_id}) has {len(group_data)} members")

        # find min x, and min y
        x_list = []
        y_list = []

        for result, data in group_data.items():
            x_list.append(int(data["task_x"]))
            y_list.append(int(data["task_y"]))

        min_x = min(x_list)
        max_x = max(x_list)
        x_width = max_x - min_x

        min_y = min(y_list)
        max_y = max(y_list)
        y_width = max_y - min_y

        new_grouped_data = {"a": {}, "b": {}}

        if x_width >= y_width:
            # first split vertically
            for result, data in group_data.items():
                # result is in first segment
                if int(data["task_x"]) < (min_x + (x_width / 2)):
                    new_grouped_data["a"][result] = data
                else:
                    new_grouped_data["b"][result] = data
        else:
            # first split horizontally
            for result, data in group_data.items():
                # result is in first segment
                if int(data["task_y"]) < (min_y + (y_width / 2)):
                    new_grouped_data["a"][result] = data
                else:
                    new_grouped_data["b"][result] = data

        for k in ["a", "b"]:
            logger.debug("there are %s results in %s" % (len(new_grouped_data[k]), k))

            for result, data in new_grouped_data[k].items():
                x_list.append(int(data["task_x"]))
                y_list.append(int(data["task_y"]))

            min_x = min(x_list)
            max_x = max(x_list)
            x_width = max_x - min_x

            min_y = min(y_list)
            max_y = max(y_list)
            y_width = max_y - min_y

            if len(new_grouped_data[k]) < group_size:

                # add this check to avoid large groups groups with few items
                if x_width * y_width > 2 * (
                    my_neighbourhood_size * my_neighbourhood_size
                ):
                    q.put([group_id, new_grouped_data[k], group_size])
                else:
                    split_groups_list.append(new_grouped_data[k])
                    logger.debug('add "a" to split_groups_dict')
            else:
                # add this group to a queue
                q.put([group_id, new_grouped_data[k], group_size])

        q.task_done()


def create_hot_tm_tasks(
    project_id: str,
    project_data: list,
    group_size: int = 15,
    neighbourhood_shape: str = "rectangle",
    neighbourhood_size: int = 5,
) -> dict:
    """
    This functions creates a dictionary of tiles which will be forming a task in the HOT Tasking Manager.
    It will create a neighbourhood list, which will function as a mask to filter tiles that are close to each other.
    The functions assigns group ids to each tile.
    For tiles that got several group ids, this will be resolved in the next step.
    Once each task has a unique group id, the function checks the size (number of tiles) for each group.
    Groups that hold too many tiles (too big to map in the Tasking Manager) will be split into smaller groups.
    Finally, a dictionary is returned which holds each group as an item.
    Each group consists of a limited number of tiles.
    """

    # final groups dict will store the groups that are exported
    final_groups_dict = {}
    highest_group_id = 0

    # create a dictionary with all results
    global yes_results_dict
    yes_results_dict = {}
    for result in project_data:
        yes_results_dict[result["id"]] = result
    logger.info(
        "created results dictionary. there are %s results." % len(yes_results_dict)
    )
    if len(yes_results_dict) < 1:
        return final_groups_dict

    global neighbour_list
    global my_neighbourhood_size
    my_neighbourhood_size = neighbourhood_size

    neighbour_list = get_neighbour_list(neighbourhood_shape, neighbourhood_size)
    logger.info(
        "got neighbour list. neighbourhood_shape: %s, neighbourhood_size: %s"
        % (neighbourhood_shape, neighbourhood_size)
    )

    global split_groups_list
    split_groups_list = []

    # test for neighbors and set groups id
    for task_id in sorted(yes_results_dict.keys()):
        try:
            # this task has already a group id, great.
            group_id = yes_results_dict[task_id]["my_group_id"]
        except KeyError:
            group_id = highest_group_id + 1
            highest_group_id += 1
            yes_results_dict[task_id]["my_group_id"] = group_id
            logger.debug("created new group id")
        logger.debug("group id: %s" % group_id)

        # check for other results in the neighbourhood and add the group id to them
        add_group_id_to_neighbours(
            yes_results_dict[task_id]["task_x"],
            yes_results_dict[task_id]["task_y"],
            yes_results_dict[task_id]["task_z"],
            group_id,
        )

    logger.info("added group ids to yes maybe results dict")

    # check if some tasks have different groups from their neighbours
    duplicates_dict = create_duplicates_dict()
    while len(duplicates_dict) > 0:
        remove_duplicates(duplicates_dict)
        duplicates_dict = create_duplicates_dict()
        logger.debug("there are %s duplicated groups" % len(duplicates_dict))

    logger.info("removed all duplicated group ids in yes maybe results dict")

    grouped_results_dict = {}
    for task_id in yes_results_dict.keys():
        group_id = yes_results_dict[task_id]["my_group_id"]
        try:
            grouped_results_dict[group_id][task_id] = yes_results_dict[task_id]
        except KeyError:
            grouped_results_dict[group_id] = {}
            grouped_results_dict[group_id][task_id] = yes_results_dict[task_id]

    logger.info("created dict item for each group")

    # reset highest group id since we merged several groups
    highest_group_id = max(grouped_results_dict)
    logger.debug("new highest group id: %s" % highest_group_id)

    q = Queue(maxsize=0)
    num_threads = 1

    for group_id in grouped_results_dict.keys():

        if len(grouped_results_dict[group_id]) < group_size:
            final_groups_dict[group_id] = grouped_results_dict[group_id]
        else:
            group_data = grouped_results_dict[group_id]
            # add this group to the queue
            q.put([group_id, group_data, group_size])

    logger.info("added groups to queue.")

    for i in range(num_threads):
        worker = threading.Thread(target=split_groups, args=(q,))
        worker.start()

    q.join()
    logger.info("split all groups.")

    logger.debug("there are %s split groups" % len(split_groups_list))

    # add the split groups to the final groups dict
    for group_data in split_groups_list:
        new_group_id = highest_group_id + 1
        highest_group_id += 1
        final_groups_dict[new_group_id] = group_data

    logger.info("created %s groups." % len(final_groups_dict))
    return final_groups_dict


def dissolve_project_data(project_data):
    """
    This functions uses the unionCascaded function to return a dissolved MultiPolygon geometry
    from several Single Part Polygon geometries.
    """

    multipolygon_geometry = ogr.Geometry(ogr.wkbMultiPolygon)
    for item in project_data:
        polygon = ogr.CreateGeometryFromWkt(item["wkt"])
        multipolygon_geometry.AddGeometry(polygon)

    dissolved_geometry = multipolygon_geometry.UnionCascaded()
    return dissolved_geometry


def generate_tasking_manager_geometries(project_id: str):
    """
    This functions runs the workflow to create a GeoJSON file ready to be used in the HOT Tasking Manager.
    First, data is loaded from the aggregated results csv file.
    Then it filers results for which a defined threshold of yes and maybe classifications has been reached.
    We then derive the Tasking Manager geometries, and a dissolved geometry of all filtered results.
    Finally, both data sets are saved into GeoJSON files.
    """

    raw_data_filename = f"{DATA_PATH}/api/agg_results/agg_results_{project_id}.csv"
    filtered_data_filename = (
        f"{DATA_PATH}/api/yes_maybe/yes_maybe_{project_id}.geojson"
    )
    tasking_manager_data_filename = (
        f"{DATA_PATH}/api/hot_tm/hot_tm_{project_id}.geojson"
    )

    # load project data from existing files
    results = load_data(project_id, raw_data_filename)

    # filter yes and maybe results
    filtered_results = filter_data(results)

    if len(filtered_results) > 0:
        # dissolve filtered results
        dissolved_filtered_results = dissolve_project_data(filtered_results)

        # create tasking manager geometries
        tasking_manager_results = create_hot_tm_tasks(project_id, filtered_results)

        # save data as geojson
        geojson_functions.create_geojson_file(
            dissolved_filtered_results, filtered_data_filename
        )
        geojson_functions.create_geojson_file_from_dict(
            tasking_manager_results, tasking_manager_data_filename
        )
