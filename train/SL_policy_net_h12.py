#-*- coding: utf-8 -*-

from keras.models import Sequential
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.convolutional import Convolution2D, ZeroPadding2D, MaxPooling2D
from keras.optimizers import SGD
from keras.callbacks import Callback
from keras import backend as K
from keras.models import model_from_json


from utils.base import *

import numpy as np

k = 32
bsize = 16
epoch = 500
lrate = 0.0075

SAVE_FOLDER_NAME = "20160604_sl12"

POSTFIX = "_x.csv"
PRO_TRAIN_FOLDER = "pro_features/"


def hidden_layers(m, k):
    m.add(ZeroPadding2D(padding=(1, 1)))
    m.add(Convolution2D(k, 3, 3))
    m.add(Activation('relu'))
    
    return m

def load_dataset():
    xs, ys = list(), list()
    file_names = get_file_names(PRO_TRAIN_FOLDER, POSTFIX)
    n_idx = 0
    for name in file_names:
        datas = list()
        cur_rows = list()
        csvfile =  open(PRO_TRAIN_FOLDER+name)
        row_reader = csv.reader(csvfile)
        for row in row_reader:
            if len(row) == 0:
                datas.append(cur_rows)
                cur_rows = list()
                continue
            c = list()
            for a in row:
                c.append(a)
            cur_rows.append(c)
        xs.append(datas)
        datas = list()
        fname = name[:len(name)-5]+"y.csv"
        f = open(PRO_TRAIN_FOLDER + fname)
        rreader = csv.reader(f)
        for row in rreader:
            for a in row:
                datas.append(float(a))
        ys.append(datas)
        n_idx += 1
        if n_idx % 100 == 0:
            print n_idx
    
    xs = np.asarray(xs, dtype=np.float)
    ys = np.asarray(ys, dtype=np.float)
    print "xs", xs.shape, "ys", ys.shape
    return xs, ys


class save_callback(Callback):

    def on_epoch_end(self, epoch, logs={}):
        self.model.save_weights(SAVE_FOLDER_NAME+"/policy_net_weights_h12__"+str(epoch)+".h5")
        if epoch % 25 == 0:
            self.model.optimizer.lr *= 0.5

if __name__ == "__main__":
    
    print "load dataset.."
    train_x, train_y = load_dataset()
    print "..finish"
    
   
    print "load model.."
    model = model_from_json(open("20160604_sl12/policy_net_model_h12.json").read())
    model.load_weights("20160604_sl12/policy_net_weights_h12_29.h5")    
    
    print "..finish"
    
    sgd = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=["accuracy"])
    stop = save_callback()
    model.fit(train_x, train_y, batch_size=bsize, nb_epoch=epoch, callbacks=[stop], verbose=1)
    
    
    
    