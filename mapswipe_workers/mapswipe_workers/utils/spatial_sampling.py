import numpy as np
import pandas as pd


def distance_on_sphere(p1, p2):
    """
    p1 and p2 are two lists that have two elements. They are numpy arrays of the long
    and lat coordinates of the points in set1 and set2

    Calculate the distance between two points on the Earth's surface using the
    haversine formula.

    Args:
        p1 (list): Array containing the longitude and latitude coordinates of points
        FROM which the distance to be calculated in degree
        p2 (list): Array containing the longitude and latitude coordinates of points
        TO which the distance to be calculated in degree

    Returns:
        numpy.ndarray: Array containing the distances between the two points on the
        sphere in kilometers.

    This function computes the distance between two points on the Earth's surface
    using the haversine formula, which takes into account the spherical shape of the
    Earth. The input arrays `p1` and `p2` should contain longitude and latitude
    coordinates in degrees. The function returns an array containing the distances
    between corresponding pairs of points.
    """
    earth_radius = 6371  # km

    p1 = np.radians(np.array(p1))
    p2 = np.radians(np.array(p2))

    delta_lat = p2[1] - p1[1]
    delta_long = p2[0] - p1[0]

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(p1[1]) * np.cos(p2[1]) * np.sin(delta_long / 2) ** 2
    )
    c = 2 * np.arcsin(np.sqrt(a))

    distances = earth_radius * c
    return distances


"""----------------------------Filtering Points-------------------------------"""


def filter_points(df, threshold_distance):
    """
    Filter points from a DataFrame based on a threshold distance.

    Args:
        df (pandas.DataFrame): DataFrame containing latitude and longitude columns.
        threshold_distance (float): Threshold distance for filtering points in kms.

    Returns:
        pandas.DataFrame: Filtered DataFrame containing selected points.
        float: Total road length calculated from the selected points.

    This function filters points from a DataFrame based on the given threshold
    distance. It calculates distances between consecutive points and accumulates them
    until the accumulated distance surpasses the threshold distance. It then selects
    those points and constructs a new DataFrame. Additionally, it manually checks the
    last point to include it if it satisfies the length condition. The function
    returns the filtered DataFrame along with the calculated road length.
    """
    road_length = 0
    mask = np.zeros(len(df), dtype=bool)
    mask[0] = True
    lat = df["lat"].to_numpy()
    long = df["long"].to_numpy()

    distances = distance_on_sphere([long[1:], lat[1:]], [long[:-1], lat[:-1]])
    road_length = np.sum(distances)

    # save the last point if the road segment is relavitely small (< 2*road_length)
    if threshold_distance <= road_length < 2 * threshold_distance:
        mask[-1] = True

    accumulated_distance = 0
    for i, distance in enumerate(distances):
        accumulated_distance += distance
        if accumulated_distance >= threshold_distance:
            mask[i + 1] = True
            accumulated_distance = 0  # Reset accumulated distance

    to_be_returned_df = df[mask]
    # since the last point has to be omitted in the vectorized distance calculation,
    # it is being checked manually
    p2 = to_be_returned_df.iloc[0]
    distance = distance_on_sphere(
        [float(p2["long"]), float(p2["lat"])], [long[-1], lat[-1]]
    )

    # last point will be added if it suffices the length condition
    # last point will be added in case there is only one point returned
    if distance >= threshold_distance or len(to_be_returned_df) == 1:
        to_be_returned_df = pd.concat(
            [
                to_be_returned_df,
                pd.DataFrame(df.iloc[-1], columns=to_be_returned_df.columns),
            ],
            axis=0,
        )
    return to_be_returned_df


def spatial_sampling(df, interval_length):
    """
    Calculate spacing between points in a GeoDataFrame.

    Args:
        df (pandas.DataFrame): DataFrame containing points with timestamps.
        interval_length (float): Interval length for filtering points in kms.

    Returns:
        geopandas.GeoDataFrame: Filtered GeoDataFrame containing selected points.
        float: Total road length calculated from the selected points.

    This function calculates the spacing between points in a GeoDataFrame by filtering
    points based on the provided interval length. It first sorts the GeoDataFrame by
    timestamp and then filters points using the filter_points function. The function
    returns the filtered GeoDataFrame along with the total road length.
    """
    if len(df) == 1:
        return df

    df["long"] = df["geometry"].apply(
        lambda geom: geom.x if geom.geom_type == "Point" else None
    )
    df["lat"] = df["geometry"].apply(
        lambda geom: geom.y if geom.geom_type == "Point" else None
    )
    sorted_df = df.sort_values(by=["captured_at"])

    sampled_sequence_df = pd.DataFrame()

    # loop through each sequence
    for sequence in sorted_df["sequence_id"].unique():
        sequence_df = sorted_df[sorted_df["sequence_id"] == sequence]

        if interval_length:
            sequence_df = filter_points(sequence_df, interval_length)
        # below line prevents FutureWarning
        # (https://stackoverflow.com/questions/73800841/add-series-as-a-new-row-into-dataframe-triggers-futurewarning)
        sequence_df["is_pano"] = sequence_df["is_pano"].astype(bool)
        sampled_sequence_df = pd.concat([sampled_sequence_df, sequence_df], axis=0)

    # reverse order such that sequence are in direction of travel
    sampled_sequence_df = sampled_sequence_df.iloc[::-1]

    return sampled_sequence_df
