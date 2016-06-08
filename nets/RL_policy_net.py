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
epoch = 125
lrate = 0.1

POSTFIX = ".csv"
def load_dataset():
    xs, ys = list(), list()
    file_names = get_file_names(TRAIN_FOLDER, POSTFIX)
    for name in file_names:
        datas = list()
        cur_rows = list()
        csvfile =  open(TRAIN_FOLDER+"/"+name)
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
            f = open(TRAIN_FOLDER +"/"+ fname)
            rreader = csv.reader(f)
            for row in rreader:
                for a in row:
                    datas.append(a)
            ys.append(datas)
    xs = np.asarray(xs, dtype=np.float)
    ys = np.asarray(ys, dtype=np.float)
    print "xs", xs.shape, "ys", ys.shape
    return xs, ys
 
def RL_policy_loss(y_true, y_pred):
    ''' y_true: 이겼을 때 1, 졌을 때 -1, bsize: 게임 횟수 * 착수 횟수 '''
    #return K.categorical_crossentropy(y_pred * K.sum(y_true) * bsize , K.abs(y_true)) / 32
    #return K.sum(K.log(K.max(y_pred, axis=0)) * K.sum(y_true, axis=0), axis=-1) / 32.0
    return K.categorical_crossentropy(y_pred, y_true) / 32.0 * float(bsize)

if __name__ == "__main__":
    
    SAVE_FOLDER_NAME = "opp_pool_2nd/"
    
    SAVE_DATA_FOLER = sys.argv[1]
    TRAIN_FOLDER = sys.argv[2]
    RLMODEL = sys.argv[3]

    prefix_fname = "2nd_rlpolicy_model_"
    MODEL_FILE_JSON = RLMODEL+".json"
    MODEL_FILE_H5 = RLMODEL+".h5"
    RLMODEL = prefix_fname + str((int(RLMODEL[len(prefix_fname):])+1))
    
    print "load dataset.."
    train_x, train_y = load_dataset()
    print "..finish"
    
    bsize = len(train_y)
    
    print "load model.."
    model = model_from_json(open(SAVE_FOLDER_NAME+MODEL_FILE_JSON).read())
    model.load_weights(SAVE_FOLDER_NAME+MODEL_FILE_H5)    
    print "..finish"
    
    json_string = model.to_json()
    open(SAVE_FOLDER_NAME+RLMODEL+".json", "w").write(json_string)
    
    bsize = len(train_y)
    
    sgd = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=['accuracy'])   
    hist = model.fit(train_x, train_y, batch_size=bsize, nb_epoch=epoch)
    model.save_weights(SAVE_FOLDER_NAME+RLMODEL+".h5")
    