import string, random, sys, math, copy
import config
from const import *
from utils import *
from types import *

from chain import Chain
from board import Board
from pos_cache import *

class GameOld:
    def __init__(self):
        self.search_cache = {}
        #self.search_trace = open("search.log", "w", 0)

    def score_move(self, move):
        """Score position after move
           and go through moves that capture block that is part of move if any.
           Return best score from these.
        """
##        if self.use_tactics:
##            self.make_move(move)
##            best_score = self.score_tactic_position()
##            if move!=PASS_MOVE:
##                block = self.current_board.blocks[move]
##                liberties = self.current_board.list_block_liberties(block)
##                #Check if this group is now in atari: even if it makes a lots of groups weak, its no use if it just gets captured...
##                if len(liberties)==1:
##                    move2 = liberties[0]
##                    if self.make_move(move2):
##                        #get score from our viewpoint: negative of opponent score
##                        score = -self.score_tactic_position()
##                        if score > best_score:
##                           best_score = score
##                        self.undo_move()
##            self.undo_move()
##            return best_score
        
        self.make_move(move)
        cboard = self.current_board
        best_score = self.score_position()
        if move!=PASS_MOVE:
            block = cboard.blocks[move]
            liberties = cboard.list_block_liberties(block)
            ok_move = True
            #Check if this group is now in atari.
            if len(liberties)==1:
                move2 = liberties[0]
                if self.make_move(move2):
                    #get score from our viewpoint: negative of opponent score
                    score = -self.score_position()
                    if score > best_score:
                       best_score = score
                    self.undo_move()
                    ok_move = False
            else:
                #Check if some our neighbour group is in atari instead.
                for stone in cboard.iterate_neighbour(move):
                    block = cboard.blocks[stone]
                    if block.color==cboard.side and cboard.block_liberties(block)==1:
                        for block2 in cboard.iterate_neighbour_blocks(block):
                            liberties = cboard.list_block_liberties(block2)
                            if len(liberties)==1:
                                move2 = liberties[0]
                                if self.make_move(move2):
                                    #get score from our viewpoint: negative of opponent score
                                    score = -self.score_position()
                                    if score > best_score:
                                       best_score = score
                                    self.undo_move()
                                    ok_move = False
            if ok_move:
                for origin in self.target_blocks:
                    block = cboard.blocks[origin]
                    if block.color==EMPTY:
                        continue
                    if move in block.neighbour:
                        bonus = 2.0 / cboard.block_liberties(block)
                        if config.debug_flag:
                            dprintnl("goal bonus:", bonus, move_as_string(origin, self.size))
                        best_score = best_score - bonus
        self.undo_move()
        return best_score

    def score_move_global(self, move):
        """Score position after move
           and go through moves that capture block that is part of move if any.
           Return best score from these.
        """
        self.make_move(move)
        cboard = self.current_board
        best_score = self.score_position()
        #select biggest of our critical groups and capture that
        block_score_list = []
        other_color = other_side[cboard.side]
        for block in cboard.iterate_blocks(other_color):
            if block.status==TACTICALLY_CRITICAL:
                score = cboard.score_block(block)
                block_score_list.append((score, block))
        if block_score_list:
            block_score_list.sort()
            block = block_score_list[-1][1]
            pos = block.get_origin()
            liberties = liberties = cboard.list_block_liberties(block)
            for move in liberties:
                if self.make_move(move):
                    if cboard.goban[pos]==other_color:
                        status = self.block_tactic_status(pos)
                    else:
                        status = TACTICALLY_DEAD
                    if status==TACTICALLY_DEAD:
                        if config.debug_flag:
                            dprintnl("critical capture of %s with %s" % (
                                self.move_as_string(pos), self.move_as_string(move)))
                        score = -self.score_position()
                        if score > best_score:
                           best_score = score
                    self.undo_move()
                    if status==TACTICALLY_DEAD:
                        break
        
        self.undo_move()
        return best_score

    def critical_move_playout(self):
        #select biggest of our critical groups and capture that
        best_score = self.score_position()
        best_moves = []
        if self.has_2_passes():
            return best_score, best_moves
        cboard = self.current_board
        block_score_list = []
        other_color = other_side[cboard.side]
        for block in cboard.iterate_blocks(other_color):
            if block.status==TACTICALLY_CRITICAL:
                score = cboard.score_block(block)
                block_score_list.append((score, block))
        block_score_list.sort()
        while block_score_list:
            last_entry = block_score_list.pop()
            block = last_entry[1]
            pos = block.get_origin()
            move = block.attack_move
            if self.make_move(move):
                #if config.debug_flag:
                #    print self.current_board
                #    print "critical capture of %s with %s" % (
                #        self.move_as_string(pos), self.move_as_string(block.attack_move))

                score, moves = self.critical_move_playout()
                best_score = -score
                best_moves = [move] + moves
                self.undo_move()

                self.make_move(PASS_MOVE)
                score, moves = self.critical_move_playout()
                score = -score
                if score > best_score:
                    best_score = score
                    best_moves = [PASS_MOVE] + moves
                self.undo_move()
                break
        return best_score, best_moves

    def score_move_with_critical_playout(self, move):
        """Score position after move
           and go through moves that capture block that is part of move if any.
           Return best score from these.
        """
        self.make_move(move)
        score, moves = self.critical_move_playout()
        if config.debug_flag:
            dprintsp("critical playout moves:")
            for move2 in moves:
                dprintsp(self.move_as_string(move2))
            dprintnl()
        self.undo_move()
        return score, [move] + moves

    def score_move_with_critical_bonus(self, move):
        self.make_move(move)
        best_score = self.score_position()
        cboard = self.current_board
        if move!=PASS_MOVE and cboard.blocks[move].status not in (UNCONDITIONAL_DEAD, TACTICALLY_DEAD, TACTICALLY_CRITICAL):
            bonus = 0.0
            for pos in cboard.iterate_neighbour(move):
                if cboard.goban[move]==cboard.goban[pos] and self.status_dict[pos]==TACTICALLY_CRITICAL:
                    bonus = self.block_size_dict[pos] * 0.5
                    if config.debug_flag:
                        dprintnl("%f bonus given for saving critical group" % bonus)
                    best_score = best_score - bonus #opponent gets it as negative
            if bonus: #give additional generic bonus for move intersection
                best_score = best_score - 0.5
        self.undo_move()
        return best_score

    def score_move_with_critical_bonus_and_dead_penalty(self, move):
        self.make_move(move)
        best_score = self.score_position()
        cboard = self.current_board
        if move==PASS_MOVE:
            move_status = UNCONDITIONAL_UNKNOWN
        else:
            bonus = 0.0
            move_status = cboard.blocks[move].status
            if move_status in (UNCONDITIONAL_DEAD, TACTICALLY_DEAD):
                bonus = -1.0
                if config.debug_flag:
                    dprintnl("%f bonus given for playing dead group" % bonus)
            elif move_status==TACTICALLY_CRITICAL:
                bonus = -0.5
                if config.debug_flag:
                    dprintnl("%f bonus given for playing critical group" % bonus)
            else:
                #global critical bonus: if move saves any critical group anywhere: size of group(s)*0.5 + additional 0.5 if any was saved
                bonus = 0.0
                for stone in self.status_dict:
                    if self.status_dict[stone]==TACTICALLY_CRITICAL and \
                       cboard.blocks[stone].status not in (UNCONDITIONAL_DEAD, TACTICALLY_DEAD, TACTICALLY_CRITICAL):
                        bonus = bonus + 0.5
                if bonus: #give additional generic bonus for move intersection
                    bonus = bonus + 0.5
                    if config.debug_flag:
                        dprintnl("%f bonus given for saving critical group(s)" % bonus)
            best_score = best_score - bonus
        self.undo_move()
        return best_score, move_status

    def score_move_with_opponent_playing_bonus(self, move):
        self.make_move(move)
        best_score = self.score_position()
        self.undo_move()
        if move!=PASS_MOVE:
            self.make_move(PASS_MOVE)
            if self.make_move(move):
                score = -self.score_position()
                if score > best_score:
                    bonus = score - best_score
                    if config.debug_flag:
                        dprintnl("opponent bonus:", bonus)
                    best_score = best_score - bonus
                self.undo_move()
            self.undo_move()
        return best_score

    def score_move_global_and_local(self, move):
        #not done!!!!!!
        self.make_move(move)
        cboard = self.current_board
        best_score = self.score_position()

        #global part
        #select biggest of our critical groups and capture that
        block_score_list = []
        other_color = other_side[cboard.side]
        for block in cboard.iterate_blocks(other_color):
            if block.status==TACTICALLY_CRITICAL:
                score = cboard.score_block(block)
                block_score_list.append((score, block))
        if block_score_list:
            block_score_list.sort()
            block = block_score_list[-1][1]
            pos = block.get_origin()
            move = block.attack_move
            if self.make_move(move):
                score = -self.score_position()
                if config.debug_flag:
                    dprintnl("critical capture of %s with %s with score %s" % (
                        self.move_as_string(pos), self.move_as_string(move), score))
                if score > best_score:
                    best_score = score
                self.undo_move()

        #local part
        if move!=PASS_MOVE:
            block = cboard.blocks[move]
            liberties = cboard.list_block_liberties(block)
            #Check if this group is now in atari.
            if len(liberties)==1:
                move2 = liberties[0]
                if self.make_move(move2):
                    #get score from our viewpoint: negative of opponent score
                    score = -self.score_position()
                    if score > best_score:
                       best_score = score
                    self.undo_move()
            else:
                #Check if some our neighbour group is in atari instead.
                for stone in cboard.iterate_neighbour(move):
                    block = cboard.blocks[stone]
                    if block.color==cboard.side and cboard.block_liberties(block)==1:
                        for block2 in cboard.iterate_neighbour_blocks(block):
                            liberties = cboard.list_block_liberties(block2)
                            if len(liberties)==1:
                                move2 = liberties[0]
                                if self.make_move(move2):
                                    #get score from our viewpoint: negative of opponent score
                                    score = -self.score_position()
                                    if score > best_score:
                                       best_score = score
                                    self.undo_move()
        
        
        self.undo_move()
        return best_score


    def score_replies(self, move):
        self.make_move(move)
        best_score = self.current_board.score_position()
        for move in self.iterate_moves():
            self.make_move(move)
            score = -self.current_board.score_position()
            if score > best_score:
                best_score = score
            self.undo_move()
        self.undo_move()
        return best_score

    def select_scored_move(self, remove_opponent_dead=False, pass_allowed=True):
        """Go through all legal moves.
           Keep track of best score and all moves that achieve it.
           Select one move from best moves and return it.
        """
        territory_moves_forbidden = pass_allowed
        all_blocks_decided = True
        if config.use_tactical_reading:
            base_score = self.score_tactic_position()
            self.status_dict = {}
            self.block_size_dict = {}
            for pos, status, attack_move, defend_move, t1, t2, t3, t4 in self.status_list:
                block = self.current_board.blocks[pos]
                if (status in (TACTICALLY_CRITICAL, UNCONDITIONAL_UNKNOWN) and block.color in WHITE+BLACK) or \
                       (status==TACTICALLY_LIVE and block.color==self.current_board.side):
                    all_blocks_decided = False
                    #print "all_blocks_decided = False:", self.move_as_string(pos), status
                for stone in block.stones:
                    self.status_dict[stone] = status
                    self.block_size_dict[stone] = block.size()
        else:
            base_score = self.current_board.score_position()
        if config.debug_flag:
            dprintnl("?", base_score)
        #if abs(base_score)==self.size**2:
        #    import pdb; pdb.set_trace()
        has_unknown_status_block = self.current_board.has_block_status(WHITE+BLACK+EMPTY, UNCONDITIONAL_UNKNOWN)
        has_opponent_dead_block = False
        #get list of unconditionally dead opponent stones:
        opponent_dead_stones = {}
        for block in self.current_board.iterate_blocks(other_side[self.current_board.side]):
            if block.status==UNCONDITIONAL_DEAD:
                opponent_dead_stones.update(block.stones)
                has_opponent_dead_block = True
        #goal: blocks attacked
        self.target_blocks = []
        if len(self.move_history)>=3:
            prev_our_move = self.move_history[-2]
            if prev_our_move!=PASS_MOVE:
                for pos in self.current_board.iterate_neighbour(prev_our_move):
                    block = self.current_board.blocks[pos]
                    if block.get_origin() in self.target_blocks:
                        continue
                    if block.color!=EMPTY and block.status==UNCONDITIONAL_UNKNOWN:
                        self.target_blocks.append(block.get_origin())
        
        #has unsettled blocks
        if has_unknown_status_block and not config.use_tactical_reading:
            pass_allowed = False
        #dead removal has been requested and there are dead opponent stones
        if remove_opponent_dead and has_opponent_dead_block:
            territory_moves_forbidden = False
            pass_allowed = False

        if territory_moves_forbidden:
            forbidden_moves = self.current_board.territory_as_dict()
        else:
            forbidden_moves = {}
            for move in self.current_board.territory_as_dict():
                for pos in self.current_board.iterate_neighbour(move):
                    if pos in opponent_dead_stones:
                        break
                else: #no opponent neighbour dead stone, do not play ever
                    forbidden_moves[move] = True
        best_score = WORST_SCORE
        best_moves = []
        self.search_dict = {}
        all_moves_dead = True
        for move in self.iterate_moves():
            if move in forbidden_moves:
                continue
            if move==PASS_MOVE and config.use_tactical_reading:
                continue
            principal_variation = [move]
            if config.use_tactical_reading:
                #score, principal_variation = self.score_move_with_critical_playout(move)
                #score = -score - base_score
                score, status = self.score_move_with_critical_bonus_and_dead_penalty(move)
                if move!=PASS_MOVE and status not in (UNCONDITIONAL_DEAD, TACTICALLY_DEAD):
                    all_moves_dead = False
                score = -score - base_score
            else:
                score = -self.score_move(move) - base_score
                all_moves_dead = False
            #score = -self.score_replies(move) - base_score
            #self.make_move(move)
            #get score from our viewpoint: negative of opponent score
            #score = -self.current_board.score_position() - base_score
            #score = -self.score_position() - base_score
            self.search_dict[move] = score, principal_variation
            if config.debug_flag:
                dprintnl(score, move_as_string(move, self.size))
            #self.undo_move()
            #Give pass move slight bonus so its preferred among do nothing moves
            if move==PASS_MOVE:
                if not pass_allowed:
                    continue
                score = score + 0.001
            if score >= best_score:
                if score > best_score:
                   best_score = score
                   best_moves = []
                best_moves.append(move)
        if config.debug_flag:
            dprintnl("!", best_score, map(lambda m,s=self.size:move_as_string(m, s), best_moves))
        if all_blocks_decided and all_moves_dead and pass_allowed:
            best_moves = [PASS_MOVE]
            if config.debug_flag:
                dprintnl("!pass forced", map(lambda m,s=self.size:move_as_string(m, s), best_moves))
        if len(best_moves)==0:
            return PASS_MOVE
        return random.choice(best_moves)

    def search_2_1_liberty(self, max_depth):
        return self.search_2_1_liberty_recursively(max_depth, 0, WORST_SCORE, BEST_SCORE)

    def search_2_1_liberty_recursively(self, max_depth, depth, alpha, beta):
        #print depth, self.node_count, alpha, beta, self.move_history[-depth:]
        best_score = WORST_SCORE
        best_variation = []
        if depth>=max_depth or self.has_2_passes():
            #return self.current_board.stone_score(), []
            return self.current_board.score_position_with_liberties(), []
        moves_seen = {}
        all_moves_list = []
        for block in self.current_board.iterate_blocks(WHITE+BLACK):
            move_lst = self.current_board.list_block_liberties(block)
            if len(move_lst)<=2:
                for move in move_lst:
                    if not move in moves_seen:
                        moves_seen[move] = True
                        if len(move_lst)==1:
                            move_score = 4
                        else:
                            move_score = 2
                        if block.color==self.current_board.side:
                            move_score = move_score - 1
                        all_moves_list.append((move_score, move))
        all_moves_list.sort()
        all_moves_list.reverse()
        #all_moves_list.insert(0, (0, PASS_MOVE))
        all_moves_list.append((0, PASS_MOVE))
        for move_score, move in all_moves_list:
            if best_score > beta:
                break
            if self.legal_move(move):
                self.make_move(move)
                score, variation = self.search_2_1_liberty_recursively(max_depth, depth+1, -beta, -alpha)
                score = -score
                self.undo_move()
                if score > best_score:
                    best_score = score
                    best_variation = [move] + variation
                    if score > alpha:
                        alpha = score
                    #print ">", depth+1, self.node_count, best_score, alpha, beta, best_variation
                    #print ">", self.move_history
        return best_score, best_variation

    def capture_either(self, blocks_with_2_liberties_list):
        if not blocks_with_2_liberties_list:
            return PASS_MOVE
        if config.debug_tactics:
            dprintnl("capture_either:", blocks_with_2_liberties_list)
        for i in range(len(blocks_with_2_liberties_list)):
            pos1, liberties1 = blocks_with_2_liberties_list[i]
            for j in range(i+1, len(blocks_with_2_liberties_list)):
                pos2, liberties2 = blocks_with_2_liberties_list[j]
                common_liberties = union_list(liberties1, liberties2)
                if common_liberties:
                    common_liberty = common_liberties[0]
                else:
                    common_liberty = None
                if common_liberty:
                    if self.make_move(common_liberty):
                        if config.debug_tactics:
                            dprintnl("capture_either try move:", self.move_as_string(common_liberty), self.move_as_string(pos1), self.move_as_string(pos2))
                        status1, attack_move, defend_move = self.block_tactic_status_recursive(pos1)
                        status2, attack_move, defend_move = self.block_tactic_status_recursive(pos2)
                        self.undo_move()
                        if status1==TACTICALLY_DEAD or status2==TACTICALLY_DEAD or \
                           (status1==status2==TACTICALLY_CRITICAL):
                            if config.debug_tactics:
                                dprintnl("capture_either succeeds:", status1, status2)
                            return common_liberty
        if config.debug_tactics:
            dprintnl("capture_either fails")
        return PASS_MOVE

    def block_tactic_status_recursive(self, pos, depth=0):
        cboard = self.current_board
        if config.debug_tactics:
            dprintnl(cboard)
            dprintnl(depth, self.move_as_string(pos))
        liberties = cboard.list_block_liberties(cboard.blocks[pos])
        block_color = cboard.blocks[pos].color
        alive = False
        if True or self.current_shadow_origin!=pos:
            if len(liberties)>=3:
                alive = True
        else:
            if len(liberties)>=5 or (len(liberties)>=4 and depth>=2) or (len(liberties)>=3 and depth>=5):
                alive = True
        if alive:
            if config.debug_tactics:
                dprintnl(depth, TACTICALLY_LIVE)
            return TACTICALLY_LIVE, PASS_MOVE, PASS_MOVE
        #can opponent attack this?
        can_attack = PASS_MOVE
        if len(liberties)==1:
            can_attack = liberties[0]
        else: #len(liberties)==2
            if block_color==cboard.side:
                pass_made = True
                self.make_move(PASS_MOVE)
            else:
                pass_made = False
            for move in liberties:
                if self.make_move(move):
                    if config.debug_tactics:
                        dprintnl(depth, "attack", other_side[cboard.side], self.move_as_string(move))
                    status, attack_move, defend_move = self.block_tactic_status_recursive(pos, depth+1)
                    either_attack = False
                    if depth==0 and status==TACTICALLY_CRITICAL and cboard.liberties(move)>1:
                        for pos2 in cboard.iterate_neighbour(move):
                            block2 = cboard.blocks[pos2]
                            if cboard.blocks[pos]!=block2 and \
                                   block2.color==cboard.side and \
                                   cboard.block_liberties(block2)<=2:
                                if config.debug_tactics:
                                    dprintnl(depth, "try double attack", self.move_as_string(pos2))
                                status2, attack_move2, defend_move2 = self.block_tactic_status_recursive(pos2, depth+1)
                                if status2 in (TACTICALLY_DEAD, TACTICALLY_CRITICAL) and \
                                       (defend_move==PASS_MOVE or defend_move!=defend_move2):
                                    either_attack = True
                                if config.debug_tactics:
                                    dprintnl(depth, "double attack result:", either_attack)
                    self.undo_move()
                    if config.debug_tactics:
                        dprintnl(depth, cboard.side, "undo")
                    if status==TACTICALLY_DEAD or either_attack:
                        if config.debug_tactics:
                            dprintnl(depth, "attack succeeds")
                        can_attack = move
                        break
            if pass_made:
                self.undo_move()

        if can_attack!=PASS_MOVE and depth and block_color==other_side[cboard.side]:
            if config.debug_tactics:
                dprintnl(depth, "instant", TACTICALLY_DEAD, self.move_as_string(can_attack))
            return TACTICALLY_DEAD, can_attack, PASS_MOVE

        if can_attack==PASS_MOVE:
            if config.debug_tactics:
                dprintnl(depth, "instant", TACTICALLY_LIVE)
            return TACTICALLY_LIVE, PASS_MOVE, PASS_MOVE

        #can we defend this?
        can_defend = PASS_MOVE
        if block_color==other_side[cboard.side]:
            pass_made = True
            self.make_move(PASS_MOVE)
        else:
            pass_made = False

        defend_moves_analysed = {}
        #see if can capture surrounding block...
        blocks_with_2_liberties_list = []
        for block2 in cboard.iterate_neighbour_blocks(cboard.blocks[pos]):
            if block2.color==other_side[cboard.side]:
                liberties2 = cboard.list_block_liberties(block2)
                if len(liberties2)==1:
                    move = liberties2[0]
                    if self.make_move(move):
                        if config.debug_tactics:
                            dprintnl(depth, "try capturing surrounding block", other_side[cboard.side], self.move_as_string(move))
                        status, attack_move, defend_move = self.block_tactic_status_recursive(pos, depth+1)
                        self.undo_move()
                        defend_moves_analysed[move] = True
                        if status in (TACTICALLY_LIVE, TACTICALLY_CRITICAL):
                            can_defend = move
                            if config.debug_tactics:
                                dprintnl(depth, "defend by capturing succeeded", other_side[cboard.side], self.move_as_string(move))
                            break
                elif len(liberties)==2 and len(liberties)==2:
                    pos2 = block2.get_origin()
                    blocks_with_2_liberties_list.append((pos2, liberties2))

        
        if can_defend==PASS_MOVE: #can't capture stone in atari
            capture_move = self.capture_either(blocks_with_2_liberties_list)
            if capture_move!=PASS_MOVE:
                if config.debug_tactics:
                    dprintnl(depth, "defend by capturing either one of surrouning block with move", self.move_as_string(capture_move))
                can_defend = capture_move

        if can_defend==PASS_MOVE: #can't capture, see if we can extend
            for move in liberties:
                if move in defend_moves_analysed:
                    continue
                if self.make_move(move):
                    if config.debug_tactics:
                        dprintnl(depth, "defend", other_side[cboard.side], self.move_as_string(move))
                    status, attack_move, defend_move = self.block_tactic_status_recursive(pos, depth+1)
                    self.undo_move()
                    if config.debug_tactics:
                        dprintnl(depth, cboard.side, "undo")
                    if status in (TACTICALLY_LIVE, TACTICALLY_CRITICAL):
                        if config.debug_tactics:
                            dprintnl(depth, "defend succeeds")
                        can_defend = move
                        break

        if pass_made:
            self.undo_move()

        if config.debug_tactics:
            dprintnl(depth, "can_attack:", self.move_as_string(can_attack))
            dprintnl(depth, "can_defend:", self.move_as_string(can_defend))
        if can_defend!=PASS_MOVE:
            if config.debug_tactics:
                dprintnl(depth, TACTICALLY_CRITICAL)
            return TACTICALLY_CRITICAL, can_attack, can_defend
        else:
            if config.debug_tactics:
                dprintnl(depth, TACTICALLY_DEAD)
            return TACTICALLY_DEAD, can_attack, can_defend


    def select_random_no_eye_fill_move(self, remove_opponent_dead=False, pass_allowed=True):
        """return randomly selected move from all legal moves but don't fill our own eyes
           not that this doesn't make difference between true 1 space eye and 1 space false eye
        """
        territory_moves_forbidden = pass_allowed
        base_score = self.current_board.score_position()
        if config.debug_flag:
            dprintnl("?", base_score)
        #if abs(base_score)==self.size**2:
        #    import pdb; pdb.set_trace()
        has_unknown_status_block = self.current_board.has_block_status(WHITE+BLACK+EMPTY, UNCONDITIONAL_UNKNOWN)
        has_opponent_dead_block = self.current_board.has_block_status(other_side[self.current_board.side], UNCONDITIONAL_DEAD)
##        #has unsettled blocks
##        if has_unknown_status_block:
##            pass_allowed = False
##        #dead removal has been requested and there are dead opponent stones
##        if remove_opponent_dead and has_opponent_dead_block:
##            territory_moves_forbidden = False
##            pass_allowed = False

##        if territory_moves_forbidden:
##            forbidden_moves = self.current_board.territory_as_dict()
##        else:
##            forbidden_moves = {}
        #self.select_scored_move handles these, not idiotbot code...
        forbidden_moves = self.current_board.territory_as_dict()


        all_moves = []
        eye_moves = []
        capture_or_defence_moves = []
        board = self.current_board
        for move in board.iterate_goban():
            if move in forbidden_moves:
                continue
            if self.legal_move(move):
                for pos in board.iterate_neighbour(move):
                    if board.goban[pos]!=board.side:
                        all_moves.append(move)
                        break
                else:
                    eye_moves.append(move)
                for pos in board.iterate_neighbour(move):
                    if board.goban[pos]!=EMPTY and board.liberties(pos)==1:
                        capture_or_defence_moves.append(move)
                        break
        if capture_or_defence_moves:
            return random.choice(capture_or_defence_moves)
        if all_moves:
            return random.choice(all_moves)
        return self.select_scored_move(remove_opponent_dead, pass_allowed)
        

    def init_fast_select_random_no_eye_fill_move(self):
        cboard = self.current_board
        self.available_moves = {}
        self.available_moves[WHITE] = cboard.goban.keys()
        self.available_moves[BLACK] = cboard.goban.keys()
        self.atari_moves = []
        
    def full_init_fast_select_random_no_eye_fill_move(self):
        cboard = self.current_board
        self.available_moves = {}
        self.available_moves[WHITE] = []
        self.available_moves[BLACK] = []
        for pos in cboard.iterate_goban():
            if cboard.goban[pos]==EMPTY:
                self.available_moves[WHITE].append(pos)
                self.available_moves[BLACK].append(pos)
        self.atari_moves = []
        for block in cboard.iterate_blocks(BLACK+WHITE):
            liberties = cboard.list_block_liberties(block)
            if len(liberties)==1:
                self.atari_moves.append(liberties[0])

    def get_fast_random_status_labels(self):
        d = {}
        for move in self.available_moves[WHITE]:
            d[move] = "W"
        for move in self.available_moves[BLACK]:
            s = d.get(move, "")
            d[move] = s + "B"
        for move in self.atari_moves:
            s = d.get(move, "")
            d[move] = s + "X"
        return d

    def show_fast_random_status(self):
        d = self.get_fast_random_status_labels()
        return self.current_board.as_sgf_with_labels(d)

    def update_fast_random_status(self):
        cboard = self.current_board

        new_moves = self.last_captures()
        for move in new_moves:
            self.available_moves[WHITE].append(move)
            self.available_moves[BLACK].append(move)

        #add new atari moves
        if self.move_history and self.move_history[-1]!=PASS_MOVE:
            move = self.move_history[-1]
            if cboard.liberties_n(move, 2)==1:
                block = cboard.blocks[move]
                move2 = cboard.list_block_liberties(block)[0]
                if move2 not in self.atari_moves:
                    self.atari_moves.append(move2)
            for pos in cboard.iterate_neighbour(move):
                if cboard.goban[pos]!=EMPTY and cboard.liberties_n(pos, 2)==1:
                    block = cboard.blocks[pos]
                    move2 = cboard.list_block_liberties(block)[0]
                    if move2 not in self.atari_moves:
                        self.atari_moves.append(move2)
                

    def fast_select_random_no_eye_fill_move(self, remove_opponent_dead=False, pass_allowed=True):
        """return randomly selected move from all legal moves but don't fill our own eyes
           not that this doesn't make difference between true 1 space eye and 1 space false eye
        """
        cboard = self.current_board
        selected_move = PASS_MOVE
        
        self.update_fast_random_status()

        #prune non-atari moves (capture or connecting might have obsoleted them)
        old_atari_moves = self.atari_moves
        self.atari_moves = []
        for move in old_atari_moves:
            for pos in cboard.iterate_neighbour(move):
                if cboard.goban[pos]!=EMPTY and cboard.liberties_n(pos, 2)==1:
                    self.atari_moves.append(move)
                    break
            
        for move in self.atari_moves:
            if self.legal_move(move):
                selected_move = move

        if selected_move!=PASS_MOVE:
            self.atari_moves.remove(selected_move)
        move_list = self.available_moves[cboard.side]
        while selected_move==PASS_MOVE and move_list:
            side_colors = {}
            #this way we get to select random move and still don't need to remove move from middle of huge list
            i = random.randint(0, len(move_list)-1)
            move = move_list[i]
            move_list[i] = move_list[-1]
            move_list.pop()
            for pos in cboard.iterate_neighbour(move):
                side_colors[cboard.goban[pos]] = True
            if len(side_colors)>1 or side_colors.keys()[0]==EMPTY:
                if self.legal_move(move):
                    selected_move = move
                    break

        if not config.purely_random_no_eye_fill and selected_move!=PASS_MOVE:
            best_score = cboard.quick_score_move(selected_move)
            best_move = selected_move
            for move in cboard.iterate_neighbour(selected_move):
                score = cboard.quick_score_move(move)
                if score > best_score and self.legal_move(move):
                    best_score = score
                    best_move = move
            selected_move = best_move
                
        return selected_move
        
