#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

import os
import psutil

def get_memory_consumption():
    process = psutil.Process(os.getpid())
    #print(process.memory_info().rss)
    return process.memory_info().rss