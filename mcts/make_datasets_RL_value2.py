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

RL_POLICY_JSON = "opp_pool/policy_net_model_299.json"
RL_POLICY_H5 = "opp_pool/policy_net_model_299.h5"

OPP_POOL_FOLDER = "opp_pool/"

SAVE_DATA_FOLER = "RL_policy_dataset/20160513_"

lrate = 0.003

def rl_policy_loss(y_true, y_pred):
    ''' y_true: �̰��� �� 1, ���� �� -1 '''
    return K.categorical_crossentropy(y_pred * K.sum(y_true)* K.ndim(y_true), K.abs(y_true))

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
    
    opp_pool = get_file_names(OPP_POOL_FOLDER, ".json")
    
    for OPP_FILE_JSON in opp_pool:
        OPP_FILE_JSON = OPP_FILE_JSON
        OPP_FILE_H5 = OPP_FILE_JSON[:-5] + ".h5"
        t1 = time.time()
        black_player = ""
        n = 0
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
        
            
        cur_model = True
        
        if random.random() < 0.5:
            cur_model = False
        
        print "setting game.."
        game = simple_go.Game(9)     
        
        komi = 6.5
        game.set_komi(komi)
        
        #ù��° ����
        if cur_model:
            pred_pos = model.predict(np.asarray([first_state()], dtype=np.float))
            black_player = "model"
        else:
            pred_pos = opp.predict(np.asarray([first_state()], dtype=np.float))
            black_player = "opp"
            
        pred_pos = np.argmax(pred_pos)
        
        tmp_row = int(pred_pos / 9)
        tmp_col = pred_pos - tmp_row * 9
        tmp_row += 1
        tmp_col += 1
        
        row = 10 - tmp_row
        col = tmp_col   
        
        game.make_move((col, row))
        print str(game.current_board)
        
        cur_model = not cur_model
        
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
            
            cur_model = not cur_model
        
        
        t2 = time.time()
        print "�ɸ� �ð�: " + str(t2 - t1)
        if score_BLACK > score_WHITE:
            print "winner:", black_player
            postfix_fname = "1"
        else:
            print "looser:", black_player
            postfix_fname = "0"
        
        f = open("RL_policy_dataset/20160510_1_"+ postfix_fname +".sgf", 'w')
        f.write(str(game))
        f.close()