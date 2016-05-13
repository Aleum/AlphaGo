
import numpy as np
from operator import itemgetter
import os
import copy
import math
import json
import sys
import time
import csv
import random

def get_file_names(path, postfix):
    res = []

    for root, dirs, files in os.walk(path):

        for file in files:
            if file[-len(postfix):] == postfix:
                res.append(file)

    return res
