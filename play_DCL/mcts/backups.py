# -*- coding: ms949 -*-

from __future__ import division
from .graph import StateNode, ActionNode
from const import *
import random
from go import *

class Bellman(object):
    """
    A dynamical programming update which resembles the Bellman equation
    of value iteration.

    See Feldman and Domshlak (2014) for reference.
    """
    def __init__(self, gamma):
        self.gamma = gamma

    def __call__(self, node):
        """
        :param node: The node to start the backups from
        """
        while node is not None:
            node.n += 1
            if isinstance(node, StateNode):
                node.q = max([x.q for x in node.children.values()])
            elif isinstance(node, ActionNode):
                n = sum([x.n for x in node.children.values()])
                node.q = sum([(self.gamma * x.q + x.reward) * x.n
                              for x in node.children.values()]) / n
            node = node.parent


def monte_carlo(node):
    """
    A monte carlo update as in classical UCT.

    See feldman amd Domshlak (2014) for reference.
    :param node: The node to start the backup from
                 StateNode 임.
    """
    r = node.reward
    while node is not None:
        node.n += 1
        node.q = ((node.n - 1)/node.n) * node.q + 1/node.n * r
        
        #threshold값을 넘으면 expansion 한다.
        if node.type == 'StateNode' and node.n > g_mcts_threshold and node.is_terminal() == True:
            #여기 수정해야함. SL을 호출해서 확장해야함.
            nextaction = random.choice(node.untried_actions)
            node.children[nextaction].sample_state()
            node.children[nextaction].active = 1
        
        node = node.parent
    
def expansionbybackup(node):
    #문제:실제 게임을 두진 않았지만, 
    tried_action_dict = {}
    for actionnode in node.tried_actions:
        #print actionnode.action.tostr()
        #(col, row)를 key로 넣음.
        tried_action_dict[(actionnode.action.move[0], actionnode.action.move[1])] = actionnode.action.tostr()
        
    move = node.state.state.network.predict(node.state.state, type = 'SLPOLICY', tried_actions = tried_action_dict)
    nextaction = GoAction([move[0], move[1]])
    #print 'expansionbybackup at : ' + str(move[0]) + ',' + str(move[1])
    t = node.children[nextaction].sample_state()
    node.children[nextaction].Pa = move[2]
    #node.children[nextaction].active = 1
    return t

def minigo_backup(node):
    '''
    node는 StateNode 임.
    '''
    v_valuenet = node.result_valuenet
    v_rollout = node.result_rollout        
#     v_movescore = node.result_movescore
    
    while node is not None:
        #threshold값을 넘으면 expansion 한다.
        if node.type == 'ActionNode' :
            #여기서 Nv, Wv, Nr, Wr, Q 업데이트
            node.Nv += 1
            node.Wv += v_valuenet
            node.Nr += 1 - g_mcts_vl
            node.Wr += v_rollout
            node.Q = (1-g_mcts_lamda)*node.Wv/node.Nv + g_mcts_lamda*node.Wr/node.Nr
    
            #threshold값을 넘으면 expansion 한다.        
            if node.Nr > g_mcts_threshold:
                #print 'expansion in backup'
                expansionbybackup(node.parent)
        
        node = node.parent
        
        
    