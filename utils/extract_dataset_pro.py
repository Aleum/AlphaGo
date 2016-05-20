#-*- coding: utf-8 -*-
import os, math, random
from feature import *
from base import *

def load_dataset():
    POSTFIX = ".sgf"
    GO_FOLDER = "C:/Users/Aleum/Desktop/data_pro/"
    
    OTHER_TRAIN_FOLDER = "C:/Users/Aleum/Desktop/train_pro/"
    OTHER_TEST_FOLDER = "C:/Users/Aleum/Desktop/test_pro/"
    
    pro_x, pro_y, pro_fnames = list(), list(), list()
    play_lists = list()
    
    print "start loading go dataset files"
    
    # FueGo 데이터 셋 추출
    file_names = get_file_names(GO_FOLDER, POSTFIX)
    for name in file_names:
        plays = Plays()
        plays.load_from_sgf(GO_FOLDER+name)
        play_lists.append(plays)
        
    idx = [i for i in range(0, len(play_lists))]
    random.shuffle(idx)
    print "finish.."
    print "start extracting test set"
    # test set 추출
    for i in range(0, 10):
        id = idx[i]
        cur_play = play_lists[id]
        for p in range(1, 4):
            play_idx = [j for j in range(int(cur_play.total_plays / 3 * (p-1)) + 1
                                         , int(cur_play.total_plays / 3 * p) + 1)]
            random.shuffle(play_idx)
            
            # 1/3 지점마다 5개씩 추출
            for k in play_idx[:5]:
                features = FeatureMap(cur_play, k)
                f = open(OTHER_TEST_FOLDER+file_names[id]+"_"+str(k)+"_x.csv", 'w')
                txt = ""
                for feature in features.input_planes:
                    for rows in feature:
                        for r in range(0, len(rows)):
                            if r == len(rows)-1:
                                txt += str(rows[r])
                            else:
                                txt += str(rows[r]) + ","
                        txt+="\n"
                    txt+="\n"
                f.write(txt)
                f.close()
                f = open(OTHER_TEST_FOLDER+file_names[id]+"_"+str(k)+"_y.csv", 'w')
                txt = ""
                for rows in features.label:
                    for r in range(0, len(rows)):
                        if r == len(rows)-1:
                            txt += str(rows[r])
                        else:
                            txt += str(rows[r]) + ","
                    txt+="\n"
                f.write(txt)
                f.close()
            
            for k in play_idx[5:]:
                features = FeatureMap(cur_play, k)
                pro_x.append(features.input_planes)
                pro_y.append(features.label)
                pro_fnames.append(file_names[id]+"_"+str(k))
                
                
    print "finish.."
    print "start extracting from play lists"           
    # 나머지에서 750개 test set, 그 외 17만개 train set
    
    for id in idx[10:]:
        cur_play = play_lists[id]
        for i in range(1, cur_play.total_plays+1):
            features = FeatureMap(cur_play, i)
            pro_x.append(features.input_planes)
            pro_y.append(features.label)
            pro_fnames.append(file_names[id]+"_"+str(i))
        
    idx = [ i for i in range(0, len(pro_y))]
    random.shuffle(idx)
    
    print "finish.."
    print "start make test set"
    for i in idx[:325]:
        f = open(OTHER_TEST_FOLDER+pro_fnames[i]+"_x.csv", 'w')
        txt = ""
        for feature in pro_x[i]:
            for rows in feature:
                for r in range(0, len(rows)):
                    if r == len(rows)-1:
                        txt += str(rows[r])
                    else:
                        txt += str(rows[r]) + ","
                txt+="\n"
            txt+="\n"
        f.write(txt)
        f.close()
        f = open(OTHER_TEST_FOLDER+pro_fnames[i]+"_y.csv", 'w')
        txt = ""
        for rows in pro_y[i]:
            for r in range(0, len(rows)):
                if r == len(rows)-1:
                    txt += str(rows[r])
                else:
                    txt += str(rows[r]) + ","
            txt+="\n"
        f.write(txt)
        f.close()
        
    print "finish.."
    print "start make train set"
    for i in idx[325:]:
        f = open(OTHER_TRAIN_FOLDER+pro_fnames[i]+"_x.csv", 'w')
        txt = ""
        for feature in pro_x[i]:
            for rows in feature:
                for r in range(0, len(rows)):
                    if r == len(rows)-1:
                        txt += str(rows[r])
                    else:
                        txt += str(rows[r]) + ","
                txt+="\n"
            txt+="\n"
        f.write(txt)
        f.close()
        f = open(OTHER_TRAIN_FOLDER+pro_fnames[i]+"_y.csv", 'w')
        txt = ""
        for rows in pro_y[i]:
            for r in range(0, len(rows)):
                if r == len(rows)-1:
                    txt += str(rows[r])
                else:
                    txt += str(rows[r]) + ","
            txt+="\n"
        f.write(txt)
        f.close()
        
    print "finish.."

if __name__ == "__main__":
    load_dataset()
        