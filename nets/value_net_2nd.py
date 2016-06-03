#-*- coding: utf-8 -*-

from keras.models import Sequential
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.convolutional import Convolution2D, ZeroPadding2D, MaxPooling2D
from keras.optimizers import SGD
from keras.callbacks import Callback
from keras import backend as K

from keras.models import model_from_json
from utils.base import *

lrate = 0.003
k = 192
bsize = 64
epoch = 500

SAVE_FOLDER_NAME = "20160531"
MODEL_FILE_JSON = "RL_value_models/value_net_model.json"
MODEL_FILE_H5 = "RL_value_models/value_net_weights_6.h5"
POSTFIX = ".csv"
OTHER_TRAIN_FOLDER = "RL_value_features_2nd/"

def hidden_layers(m, k):
    m.add(ZeroPadding2D(padding=(2, 2)))
    m.add(Convolution2D(k, 3, 3))
    m.add(Activation('relu'))
    
    return m

def load_dataset():
    FOLDER = list()
    FOLDER.append(OTHER_TRAIN_FOLDER)
    xs, ys = list(), list()
    for folder in FOLDER:
        file_names = get_file_names(folder, POSTFIX)
        for name in file_names:
            datas = list()
            cur_rows = list()
            csvfile =  open(folder+name)
            row_reader = csv.reader(csvfile)
            if name[-5] == 'x':
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
                f = open(folder + fname)
                y_label = f.read()
                if y_label == "0":
                    ys.append(-1)
                else:
                    ys.append(1)
    xs = np.asarray(xs, dtype=np.float)
    ys = np.asarray(ys, dtype=np.float)
    print "xs", xs.shape, "ys", ys.shape
    return xs, ys

class save_callback(Callback):

    def on_epoch_end(self, epoch, logs={}):
        self.model.save_weights(SAVE_FOLDER_NAME+"/value_net_weights_"+str(epoch)+".h5")

if __name__ == "__main__":


    print "load dataset.."
    train_x, train_y = load_dataset()
    print "..finish"
    
    print "load model.."
    model = model_from_json(open(MODEL_FILE_JSON).read())
    model.load_weights(MODEL_FILE_H5)    
    print "..finish"
    
    sgd = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    model.compile(loss='MSE', optimizer=sgd, metrics=["accuracy"])   
    stop = save_callback()
    model.fit(train_x, train_y, batch_size=bsize, nb_epoch=epoch, callbacks=[stop])
    