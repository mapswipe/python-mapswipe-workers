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

import logging
from auth import firebase_admin_auth

firebase = firebase_admin_auth()
fb_db = firebase.database()

group_ids = [110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 708, 709, 710, 711, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 1235, 1236, 1237]

for group_id in group_ids:
    fb_db.child("groups").child("13505").child(group_id).remove()
