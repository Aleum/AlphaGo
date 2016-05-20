import string, random, sys, math, copy
import config
from const import *
from utils import *

from block import Block
from eye import Eye
from gothread import Thread
from board_experimental import BoardExperimental
from board_analysis import BoardAnalysis

class FloodFill:
    def __init__(self, pos, board):
        self.board = board
        self.neighbour = {}
        self.seen = {}
        self.color = board.goban[pos]
        self.generator = self.flood_fill(pos)
        self.next = self.generator.next

    def flood_fill(self, pos):
        """return all stones reachable from given position:
           width first and don't show positions already seen
           also update neighbour dictionary
        """
        if pos in self.seen:
            return
        self.seen[pos] = True
        yield pos
        generator_list = []
        for pos2 in self.board.iterate_neighbour(pos):
            if self.board.goban[pos2]==self.color:
                generator_list.append(self.flood_fill(pos2))
            else:
                self.neighbour[pos2] = True
        i = 0
        while generator_list:
            if i>=len(generator_list):
                i = 0
            try:
                yield generator_list[i].next()
                i = i + 1
            except StopIteration:
                del generator_list[i]

    def create_block(self):
        block = Block(self.color)
        block.stones.update(self.seen)
        block.neighbour.update(self.neighbour)
        return block
    

class Board(BoardExperimental, BoardAnalysis):
    """Go board: one position in board and relevant methods

       Attributes:
       size: board size
       side: side to move
       self.goban: actual board
       blocks: solidly connected group of stones or empty points as defined in Go rules
               there is reference to same block from every position block has stone
       chains: connected group of stones
               This is for v0.2 or later. Not used currently.
    """
    def __init__(self, size):
        """Initialize board:
           argument: size
        """
        self.size = size
        self.side = BLACK
        self.goban = {} #actual board
        self.init_hash()
        #Create and initialize board as empty size*size
        for pos in self.iterate_goban():
            #can't use set_goban method here, because goban doesn't yet really exists
            self.goban[pos] = EMPTY
            self.current_hash = self.current_hash ^ self.board_hash_values[EMPTY, pos]
        self.blocks = {} #blocks dictionary
        #Create and initialize one whole board empty block
        new_block = Block(EMPTY)
        for pos in self.iterate_goban():
            new_block.add_stone(pos)
        self.block_dict = {}
        self.add_block(new_block)
        self.chains = {}
        self.stone_count = {}
        for color in EMPTY+BLACK+WHITE:
            self.stone_count[color] = 0
        self.ko_flag = PASS_MOVE
        BoardAnalysis.__init__(self)

    def iterate_goban(self):
        """This goes through all positions in goban
           Example usage: see above __init__ method
        """
        for y in range(1, self.size+1):
            for x in range(1, self.size+1):
                yield x, y

    def iterate_neighbour(self, pos):
        """This goes through all neighbour positions in clockwise:
           up, right, down, left
           Example usage: see legal_move method
        """
        x, y = pos
        for x2,y2 in ((x,y+1), (x+1,y), (x,y-1), (x-1,y)):
            if 1<=x2<=self.size and 1<=y2<=self.size:
                yield (x2, y2)

    def iterate_diagonal_neighbour(self, pos):
        """This goes through all neighbour positions in clockwise:
           NE, SE, SW, NW
           Example usage: see analyse_eye_point method
        """
        x, y = pos
        for x2,y2 in ((x+1,y+1), (x+1,y-1), (x-1,y-1), (x-1,y+1)):
            if 1<=x2<=self.size and 1<=y2<=self.size:
                yield (x2, y2)

    def iterate_neighbour_and_diagonal_neighbour(self, pos):
        for pos2 in self.iterate_neighbour(pos):
            yield pos2
        for pos2 in self.iterate_diagonal_neighbour(pos):
            yield pos2

    def pos_near_edge(self, pos):
        x, y = pos
        if x in (1, self.size):
            return True
        if y in (1, self.size):
            return True
        return False

    def pos_near_corner(self, pos):
        x, y = pos
        if x in (1, self.size) and y in (1, self.size):
            return True
        return False

    def iterate_blocks(self, colors):
        """This goes through all distinct blocks on board with given colors.
           Example usage: see analyze_unconditionally_alive
        """
        for block_id in self.block_dict:
            block = self.block_dict[block_id]
            if block.color in colors:
                yield block

    def iterate_neighbour_blocks(self, block):
        """Go through all neighbour positions and add new blocks.
           Return once for each new block
        """
        blocks_seen = {}
        stone_list = block.neighbour.keys()
        for stone in stone_list:
            block2 = self.blocks[stone]
            origin2 = block2.get_origin()
            if origin2 not in blocks_seen:
                blocks_seen[origin2] = True
                yield block2

    def iterate_neighbour_eye_blocks(self, eye):
        """First copy eye blocks to list of blocks seen
           Then go through all neighbour positions and add new blocks.
           Return once for each new block
        """
        blocks_seen = eye.parts[:]
        for block in eye.parts:
            for pos in block.neighbour:
                block2 = self.blocks[pos]
                if block2 not in blocks_seen:
                    yield block2
                    blocks_seen.append(block2)

    def init_hash(self):
        """Individual number for every possible color and position combination"""
        random_state = random.getstate()
        random.seed(1)
        self.board_hash_values = {}
        for color in EMPTY+WHITE+BLACK:
            for pos in self.iterate_goban():
                self.board_hash_values[color, pos] = random.randint(-sys.maxint-1, sys.maxint)
        self.current_hash = 0
        #capture hash, for super-ko detection
        self.board_capture_hash_values = {}
        for color in WHITE+BLACK:
            for pos in self.iterate_goban():
                self.board_capture_hash_values[color, pos] = random.randint(-sys.maxint-1, sys.maxint)
        self.current_capture_hash = 0
        random.setstate(random_state)

    def set_goban(self, color, pos):
        """Set stone at position to color and update hash value"""
        old_color = self.goban[pos]
        self.current_hash = self.current_hash ^ self.board_hash_values[old_color, pos]
        self.goban[pos] = color
        self.current_hash = self.current_hash ^ self.board_hash_values[color, pos]
        self.stone_count[old_color] = self.stone_count[old_color] - 1
        self.stone_count[color] = self.stone_count[color] + 1

    def get_goban(self, pos):
        """return stone in goban or if outside, return EDGE"""
        return self.goban.get(pos, EDGE)

    def key(self):
        """This returns unique key for board.
           Returns hash value for current position (Zobrist hashing)
           Key can be used for example in super-ko detection
        """
        return self.current_hash
##        stones = []
##        for pos in self.iterate_goban():
##            stones.append(self.goban[pos])
##        return string.join(stones, "")

    def change_side(self):
        self.side = other_side[self.side]

    def are_adjacent_points(self, pos1, pos2):
        """Tests whether pos1 and pos2 are adjacent.
           Returns True or False.
        """
        for pos in self.iterate_neighbour(pos1):
            if pos==pos2:
                return True
        return False

    def list_empty_3x3_neighbour(self, pos):
        #check normal neighbour positions first
        neighbour_list = []
        for pos2 in self.iterate_neighbour(pos):
            if self.goban[pos2]==EMPTY:
                neighbour_list.append(pos2)

        #check diagonal neighbour positions first
        #this is done to ensure that empty block is/will not splitted
        diagonal_neighbour_list = []
        for pos2 in self.iterate_diagonal_neighbour(pos):
            if self.goban[pos2]==EMPTY:
                diagonal_neighbour_list.append(pos2)
                
        return neighbour_list, diagonal_neighbour_list

    def is_3x3_empty(self, pos):
        if self.goban[pos]!=EMPTY: return False
        neighbour_list, diagonal_neighbour_list = self.list_empty_3x3_neighbour(pos)
        if len(neighbour_list)==4 and len(diagonal_neighbour_list)==4:
            return True
        return False

    def check_neighbour(self, block, pos):
        if pos in block.stones: #this is slight optimization: can't be neighbour if belongs to block
            return
        for pos2 in self.iterate_neighbour(pos):
            if pos2 in block.stones:
                break #yes, pos is neighbour
        else: #no, it's not neighbour
            #was it neighbour to block? remove it if it is
            if pos in  block.neighbour:
                del block.neighbour[pos]

    def add_stone(self, color, pos):
        """add stone or empty at given position
           color: color of stone or empty
           pos: position of stone
           This will add stone to existing block or create new block.
           In case need to join blocks, smaller blocks are added to bigger blocks one stone at time.
           Everytime stone is added, neighbour attribute is also updated.
           If there is possibility of split, then we flood fill each neighbour width first step at time until floods meet or smaller fill stops.
           Flood is continued as long as there is more than one active flood area.
           If flood fill shows split, then smaller block is removed from bigger block.           
        """
        #global board_backup
        #board_backup = copy.deepcopy(self)
        old_block = self.blocks[pos]
        old_color = old_block.color
        self.set_goban(color, pos)
        
        base_add_block = None #biggest block
        blocks_add_list = [] #other blocks being combined
        add_block_neighbour = {} #potentially new neighbours
        pos_split_list = [] #positions that might now belong to separate blocks
        
        #analyze changes
        for pos2 in self.iterate_neighbour(pos):
            stone = self.goban[pos2]
            if stone==color:
                other_block = self.blocks[pos2]
                if other_block==base_add_block or other_block in blocks_add_list:
                    continue
                if base_add_block:
                    if base_add_block.size()<other_block.size():
                        blocks_add_list.append(base_add_block)
                        base_add_block = other_block
                    else:
                        blocks_add_list.append(other_block)
                else:
                    base_add_block = other_block
            else:
                add_block_neighbour[pos2] = True
                if stone==old_color:
                    pos_split_list.append(pos2)
        
        #combine blocks
        if not base_add_block:
            new_block = Block(color)
            new_block.add_stone(pos)
            self.add_block(new_block)
        else:
            base_add_block.add_stone(pos)
            self.blocks[pos] = base_add_block
            for other_block in blocks_add_list:
                self.combine_blocks(base_add_block, other_block)
            del base_add_block.neighbour[pos]
            new_block = base_add_block
        new_block.neighbour.update(add_block_neighbour)

        #split blocks
        if len(pos_split_list)==0:
            self.delete_block(old_block)
        else:
            #ff=flood_fill
            flood_fill_list = []
            for pos2 in pos_split_list:
                ff = FloodFill(pos2, self)
                flood_fill_list.append(ff)
            blocks_created = []
            i = 0
            #iterate until meets another or exhausted
            while len(flood_fill_list)>1:
                if i>=len(flood_fill_list):
                    i = 0
                try:
                    pos2 = flood_fill_list[i].next()
                    #meets another, remove extra
                    for j in range(len(flood_fill_list)):
                        if j==i:
                            continue
                        ff2 = flood_fill_list[j]
                        if pos2 in ff2.seen:
                            del flood_fill_list[i]
                            break
                    else:
                        i = i + 1
                except StopIteration:
                    #exhausted, create new block
                    block = flood_fill_list[i].create_block()
                    blocks_created.append(block)
                    del flood_fill_list[i]
            #remove new blocks from old blocks
            for block in blocks_created:
                for stone in block.stones:
                    old_block.remove_stone(stone)
                for pos2 in block.neighbour:
                    self.check_neighbour(old_block, pos2)
                self.add_block(block)
            old_block.remove_stone(pos)
            old_block.neighbour[pos] = True
            #are pos neighbour positions also neighbour to reduced old_block?
            for pos2 in self.iterate_neighbour(pos):
                self.check_neighbour(old_block, pos2)

        #if not self.check_block_consistency():
        #    self.__dict__ = board_backup.__dict__
        #    self.add_stone(color, pos)

    def check_block_consistency(self):
        for block in self.iterate_blocks():
            for pos in block.stones:
                if self.blocks[pos]!=block:
                    stop()
                    print block, pos
                    return False
                for pos2 in self.iterate_neighbour(pos):
                    if self.goban[pos2]==block.color and pos2 not in block.stones:
                        stop()
                        print block, pos, pos2
                        return False
            block_old_neighbour = block.neighbour
            self.calculate_neighbour(block)
            if block_old_neighbour!=block.neighbour:
                stop()
                print block, block_old_neighbour, block.neighbour
                return False
        for pos in self.iterate_goban():
            block = self.blocks[pos]
            if id(block) not in self.block_dict:
                stop()
                print block, pos
                return False
            ff = FloodFill(pos, self)
            try:
                while 1:
                    ff.next()
            except StopIteration:
                pass
            block2 = ff.create_block()
            if block2.stones!=block.stones:
                stop()
                print block, pos, block.stones, block2.stones
                return False
            if block2.neighbour!=block.neighbour:
                stop()
                print block, pos, block.neighbour, block2.neighbour
                return False
        return True

    def add_block(self, block):
        self.block_dict[id(block)] = block
        for stone in block.stones:
            self.blocks[stone] = block

    def delete_block(self, block):
        del self.block_dict[id(block)]

    def combine_blocks(self, new_block, other_block):
        """add all stones from other block to new block
           make board positions to point at new block
        """
        new_block.add_block(other_block)
        for stone in other_block.stones:
            self.blocks[stone] = new_block
        self.delete_block(other_block)

    def split_marked_group(self, block, mark):
        """move all stones with given mark to new block
           Return splitted group.
        """
        new_block = Block(block.color)
        for stone, value in block.stones.items():
            if value==mark:
                block.remove_stone(stone)
                new_block.add_stone(stone)
        return new_block

    def flood_mark(self, block, start_pos, mark):
        """mark all stones reachable from given
           starting position with given mark
        """
        to_mark = [start_pos]
        while to_mark:
            pos = to_mark.pop()
            if block.stones[pos]==mark: continue
            block.stones[pos] = mark
            for pos2 in self.iterate_neighbour(pos):
                if pos2 in block.stones:
                    to_mark.append(pos2)

    def calculate_neighbour(self, block):
        """find all neighbour positions for block
        """
        block.neighbour = {}
        for stone in block.stones:
            for pos in self.iterate_neighbour(stone):
                if pos not in block.stones:
                    block.neighbour[pos] = True

    def change_block_color(self, color, pos):
        """change block color and
           set same color to all block positions in goban
        """
        block = self.blocks[pos]
        block.color = color
        for pos2 in self.blocks[pos].stones:
            self.set_goban(color, pos2)

    def remove_block(self, pos):
        self.change_block_color(EMPTY, pos)

    def list_block_liberties_and_stones(self, block):
        """Returns list of liberties for block of stones.
        """
        liberties = []
        stones = []
        for pos2 in block.neighbour:
            if self.goban[pos2]==EMPTY:
                liberties.append(pos2)
            else:
                stones.append(pos2)
        return liberties, stones

    def list_block_liberties_all_distances(self, block, liberties_distance=1):
        """Returns list of liberties for block of stones.
        """
        liberties = []
        for pos2 in block.neighbour:
            if self.goban[pos2]==EMPTY:
                liberties.append(pos2)
        liberty_dict = {}
        for liberty in liberties:
           liberty_dict[liberty] = True
        if liberties_distance<=1:
            return liberties, liberty_dict

        liberties_distance = liberties_distance - 1
        while liberties_distance:
            liberties = self.next_order_block_liberties(block, liberty_dict)
            liberties_distance = liberties_distance - 1
        return liberties, liberty_dict

    def list_block_liberties(self, block, liberties_distance=1):
        """Returns list of liberties for block of stones.
        """
        liberties, liberty_dict = self.list_block_liberties_all_distances(block, liberties_distance)
        return liberties

    def list_liberties(self, pos):
        block = self.blocks[pos]
        return self.list_block_liberties(block)

    def block_liberties(self, block, liberties_distance=1):
        """Returns number of liberties for block of stones.
        """
        liberties = self.list_block_liberties(block, liberties_distance)
        return len(liberties)

    def liberties(self, pos):
        """Returns number of liberties for block of stones in given position.
        """
        return self.block_liberties(self.blocks[pos])

    def liberties_n(self, pos, maxn):
        block = self.blocks[pos]
        count = 0
        for pos2 in block.neighbour:
            if self.goban[pos2]==EMPTY:
                count = count + 1
                if count>=maxn:
                    return count
        return count

    def initialize_undo_log(self):
        """Start new undo log
        """
        self.undo_log = []

    def add_undo_info(self, method, color, pos):
        """Add info needed to undo move
           at start of log.
           Its added to start because changes are undone in reverse direction.
        """
        self.undo_log.insert(0, (method, color, pos))

    def apply_undo_info(self, method, color, pos):
        """Apply given change to undo part of move.
        """
        if method=="add_stone":
            self.add_stone(color, pos)
        elif method=="change_block_color":
            self.change_block_color(color, pos)
        elif method=="ko_flag":
            self.ko_flag = pos

    def legal_move(self, move):
        """Test whether given move is legal.
           Returns truth value.
        """
        if move==PASS_MOVE:
            return True
        if move not in self.goban: return False
        if self.goban[move]!=EMPTY: return False
        for pos in self.iterate_neighbour(move):
            if self.goban[pos]==EMPTY: return True
            if self.goban[pos]==self.side and self.liberties_n(pos, 2)>1: return True
            if self.goban[pos]==other_side[self.side] and self.liberties_n(pos, 2)==1: return True
        return False

    def make_move(self, move):
        """Make move given in argument.
           Returns move or None if illegl.
           First we check given move for legality.
           Then we make move and remove captured opponent groups if there are any.
           While making move record what is needed to undo the move.
        """
        self.initialize_undo_log()
        if move==PASS_MOVE:
            self.change_side()
            return move
        if self.legal_move(move):
            self.add_stone(self.side, move)
            self.add_undo_info("add_stone", EMPTY, move)
            remove_color = other_side[self.side]
            blocks_removed = 0
            ko_pos = PASS_MOVE
            for pos in self.iterate_neighbour(move):
                if self.goban[pos]==remove_color and self.liberties_n(pos, 1)==0:
                    blocks_removed = blocks_removed + 1
                    if self.blocks[pos].size()==1:
                        ko_pos = pos
                    self.remove_block(pos)
                    self.add_undo_info("change_block_color", remove_color, pos)
            self.change_side()
            if blocks_removed!=1:
                ko_pos = PASS_MOVE
            if ko_pos!=PASS_MOVE and self.liberties_n(move, 2)>1:
                ko_pos = PASS_MOVE
            self.add_undo_info("ko_flag", self.side, self.ko_flag)
            self.ko_flag = ko_pos
            return move
        return None

    def undo_move(self, undo_log):
        """Undo move using undo_log.
        """
        self.change_side()
        for method, color, pos in undo_log:
            self.apply_undo_info(method, color, pos)

    def has_block_status(self, colors, status):
        for block in self.iterate_blocks(colors):
            if block.status==status:
                return True
        return False

    def territory_as_dict(self):
        territory = {}
        for block in self.iterate_blocks(EMPTY):
            if block.status in (WHITE_UNCONDITIONAL_TERRITORY, BLACK_UNCONDITIONAL_TERRITORY):
                territory.update(block.stones)
        return territory

    def __str__(self):
        """Convert position to string suitable for printing to screen.
           Returns board as string.
        """
        s = self.side + " to move:\n"
        board_x_coords = "   " + x_coords_string[:self.size]
        s = s + board_x_coords + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        for y in range(self.size, 0, -1):
            if y < 10:
                board_y_coord = " " + str(y)
            else:
                board_y_coord = str(y)
            line = board_y_coord + "|"
            for x in range(1, self.size+1):
                line = line + self.goban[x,y]
            s = s + line + "|" + board_y_coord + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        s = s + board_x_coords + "\n"
        return s

    def as_sgf_with_labels(self, label_dict):
        s = ["(;GM[1]SZ[%i]" % self.size]
        swhite = ["AW"]
        sblack = ["AB"]
        slabel = ["LB"]
        for pos in self.iterate_goban():
            if self.goban[pos]==WHITE:
                swhite.append("[" + move_as_sgf(pos, self.size) + "]")
            if self.goban[pos]==BLACK:
                sblack.append("[" + move_as_sgf(pos, self.size) + "]")
        for pos in label_dict:
            slabel.append("[%s:%s]" % (move_as_sgf(pos, self.size), label_dict[pos]))
        if len(swhite)>1: s.append(string.join(swhite, ""))
        if len(sblack)>1: s.append(string.join(sblack, ""))
        if len(slabel)>1: s.append(string.join(slabel, ""))
        s.append(")")
        return string.join(s, "\n")

    def print_move_list(self, move_list):
        d = list2dict(move_list, "@")
        print self.as_sgf_with_labels(d)
        print move_list_as_string(move_list)
