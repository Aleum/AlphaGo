import numpy as np

class MazeAction(object):
    def __init__(self, move):
        self.move = np.asarray(move)

    def __eq__(self, other):
        return all(self.move == other.move)
    def __hash__(self):
        return 10*self.move[0] + self.move[1]
    def __str__(self):
        return str(self.move[0]) + "," + str(self.move[1])
    def tostr(self):
        return str(self.move[0]) + "," + str(self.move[1])

class MazeState(object):
    def __init__(self, pos):f
        self.pos = np.asarray(pos)
        self.actions = [MazeAction([1, 0]),
                        MazeAction([0, 1]),
                        MazeAction([-1, 0]),
                        MazeAction([0, -1])]

    def perform(self, action):
        pos = self.pos + action.move  
        '''      
        pos[0] = min(pos[0], 2)
        pos[1] = min(pos[1], 2)
        pos[0] = max(pos[0], 0)
        pos[1] = max(pos[1], 0)
        '''        
        return MazeState(pos)

    def reward(self, parent, action):
        if all(self.pos == np.array([2, 2])):
            return 10
        else:
            return -1

    def is_terminal(self):
        return False

    def __eq__(self, other):
        return all(self.pos == other.pos)
    def __hash__(self):
        return 10 * self.pos[0] + self.pos[1]    
    def __str__(self):
        return str(self.pos[0]) + ", " + str(self.pos[1])
    
    def tostr(self):
        return str(self.pos[0]) + ", " + str(self.pos[1])
