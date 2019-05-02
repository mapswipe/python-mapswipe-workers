import json
import pprint


def tasks_duplicated(projectId):
    input_file = 'build_area_project_{}_tasks.json'.format(projectId)
    with open(input_file) as f:
        groups = json.load(f)

    group_ids = list(groups.keys())
    print('There are %s groups.' % len(group_ids))

    duplicates = {}
    list_dicts_overlap = []

    while len(group_ids) > 0:
        for group_id in group_ids:

            tasks = groups[group_id]
            '''
            {"projectId": "E6L057UQ", "groupId": 101, "taskId": "14-9783-8921", "taskX": "9783", "taskY": "8921",  "url": "https://services.sentinel-hub.com/ogc/wmts/sinergise_key?request=getTile&tilematrixset=PopularWebMercator256&tilematrix=14&tilecol=9783&tilerow=8921&layer=FALSE_COLOR"}
             '''

            group_ids.remove(group_id)

            for group_id_B in group_ids:
                tasks_B = groups[group_id_B]

                set_list1 = set(tuple(sorted(d.items())) for d in tasks)
                set_list2 = set(tuple(sorted(d.items())) for d in tasks_B)

                set_overlapping = set_list1.intersection(set_list2)
                if len(set_overlapping) > 0:
                    print(len(set_overlapping))
                    print(set_overlapping)

                    for tuple_element in set_overlapping:
                        list_dicts_overlap.append(dict((x, y) for x, y in tuple_element))


    if len(list_dicts_overlap) > 0:
        print("Didn't pass test. There are %s duplicated tasks." % len(list_dicts_overlap))
        print(list_dicts_overlap)
        return False
    else:
        print("No duplicated tasks")
        return True


if __name__ == '__main__':
    projectId = 'E6L057UQ'
    #projectId = 'O7XR5GXJ'
    tasks_duplicated(projectId)