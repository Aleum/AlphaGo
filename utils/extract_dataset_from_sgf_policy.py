#-*- coding: utf-8 -*-
import os, math, random
from feature.FeatureMap import *
from feature.Plays import *
import numpy as np
from utils.base import get_file_names
from types import NoneType
import sys

def load_dataset():
    
    print "start"
    
    num_saves = 0
    file_names = get_file_names(SGF_FOLDER, POSTFIX)
    for name in file_names:
        plays = Plays()
        plays.load_from_sgf(SGF_FOLDER+"/"+name)
        if plays.total_nonpass_plays < 10:
            continue
        for play_num in range(0, plays.total_plays+1):
            features = FeatureMap(plays, play_num)
            if type(features) is NoneType:
                continue
            f = open(SAVE_FOLDER+"/"+name+"_"+str(play_num)+"_x"+".csv", 'w')
            txt = ""
            inputs = features.input_planes_policynet
            for feature in inputs:
                for rows in feature:
                    for r in range(0, len(rows)):
                        if r == len(rows)-1:
                            txt += str(rows[r])
                        else:
                            txt += str(rows[r]) + ","
                    txt+="\n"
                txt+="\n"
            f.write(txt)
            f.close()
            
            txt = ""
            f = open(SAVE_FOLDER+"/"+name+"_"+str(play_num)+"_y"+".csv", 'w')
            for rows in features.label:
                for r in range(0, len(rows)):
                    r_value = rows[r]
                    if r == len(rows)-1:
                        txt += str(r_value)
                    else:
                        txt += str(r_value) + ","
                txt+="\n"
            f.write(txt)
            f.close()
        num_saves += 1
        if num_saves % 100 == 0:
            print "finish "+str(num_saves)+" sgf files.."

    print "finish all.."

if __name__ == "__main__":
    POSTFIX = ".sgf"
    
    SGF_FOLDER = sys.argv[1]
    SAVE_FOLDER = sys.argv[2]
    
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)
    
    load_dataset()
