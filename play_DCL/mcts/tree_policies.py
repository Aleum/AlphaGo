from __future__ import division
import numpy as np
from const import *
from play_gtp import *

class UCB1(object):
    """
    The typical bandit upper confidence bounds algorithm.
    """
    def __init__(self, c):
        self.c = c

    def __call__(self, action_node):
        if self.c == 0:  # assert that no nan values are returned
                        # for action_node.n = 0
            return action_node.q

        return (action_node.q +
                self.c * np.sqrt(2 * np.log(action_node.parent.n) /
                                 action_node.n))


def flat(_):
    """
    All actions are considered equally useful
    :param _:
    :return:
    """
    return 0


class PUCT(object):
    """
    The typical bandit upper confidence bounds algorithm.
    """
    def __init__(self, c):
        self.c = c

    def __call__(self, action_node):
        if self.c == 0:
            return action_node.Q
        
        '''
        col = action_node.action.move[0]
        row = action_node.action.move[1]
        simulgame = action_node.parent.state.state
        ms = simulgame.score_move((col, row))
        '''
        
        if action_node.active == 0:
            return 0
        
        sumofNv = 0
        for sibling in action_node.parent.children.values():
            sumofNv += sibling.Nv
         
        u = self.c*action_node.Pa*np.sqrt(sumofNv)/(1+action_node.Nv)
        
        sum = action_node.Q + u
        print action_node.action.tostr() + ', sum : ' + str(sum) + ', u : ' + str(u) + ', Q : ' + str(action_node.Q)

        #return (action_node.Q + u)
        #return (action_node.Q + u + g_mcts_msweight*action_node.Wms)
        return (action_node.Q + u)
        
        