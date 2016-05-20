import string, random, sys, math, copy
import config
from const import *
from utils import *

from block import Block
from eye import Eye
from gothread import Thread

class BoardExperimental:
    """experimental and old code
       some of this is actually still used, for example play_gtp.py:final_score_as_string calls score_position() which calls score_position_with_liberties()
    """
    
    def simple_same_block(self, pos_list):
        """Check if all positions in pos_list are in same block.
           This searches only at immediate neighbour.
           Return True if they are or False if not or can't decide with this simple search.
        """
        if len(pos_list) <= 1:
            return True
        color = self.goban[pos_list[0]]
        temp_block = Block(color)
        #Add all stones in pos_list and their neighbour to block if they have same color.
        for pos in pos_list:
            temp_block.add_stone(pos)
            for pos2 in self.iterate_neighbour(pos):
                if self.goban[pos2]==color:
                    temp_block.add_stone(pos2)
        
        new_mark = 2 #When stones are added they get by default value True (==1)
        self.flood_mark(temp_block, pos_list[0], new_mark)
        for pos in pos_list:
            if temp_block.stones[pos]!=new_mark:
                return False
        return True

    def old_add_stone(self, color, pos):
        """add stone or empty at given position
           color: color of stone or empty
           pos: position of stone
           This will create new block for stone
           and add stones from same colored neighbour blocks if any.
           Also makes every position in combined block to point to block.
           Remove pos from existing block and potentially split it.
           Finally calculate new neighbours for all changed blocks:
           This is needed only when block is split into 2 or more blocks.
           Other cases are handed in need to do basis.
        """
        old_block = self.blocks[pos]
        old_color = old_block.color
        old_block.remove_stone(pos)
        if old_block.size()==0:
            self.block_list.remove(old_block)
        self.set_goban(color, pos)
        new_block = Block(color)
        new_block.add_stone(pos)
        self.add_block(new_block)
        changed_blocks = [] #only those blocks that need complete neighbour calculation

        #old_block: Is anything left?
        #           Is it split into pieces?
        #new_block: Is there existing same colored neighbour blocks?
        #both and all existing neighbours: calculate neighbor list (from scratch?)
        #........OO.........
        #......OO.O.........
        #......O.!.O...OOOO.
        #.......O.OO...O..O.
        #.XXX...XX....XX.O..
        #.X.!XX.X.!XX.X.!...
        #.XXX...XX.....X.O..
        #..........X!X......
        #...........O.......

        #combine and split blocks as needed
        split_list = []
        for pos2 in self.iterate_neighbour(pos):
            other_block = self.blocks[pos2]
            if self.goban[pos2]==color:
                new_block = self.combine_blocks(new_block, other_block)
            else:
                new_block.neighbour[pos2] = True
                if self.goban[pos2]==old_color:
                    split_list.append(pos2)
        
        #If these splits are actually trivially same: do update fast
        if self.simple_same_block(split_list):
            old_block.neighbour[pos] = True
            #are pos neighbour positions also neighbour to reduced old_block?
            for pos2 in self.iterate_neighbour(pos):
                if pos2 not in old_block.stones: #this if is slight optimization: can't be neighbour if belongs to block
                    for pos3 in self.iterate_neighbour(pos2):
                        if pos3 in old_block.stones:
                            break #yes, pos2 is neighbour
                    else: #no, it's not neighbour
                        #was it neighbour to old_block? remove it if it is
                        if pos2 in  old_block.neighbour:
                            del old_block.neighbour[pos2]
        else:
            changed_blocks.append(old_block) #now we need this
            old_block.mark_stones(0)
            last_old_mark = 0
            for pos2 in split_list:
                other_block = self.blocks[pos2]
                if other_block.stones[pos2]==0:
                    last_old_mark = last_old_mark + 1
                    self.flood_mark(other_block, pos2, last_old_mark)
                    if last_old_mark>1:
                        splitted_block = self.split_marked_group(other_block, last_old_mark)
                        self.add_block(splitted_block)
                        changed_blocks.append(splitted_block)

        if pos in new_block.neighbour:
            del new_block.neighbour[pos]

        for block in changed_blocks:
            self.calculate_neighbour(block)

##        for block in self.block_list:
##            old_neighbour = block.neighbour
##            self.calculate_neighbour(block)
##            if old_neighbour!=block.neighbour:
##                print old_neighbour
##                print block.neighbour
##                import pdb; pdb.set_trace()

    def old_combine_blocks(self, new_block, other_block):
        """add all stones from other block to new block
           make board positions to point at new block
        """
        if new_block==other_block: return new_block
        if new_block.size() < other_block.size():
            #Optimization: for example if new_block size is one as is usually case
            #and other_block is most of board as is often case when combining empty point to mostly empty board.
            new_block, other_block = other_block, new_block
        new_block.add_block(other_block)
        for stone in other_block.stones:
            self.blocks[stone] = new_block
        self.block_list.remove(other_block)
        return new_block

    def next_order_block_liberties(self, block, liberty_dict):
        liberties = []
        pos2check = liberty_dict.keys()
        while pos2check:
            pos = pos2check.pop()
            for pos2 in self.iterate_neighbour(pos):
                if pos2 in liberty_dict:
                    continue
                if self.goban[pos2]==EMPTY:
                    liberties.append(pos2)
                    liberty_dict[pos2] = True
                elif block and self.goban[pos2]==block.color:
                    pos2check.append(pos2)
                    liberty_dict[pos2] = True
        return liberties

    def score_stone_block(self, block):
        """Score white/black block.
           All blocks whose status we know will get full score.
           Other blocks with unknown status will get score depending on their liberties and number of stones.

           ....8....8-4=4....
           ...XXX...XXX.O....
           ..................
           .7-4=3..6-2=4.....
           ....XX...XX..7-3=4
           .....X...OX...XXX.
           ...............O..
           .....O............
           ..................
           ..................

           ..................
           .....@OOO.........
           .AXXXBxxxO........
           .....@OOO.........
           ..................
           ..................
           @:filled(@) or empty(.)
           s = block.size()
           l = block.liberties()
           L = block.max_liberties()
           s * l / L
           X:3
           x:3/8(.375)
           AX:4 
           XBx@:7*7/16(3.0625)
           XBx.:7*9/16(3.9375)
           X+x:3.375
           AX+x:4.375
           
           r = l / L
           s * (1 - (1-r)^2)
           X:3
           x:0.703125
           AX:4
           XBx@:4.78515625
           XBx.:5.66015625
           X+x:3.703125
           AX+x:4.703125

           ..................
           .....@OO..........
           ..AXXBxxO.........
           .....@OO..........
           ..................
           ..................
           r = l / L
           s * (1 - (1-r)^2)
           X:2
           x:0.611111111112
           X+x:2.611111111112
           AX:3
           AX+x:3.611111111112
           XBx@:3.29861111112
           XBx.:4.13194444444
           
           0.525 A3
           0.2296875 B3
           0.0875 C1
           -0.13125 C3

             ABC    A3
            +---+
           3|x..|3  X:1.5
           2|OXX|2  x:0.4375
           1|.o.|1  O:-0.4375
            +---+    :1.5
             ABC

             ABC    B3
            +---+
           3|.X.|3  X:1.828125
           2|OXX|2  O:-0.75
           1|.o.|1   :1.078125
            +---+   ->.328125
             ABC
        """

        if block.status==UNCONDITIONAL_LIVE:
            score = block.size()
        elif block.status==UNCONDITIONAL_DEAD:
            score = - block.size()
        else:
            if config.use_tactical_reading and config.use_nth_order_liberties:
                liberties_dict = {}
                for pos in block.neighbour:
                    if self.goban[pos]==EMPTY:
                        liberties_dict[pos] = 1.0
                    else: #opponent block
                        block2 = self.blocks[pos]
                        if block2.status==TACTICALLY_DEAD:
                            liberties_dict[pos] = 0.9
                        elif block2.status==TACTICALLY_CRITICAL:
                            if block2.color==self.side:
                                liberties_dict[pos] = 0.1
                            else:
                                liberties_dict[pos] = 0.4
                depth = 1
                liberties_dict2 = liberties_dict
                while depth < config.use_nth_order_liberties:
                    pos_lst = liberties_dict2.keys()
                    liberties_dict2 = {}
                    depth = depth + 1
                    ratio = 1.0 / depth
                    while pos_lst:
                        pos = pos_lst.pop()
                        for pos2 in self.iterate_neighbour(pos):
                            if pos2 in liberties_dict:
                                continue
                            if self.goban[pos2]==EMPTY:
                                liberties_dict2[pos2] = liberties_dict[pos2] = ratio
                            elif self.goban[pos2]==block.color:
                                pos_lst.append(pos2)
                                liberties_dict[pos2] = 0.0
                            else: #self.goban[pos2]==other_side[block.color]:
                                block2 = self.blocks[pos2]
                                if block2.status==TACTICALLY_DEAD:
                                    liberties_dict2[pos2] = liberties_dict[pos2] = ratio * 0.9
                                elif block2.status==TACTICALLY_CRITICAL:
                                    if block2.color==self.side:
                                        liberties_dict2[pos2] = liberties_dict[pos] = ratio * 0.1
                                    else:
                                        liberties_dict2[pos2] = liberties_dict[pos] = ratio * 0.4
                liberties = sum(liberties_dict.values())
                self.tmp_liberties_dict = liberties_dict
            else:
                liberties = float(self.block_liberties(block))
                if config.use_tactical_reading:
                    #grant liberty bonus for critical/dead neighbours
                    for block2 in self.iterate_neighbour_blocks(block):
                        if block2.color==EMPTY:
                            continue
                        if block2.status==TACTICALLY_DEAD:
                            bonus = 0.9
                        elif block2.status==TACTICALLY_CRITICAL:
                            if block2.color==self.side:
                                bonus = 0.1
                            else:
                                bonus = 0.4
                        else:
                            continue
                        for stone in block.neighbour:
                            if stone in block2.stones:
                                liberties = liberties + bonus
                else:
                    #grant half liberty for each neightbour stone in atari
                    for block2 in self.iterate_neighbour_blocks(block):
                        if block2.color==other_side[block.color] and self.block_liberties(block2)==1:
                            for stone in block.neighbour:
                                if stone in block2.stones:
                                    liberties = liberties + 0.5


                if config.use_nth_order_liberties:
                    for i in range(2, config.use_nth_order_liberties+1):
                        liberties = liberties + self.block_liberties(block, i) / float(i)
##                liberties = liberties + 0.5 * self.block_liberties(block, 2)
##                liberties = liberties + 1.0/3.0 * self.block_liberties(block, 3)

            if config.use_oxygen:
                liberties = 0.0
                for stone in block.stones:
                    liberties = liberties + self.oxygen.get(stone, 0.0)
            liberty_ratio = liberties / block.max_liberties()

            if block.status==TACTICALLY_DEAD:
                value_ratio = dead_stone_value_ratio
            elif block.status==TACTICALLY_CRITICAL:
                if block.color==self.side:
                    value_ratio = our_critical_stone_value
                else:
                    value_ratio = other_critical_stone_value
            else:
                value_ratio = normal_stone_value_ratio
            score = block.size() * value_ratio * liberty_ratio
            
            #if config.use_nth_order_liberties:
            #    score = block.size() * normal_stone_value_ratio * liberty_ratio
            #else:
            #    score = block.size() * normal_stone_value_ratio * (1 - (1-liberty_ratio)**2)
        return score

    def score_block(self, block):
        """Score block.
           All blocks whose status we know will get full score.
           White/black blocks will be scored by separate method and
           then we change sign if block was for other side.
        """
        if block.color==EMPTY:
            if block.status==self.side + UNCONDITIONAL_TERRITORY:
                score = block.size()
            elif block.status==other_side[self.side] + UNCONDITIONAL_TERRITORY:
                score = -block.size()
            else: #empty block with unknown status
                score = 0
        else:
            if block.color==self.side:
                score = self.score_stone_block(block)
            else: #block.color==other_side[self.side]
                score = -self.score_stone_block(block)
        return score

    def score_position_with_liberties(self):
        """Score position.
           Analyze position and then sum score for all blocks.
           All blocks whose status we know will get full score.
           Returned score is from side to move viewpoint.
        """
        score = 0
        self.analyze_unconditional_status()
        if config.use_oxygen:
            self.oxygen = self.oxygen_influence()
        for block in self.iterate_blocks(BLACK+WHITE+EMPTY):
            score = score + self.score_block(block)
        return score

    def chinese_score_block(self, block):
        """Score block.
           All blocks whose status we know will get full score.
           White/black blocks will be scored by separate method and
           then we change sign if block was for other side.
        """
        if block.color==EMPTY:
            if block.status==self.side + UNCONDITIONAL_TERRITORY:
                score = block.size()
            elif block.status==other_side[self.side] + UNCONDITIONAL_TERRITORY:
                score = -block.size()
            else: #empty block with unknown status
                color_dict = {}
                for pos in block.neighbour:
                    color = self.goban[pos]
                    color_dict[color] = True
                if len(color_dict)==1: #completely surrounded by one
                    if color==self.side:
                        score = block.size()
                    else: #color==other_side[self.side]
                        score = -block.size()
                else:
                    score = 0
        else:
            if block.color==self.side:
                score = block.size()
            else: #block.color==other_side[self.side]
                score = -block.size()
            if block.status==UNCONDITIONAL_DEAD:
                score = -score
        return score

    def chinese_score_position(self):
        """Score position.
           Analyze position and then sum score for all blocks.
           All blocks whose status we know will get full score.
           Returned score is from side to move viewpoint.
        """
        score = 0
        self.analyze_unconditional_status()
        for block in self.iterate_blocks(BLACK+WHITE+EMPTY):
            score = score + self.chinese_score_block(block)
        return score

    def unconditional_score(self, colors):
        score = [0] * len(colors)
        self.analyze_unconditional_status()
        for block in self.iterate_blocks(WHITE+BLACK+EMPTY):
            for i in range(len(colors)):
                color = colors[i]
                if block.status == color + UNCONDITIONAL_TERRITORY or \
                       (block.color == color and block.status == UNCONDITIONAL_LIVE) or \
                       (block.color == other_side[color] and block.status == UNCONDITIONAL_DEAD):
                    score[i] = score[i] + block.size()
        if len(score)==1:
            return score[0]
        return score

    def calculate_distance_to_stones_or_edge(self):
        self.liberty_distance = {}
        #initialize stones
        for block in self.iterate_blocks(WHITE+BLACK):
            for stone in block.stones:
                self.liberty_distance[stone] = 0
            for pos in self.list_block_liberties(block):
                if pos not in self.liberty_distance:
                    self.liberty_distance[pos] = 1
        #initialize edge
        for i in range(1, self.size+1):
            for pos in ((1, i), (i, 1), (self.size, i), (i, self.size)):
                if pos not in self.liberty_distance:
                    self.liberty_distance[pos] = 1

        pos_list = self.liberty_distance.keys()
        while pos_list:
            pos_list2 = []
            for pos in pos_list:
                new_dist = self.liberty_distance[pos] + 1
                for pos2 in self.iterate_neighbour(pos):
                    if pos2 in self.liberty_distance:
                        continue
                    self.liberty_distance[pos2] = new_dist
                    pos_list2.append(pos2)
            pos_list = pos_list2
                    

    def calculate_initial_distance(self):
        self.thread_color_distance = {}
        for color in WHITE, BLACK:
            self.thread_color_distance[color] = {}
            for pos in self.iterate_thread_anchors():
                self.thread_color_distance[color][pos] = {}
                #print "calculate_initial_distance:", move_as_string(pos, self.size)
                self.flood_fill_calculate_distance(self.thread_color_distance[color][pos], pos, color)

    def flood_fill_calculate_distance(self, dist_dict, start_pos, color):
        other_color = other_side[color]
        dist_dict[start_pos] = 0
        new_pos = {}
        new_pos[start_pos] = True
        while new_pos:
            new_pos_list = new_pos.keys()
            new_pos = {}
            for pos1 in new_pos_list:
                old_distance = dist_dict[pos1]
                for pos2 in self.iterate_neighbour(pos1):
                    if self.goban[pos2] == other_color:
                        continue
                    if self.goban[pos2]==EMPTY:
                        new_dist = old_distance + 1
                    else: #==color
                        new_dist = old_distance #no cost on connecting over stone because it already is there
                    if pos2 not in dist_dict or new_dist < dist_dict[pos2]:
                        dist_dict[pos2] = new_dist
                        #if start_pos==(1,1) and color==WHITE:
                        #    print pos1, pos2, dist_dict[pos2]
                        new_pos[pos2] = True

    def iterate_thread_anchors(self):
        for pos in self.iterate_goban():
            if self.goban[pos]!=EMPTY:
                continue
            count = 0
            for pos2 in self.iterate_neighbour(pos):
                count = count + 1
                if self.goban[pos2] in WHITE+BLACK:
                    yield pos
                    break
            else:
                if count < 4:
                    yield pos

    def thread_has_anchor_color(self, new_thread, pos, color):
        for pos2 in self.iterate_neighbour(pos):
            block = self.blocks[pos2]
            if block.color==color:
                return True
        return False

    def anchor_thread(self, new_thread, pos, color):
        for pos2 in self.iterate_neighbour(pos):
            block = self.blocks[pos2]
            if block.color==color:
                if not pos in block.threads: block.threads[pos] = {}
                if pos==new_thread.pos1:
                    pos3 = new_thread.pos2
                else:
                    pos3 = new_thread.pos1
                block.threads[pos][pos3] = new_thread

    def create_thread(self, pos1, pos2):
        #if pos1==(4, 1) and pos2==(6, 1):
        #    import pdb; pdb.set_trace()            
        for color in WHITE, BLACK:
            if self.thread_color_distance[color][pos1].has_key(pos2):
                new_thread = Thread(pos1, pos2, self.thread_color_distance[color][pos1][pos2] + 1, color)
                anchor1 = self.thread_has_anchor_color(new_thread, pos1, color)
                anchor2 = self.thread_has_anchor_color(new_thread, pos2, color)
                if anchor1 or anchor2:
                    self.anchor_thread(new_thread, pos1, color)
                    self.anchor_thread(new_thread, pos2, color)
                

    def create_all_threads(self):
        self.calculate_initial_distance()
        for block in self.iterate_blocks(WHITE+BLACK):
            block.threads = {}
        for pos1 in self.iterate_thread_anchors():
            for pos2 in self.iterate_thread_anchors():
                if pos1 > pos2:
                    continue
                self.create_thread(pos1, pos2)

    def calculate_threads(self):
        self.create_all_threads()
        for block in self.iterate_blocks(WHITE+BLACK):
            block.strength_sum = 0
            for thread in block.iterate_threads():
                block.strength_sum = block.strength_sum + thread.strength

    def iterate_threads(self):
        seen_thread = {}
        for block in self.iterate_blocks(WHITE+BLACK):
            for thread in block.iterate_threads():
                if (block.color, thread.key()) in seen_thread: continue
                yield thread
                seen_thread[(block.color, thread.key())] = thread

    def score_position_with_threads(self):
        """Score position.
           Analyze position and then sum score for all blocks.
           Returned score is from side to move viewpoint.
        """
        score = 0
        self.analyze_unconditional_status() #other code depends on this, not thread code (not yet at least)
        self.calculate_threads()
        for block in self.iterate_blocks(BLACK+WHITE):
            if block.color==self.side:
                score = score + block.strength_sum
            else:
                score = score - block.strength_sum
        return score

    def calculate_and_normalized_liberty_score(self, thread_routes, reference_point=None):
        liberty_score = {}
        for pos in self.iterate_goban():
            liberty_score[pos] = 0
        for pos in thread_routes:
            for thread, score in thread_routes[pos]:
                liberty_score[pos] = liberty_score[pos] + thread.strength * score

        if reference_point:
            max_score = liberty_score[reference_point]
        else:
            max_score = 0
            for pos in liberty_score:
                max_score = max(max_score, abs(liberty_score[pos]))
            max_score = -max_score

        if max_score==0.0:
            max_score = 1.0
        for pos in liberty_score:
            liberty_score[pos] = liberty_score[pos] * 100.0 / max_score

        return liberty_score
        

    def score_position_with_thread_liberties(self):
        """Score position.
           Analyze position and then sum score for all blocks.
           Returned score is from side to move viewpoint.
        """
        debug_this = True
        score = 0
        self.analyze_unconditional_status() #other code depends on this, not thread code (not yet at least)
        self.calculate_threads()
        self.liberty_score = {}
        for pos in self.iterate_goban():
            self.liberty_score[pos] = 0

        #already initialized
##        for thread in self.iterate_threads():
##            thread.strength = 1.0

        thread_routes = {}

        for block in self.iterate_blocks(BLACK+WHITE):
            for thread in block.iterate_threads():
                pos1, pos2 = thread.pos1, thread.pos2
                if pos1 in block.neighbour:
                    pos1, pos2 = pos2, pos1
                #if not (pos2==(16,15) and pos1==(7,1)): continue
                #import pdb; pdb.set_trace()
                x1, y1 = pos1
                dist_dict2 = self.thread_color_distance[block.color][pos2]
                max_dist = dist_dict2[pos1]
                while pos2:
                    dist2 = dist_dict2[pos2]
                    #score = thread.strength / (1.0 + dist2)
                    #score = math.sqrt(thread.strength) / (1.0 + dist2)
                    score = 1/(1.0+dist2)
                    #score = thread.strength
                    if block.color!=self.side:
                        score = -score
                    self.liberty_score[pos2] =  self.liberty_score[pos2] + score

                    #crossing
                    route_list = thread_routes.get(pos2, [])
                    route_list.append((thread, score))
                    thread_routes[pos2] = route_list
                    
                    shortest_math_dist = INFINITE_DISTANCE
                    new_pos2 = None
                    for pos3 in self.iterate_neighbour(pos2):
                        if self.goban[pos3]==EMPTY and dist2+1 == dist_dict2[pos3] <= max_dist:
                            x3, y3 = pos3
                            math_dist = math.sqrt((x3-x1)**2 + (y3-y1)**2)
                            if math_dist < shortest_math_dist:
                                shortest_math_dist = math_dist
                                new_pos2 = pos3
                    pos2 = new_pos2

        if 0: #do iteration1
            #liberty_score0 = self.calculate_and_normalized_liberty_score(thread_routes, (5, 16))
            liberty_score0 = self.calculate_and_normalized_liberty_score(thread_routes)
            if debug_this:
                print self.as_sgf_with_labels(liberty_score0)
                print "-"*60
            #increase/decrease strength based on crossing
            for thread in self.iterate_threads():
                thread.add_strength = 0.0

            crossings = {}
            for pos in thread_routes:
                for thread1, score1 in thread_routes[pos]:
                    for thread2, score2 in thread_routes[pos]:
                        key1 = thread1.key()
                        key2 = thread2.key()
                        if key1<=key2:
                            cross_key = key1, key2
                        else:
                            cross_key = key2, key1
                        if cross_key in crossings:
                            old_value = crossings[cross_key][0]
                        else:
                            old_value = 0.0
                        new_value = score1 * score2
                        if abs(new_value) > abs(old_value):
                            crossings[cross_key] = (new_value, thread1, thread2)

            for value, thread1, thread2 in crossings.values():
                thread1.add_strength = thread1.add_strength + value
                thread2.add_strength = thread2.add_strength + value

            min_add = 1e30
            max_add = 0.0

            for thread in self.iterate_threads():
                min_add = min(min_add, thread.add_strength)
                max_add = max(max_add, thread.add_strength)
                thread.strength = thread.strength + thread.add_strength

            if debug_this:
                print min_add, max_add
            self.liberty_score_old = self.liberty_score

            #liberty_score1 = self.calculate_and_normalized_liberty_score(thread_routes, (5, 16))
            liberty_score1 = self.calculate_and_normalized_liberty_score(thread_routes)
            if debug_this:
                print self.as_sgf_with_labels(liberty_score1)
                print "-"*60

            iter0_score = 0
            for pos in self.iterate_goban():
                iter0_score = iter0_score + self.liberty_score[pos]
            print "iter0_score:", iter0_score

            self.liberty_score = liberty_score1
            for pos in self.liberty_score:
                self.liberty_score[pos] = -self.liberty_score[pos]

            liberty_score_diff = {}
            for pos in liberty_score0:
                liberty_score_diff[pos] = liberty_score1[pos] - liberty_score0[pos]
            if debug_this:
                print self.as_sgf_with_labels(liberty_score_diff)

        #import pdb; pdb.set_trace()

        for pos in self.iterate_goban():
            add_score = self.liberty_score[pos]
            if 0:
                if add_score > 1.0: add_score = 1.0
                if add_score < -1.0: add_score = -1.0
            #print pos, add_score
            score = score + add_score
        return score

    def oxygen_influence(self):
        """This code is based on blubb's oxygen influence idea.
        """
        has_stones = False
        oxygen = {}
        flow_amount = 0.0
        for pos in self.iterate_goban():
            if self.goban[pos]==EMPTY:
                oxygen[pos] = 1.0
                flow_amount = flow_amount + 1
            else:
                oxygen[pos] = 0.0
                has_stones = True
        if not has_stones:
            return oxygen

        iter = 0
        #print iter, flow_amount
        #while flow_amount>=1.0:
        #while flow_amount>=0.001:
        while flow_amount>=0.1 and iter<5:
            flow_amount = 0.0
            iter = iter + 1
            new_oxygen = {}
            for pos in self.iterate_goban():
                if self.goban[pos]==EMPTY:
                    pos2_list = list(self.iterate_neighbour(pos))
                    for pos2 in pos2_list:
                        new_amount = oxygen.get(pos, 0.0) / len(pos2_list)
                        flow_amount = flow_amount + new_amount
                        new_oxygen[pos2] = new_oxygen.get(pos2, 0.0) + new_amount
                else:
                    new_oxygen[pos] = new_oxygen.get(pos, 0.0) + oxygen.get(pos, 0.0)
            oxygen = new_oxygen
            #print iter, flow_amount
        return oxygen

    def score_position_with_oxygen(self):
        self.analyze_unconditional_status() #other code depends on this, not oxygen code (not yet at least)
        oxygen = self.oxygen_influence()
        score = 0.0
        for pos in self.iterate_goban():
            if self.goban[pos]==self.side:
                score = score + oxygen.get(pos, 0.0)
            else:
                score = score - oxygen.get(pos, 0.0)
        return score

    def stone_score(self):
        return self.stone_count[self.side] - self.stone_count[other_side[self.side]]

