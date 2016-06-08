# -*- coding: ms949 -*-
#from __future__ import print_function

import random
import utils

from network import *
from go import *

import sys

class MCTS(object):
    """
    The central MCTS class, which performs the tree search. It gets a
    tree policy, a default policy, and a backup strategy.
    See e.g. Browne et al. (2012) for a survey on monte carlo tree search
    """
    def __init__(self, tree_policy, default_policy, backup):
        self.tree_policy = tree_policy
        self.default_policy = default_policy
        self.backup = backup

    def __call__(self, root, n=10):
        """
        Run the monte carlo tree search.

        :param root: The StateNode
        :param n: The number of roll-outs to be performed
        :return:
        """
        if root.parent is not None:
            raise ValueError("Root's parent must be None.")

        a = 0
        for _ in range(n):
            #node = _get_next_node(root, self.tree_policy)            
            node = _get_next_node2(root, self.tree_policy)
            node.reward = self.default_policy(node)
            print (a, " : ", node, ",", node.reward)
            self.backup(node)
            
            #printgraph('result\\temp' + str(a) + '.gv', root)            
            a = a + 1

        return utils.rand_max(root.children.values(), key=lambda x: x.q).action
    
    def doaction(self, root):
        node = _get_next_node2(root, self.tree_policy)
        node.reward = self.default_policy(node)        
        self.backup(node)
        
    def selection(self, root):
        return _get_next_node2(root, self.tree_policy)

def _expand(state_node):
    action = random.choice(state_node.untried_actions)
    #print("selected action : ", action)
    return state_node.children[action].sample_state()


def _best_child(state_node, tree_policy):
    best_action_node = utils.rand_max(state_node.children.values(),
                                      key=tree_policy)
    return best_action_node.sample_state()

#select과 expansion을 한번에 함.
def _get_next_node(state_node, tree_policy):
    while not state_node.is_terminal():
        if state_node.untried_actions:
            return _expand(state_node)
        else:
            state_node = _best_child(state_node, tree_policy)
    return state_node


'''
def _best_child2(state_node, tree_policy):
    #실제로 확장하지 않은 node에 대해서 그냥 확장해버림. 여기 문제임.
    best_action_node = utils.rand_max(state_node.children.values(), key=tree_policy)
    best_action_node.Nr += g_mcts_vl #virtual loss
    return best_action_node.sample_state()


def _get_next_node2(state_node, tree_policy):
    a = 0
    while state_node.is_terminal() == False:
        state_node = _best_child2(state_node, tree_policy)        
        a += 1
    
    #1. 처음 호출시 여기 들어와서 expansion을 한번 한다.
    #그러면 저 위 while문의 False가 되면서 매번 expansion 한다.
    #5번만 expansion하게하기.
    if a == 0:
    
        try:
            print 'state_node.get_tried_actions_count() : ' + str(state_node.get_tried_actions_count())
            if state_node.get_tried_actions_count() < 5:
                #nextaction = random.choice(state_node.untried_actions)
                move = state_node.state.state.network.predict(state_node.state.state, type = 'SLPOLICY')
                nextaction = GoAction([move[0], move[1]])
                t = state_node.children[nextaction].sample_state()
                state_node.children[nextaction].Nr += g_mcts_vl
                state_node = t
        except Exception as e:
            print "Unexpected error in _get_next_node2 : ", sys.exc_info()[0]
            print e
            state_node = None
            pass
    
    return state_node
'''

def _best_child2(state_node, tree_policy):
    #실제로 확장하지 않은 node에 대해서 그냥 확장해버림. 여기 문제임.
    #실제로 확장한 node만 rand_max의 인자로 넣어야 함. move가 key이고, value가 ActionNode 임.
    best_action_node = utils.rand_max(state_node.tried_actions, key=tree_policy)
    best_action_node.Nr += g_mcts_vl #virtual loss
    return best_action_node.sample_state()
    
'''
def _get_next_node2(state_node, tree_policy):
    try:
        while True:
            #1. 확장한게 2개를 넘으면 best를 찾음.
            if state_node.get_tried_actions_count() >= 2:
                print 'MCTS10'
                state_node = _best_child2(state_node, tree_policy)
            else:
                print 'MCTS20:' + str(state_node.get_tried_actions_count())

                tried_action_dict = {}
                for actionnode in state_node.tried_actions:
                    print actionnode.action.tostr()
                    #(col, row)를 key로 넣음.
                    tried_action_dict[(actionnode.action.move[0], actionnode.action.move[1])] = actionnode.action.tostr()
            
                move = state_node.state.state.network.predict(state_node.state.state, type = 'SLPOLICY', tried_actions = tried_action_dict)
                nextaction = GoAction([move[0], move[1]])
                t = state_node.children[nextaction].sample_state()
                state_node.children[nextaction].Nr += g_mcts_vl
                print 'MCTS21:' + str(move[0]) + ',' + str(move[1]) + ':' + str(state_node.get_tried_actions_count())
                state_node = t
                
            #print 'state_node.get_tried_actions_count() : ' + str(state_node.get_tried_actions_count())
            if state_node.is_terminal() == True:
                print 'MCTS30'
                break
                
        print '----------------------------------------------------'
    
    except Exception as e:
        print "Unexpected error in _get_next_node2 : ", sys.exc_info()[0]
        print e
        state_node = None
        pass
    
    return state_node
'''

def expansionbyselection(node):
    #문제:실제 게임을 두진 않았지만, 
    tried_action_dict = {}
    for actionnode in node.tried_actions:
        #print actionnode.action.tostr()
        #(col, row)를 key로 넣음.
        tried_action_dict[(actionnode.action.move[0], actionnode.action.move[1])] = actionnode.action.tostr()
    
#     print 'EBS01'
    move = node.state.state.network.predict(node.state.state, type = 'SLPOLICY', tried_actions = tried_action_dict)
#     print 'EBS02'
    nextaction = GoAction([move[0], move[1]])
#     print 'EBS03'
    print 'expansionbyselection at : ' + str(move[0]) + ',' + str(move[1])
    t = node.children[nextaction].sample_state()
#     print 'EBS04'
    node.children[nextaction].Nr += g_mcts_vl
    node.children[nextaction].Pa = move[2]
#     print 'EBS05'
    return t
    
def _get_next_node2(state_node, tree_policy):
    while state_node.is_terminal() == False:
        if state_node.get_tried_actions_count() < 3:
            state_node = expansionbyselection(state_node)
            break
        else:
            state_node = _best_child2(state_node, tree_policy)                
            if state_node.is_terminal() == True:
                expansionbyselection(state_node)
                break
                
    

    return state_node
