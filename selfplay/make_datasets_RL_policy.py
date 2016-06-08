# -*- coding: ms949 -*-

from feature.FeatureMap import *
from SimpleGo.go import *
from SimpleGo.const import *
import numpy as np
import random, copy, time

from keras.models import model_from_json
from keras.optimizers import SGD
from keras import backend as K

from utils.base import *
OPP_POOL_FOLDER = "opp_pool_2nd/"

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
    RL_POLICY_JSON = sys.argv[3]+".json"
    RL_POLICY_H5 = sys.argv[3]+".h5"
    SAVE_DATA_FOLER = sys.argv[1]
    SAVE_FEATURE_FOLDER = sys.argv[2]
    
    opp_pool = get_file_names(OPP_POOL_FOLDER, ".json")
    
    random_opp_poll = [i for i in range(0, len(opp_pool))]
    
    for m in range(0, 32):
        
        ropp = int(random.random() * len(random_opp_poll))
        
        OPP_FILE_JSON = opp_pool[ropp]
        OPP_FILE_H5 = OPP_FILE_JSON[:-5] + ".h5"
        t1 = time.time()
        black_player = ""
        n = 0
        score_BLACK = 0    
        score_WHITE = 0
        start = True
        
        sgd1 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
        model = model_from_json(open(OPP_POOL_FOLDER+RL_POLICY_JSON).read())
        model.load_weights(OPP_POOL_FOLDER+RL_POLICY_H5)
        model.compile(loss='categorical_crossentropy', optimizer=sgd1)   
        
        sgd2 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
        opp = model_from_json(open(OPP_POOL_FOLDER+OPP_FILE_JSON).read())
        opp.load_weights(OPP_POOL_FOLDER+OPP_FILE_H5)
        opp.compile(loss='categorical_crossentropy', optimizer=sgd2)
            
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
        
        game.current_board.analyze_unconditional_status()
        score = 0
        for block in game.current_board.iterate_blocks(BLACK):
            score = score + game.current_board.chinese_score_block(block)
        score_WHITE = -score
        score = 0
        for block in game.current_board.iterate_blocks(WHITE):
            score = score + game.current_board.chinese_score_block(block)
        score_WHITE = -score
        
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
            
            X = features.input_planes_policynet
            
            
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
            
            while True:
                if game.legal_move((col, row)):
                    break
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
                
            if not start:
                break
            game.make_move((col, row))
            print str(game.current_board)
            print game.getscore()
            if n >= 50:
                if game.is_end(True):
                    start = False
            
            legalmove = {}
            legalmove = copy.copy(game.list_moves())
            legalmove.remove((-1, -1))
            if len(legalmove) == 0 or abs(score_BLACK - score_WHITE) > 10:
                start = False
                
            if not start:
                break
            
            cur_model = not cur_model
        
        
        t2 = time.time()
        print "time " +  str(t2 - t1)
        if game.getwinner() == 0 and black_player == "model":
            print "win", game.getwinner(), game.getscore()
            postfix_fname = "1"
        elif game.getwinner() == 1 and black_player == "opp":
            print "win", game.getwinner(), game.getscore()
            postfix_fname = "1"
        else:
            postfix_fname = "0"
            print "lose", game.getwinner(), game.getscore()
        
        f = open(SAVE_DATA_FOLER+"/"+OPP_FILE_JSON+"_"+str(m)+"_"+postfix_fname +".sgf", 'w')
        f.write(str(game))
        f.close()

        