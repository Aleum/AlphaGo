import config
from const import *

class Block:
    """Solidly connected group of stones or empy points as defined in Go rules

       Attributes:
       stones: position of stones or empty points
               empty points are like trasparent stones
       liberties: position of liberties
       color: color of stones
    """
    def __init__(self, color):
        self.stones = {}
        self.neighbour = {}
        self.color = color
        self.chain = None

    def add_stone(self, pos):
        """add stone or empty point at given position
        """
        self.stones[pos] = True

    def remove_stone(self, pos):
        """remove stone or empty point at given position
        """
        del self.stones[pos]

    def add_block(self, other_block):
        """add all stones and neighbours to this block
        """
        self.stones.update(other_block.stones)
        self.neighbour.update(other_block.neighbour)

    def mark_stones(self, mark):
        """mark all stones with given value
        """
        for stone in self.stones:
            self.stones[stone] = mark

    def size(self):
        """returns block size
        """
        return len(self.stones)

    def max_liberties(self):
        """returns maximum amount liberties possible for this block size
               44
              4334
             432234
            43211234
           4321XX1234
            43211234
             432234
              4334
               44
        """
        if config.use_nth_order_liberties>1:
            res = 0.0
            for i in range(1, config.use_nth_order_liberties+1):
                res += self.size() * 2 + 2 + 4*(i-1) / float(i)
            return res
##            return self.size() * 2 + 2 +\
##                   0.5 * (self.size() * 2 + 6) +\
##                   1.0/3.0 * (self.size() * 2 + 10)
        else:
            return self.size() * 2 + 2

    def iterate_threads(self):
        for pos1 in self.threads:
            for pos2 in self.threads[pos1]:
                yield self.threads[pos1][pos2]

    def get_origin(self):
        """return origin pos of block
        """
        return min(self.stones)

