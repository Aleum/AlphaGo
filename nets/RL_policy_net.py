#-*- coding: utf-8 -*-

from keras.models import Sequential
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.convolutional import Convolution2D, ZeroPadding2D, MaxPooling2D
from keras.optimizers import SGD
from keras.callbacks import Callback
from keras import backend as K
from keras.models import model_from_json

from utils.base import *

k = 32
bsize = 32
epoch = 300
lrate = 0.003

SAVE_FOLDER_NAME = "20160511RL"

MODEL_FILE_JSON = "/home/sclab3/Aleum/SCGo/SLpolicy_net_model.json"
MODEL_FILE_H5 = "/home/sclab3/Aleum/SCGo/20160503/policy_net_weights_499.h5"

POSTFIX = ".csv"
TRAIN_FOLDER = "RL_train/"

def load_dataset():
    xs, ys = list(), list()
    file_names = get_file_names(TRAIN_FOLDER, POSTFIX)
    for name in file_names:
        datas = list()
        cur_rows = list()
        csvfile =  open(TRAIN_FOLDER+name)
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
            f = open(TRAIN_FOLDER + fname)
            rreader = csv.reader(f)
            for row in rreader:
                for a in row:
                    datas.append(a)
            ys.append(datas)
    xs = np.asarray(xs, dtype=np.float)
    ys = np.asarray(ys, dtype=np.float)
    print "xs", xs.shape, "ys", ys.shape
    return xs, ys


class save_callback(Callback):

    def on_epoch_end(self, epoch, logs={}):
        json_string = model.to_json()
        open(SAVE_FOLDER_NAME+"/policy_net_model_"+str(epoch)+".json", "w").write(json_string)
        self.model.save_weights(SAVE_FOLDER_NAME+"/policy_net_weights_"+str(epoch)+".h5")


def RL_policy_loss(y_true, y_pred):
    ''' y_true: 이겼을 때 1, 졌을 때 -1 '''
    return K.categorical_crossentropy(y_pred    * K.sum(y_true)* bsize, K.abs(y_true))


if __name__ == "__main__":
    
    print "load dataset.."
    train_x, train_y = load_dataset()
    print "..finish"
    
    print "load model.."
    model = model_from_json(open(MODEL_FILE_JSON).read())
    model.load_weights(MODEL_FILE_H5)    
    print "..finish"
    
    bsize = len(train_y)
    
    sgd = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    model.compile(loss=RL_policy_loss, optimizer=sgd)   
    stop = save_callback()
    model.fit(train_x, train_y, batch_size=bsize, nb_epoch=epoch, callbacks=[stop])
    
    
    
    