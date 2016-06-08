# -*- coding: ms949 -*-
import random, time

from play_gtp import *
from const import *
import copy
from go import *

def immediate_reward(state_node):
    """
    Estimate the reward with the immediate return of that state.
    :param state_node:
    :return:
    """
    return state_node.state.reward(state_node.parent.parent.state,
                                   state_node.parent.action)


class RandomKStepRollOut(object):
    """
    Estimate the reward with the sum of returns of a k step rollout
    """
    def __init__(self, k):
        self.k = k

    def __call__(self, state_node):
        self.current_k = 0

        def stop_k_step(state):
            self.current_k += 1
            return self.current_k > self.k or state.is_terminal()

        return _roll_out(state_node, stop_k_step)


def random_terminal_roll_out(state_node):
    """
    Estimate the reward with the sum of a rollout till a terminal state.
    Typical for terminal-only-reward situations such as games with no
    evaluation of the board as reward.

    :param state_node:
    :return:
    """
    def stop_terminal(state):
        return state.is_terminal()

    return _roll_out(state_node, stop_terminal)


def _roll_out(state_node, stopping_criterion):
    reward = 0
    state = state_node.state
    parent = state_node.parent.parent.state
    action = state_node.parent.action
    while not stopping_criterion(state):
        reward += state.reward(parent, action)

        action = random.choice(state_node.state.actions)
        parent = state
        state = parent.perform(action)

    return reward


def evaluation_RL_FR(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
    #print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'RLPOLICY')
    
    simulgame.make_move((col, row))
    #print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'ROLLOUT')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getscore() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return t    

def evaluation_SL_FR(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
    #print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'SLPOLICY')
    
    simulgame.make_move((col, row))
    #print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'ROLLOUT')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getscore() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn  
    
def evaluation_FR_FR(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
    #print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'ROLLOUT')
    
    simulgame.make_move((col, row))
    #print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'ROLLOUT')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getscore() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn
    
def evaluation_SL_SL(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
#     print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'SLPOLICY')
    
    simulgame.make_move((col, row))
#     print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'SLPOLICY')
        
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getwinner() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn

def evaluation_RL_RL(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy.copy(state_node.state.state)
    
#     print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'RLPOLICY')
    simulgame.make_move((col, row))
#     print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'RLPOLICY')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getwinner() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn

def evaluation_FR_RL(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
    #print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'ROLLOUT')
    
    simulgame.make_move((col, row))
    #print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'RLPOLICY')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getscore() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn

def evaluation_FR_SL(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
    #print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'ROLLOUT')
    
    simulgame.make_move((col, row))
    #print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'SLPOLICY')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getscore() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn

def evaluation_SL_RL(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
    #print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'SLPOLICY')
    
    simulgame.make_move((col, row))
    #print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'RLPOLICY')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getscore() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn

def evaluation_RL_SL(state_node):
    '''
    state_node : StateNode
        
    if state_node.parent is None:
        return state_node.reward
    if state_node.parent.parent is None:
        return state_node.reward
    '''
    
    t1 = time.time()
    
    '''
    . 여기서 valuenet으로 계산하고,
    . reward로 쭉쭉 계산한다. 게임 끝까지.
    '''
    simulgame = simple_go.Game(9)
    simulgame = copy(state_node.state.state)
    
    #print "simulgame : \n" + str(simulgame.current_board)    
        
    if state_node.result_valuenet == 0:
        state_node.result_valuenet = simulgame.network.predict_valuenet(simulgame)
        
    #nextaction은 GoAction 이다.
    col, row, prob = simulgame.network.predict(simulgame, type = 'RLPOLICY')
    
    simulgame.make_move((col, row))
    #print "simulgame after 1 run by SL " + str(row) + ", " + str(col) + " : \n" + str(simulgame.current_board)

    turn = 0
    sumofmovescore = 0
    while simulgame.is_end(by_score=True) == False:
        col, row, prob = simulgame.network.predict(simulgame, type = 'SLPOLICY')
        
        sumofmovescore += simulgame.score_move((col, row))
                
        #print "predict result by ROLLOUT: " + str(col) + ", " + str(row)        
                
        #if simulgame.legal_move(tt) == True: 
        result = simulgame.make_move((col, row))
        if result == None:
            print 'exit1'
            break
            #else:
                #print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(simulgame.current_board)                
        #else:
            #print 'exit3'
            #break
        
        turn += 1
    
    #여기 나중에 코드 추가. score_BLACK, score_WHITE를 비교해서 자신이 이겼으면 1, 아니면 0
    if simulgame.getscore() > 0:
        state_node.result_rollout = 1
    else:
        state_node.result_rollout = -1

    t2 = time.time()
    print "Evaluation Elapsed : " + str(t2 - t1) + " turn : " + str(turn)
    return turn