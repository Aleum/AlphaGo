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
        self.m_VALUE = None
        self.curpath = os.path.dirname( os.path.abspath( __file__ ) ) + '/'
        
    def init2(self):
        try:
            print "AA00"
            #SLPOLICY
            sgd1 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
            print "AA01:" + SLPOLICY_JSON
            t = model_from_json(open(self.curpath + SLPOLICY_JSON).read())
            print "AA01-1"
            self.m_SLPOLICY = t
            print "AA02"
            self.m_SLPOLICY.load_weights(self.curpath + SLPOLICY_H5)
            print "AA03"
            self.m_SLPOLICY.compile(loss='categorical_crossentropy', optimizer=sgd1)
            print "AA04"
            
            #ROLLOUT
            sgd2 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
            print "AA10:" + ROLLOUT_JSON
            s = model_from_json(open(self.curpath + ROLLOUT_JSON).read())
            print "AA11-1"
            self.m_ROLLOUT = s
            print "AA11"
            self.m_ROLLOUT.load_weights(self.curpath + ROLLOUT_H5)
            print "AA12"
            self.m_ROLLOUT.compile(loss='categorical_crossentropy', optimizer=sgd2)
            print "AA13"
            
            #VALUE
            sgd3 = SGD(lr=0.003, decay=0.0, momentum=0.0, nesterov=False)
            print "AA20:" + VALUE_JSON
            s = model_from_json(open(self.curpath + VALUE_JSON).read())
            print "AA21-1"
            self.m_VALUE = s
            print "AA21"
            self.m_VALUE.load_weights(self.curpath + VALUE_H5)
            print "AA22"
            self.m_VALUE.compile(loss='MSE', optimizer=sgd3)
            print "AA23"
            
            #RLPOLICY
            sgd4 = SGD(lr=lrate, decay=0.0, momentum=0.0, nesterov=False)
            print "AA31:" + RLPOLICY_JSON
            t = model_from_json(open(self.curpath + RLPOLICY_JSON).read())
            print "AA31-1"
            self.m_RLPOLICY = t
            print "AA32"
            self.m_RLPOLICY.load_weights(self.curpath + RLPOLICY_H5)
            print "AA33"
            self.m_RLPOLICY.compile(loss='categorical_crossentropy', optimizer=sgd4)
            print "AA34"
            
            self.init = True
            
            print "load pass"
        except:
            print "load failed:", sys.exc_info()[0]
            pass
        
    def predict(self, game, type = 'SLPOLICY', tried_actions = None):
        row, col = 0, 0
        Pa = 0.1
        
        #print 'predict00'
        
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
                model = self.m_ROLLOUT
            elif type == 'RLPOLICY':
                model = self.m_RLPOLICY
            else:
                model = self.m_ROLLOUT
            
            #print 'predict01'
            
            tt = game.getargumenttopredict()
            if tt is None:
                return RESIGN_MOVE
            
            #print 'predict02'
            
#             t1 = time.time()
            pred_pos = model.predict(np.asarray([tt], dtype=np.float))
            pred_pos_org = copy.copy(pred_pos[0])
            #print 'pred_pos.dtype : ' + str(pred_pos.dtype)
#             t2 = time.time()
            
            #print 'predict03'
            
            tmp_pred_pos = np.argmax(pred_pos)
            #print 'tmp_pred_pos.dtype : ' + str(tmp_pred_pos.dtype)
            tmp_row = int(tmp_pred_pos / 9)
            tmp_col = tmp_pred_pos - tmp_row * 9
            tmp_row += 1
            tmp_col += 1
            
            #print 'predict04'
            
            row = 10 - tmp_row
            col = tmp_col
            Pa = pred_pos_org[tmp_pred_pos]
            
            #print 'predict05'
            
            #print 'colrow10 : (' + str(col) + ',' + str(row) + ')' + ', Pa : ' + str(Pa)
            
#             while not game.legal_move((col, row)):
#                 pred_pos = np.delete(pred_pos, tmp_pred_pos)
#                 
#                 #print 'predict05-deleted'
#                 
#                 if len(pred_pos) == 0:
#                     start = False
#                     break
#                 
#                 tmp_pred_pos = np.argmax(pred_pos)
#                 tmp_row = int(tmp_pred_pos / 9)
#                 tmp_col = tmp_pred_pos - tmp_row * 9
#                 tmp_row += 1
#                 tmp_col += 1
#                 
#                 row = 10 - tmp_row
#                 col = tmp_col
#                 Pa = pred_pos_org[tmp_pred_pos]
#                 
            #print 'colrow20 : (' + str(col) + ',' + str(row) + ')' + ', Pa : ' + str(Pa)
                
            #game.move_history에 있는데도 이미 둔수를 주는 경우가 있음. 그거 빼기.
            already_actions = {}
            if tried_actions is not None:
                already_actions = tried_actions
                
            #print 'predict100'
                
            for move in game.move_history:
                already_actions[(move[0], move[1])] = str(move[0]) + ',' + str(move[1])
                #already_actions[(move[0], move[1])] = (move[0], move[1])
                #print 'already_actions : (' + str(move[0]) + ',' + str(move[1]) + ')' + ', Pa : ' + str(Pa)
            
            #print 'predict101'
                
            if already_actions is not None:
                while True:
                    if (col, row) not in already_actions and game.legal_move((col, row)):
                        break
                    pred_pos = np.delete(pred_pos, tmp_pred_pos)
                    #print 'predict101-deleted'
                    
                    if len(pred_pos) == 0:
                        #print 'exit by if len(pred_pos) == 0: 111'
                        start = False
                        break
                    
                    tmp_pred_pos = np.argmax(pred_pos)
                    tmp_row = int(tmp_pred_pos / 9)
                    tmp_col = tmp_pred_pos - tmp_row * 9
                    tmp_row += 1
                    tmp_col += 1
                    
                    #print 'predict103:tmp_pred_pos : ' + str(tmp_pred_pos)
                    #print 'pred_pos : ' + pred_pos
                    
                    row = 10 - tmp_row
                    col = tmp_col
                    Pa = pred_pos_org[tmp_pred_pos]
            
            #print 'colrow30 : (' + str(col) + ',' + str(row) + ')' + ', Pa : ' + str(Pa)
            
            '''
            #tried_actions는 dict인데, 여기 있으면 빼고 리턴한다.
            if tried_actions is not None:
                while (col, row) in tried_actions:
                    pred_pos = np.delete(pred_pos, tmp_pred_pos)
                    
                    if len(pred_pos) == 0:
                        print 'exit by if len(pred_pos) == 0: 222'
                        start = False
                        break
                    
                    tmp_pred_pos = np.argmax(pred_pos)
                    tmp_row = int(tmp_pred_pos / 9)
                    tmp_col = tmp_pred_pos - tmp_row * 9
                    tmp_row += 1
                    tmp_col += 1
                    
                    row = 10 - tmp_row
                    col = tmp_col
                    Pa = pred_pos_org[tmp_pred_pos]
        
            print "predict Elapsed : " + str(t2 - t1) + " type : " + type + "   " + str(col) + ", " + str(row) + ', Pa : ' + str(Pa)
            '''
            
        #print 'colrow50 : (' + str(col) + ',' + str(row) + ')' + ', Pa : ' + str(Pa)
        #Pa = round(Pa, 4)
        return (col, row, Pa)
    
    def predict_valuenet(self, game):
        #나중에 여기 valuenet call해서 리턴하게 수정해야함.
        #return random.choice([-1, 1])
    
        result = 1
    
        try:
            tt = game.getargumenttopredictvalue()
            if tt is None:
                return -1
            
            #print 'predict_valuenet01'
            
            predicted_value = self.m_VALUE.predict(np.asarray([tt], dtype=np.float))
            if predicted_value[0][0] < 0:
                result = -1
            
            #print 'predict_valuenet02'
        except Exception as e:
            print "Unexpected error in predict_valuenet : ", sys.exc_info()[0]
            print e
            pass
        
        return result
    
        #return random.choice([-1, 1])