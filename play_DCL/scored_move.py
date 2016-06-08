from utils import move_as_string

from random import random

class ScoredMove:
    def __init__(self, move, score):
        self.move = move
        self.score = score
        self.rand = random() / 1000
        self.nodes = 0
        
    def __cmp__(self, other):
        return cmp(self.score+self.rand, other.score+other.rand)

    def __str__(self):
        s = "(%s, %s" % (move_as_string(self.move), self.score)
        if hasattr(self, "tactical_status"):
            s = s + ", %s" % (self.tactical_status,)
        if self.nodes:
            s = s + ", %s" % (self.nodes,)
        return s + ")"
                             
