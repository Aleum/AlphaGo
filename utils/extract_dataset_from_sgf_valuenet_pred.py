#-*- coding: utf-8 -*-
import os, math, random
from feature.FeatureMap_RL import *
from feature.Plays_RL import *
from utils.base import get_file_names
from types import NoneType
import sys

from keras.models import model_from_json
from keras.optimizers import SGD
from keras import backend as K
import numpy as np

RL_VALUE_H5 = "RL_value_models/value_net_weights_6.h5"
RL_VALUE_JSON = "RL_value_models/value_net_model.json"

def load_dataset():
    
    print "start loading go dataset files"
    
    file_names = get_file_names(GO_FOLDER, POSTFIX)
    for name in file_names:
        plays = Plays_RL()
        plays.load_from_sgf(GO_FOLDER+"/"+name)
        if plays.total_nonpass_plays < 10:
            continue
        for play_num in range(1, plays.total_plays+1):
            features = FeatureMap_RL(plays, play_num)
            if type(features) is NoneType:
                continue
            f = open(OTHER_TRAIN_FOLDER+"/"+name+"_"+str(play_num)+"_x"+".csv", 'w')
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
            inputs = features.input_planes_valuenet
            predicted_value = rl_value_net.predict(np.asarray([inputs], dtype=np.float))
            
            f = open(OTHER_TRAIN_FOLDER+"/"+name+"_"+str(play_num)+"_y"+".csv", 'w')
            txt = ""
            for rows in features.label:
                for r in range(0, len(rows)):
                    r_value = rows[r]
                    if r_value == 1 or r_value == -1:
                        r_value = r_value - predicted_value[0][0]
                    if r == len(rows)-1:
                        txt += str(r_value)
                    else:
                        txt += str(r_value) + ","
                txt+="\n"
            f.write(txt)
            f.close()

    print "finish.."

if __name__ == "__main__":
    POSTFIX = ".sgf"
    
    sgd = SGD(lr=0.003, decay=0.0, momentum=0.0, nesterov=False)
    rl_value_net = model_from_json(open(RL_VALUE_JSON).read())
    rl_value_net.load_weights(RL_VALUE_H5)
    rl_value_net.compile(loss='MSE', optimizer=sgd)   
    
    GO_FOLDER = sys.argv[1]
    OTHER_TRAIN_FOLDER = sys.argv[2]
    RLMODEL = sys.argv[3]
    load_dataset()
