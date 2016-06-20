# -*- coding: ms949 -*-

from feature.Plays import *
from feature.FeatureMap import *
from go import *
from const import *
import numpy as np
import random, copy, time

from keras.models import model_from_json
from keras.optimizers import SGD

lrate = 0.003

class network():
    """network"""
    def __init__(self):
        self.init = False
        self.m_SLPOLICY = None
        self.m_ROLLOUT = None
        
    def init2(self):
        try:
            print "AA00"
            #SLPOLICY
            sgd1 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
            print "AA01:" + SLPOLICY_JSON
            t = model_from_json(open(SLPOLICY_JSON).read())
            print "AA01-1"
            self.m_SLPOLICY = t
            print "AA02"
            self.m_SLPOLICY.load_weights(SLPOLICY_H5)
            print "AA03"
            self.m_SLPOLICY.compile(loss='categorical_crossentropy', optimizer=sgd1)
            print "AA04"
            
            #ROLLOUT
            sgd2 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
            print "AA10:" + ROLLOUT_JSON
            s = model_from_json(open(ROLLOUT_JSON).read())
            print "AA11-1"
            self.m_m_ROLLOUT = s
            print "AA11"
            self.m_m_ROLLOUT.load_weights(ROLLOUT_H5)
            print "AA12"
            self.m_m_ROLLOUT.compile(loss='categorical_crossentropy', optimizer=sgd2)
            print "AA13"
            
            self.init = True
            
            print "load pass"
        except:
            print "load failed:", sys.exc_info()[0]
            pass
        
    def predict(self, game, type = 'SLPOLICY'):
        row, col = 0, 0
        
        if self.init == False:            
            legalmove = {}
            legalmove = copy.copy(game.list_moves())
            legalmove.remove((-1, -1))
            
            row = legalmove[0][0]
            col = legalmove[0][1]
        else:
            model = None
            if type == 'SLPOLICY':
                model = self.m_SLPOLICY
            elif type == 'ROLLOUT':
                model = self.m_m_ROLLOUT
            else:
                model = self.m_m_ROLLOUT
            
            tt = game.getargumenttopredict()
            t1 = time.time()
            pred_pos = model.predict(np.asarray([tt], dtype=np.float))
            t2 = time.time()
            
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
        
            #print "predict Elapsed : " + str(t2 - t1) + " type : " + type + "   " + str(col) + ", " + str(row)
        return (col, row)
    
    def predict_valuenet(self, game):
        #나중에 여기 valuenet call해서 리턴하게 수정해야함.
        return random.choice([-1, 1])