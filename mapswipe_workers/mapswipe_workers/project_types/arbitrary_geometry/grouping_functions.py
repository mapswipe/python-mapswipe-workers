import argparse
import json

########################################################################################
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument(
    "-i",
    "--input_file",
    required=False,
    default=None,
    type=str,
    help="the input file containning the geometries as geojson",
)
parser.add_argument(
    "-g",
    "--group_size",
    required=False,
    default=50,
    type=int,
    help="the size of each group",
)
########################################################################################


def group_input_geometries(input_geometries_file, group_size):
    """
    The function to create groups of input geometries using the given size (number of
    features) per group

    Parameters
    ----------
    input_geometries_file : str
        the path to the GeoJSON file containing the input geometries
    group_size : int
        the maximum number of features per group

    Returns
    -------
    groups : dict
        the dictionary containing a list of "feature_ids" and a list of
        "feature_geometries" per group with given group id key
    """

    with open(input_geometries_file, "r") as infile:
        layer = json.load(infile)
    groups = {}

    # we will simply start with min group id = 100
    group_id = 100
    group_id_string = f"g{group_id}"
    feature_count = 0
    for feature in layer["features"]:
        feature_count += 1
        # feature count starts at 1
        # assuming group size would be 10
        # when feature_count = 11 then we enter the next group
        if feature_count % (group_size + 1) == 0:
            group_id += 1
            group_id_string = f"g{group_id}"

        try:
            groups[group_id_string]
        except KeyError:
            groups[group_id_string] = {"feature_ids": [], "feature": []}

        # we use a new id here based on the count
        # since we are not sure that GetFID returns unique values
        groups[group_id_string]["feature_ids"].append(feature_count)

        # this is relevant for the tutorial
        if "screen" in feature.keys():
            feature["properties"]["reference"] = int(feature["reference"])
            feature["properties"]["screen"] = int(feature["screen"])

        groups[group_id_string]["feature"].append(feature)

    return groups


########################################################################################
if __name__ == "__main__":

    args = parser.parse_args()

    groups = group_input_geometries(args.input_file, args.group_size)

    print(groups)
