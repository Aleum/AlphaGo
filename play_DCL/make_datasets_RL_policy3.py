# -*- coding: ms949 -*-

from feature.Plays import *
from feature.FeatureMap import *
from go import *
from const import *
import numpy as np
import random, copy, time

from keras.models import model_from_json
from keras.optimizers import SGD

MODEL_FILE_JSON = "rollout_policy_net_model.json"
MODEL_FILE_H5 = "rollout_policy_net_weights_168.h5"
OPP_FILE_JSON = "rollout_policy_net_model.json"
OPP_FILE_H5 = "rollout_policy_net_weights_168.h5"

lrate = 0.003

def first_state():
    state = list()
    state.append(np.zeros((9, 9)))
    state.append(np.zeros((9, 9)))
    state.append(np.ones((9, 9)))
    state.append(np.ones((9, 9)))
    for a in range(0, 34):
        state.append(np.zeros((9, 9)))
    return np.asarray(state, dtype=np.float)

if __name__ == "__main__":    
    t1 = time.time()
    n = 0
    nCount = 0
    score_BLACK = 0    
    score_WHITE = 0
    start = True
    
    sgd1 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    model = model_from_json(open(MODEL_FILE_JSON).read())
    model.load_weights(MODEL_FILE_H5)
    model.compile(loss='categorical_crossentropy', optimizer=sgd1)   
    
    sgd2 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    opp = model_from_json(open(OPP_FILE_JSON).read())
    opp.load_weights(OPP_FILE_H5)
    opp.compile(loss='categorical_crossentropy', optimizer=sgd2)   
    
    #t1 = time.time()    
    cur_model = True
    
    if random.random() < 0.5:
        cur_model = False
    
    print "setting game.."
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #첫번째 착수
    if cur_model:
        pred_pos = model.predict(np.asarray([first_state()], dtype=np.float))
    else:
        pred_pos = opp.predict(np.asarray([first_state()], dtype=np.float))
        
    pred_pos = np.argmax(pred_pos)
    
    tmp_row = int(pred_pos / 9)
    tmp_col = pred_pos - tmp_row * 9
    tmp_row += 1
    tmp_col += 1
    
    row = 10 - tmp_row
    col = tmp_col   
    
    game.make_move((col, row))
    nCount += 1
    print str(game.current_board)
    
    cur_model = not cur_model
    
    while True:
        #make argument to call model.predict
        taat1 = time.time()
        
        playlist = []
        n = 1
        for move in game.move_history:
            if n%2 == 1:
                playlist.append(('b', (move[0]-1, move[1]-1)))
            else:
                playlist.append(('w', (move[0]-1, move[1]-1)))  
            n += 1 
        
        caat1 = time.time()
        plays = Plays(playlist)
        features = FeatureMap(plays, len(playlist))
        caat2 = time.time()
        print "Elapsed for input feature: " + str(caat2 - caat1)
        X = features.input_planes        
        
        daat1 = time.time()
        row, col = 0, 0
        if cur_model:
            pred_pos = model.predict(np.asarray([X], dtype=np.float))
        else:
            pred_pos = opp.predict(np.asarray([X], dtype=np.float))
            
        tmp_pred_pos = np.argmax(pred_pos)
        
        tmp_row = int(tmp_pred_pos / 9)
        tmp_col = tmp_pred_pos - tmp_row * 9
        tmp_row += 1
        tmp_col += 1
        
        row = 10 - tmp_row
        col = tmp_col
        daat2 = time.time()
        print "Elapsed for predict: " + str(daat2 - daat1)
        
        aat1 = time.time()
        while not game.legal_move((col, row)):
            pred_pos = np.delete(pred_pos, tmp_pred_pos)
            
            if len(pred_pos) == 0:
                start = False
                break
            
            tmp_pred_pos = np.argmax(pred_pos)
            tmp_row = int(tmp_pred_pos / 9)
            tmp_col = tmp_pred_pos - tmp_row * 9
            tmp_row += 1
            tmp_col += 1
            
            row = 10 - tmp_row
            col = tmp_col
        aat2 = time.time()
        print "Elapsed for check legal_move. : " + str(aat2 - aat1)
            
        baat1 = time.time()
        game.make_move((col, row))
        nCount += 1
        baat2 = time.time()
        print "Elapsed for make_move : " + str(baat2 - baat1)
        print str(game.current_board) + '\nwinner is ' + str(game.getwinner()) + ' with ' + str(game.getscore()) 
        
        at1 = time.time()
        if game.is_end(by_score=True) == True:
            print 'exit1'          
            break
        at2 = time.time()
        print "Elapsed for is_end : " + str(at2 - at1)
        
        cur_model = not cur_model
        
        taat2 = time.time()
        print "Elapsed for 1 run : " + str(taat2 - taat1) + '\n\n'  
    
    t2 = time.time()
    print "Elapsed: " + str(t2 - t1)
    print 'ended game. winner is ' + str(game.getwinner()) + ' with ' + str(game.getscore()) + ' nCount : ' + str(nCount)
    
    f = open("RL_policy_dataset/20160510_1.sgf", 'w')
    f.write(str(game))
    f.close()      
        
