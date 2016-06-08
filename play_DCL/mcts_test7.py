#-*- coding: utf-8 -*-
import os, math, random
from feature.FeatureMap import *
from feature.Plays import *
from types import NoneType
import sys

from keras.models import model_from_json
from keras.optimizers import SGD
from keras import backend as K
import numpy as np


if __name__ == "__main__":
    # 모델 파일 지정
    RL_VALUE_JSON = "network/value_net_model.json"
    RL_VALUE_H5 = "network/value_net_weights_5.h5"
    
    # 모델 로드
    sgd = SGD(lr=0.003, decay=0.0, momentum=0.0, nesterov=False)
    rl_value = model_from_json(open(RL_VALUE_JSON).read())
    rl_value.load_weights(RL_VALUE_H5)
    rl_value.compile(loss='MSE', optimizer=sgd)
    
    plays = Plays()
    plays.load_from_sgf("sgfs/test.sgf")
    
    # value net feature 추출 (policy net보다 1개 많음)
    features = FeatureMap(plays, len(plays))
    inputs = features.input_planes_valuenet
    # policy net의 경우, inputs = featuers.input_planes_policynet
    
    # value net output
    predicted_value = rl_value.predict(np.asarray([inputs], dtype=np.float))

    print predicted_value
        
