#-*- coding: utf-8 -*-
import os, math, random
from feature.FeatureMap import *
from feature.Plays import *
from base import get_file_names
from types import NoneType

def load_dataset():
    POSTFIX = ".sgf"
    GO_FOLDER = "C:/Users/Aleum/Desktop/sgf2/"
    
    OTHER_TRAIN_FOLDER = "C:/Users/Aleum/Desktop/train_other_rollout/"
    OTHER_TEST_FOLDER = "C:/Users/Aleum/Desktop/test_other_rollout/"
    
    pro_x, pro_y, pro_fnames = list(), list(), list()
    play_lists = list()
    
    print "start loading go dataset files"
    
    # FueGo 데이터 셋 추출
    file_names = get_file_names(GO_FOLDER, POSTFIX)
    for name in file_names:
        plays = Plays()
        plays.load_from_sgf(GO_FOLDER+name)
        if plays.total_nonpass_plays < 10:
            continue
        play_lists.append(plays)
        
    idx = [i for i in range(0, len(play_lists))]
    random.shuffle(idx)
    print "finish.."
    print "start extracting test set"
    # test set 추출
    for i in range(0, 50):
        id = idx[i]
        cur_play = play_lists[id]
        for p in range(1, 4):
            play_idx = [j for j in range(int(cur_play.total_nonpass_plays / 3 * (p-1)) + 1
                                         , int(cur_play.total_nonpass_plays / 3 * p) + 1)]
            random.shuffle(play_idx)
            
            # 1/3 지점마다 5개씩 추출
            for k in play_idx[:5]:
                features = FeatureMap(cur_play, k)
                f = open(OTHER_TEST_FOLDER+file_names[id]+"_"+str(k)+"_x"+".csv", 'w')
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
                f = open(OTHER_TEST_FOLDER+file_names[id]+"_"+str(k)+"_y"+".csv", 'w')
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
                pro_fnames.append(file_names[id])
                
                
    print "finish.."
    print "start extracting from play lists"           
    # 나머지에서 750개 test set, 그 외 17만개 train set
    
    total_play_num = list()
    pro_fnames = list()
    t = 0
    for id in idx[50:]:
        cur_play = play_lists[id]
        t += play_lists[id].total_nonpass_plays
        total_play_num.append(t)
        pro_fnames.append(file_names[id])
        
    idx = [ i for i in range(0, t)]
    random.shuffle(idx)
    
    print "finish.."
    print "start make test set"
    t = 0
    id = 0
    for i in idx[0:750]:
        id = -1
        for k in range(0, len(total_play_num)):
            if total_play_num[k] >= i:
                id = k
                break
        cur_play = play_lists[id]
        if id - 1 >= 0:
            pre_play_num = total_play_num[id-1]
        else: 
            pre_play_num = 0
        features = FeatureMap(cur_play, i - pre_play_num)
        if type(features.input_planes) is NoneType:
            continue
        
        f = open(OTHER_TEST_FOLDER+pro_fnames[id]+"_"+str(i-pre_play_num)+"_x"+".csv", 'w')
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
        f = open(OTHER_TEST_FOLDER+pro_fnames[id]+"_"+str(i-pre_play_num)+"_y"+".csv", 'w')
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
        
    print "finish.."
    print "start make train set"
    for i in idx[750:171000]:
        id = -1
        for k in range(0, len(total_play_num)):
            if total_play_num[k] >= i:
                id = k
                break
        cur_play = play_lists[id]
        if id - 1 >= 0:
            pre_play_num = total_play_num[id-1]
        else:
            pre_play_num = 0
        features = FeatureMap(cur_play, i - pre_play_num)
        if type(features.input_planes) is NoneType:
            continue
        
        f = open(OTHER_TRAIN_FOLDER+pro_fnames[id]+"_"+str(i-pre_play_num)+"_x"+".csv", 'w')
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
        f = open(OTHER_TRAIN_FOLDER+pro_fnames[id]+"_"+str(i-pre_play_num)+"_y"+".csv", 'w')
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
        
    print "finish.."

if __name__ == "__main__":
    load_dataset()
        