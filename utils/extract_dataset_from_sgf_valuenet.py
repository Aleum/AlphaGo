#-*- coding: utf-8 -*-
import os, math, random
from feature.FeatureMap import *
from feature.Plays import *
from utils.base import get_file_names
from types import NoneType
import sys

def load_dataset():
    
    print "start loading go dataset files"
    
    # sgf에서 plays 추출
    file_names = get_file_names(GO_FOLDER, POSTFIX)
    for name in file_names:
        plays = Plays()
        plays.load_from_sgf(GO_FOLDER+"/"+name)
        splitted_name = name.split("_")
        play_num = int(splitted_name[1])
        features = FeatureMap(plays, play_num)
        f = open(OTHER_TRAIN_FOLDER+"/"+name+"_"+str(play_num)+"_x"+".csv", 'w')
        txt = ""
        for feature in features.input_planes_valuenet:
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
        f = open(OTHER_TRAIN_FOLDER+"/"+name+"_"+str(play_num)+"_y"+".csv", 'w')
        cur_label = splitted_name[2][0]
        f.write(cur_label)
        f.close()

    print "finish.."

if __name__ == "__main__":
    POSTFIX = ".sgf"
    
    GO_FOLDER = sys.argv[1]
    OTHER_TRAIN_FOLDER = sys.argv[2]
    load_dataset()
    
