# -*- coding: ms949 -*-

from feature.Plays import *
from feature.FeatureMap import *
from SimpleGo.go import *
from SimpleGo.const import *
import numpy as np
import random, copy, time

from keras.models import model_from_json
from keras.optimizers import SGD
from keras import backend as K
from utils.base import get_file_names

SL_POLICY_JSON = "opp_pool/slpolicy_net_model.json"
SL_POLICY_H5 = "opp_pool/slpolicy_net_model.h5"

RL_POLICY_JSON = "opp_pool/policy_net_model_299.json"
RL_POLICY_H5 = "opp_pool/policy_net_model_299.h5"

SAVE_DATA_FOLER = "RL_value_dataset/20160513_"

lrate = 0.003

def get_state(max_pos):
    tmp_row = int(max_pos / 9)
    tmp_col = max_pos - tmp_row * 9
    tmp_row += 1
    tmp_col += 1
    
    row = 10 - tmp_row
    col = tmp_col
    return col, row

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
    black_player = ""
    n = 0
    score_BLACK = 0    
    score_WHITE = 0
    start = True
    
    sgd1 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    sl_policy = model_from_json(open(SL_POLICY_JSON).read())
    sl_policy.load_weights(SL_POLICY_H5)
    sl_policy.compile(loss='categorical_crossentropy', optimizer=sgd1)   
    
    sgd2 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
    rl_policy = model_from_json(open(RL_POLICY_JSON).read())
    rl_policy.load_weights(RL_POLICY_H5)
    rl_policy.compile(loss=rl_policy_loss, optimizer=sgd2)   
    
    if random.random() < 0.5:
        cur_model = False
    
    print "setting game.."
    game = simple_go.Game(9)     
    komi = 6.5
    print "...finish"
    
    rand_move_number = int(random.random() * 40)
    
    print "random move:", rand_move_number
    
    pred_pos = sl_policy.predict(np.asarray([first_state()], dtype=np.float))
    
    tmp_pred_pos = np.argmax(pred_pos)
    col, row = get_state(tmp_pred_pos)
    
    while not game.legal_move((col, row)):
    
        pred_pos = np.delete(pred_pos, tmp_pred_pos)
        
        if len(pred_pos) == 0:
            start = False
            break
        
        tmp_pred_pos = np.argmax(pred_pos)
        col, row = get_state(tmp_pred_pos)
    
    game.make_move((col, row))
    print str(game.current_board)
    
    
    m = 0
    while m < rand_move_number:
        #make argument to call model.predict
        playlist = []
        n = 1
        for move in game.move_history:
            if n%2 == 1:
                playlist.append(('b', (move[0]-1, move[1]-1)))
            else:
                playlist.append(('w', (move[0]-1, move[1]-1)))  
            n += 1 
        
        plays = Plays(playlist)
        features = FeatureMap(plays, len(playlist))
        
        X = features.input_planes
        
        pred_pos = sl_policy.predict(np.asarray([X], dtype=np.float))
        
        tmp_pred_pos = np.argmax(pred_pos)
        col, row = get_state(tmp_pred_pos)
        
        while not game.legal_move((col, row)):
        
            pred_pos = np.delete(pred_pos, tmp_pred_pos)
            
            if len(pred_pos) == 0:
                start = False
                break
            
            tmp_pred_pos = np.argmax(pred_pos)
            col, row = get_state(tmp_pred_pos)
        
        game.make_move((col, row))
        print str(game.current_board)
        
        legalmove = {}
        legalmove = copy.copy(game.list_moves())
        legalmove.remove((-1, -1))
        
        if len(legalmove) == 0:
            game.current_board.side = BLACK
            score_BLACK = game.score_position() 
            game.current_board.side = WHITE
            score_WHITE = game.score_position()
            start = False
            
        if not start:
            break
        m += 1
    
    col, row = get_state(int(random.random() * 81))
    #랜덤 착수
    while not game.legal_move((col, row)):
        col, row = get_state(int(random.random() * 81))
        
    game.make_move((col, row))
    print str(game.current_board)
    
    while True:
        #make argument to call model.predict
        playlist = []
        n = 1
        for move in game.move_history:
            if n%2 == 1:
                playlist.append(('b', (move[0]-1, move[1]-1)))
            else:
                playlist.append(('w', (move[0]-1, move[1]-1)))  
            n += 1 
        
        plays = Plays(playlist)
        features = FeatureMap(plays, len(playlist))
        
        X = features.input_planes
        
        
        pred_pos = rl_policy.predict(np.asarray([X], dtype=np.float))
        
        tmp_pred_pos = np.argmax(pred_pos)
        col, row = get_state(tmp_pred_pos)
        
        while not game.legal_move((col, row)):
        
            pred_pos = np.delete(pred_pos, tmp_pred_pos)
            
            if len(pred_pos) == 0:
                start = False
                break
            
            tmp_pred_pos = np.argmax(pred_pos)
            col, row = get_state(tmp_pred_pos)
        
        game.make_move((col, row))
        print str(game.current_board)
        
        legalmove = {}
        legalmove = copy.copy(game.list_moves())
        legalmove.remove((-1, -1))
        
        if len(legalmove) == 0:
            game.current_board.side = BLACK
            score_BLACK = game.score_position() 
            game.current_board.side = WHITE
            score_WHITE = game.score_position()
            start = False
            
        if not start:
            break
    
    t2 = time.time()
    print "걸린 시간: " + str(t2 - t1)
    
    f = open(SAVE_DATA_FOLER+ "1.sgf", 'w')
    f.write(str(game))
    f.close()
        