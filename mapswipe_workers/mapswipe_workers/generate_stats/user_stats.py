import pandas as pd


def calc_agreement_counts(row):
    """Calc number of agreeig and disagreeing results from other users."""
    this_user_label = row["result"]
    other_user_labels = []

    for label in [0, 1, 2, 3]:
        if label == this_user_label:
            label_count = row[f"{label}_count"] - 1
        else:
            label_count = row[f"{label}_count"]
        other_user_labels.extend([label] * label_count)

    agreeing_contributions = other_user_labels.count(this_user_label)
    disagreeing_contributions = len(other_user_labels) - agreeing_contributions

    return agreeing_contributions, disagreeing_contributions


def calc_agreement_score(row):
    """Calc simple agreement score as share of agreeing contributions."""
    agreement_score = row["agreeing_contributions"] / (
        row["agreeing_contributions"] + row["disagreeing_contributions"]
    )
    return agreement_score


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
    raw_contributions_df[
        ["agreeing_contributions", "disagreeing_contributions"]
    ] = raw_contributions_df.apply(
        lambda row: calc_agreement_counts(row), axis=1, result_type="expand"
    )

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

    agg_results_by_user_id_df[
        "simple_agreement_score"
    ] = agg_results_by_user_id_df.apply(lambda row: calc_agreement_score(row), axis=1)

    agg_results_by_user_id_df.reset_index(inplace=True)

    return agg_results_by_user_id_df
