#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import sys
import json
# add some files in different folders to sys.
# these files can than be loaded directly
sys.path.insert(0, '../cfg/')
sys.path.insert(0, '../utils/')

from auth import firebase_admin_auth

firebase = firebase_admin_auth()
fb_db = firebase.database()

group_ids = [110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 708, 709, 710, 711, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 1235, 1236, 1237]

groups_file = '../import_module/data/groups_13505.json'

with open(groups_file, 'r') as fp:
    data = json.load(fp)
    for group_id, value in data.items():
        if int(group_id) in group_ids:
            print(group_id)
            print(value)
            fb_db.child("groups").child("13505").child(group_id).set(value)

