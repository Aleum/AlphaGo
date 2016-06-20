#-*- coding: utf-8 -*-

from keras.models import Sequential
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.convolutional import Convolution2D, ZeroPadding2D, MaxPooling2D
from keras.optimizers import SGD
from keras.callbacks import Callback
from keras import backend as K
from keras.models import model_from_json
import sys

if __name__ == "__main__":
    
    MODEL_FILE_JSON = sys.argv[1]
    MODEL_FILE_H5 = sys.argv[2]
    
    model = model_from_json(open(MODEL_FILE_JSON).read())
    model.load_weights(MODEL_FILE_H5)
    
    model.save_weights(MODEL_FILE_H5+".v3")   
    
    