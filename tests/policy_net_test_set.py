#-*- coding: utf-8 -*-

import numpy as np
from keras.models import model_from_json
import time, csv, os
from keras.optimizers import SGD

OTHER_TRAIN_FOLDER = "test_pro/"
POSTFIX = ".csv"
lrate = 0.003

def get_file_names(path, postfix):
    res = []

    for root, dirs, files in os.walk(path):

        for file in files:
            if file[-len(postfix):] == postfix:
                res.append(file)

    return res

def load_dataset():
    FOLDER = list()
    FOLDER.append(OTHER_TRAIN_FOLDER)
    xs, ys = list(), list()
    file_names = get_file_names(OTHER_TRAIN_FOLDER, POSTFIX)
    for name in file_names:
        datas = list()
        cur_rows = list()
        csvfile =  open(OTHER_TRAIN_FOLDER+name)
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
            f = open(OTHER_TRAIN_FOLDER + fname)
            rreader = csv.reader(f)
            for row in rreader:
                for a in row:
                    datas.append(a)
            ys.append(datas)
            break
    '''
    file_names = get_file_names(OTHER_TRAIN_FOLDER, POSTFIX)
    for name in file_names:
        datas = list()
        cur_rows = list()
        csvfile =  open(OTHER_TRAIN_FOLDER+name)
        row_reader = csv.reader(csvfile)
        if name[-6] == 'x':
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
            fname = name[:len(name)-6]+"y_.csv"
            f = open(OTHER_TRAIN_FOLDER + fname)
            rreader = csv.reader(f)
            for row in rreader:
                for a in row:
                    datas.append(a)
            ys.append(datas)'''
    xs = np.asarray(xs, dtype=np.float)
    ys = np.asarray(ys, dtype=np.float)
    print "xs", xs.shape, "ys", ys.shape
    return xs, ys


if __name__ == "__main__":
    cor, uncor = 0, 0
    
    X, Y = load_dataset()
    model = model_from_json(open('rollout_policy_net_moodel.json').read())
    model.load_weights('rollout_policy_net_weights_168.h5')
    sgd = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    model.compile(loss='categorical_crossentropy', optimizer=sgd)   
    before = time.time()
    pResult = model.predict(X)
    after = time.time()
    print "걸린 시간", after-before
    for i in range(0, len(pResult)):
        pred = pResult[i].argmax()
        real = Y[i].argmax()
        if pred == real:
            cor += 1
        else:
            uncor += 1
    ACC = 100.0 * cor / len(Y)
    print "맞은 개수:", cor
    print "틀린 개수:", uncor
    print "정확도: %.5f" % ACC
    