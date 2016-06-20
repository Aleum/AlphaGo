#-*- coding: utf-8 -*-

import numpy as np
from keras.models import model_from_json
from keras.optimizers import SGD
import time, csv, os, sys


POSTFIX = ".csv"
lrate = 0.003
bsize = 16

def get_file_names(path, postfix):
    res = []

    for root, dirs, files in os.walk(path):

        for file in files:
            if file[-len(postfix):] == postfix:
                res.append(file)

    return res

def load_dataset():
    xs, ys = list(), list()
    file_names = get_file_names(DATA_FOLDER, POSTFIX)
    
    for name in file_names:
        datas = list()
        cur_rows = list()
        csvfile =  open(DATA_FOLDER+name)
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
            f = open(DATA_FOLDER + fname)
            rreader = csv.reader(f)
            for row in rreader:
                for a in row:
                    datas.append(a)
            ys.append(datas)
    xs = np.asarray(xs, dtype=np.float)
    ys = np.asarray(ys, dtype=np.float)
    print "xs", xs.shape, "ys", ys.shape
    return xs, ys


if __name__ == "__main__":
    
    MODEL_JSON = sys.argv[1]
    MODEL_H5 = sys.argv[2]
    DATA_FOLDER = sys.argv[3]
    
    cor, uncor = 0, 0
    
    X, Y = load_dataset()
    model = model_from_json(open(MODEL_JSON).read())
    model.load_weights(MODEL_H5)
    sgd = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    model.compile(loss="categorical_crossentropy", optimizer=sgd)   
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
    