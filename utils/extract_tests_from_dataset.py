import numpy as np
import random
from utils.base import *
import os

DATA_FOLDER = "20160608/datasets/phase01/"
TEST_FOLDER = "20160608/datasets/test/"
POSTFIX = "_x.csv"

RATIO = 9527

if __name__ == "__main__":
    all_fnames = get_file_names(DATA_FOLDER, POSTFIX)
    f_idx = [i for i in range(0, len(all_fnames))]
    random.shuffle(f_idx)
    
    print "start"
    
    num = 0
    
    for idx in f_idx[:RATIO]:
        fname = all_fnames[idx]
        f_x = open(DATA_FOLDER + fname, 'r+')
        X = f_x.read()
        f_x.close()
        
        f_y = open(DATA_FOLDER + fname[:-len(POSTFIX)] + "_y.csv", 'r+')
        Y = f_y.read()
        f_y.close()
        
        f_x = open(TEST_FOLDER + fname, 'w')
        f_x.write(X)
        f_x.close()
        
        f_y = open(TEST_FOLDER + fname[:-len(POSTFIX)] + "_y.csv", 'w')
        f_y.write(Y)
        f_y.close()
        
        os.remove(DATA_FOLDER + fname)
        os.remove(DATA_FOLDER + fname[:-len(POSTFIX)] + "_y.csv")
        
        num += 1
        if num % 100 == 0:
            print "."
    
    print "finish.."
    