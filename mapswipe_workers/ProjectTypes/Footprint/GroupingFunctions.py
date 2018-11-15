
import ogr
import argparse
import json


########################################################################################################################
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-i', '--input_file', required=False, default=None, type=str,
                    help='the input file containning the geometries as geojson')
parser.add_argument('-g', '--group_size', required=False, default=50, type=int,
                    help='the size of each group')
########################################################################################################################

def group_input_geometries(input_geometries_file, group_size):

    driver = ogr.GetDriverByName('GeoJSON')
    datasource = driver.Open(input_geometries_file, 0)
    layer = datasource.GetLayer()

    groups = {}

    # we will simply, we will start with min group id = 100
    group_id = 100
    feature_count = 0
    for feature in layer:
        feature_count += 1
        if feature_count % (group_size+1) == 0:
            group_id += 1

        try:
            groups[group_id]
        except:
            groups[group_id] = {
                "feature_ids": [],
                "feature_geometries": []
            }

        groups[group_id]['feature_ids'].append(feature.GetFID())
        groups[group_id]['feature_geometries'].append(json.loads(feature.GetGeometryRef().ExportToJson()))

    return groups


########################################################################################################################
if __name__ == '__main__':

    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    groups = group_input_geometries(args.input_file, args.group_size)

    print(groups)