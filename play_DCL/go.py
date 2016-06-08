# -*- coding: ms949 -*-
import numpy as np
from play_gtp import *

import copy
from const import *
import sys
sys.setrecursionlimit(10000)
class GoAction(object):
    def __init__(self, move):
        self.move = np.asarray(move)

    def __eq__(self, other):
        return all(self.move == other.move)
    def __hash__(self):
        return 10*self.move[0] + self.move[1]
    def __str__(self):
        #return str(self.move[0]) + "," + str(self.move[1])
        return x_coords_string[self.move[0]-1] + "," + str(self.move[1])
    def tostr(self):
        #return str(self.move[0]) + "," + str(self.move[1])
        return x_coords_string[self.move[0]-1] + "," + str(self.move[1])
    
    

class GoState(object):
    def __init__(self, state):
        self.state = simple_go.Game(9)
        self.state = state              #state가 여기서는 Game 임.
        
        legalmove = {}
        legalmove = self.state.list_moves()
        legalmove.remove((-1, -1))
                
        count_restrict = 0
        self.actions = []
        for move in legalmove:
            count_restrict = count_restrict + 1
            if count_restrict < g_mcts_legalmove_restrict:
                self.actions.append(GoAction([move[0], move[1]]))
            else:
                break            

    def perform(self, action):
        #현재상태에서 들어온 action으로 착수해야함.
        
        clonestate = simple_go.Game(9)
        clonestate = copy.deepcopy(self.state)
        clonestate.make_move((action.move[0], action.move[1]))
                
        return GoState(clonestate)

    def reward(self, parent, action):
        return 10
        '''
        if all(self.pos == np.array([2, 2])):
            return 10
        else:
            return -1
        '''

    def is_terminal(self):
        return False

    def __eq__(self, other):
        return self.state.move_history == other.state.move_history
    
    def __hash__(self):
        sum = 0
        for i in range(0, 81):
            if self.state.current_board.goban[i/9+1,i%9+1] != '.':
                sum = sum + pow(2,i)
        return sum
    
    def __str__(self):            
        return self.state.current_board.str2()
    
    def tostr(self):
        return self.state.current_board.str2()
    
    def tostr2(self):
        s = ""
        for move in self.state.move_history:
            s = s + str(move[0]) + str(move[1])        
        return s