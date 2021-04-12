import datetime

import pandas as pd

from mapswipe_workers.definitions import logger


def calc_results_progress(
    number_of_users: int,
    number_of_users_required: int,
    cum_number_of_users: int,
    number_of_tasks: int,
    number_of_results: int,
) -> int:
    """
    for each project the progress is calculated
    not all results are considered when calculating the progress
    if the required number of users has been reached for a task
    all further results will not contribute to increase the progress
    """

    if cum_number_of_users <= number_of_users_required:
        # this is the simplest case, the number of users is less than the required
        # number of users all results contribute to progress
        number_of_results_progress = number_of_results
    elif (cum_number_of_users - number_of_users) < number_of_users_required:
        # the number of users is bigger than the number of users required
        # but the previous number of users was below the required number
        # some results contribute to progress
        number_of_results_progress = (
            number_of_users_required - (cum_number_of_users - number_of_users)
        ) * number_of_tasks
    else:
        # for all other cases: already more users than required
        # all results do not contribute to progress
        number_of_results_progress = 0

    return number_of_results_progress


def is_new_user(day: datetime.datetime, first_day: datetime.datetime):
    """
    Check if user has contributed results to this project before
    """

    if day == first_day:
        return 1
    else:
        return 0


def get_progress_by_date(
    results_df: pd.DataFrame, groups_df: pd.DataFrame
) -> pd.DataFrame:
    """
    for each project we retrospectively generate the following attributes for a given
    date utilizing the results.

    number_of_results:
        - number of results that have been contributed per day
        - not used in firebase

    cum_number_of_results:
        - sum of daily number of results up to that day

    progress:
        - relative progress per day
        (e.g. overall progress increased by 0.15 on that day)
        - not used in firebase

    cum_progress:
        - absolute progress up to that day
        - refers to the project progress attribute in firebase
    """

    groups_df["required_results"] = (
        groups_df["number_of_tasks"] * groups_df["number_of_users_required"]
    )
    required_results = groups_df["required_results"].sum()
    logger.info(f"calcuated required results: {required_results}")

    results_with_groups_df = results_df.merge(
        groups_df, left_on="group_id", right_on="group_id"
    )
    results_by_group_id_df = results_with_groups_df.groupby(
        ["project_id_x", "group_id", "day"]
    ).agg(
        number_of_tasks=pd.NamedAgg(column="number_of_tasks", aggfunc="min"),
        number_of_users_required=pd.NamedAgg(
            column="number_of_users_required", aggfunc="min"
        ),
        number_of_users=pd.NamedAgg(column="user_id", aggfunc=pd.Series.nunique),
    )
    results_by_group_id_df["number_of_results"] = (
        results_by_group_id_df["number_of_users"]
        * results_by_group_id_df["number_of_tasks"]
    )
    results_by_group_id_df["cum_number_of_users"] = (
        results_by_group_id_df["number_of_users"]
        .groupby(["project_id_x", "group_id"])
        .cumsum()
    )
    results_by_group_id_df["number_of_results_progress"] = results_by_group_id_df.apply(
        lambda row: calc_results_progress(
            row["number_of_users"],
            row["number_of_users_required"],
            row["cum_number_of_users"],
            row["number_of_tasks"],
            row["number_of_results"],
        ),
        axis=1,
    )

    progress_by_date_df = (
        results_by_group_id_df.reset_index()
        .groupby(["day"])
        .agg(
            number_of_results=pd.NamedAgg(column="number_of_results", aggfunc="sum"),
            number_of_results_progress=pd.NamedAgg(
                column="number_of_results_progress", aggfunc="sum"
            ),
        )
    )
    progress_by_date_df["cum_number_of_results"] = progress_by_date_df[
        "number_of_results"
    ].cumsum()
    progress_by_date_df["cum_number_of_results_progress"] = progress_by_date_df[
        "number_of_results_progress"
    ].cumsum()
    progress_by_date_df["progress"] = (
        progress_by_date_df["number_of_results_progress"] / required_results
    )
    progress_by_date_df["cum_progress"] = (
        progress_by_date_df["cum_number_of_results_progress"] / required_results
    )

    logger.info("calculated progress by date")
    return progress_by_date_df


def get_contributors_by_date(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    for each project we retrospectively generate the following attributes for a given
    date utilizing the results:

    number_of_users:
        - number of distinct users active per day
        - not used in firebase

    number_of_new_users:
        - number of distinct users who mapped the first group in that project per day
        - not used in firebase

    cum_number_of_users:
        - overall number of distinct users active up to that day
        - refers to the project contributorCount attribute in firebase
    """

    user_first_day_df = results_df.groupby(["user_id"]).agg(
        first_day=pd.NamedAgg(column="day", aggfunc="min")
    )
    logger.info("calculated first day per user")

    results_by_user_id_df = results_df.groupby(["project_id", "user_id", "day"]).agg(
        number_of_results=pd.NamedAgg(column="user_id", aggfunc="count")
    )
    results_by_user_id_df = results_by_user_id_df.reset_index().merge(
        user_first_day_df, left_on="user_id", right_on="user_id"
    )
    results_by_user_id_df["new_user"] = results_by_user_id_df.apply(
        lambda row: is_new_user(row["day"], row["first_day"]), axis=1
    )

    contributors_by_date_df = (
        results_by_user_id_df.reset_index()
        .groupby(["project_id", "day"])
        .agg(
            number_of_users=pd.NamedAgg(column="user_id", aggfunc=pd.Series.nunique),
            number_of_new_users=pd.NamedAgg(column="new_user", aggfunc="sum"),
        )
    )
    contributors_by_date_df["cum_number_of_users"] = contributors_by_date_df[
        "number_of_new_users"
    ].cumsum()

    logger.info("calculated contributors by date")
    return contributors_by_date_df


def get_project_history(
    results_df: pd.DataFrame, groups_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the progress df for every day based on results and groups df.
    The Calculate the contributors for every day based on results df.
    Merge both dataframes.
    Return project history dataframe.

    Parameters
    ----------
    results_df
    groups_df
    """

    # calculate progress by date
    progress_by_date_df = get_progress_by_date(results_df, groups_df)

    # calculate contributors by date
    contributors_by_date_df = get_contributors_by_date(results_df)

    # merge contributors and progress
    project_history_df = progress_by_date_df.merge(
        contributors_by_date_df, left_on="day", right_on="day"
    )

    return project_history_df
