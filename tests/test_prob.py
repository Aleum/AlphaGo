#-*- coding: utf-8 -*-

import numpy as np
from keras.models import model_from_json
from keras.optimizers import SGD
import time, csv, os, sys
from datetime import datetime

POSTFIX = ".csv"
lrate = 0.003
bsize = 16
Y_names = list()
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
            Y_names.append(fname)
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
    SAVE_FOLDER = sys.argv[4]
    
    CUR_DATETIME = datetime.now().strftime("%y%m%d_%H%M%S")
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
    
    print "피쳐 저장 중.."
    txt = ""
    lY = Y.tolist()
    n_y = 0
    for y in lY:
        txt += Y_names[n_y] +"\n"
        convert_y = np.zeros((9,9))
        for n_row in range(0, len(y)):
            cur_prob = y[n_row]
            convert_row = int(n_row / 9)
            convert_col = n_row - convert_row * 9
            convert_row += 1
            convert_col += 1
            row = 10 - convert_row -1
            col = convert_col -1
            convert_y[row][col] = cur_prob
        convert_y = convert_y.tolist()
        for n_row in range(0, len(convert_y)):
            for n_comp in range(0, len(convert_y[n_row])):
                txt += "%.5f" % convert_y[n_row][n_comp]
                if n_comp < len(convert_y[n_row])-1:
                    txt += ","
            txt += "\n"
        txt += "\n"
        n_y += 1
    fname = CUR_DATETIME +"_features.csv"
    open(SAVE_FOLDER+fname, 'w').write(txt)
    print "..피쳐 저장 끝, 파일 이름:", fname
    
    print "확률 저장 중.."
    txt = ""
    lResult = pResult.tolist()
    for result in lResult:
        convert_result = np.zeros((9,9))
        for n_row in range(0, len(result)):
            cur_prob = result[n_row]
            convert_row = int(n_row / 9)
            convert_col = n_row - convert_row * 9
            convert_row += 1
            convert_col += 1
            row = 10 - convert_row -1
            col = convert_col -1
            convert_result[row][col] = cur_prob
        convert_result = convert_result.tolist()
        for n_row in range(0, len(convert_result)):
            for n_comp in range(0, len(convert_result[n_row])):
                txt += "%.5f" % convert_result[n_row][n_comp]
                if n_comp < len(convert_result[n_row])-1:
                    txt += ","
            txt += "\n"
        txt += "\n"
    fname = CUR_DATETIME+"_result.csv"
    open(SAVE_FOLDER+fname, 'w').write(txt)
    
    print "..확률 저장 끝, 파일 이름:", fname
    