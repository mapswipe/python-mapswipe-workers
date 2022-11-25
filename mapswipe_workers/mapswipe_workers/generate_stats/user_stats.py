import pandas as pd


def get_agg_results_by_user_id(
    results_df: pd.DataFrame, agg_results_df: pd.DataFrame
) -> pd.DataFrame:
    """
    For each users we calcuate the number of total contributions (tasks)
    and completed groups.
    Then we compute agreeing and disagreeing contributions from other users.
    This is the basis for a simple agreement score.
    The agreement score tells you how often the results from other users
    coincide with the results of this user. E.g 0.8 means, that 80% of the
    results from other users are the same as the results for that user.
    Returns a pandas dataframe.
    """
    raw_contributions_df = results_df.merge(
        agg_results_df, left_on="task_id", right_on="task_id"
    )
    # compare to classifications of other users
    # Calc number of agreeig and disagreeing results from other users.
    raw_contributions_df.loc[
        raw_contributions_df["result"] == 0, "agreeing_contributions"
    ] = (raw_contributions_df["0_count"] - 1)
    raw_contributions_df.loc[
        raw_contributions_df["result"] == 1, "agreeing_contributions"
    ] = (raw_contributions_df["1_count"] - 1)
    raw_contributions_df.loc[
        raw_contributions_df["result"] == 2, "agreeing_contributions"
    ] = (raw_contributions_df["2_count"] - 1)
    raw_contributions_df.loc[
        raw_contributions_df["result"] == 3, "agreeing_contributions"
    ] = (raw_contributions_df["3_count"] - 1)

    raw_contributions_df["disagreeing_contributions"] = raw_contributions_df[
        "total_count"
    ] - (raw_contributions_df["agreeing_contributions"] + 1)

    agg_results_by_user_id_df = raw_contributions_df.groupby(
        ["project_id", "user_id"]
    ).agg(
        groups_completed=pd.NamedAgg(column="group_id", aggfunc=pd.Series.nunique),
        total_contributions=pd.NamedAgg(column="user_id", aggfunc="count"),
        agreeing_contributions=pd.NamedAgg(
            column="agreeing_contributions", aggfunc="sum"
        ),
        disagreeing_contributions=pd.NamedAgg(
            column="disagreeing_contributions", aggfunc="sum"
        ),
    )

    # Calc simple agreement score as share of agreeing contributions.
    agg_results_by_user_id_df["simple_agreement_score"] = agg_results_by_user_id_df[
        "agreeing_contributions"
    ] / (
        agg_results_by_user_id_df["agreeing_contributions"]
        + agg_results_by_user_id_df["disagreeing_contributions"]
    )

    agg_results_by_user_id_df.reset_index(inplace=True)

    return agg_results_by_user_id_df
