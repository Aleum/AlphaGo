#-*- coding: utf-8 -*-
import os, math, random
from feature.FeatureMap_RL import *
from feature.Plays_RL import *
from utils.base import get_file_names
from types import NoneType
import sys

def load_dataset():
    
    print "start loading go dataset files"
    
    # sgf에서 plays 추출
    file_names = get_file_names(GO_FOLDER, POSTFIX)
    for name in file_names:
        plays = Plays_RL()
        plays.load_from_sgf(GO_FOLDER+"/"+name)
        if plays.total_nonpass_plays < 10:
            continue
        for play_num in range(1, plays.total_plays+1):
            features = FeatureMap_RL(plays, play_num)
            if type(features.input_planes) is NoneType:
                continue
            f = open(OTHER_TRAIN_FOLDER+"/"+name+"_"+str(play_num)+"_x"+".csv", 'w')
            txt = ""
            for feature in features.input_planes:
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
            txt = ""
            for rows in features.label:
                for r in range(0, len(rows)):
                    if r == len(rows)-1:
                        txt += str(rows[r])
                    else:
                        txt += str(rows[r]) + ","
                txt+="\n"
            f.write(txt)
            f.close()

    print "finish.."

if __name__ == "__main__":
    POSTFIX = ".sgf"
    
    GO_FOLDER = sys.argv[1]
    OTHER_TRAIN_FOLDER = sys.argv[2]
    RLMODEL = sys.argv[3]
    load_dataset()
    os.system("python RL_policy_net.py " + GO_FOLDER + " " + OTHER_TRAIN_FOLDER + " " + RLMODEL)
    
