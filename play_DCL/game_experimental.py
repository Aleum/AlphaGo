import string, random, sys, math, copy, time, os
import config
from const import *
from utils import *
from types import *

from chain import Chain
from board import Board
from pos_cache import *

if config.use_c:
    import c_board

class GameExperimental:
    def __init__(self):
        pass

    def find_different_positions(self):
        self.diff_fp = open("diff.log", "w")
        self.different_positions = {}
        self.diff_positions_max_depth = 0
        key = self.plain_key()
        self.different_positions[key] = True
        new_list = [key]
        prev_length = 0
        while new_list:
            print self.diff_positions_max_depth, len(new_list), len(self.different_positions)
            self.diff_positions_max_depth = self.diff_positions_max_depth + 1
            old_list = new_list
            new_list = []
            for key in old_list:
                self.set_board_from_plain_key(key)
                for move in self.iterate_moves():
                    self.make_move(move)
                    key = self.plain_key()
                    if key not in self.different_positions:
                        self.different_positions[key] = True
                        new_list.append(key)
                        self.diff_fp.write(key+"\n")
                    self.undo_move()
        self.diff_fp.close()

    def search(self, max_depth):
        self.search_trace.write("\nstart iteration: %s\n" % max_depth)
        return self.search_recursively(max_depth, 0, WORST_SCORE, BEST_SCORE)

    def search_recursively(self, max_depth, depth, alpha, beta):
        #print depth, self.node_count, alpha, beta, self.move_history[-depth:]
        best_score = WORST_SCORE
        best_variation = []
        if depth>=max_depth or self.has_2_passes():
            #return self.current_board.stone_score(), []
            return self.current_board.chinese_score_position(), []
        self.current_board.score_position()
        forbidden_moves = self.current_board.territory_as_dict()
        move_list = list(self.iterate_moves())
        key = self.current_board.key()
        if key in self.search_cache:
            old_entry = self.search_cache[key]
            if old_entry.move in move_list:
                move_list.remove(old_entry.move)
                move_list.insert(0, old_entry.move)
        old_alpha = alpha
        for move in move_list:
            if move in forbidden_moves:
                continue
            if best_score > beta:
                break
            if best_score==self.size**2:
                break #no need to search inferior moves, can't get better score than whole board win ;-)
            self.make_move(move)
            score, variation = self.search_recursively(max_depth, depth+1, -beta, -alpha)
            score = -score
            self.undo_move()
            if score > best_score:
                best_score = score
                best_variation = [move] + variation
                if score > alpha:
                    alpha = score
                #print ">", depth+1, self.node_count, best_score, alpha, beta, best_variation
                #print ">", self.move_history
        #store to cache
        self.search_trace.write("\n%smoves=%s\nscore=%s\nalpha=%s\nbeta=%s\nvariation=%s\nnodes=%s\n" % (self.current_board, self.move_history, best_score, old_alpha, beta, best_variation, self.node_count))
        exact = old_alpha < score < beta
        search_depth = max_depth - depth
        if key==-417640481:
            import pdb; pdb.set_trace()
        if best_variation:
            best_move = best_variation[0]
            new_entry = PositionCache(key, best_score, best_move, search_depth, exact)
            if key in self.search_cache:
                self.search_trace.write("old cache: %s\n" % self.search_cache[key])
                if new_entry > self.search_cache[key]:
                    self.search_cache[key] = new_entry
                    self.search_trace.write("new cache: %s\n" % new_entry)
            else:
                self.search_cache[key] = new_entry
        return best_score, best_variation


    def form_chains(self):
        self.chains = []
        cboard = self.current_board
        for color in (BLACK, WHITE):
            for block in cboard.iterate_blocks(color):
                block.chain = None

            for block1 in cboard.iterate_blocks(color):
                if block1.chain: continue
                chain = Chain()
                self.chains.append(chain)
                chain.add_block(block1)
                block_added = True
                while block_added:
                    block_added = False
                    for block2 in cboard.iterate_blocks(color):
                        if block2.chain: continue
                        for block3 in chain.blocks.values():
                            if len(cboard.block_connection_status(block3.get_origin(), block2.get_origin()))>=2:
                                chain.add_block(block2)
                                block_added = True
                                break

    def score_chain(self, chain):
        cboard = self.current_board
        
        chain_status = UNCONDITIONAL_UNKNOWN

        for block in chain.blocks.values():
            if block.status==UNCONDITIONAL_LIVE:
                chain_status = UNCONDITIONAL_LIVE
                unconditional_value = 1.0
                break
            elif block.status==UNCONDITIONAL_DEAD:
                chain_status = UNCONDITIONAL_DEAD
                unconditional_value = -1.0
                break

        score = 0
        #if is unconditionally decided? well if part of chain is unconditionally alive, it doesn't mean all of it is: we just assume so
        if chain_status in (UNCONDITIONAL_LIVE, UNCONDITIONAL_DEAD):
            for block in chain.blocks.values():
                score = score + unconditional_value * block.size()
        else: #not unconditionally decided
            liberties_dict = {}
            chain_size = 0
            for block in chain.blocks.values():
                chain_size = chain_size + block.size()
                if block.status==TACTICALLY_DEAD:
                    value_ratio = dead_stone_value_ratio
                elif block.status==TACTICALLY_CRITICAL:
                    if block.color==cboard.side:
                        value_ratio = our_critical_stone_value
                    else:
                        value_ratio = other_critical_stone_value
                else:
                    value_ratio = normal_stone_value_ratio
                for liberty in cboard.list_block_liberties(block):
                    liberties_dict[liberty] = min(liberties_dict.get(liberty, 1.0), value_ratio)
            liberty_value = sum(liberties_dict.values())
            liberty_ratio = liberty_value / (chain_size * 2 + 2)
            score = chain_size * liberty_ratio
            
        if chain.get_color()!=cboard.side:
            score = -score
        print "chain:", self.move_as_string(chain.get_origin()), score
        return score

    def generate_eye_score_move(self):
        cboard = self.current_board
        cboard.score_position()
        forbidden_moves = cboard.territory_as_dict()
        move_list = self.list_moves()
        for block in cboard.iterate_blocks(WHITE+BLACK):
            block.status = UNCONDITIONAL_LIVE
        best_move = PASS_MOVE
        best_score = 0
        #if not hasattr(self, "random_flag"):
        #    self.random_flag = False
        #self.random_flag = not self.random_flag
        self.random_flag = len(self.move_history) < 10
        for move in move_list:
            if move in forbidden_moves or move==PASS_MOVE:
                continue
            if self.random_flag:
                score = random.random()
            else:
                score = 1 #always better than pass move
                for block in cboard.iterate_blocks(BLACK+WHITE):
                    origin = block.get_origin()
                    score = score + cboard.eye_score_move(move, origin)
            if score > best_score:
                best_move = move
                best_score = score
        if config.debug_flag:
            dprintnl(best_score, move_as_string(best_move))
        return best_move
    
    def generate_connection_score_move(self):
        global_gain_flag = False
        connection_only = False
        cboard = self.current_board
        cboard.score_position()
        forbidden_moves = cboard.territory_as_dict()
        move_list = self.list_moves()
        pair_list = []
        for color in (WHITE, BLACK):
            origin_list = []
            for block in cboard.iterate_blocks(color):
                origin_list.append(block.get_origin())
            for i in range(0, len(origin_list)-1):
                origin1 = origin_list[i]
                for j in range(i+1, len(origin_list)):
                    origin2 = origin_list[j]
                    score = cboard.connection_score(origin1, origin2)
                    if score < 10.0:
                        pair_list.append((origin1, origin2, score))
        #if not hasattr(self, "random_flag"):
        #    self.random_flag = False
        #self.random_flag = len(self.move_history) < 10 or not self.random_flag
        #self.random_flag = len(self.move_history) < 10
        #self.random_flag = (len(self.move_history) % 4) in (0,1)
        self.random_flag = (len(self.move_history) % 8)==1
        if not self.random_flag:
            gain_dict = {}
            for origin1, origin2, score in pair_list:
                if connection_only and cboard.goban[origin1]!=cboard.side:
                    continue
                best_move = PASS_MOVE
                best_score = 1000.0
                for move in move_list:
                    if global_gain_flag:
                        continue
                    score1 = cboard.connection_score_move(move, origin1)
                    score2 = cboard.connection_score_move(move, origin2)
                    score = score1 + score2
                    if score < best_score:
                        best_score = score
                        best_move = move
                gain_dict[best_move] = gain_dict.get(best_move, 0.0) + best_score
                if config.debug_flag:
                    dprintnl("Initial scores:", move_as_string(origin1), move_as_string(origin2), score, "Best gain with move:", move_as_string(best_move), best_score)
                    
        best_move = PASS_MOVE
        best_score = 0.0
        self.search_dict = {}
        for move in move_list:
            if move in forbidden_moves or move==PASS_MOVE:
                continue
            if self.random_flag:
                score = random.random()
            else:
                score = 0.0
                if global_gain_flag:
                    for origin1, origin2, score0 in pair_list:
                        if cboard.goban[origin1]!=cboard.side:
                            continue
                        score1 = cboard.connection_score_move(move, origin1)
                        score2 = cboard.connection_score_move(move, origin2)
                        score_gain = score0 - (score1 + score2)
                        if score_gain > 0:
                            score = score + score_gain
                else:
                    score = gain_dict.get(move, 0.0)
                if config.debug_flag:
                    dprintnl("total score gain for move", move_as_string(move), score)
                self.search_dict[move] = score, str(score)
                score = score + 1.0 #always better than pass move
            if score > best_score:
                best_move = move
                best_score = score
        if config.debug_flag:
            dprintnl(best_score, move_as_string(best_move))
        return best_move
    
    def generate_local_move(self, origin, position_statistics = {}, use_random = True, return_score = False, return_all_moves = False):
        if config.debug_flag:
            dprintnl("Local move:", move_as_string(origin))
        cboard = self.current_board
        block = cboard.blocks[origin]
        origin = block.get_origin()
        self.current_shadow_origin_color = block.color
        other_color = other_side[block.color]
        liberty_count = cboard.block_liberties(block)
        #liberty moves
        liberty_moves = self.find_relevant_liberties(origin, min(config.liberty_range-1, liberty_count-1))
        liberty_scores = {}
        best_liberty_score = -10.0
        best_liberty_move = PASS_MOVE
        for move in liberty_moves:
            score = cboard.quick_score_move(move)
            if move in block.neighbour:
                new_liberty_count = liberty_count - 1
                for pos in cboard.iterate_neighbour(move):
                    if cboard.goban[pos]==EMPTY and pos not in block.neighbour:
                        new_liberty_count = new_liberty_count + 1
                if new_liberty_count > liberty_count:
                    if liberty_count==1 and score > 0.0:
                        score = score * 8
                    elif liberty_count==2 and score > 0.0:
                        score = score * 4
                    elif liberty_count==3 and score > 0.0:
                        score = score * 2
            for pos in cboard.iterate_neighbour(move): #capture block bonus
                if cboard.goban[pos]==other_side[block.color] and cboard.liberties_n(pos, 2)==1:
                    score = score + 1.0
            if move in block.neighbour:
                score = score * 1.3
            if score > best_liberty_score:
                best_liberty_score = score
                best_liberty_move = move
            liberty_scores[move] = score
        if config.debug_flag:
            dprintnl("Liberty:", move_as_string(best_liberty_move), best_liberty_score)
            dprintnl(cboard.as_sgf_with_labels(liberty_scores))

        #eye moves
        #eye_moves = self.find_relevant_eye_moves(origin, min(1, liberty_count-1))
        tmp, tmp_dict = cboard.list_block_liberties_all_distances(block, config.eye_range)
        eye_moves = []
        for pos in tmp_dict:
            if cboard.goban[pos]==EMPTY:
                eye_moves.append(pos)
        eye_scores = {}
        best_eye_score = -10.0
        best_eye_move = PASS_MOVE
        for move in eye_moves:
            score = cboard.eye_score_move(move, origin) / 100.0
            if score >= 1.0 and move not in liberty_scores:
                score = score + 0.8
            if score > best_eye_score:
                best_eye_score = score
                best_eye_move = move
            eye_scores[move] = score
        if config.debug_flag:
            dprintnl("Eyes:", move_as_string(best_eye_move), best_eye_score)
            dprintnl(cboard.as_sgf_with_labels(eye_scores))

        #connection moves and blocks
        lib_list, lib_dict = cboard.list_block_liberties_all_distances(block, config.connection_range)
        connection_moves = []
        other_blocks = {}
        for pos in lib_dict.keys():
            if cboard.goban[pos]==EMPTY:
                connection_moves.append(pos)
            else:
                block2 = cboard.blocks[pos]
                origin2 = block2.get_origin()
                if origin2!=origin:
                    other_blocks[origin2] = True
                    
        #get orignal scores
        connection_eval_count = 0
        origin_list = [origin] + other_blocks.keys()
        pair_list = []
        for i in range(0, len(origin_list)-1):
            origin1 = origin_list[i]
            block1 = cboard.blocks[origin1]
            liberties1 = cboard.list_block_liberties(block1)
            for j in range(i+1, len(origin_list)):
                origin2 = origin_list[j]
                score = cboard.connection_score(origin1, origin2)
                connection_eval_count = connection_eval_count + 1
                if score < 10.0:
                    liberties2 = cboard.list_liberties(origin2)
                    pair_ok = True
                    if not union_list(liberties1, liberties2):
                        lib_dict = list2dict(liberties1)
                        count_trough = 0
                        while True:
                            count_trough = count_trough + 1
                            lib_list = cboard.next_order_block_liberties(block1, lib_dict)
                            if union_list(lib_list, liberties2):
                                break
                        lib_dict = list2dict(liberties1)
                        count_around = 0
                        while count_around <= count_trough:
                            count_around = count_around + 1
                            lib_list = cboard.next_order_block_liberties(None, lib_dict)
                            if not lib_list:
                                count_around = count_trough + 1
                                break
                            if union_list(lib_list, liberties2):
                                break
                        if count_trough < count_around:
                            pair_ok = False
                    if pair_ok:
                        lib_dict1 = list2dict(liberties1)
                        lib_dict2 = list2dict(liberties2)
                        while True:
                            connection_points = union_dict(lib_dict1, lib_dict2)
                            if connection_points:
                                break
                            cboard.next_order_block_liberties(None, lib_dict1)
                            cboard.next_order_block_liberties(None, lib_dict2)
                        connection_dict = list2dict(connection_points)
                        pair_list.append((origin1, origin2, score, connection_dict))
                        if config.debug_flag:
                            dprintnl("connection pair:", move_as_string(origin1), move_as_string(origin2), score, move_list_as_string(connection_points))
                    else:
                        if config.debug_flag:
                            dprintnl("pruned pair", move_as_string(origin1), move_as_string(origin2))
        if config.debug_flag:
            dprintnl("basic connection_eval_count:", connection_eval_count)

        #get connection move scores
        best_connection_score = -10.0
        best_connection_move = PASS_MOVE
        connection_scores = {}
        for move in connection_moves:
            best_score = -10.0
            best_pair = PASS_MOVE, PASS_MOVE
            for origin1, origin2, original_score, connection_dict in pair_list:
                if move not in connection_dict:
                    continue
                score1 = cboard.connection_score_move(move, origin1)
                score2 = cboard.connection_score_move(move, origin2)
                connection_eval_count = connection_eval_count + 2
                score = score1 + score2
                score = original_score - score
                if best_eye_score < 2.0 and best_liberty_score < 2.0:
                    score = score * 3.0
                if score > best_score:
                    best_score = score
                    best_pair = origin1, origin2, original_score, score1, score2
            if best_score > 0.0:
                origin1, origin2, original_score, score1, score2 = best_pair
                for pos in cboard.iterate_neighbour(move):
                    if cboard.goban[pos]!=cboard.side:
                        break
                else:
                    #completely surrounded eye point: most of time useless thing to fill it
                    eye_type = cboard.analyse_eye_point(move, other_side[cboard.side], assume_opponent_alive=True)
                    if eye_type==True:
                        best_score = best_score / 10.0
                if origin not in (origin1, origin2):
                    score = score / 1.3
                if config.debug_flag:
                    dprintnl(move_as_string(move), best_score, move_as_string(origin1), move_as_string(origin2), original_score, score1, score2)
                connection_scores[move] = best_score
                if best_score > best_connection_score:
                    best_connection_score = best_score
                    best_connection_move = move
            
        if config.debug_flag:
            dprintnl("Connection:", move_as_string(best_connection_move), best_connection_score)
            dprintnl("total connection_eval_count:", connection_eval_count)
            dprintnl(cboard.as_sgf_with_labels(connection_scores))

        #combined
        combined_scores = copy.copy(eye_scores)
        for move, score in liberty_scores.items():
            combined_scores[move] = combined_scores.get(move, 0.0) + score
        for move, score in connection_scores.items():
            combined_scores[move] = combined_scores.get(move, 0.0) + score
        best_score = -1000.0
        best_move = PASS_MOVE
        self.search_dict = {}
        this_stat = position_statistics.get(self.search_key(), {})
        sorted_moves = []
        for move, score in combined_scores.items():
##            if move in this_stat:
##                lost, won = this_stat[move][:2]
##                min_max_score = this_stat[move][3]
##                if block.color!=cboard.side:
##                    lost, won = won, lost
##                #score = score + 0.5 * (-lost + won)
##                score = score + 0.5 * min_max_score
            if use_random:
                score = score + random.random()
            sorted_moves.append((score, move))
            self.search_dict[move] = score, str(score)
        sorted_moves.sort()
        while sorted_moves:
            score, move = sorted_moves.pop()
            if self.make_move(move):
                best_score = score
                best_move = move
                #eye amount heuristics
                if 0:
                    eye_count = 0
                    lib_list = cboard.list_liberties(origin)
                    for pos in lib_list:
                        if cboard.analyse_eye_point(pos, other_color, assume_opponent_alive=True):
                            eye_count = eye_count + 1
                    self.search_dict[PASS_MOVE] = 1000 + eye_count, "%i %i" % (len(lib_list), eye_count)
                self.undo_move()
                sorted_moves.append((score, move))
                break
        if config.debug_flag:
            dprintnl("Combined:", move_as_string(best_move), best_score)
            dprintnl(cboard.as_sgf_with_labels(combined_scores))

        sorted_moves.reverse()
        if return_all_moves:
            return sorted_moves

        if return_score:
            return best_move, best_score
        return best_move

    def generate_local_score_move(self):
        cboard = self.current_board
        cboard.score_position()
        forbidden_moves = cboard.territory_as_dict()
        move_list = self.list_moves()

        move_scores = {}
        origin_list = []
        for block in cboard.iterate_blocks(BLACK+WHITE):
            origin_list.append(block.get_origin())
        for origin in origin_list:
            move, score = self.generate_local_move(origin, use_random = False)
            move_scores[move] = move_scores.get(move, 0.0) + score

        best_move = PASS_MOVE
        best_score = 0
        for move in move_list:
            if move in forbidden_moves or move==PASS_MOVE:
                continue
            score = random.random() / 10000.0
            score = score + cboard.quick_score_move(move) / 100.0
            score = score + move_scores.get(move, 0.0)
            if score > best_score:
                best_move = move
                best_score = score
        if config.debug_flag:
            dprintnl(best_score, move_as_string(best_move))
        return best_move
    
    def do_block_playout(self, origin, position_statistics = {}, use_random=False):
        cboard = self.current_board
        origin_color = cboard.goban[origin]
        other_color = other_side[origin_color]
        inital_move_count = len(self.move_history)
        move_list = []
        liberty_count_history = []
        eye_count_history = []
        positions_seen = {}
        #if config.debug_flag:
        #    dprintsp("playout:", move_as_string(origin))
        #play out
        while True:
            old_debug = config.debug_flag
            config.debug_flag = False
            move = self.generate_local_move(origin, position_statistics, use_random)
            move_list.append(move)
            config.debug_flag = old_debug
            #if config.debug_flag:
            #    dprintsp(move_as_string(move))
            positions_seen[self.search_key()] = move
            if move==PASS_MOVE:
                if cboard.side==origin_color:
                    status = 0
                else:
                    status = 1
                break
            result = self.make_move(move)
            live_status = cboard.block_unconditional_status(origin)
            if not result or cboard.goban[origin]==EMPTY or live_status:
                if live_status:
                    status = 1
                else:
                    status = 0
                break

            #eye amount heuristics
            eye_dict = {}
            lib_list = cboard.list_liberties(origin)
            for pos in lib_list:
                if cboard.analyse_eye_point(pos, other_color, assume_opponent_alive=True):
                    for pos2 in cboard.iterate_neighbour(pos):
                        if pos2 in eye_dict:
                            break
                    else:
                        eye_dict[pos] = True
            liberty_count_history.append(len(lib_list))
            eye_count_history.append(len(eye_dict))
            if config.fast_playout and len(self.move_history) - inital_move_count > config.eye_heuristic_move_limit:
                if liberty_count_history[-1] >= liberty_count_history[-4] >= 4:
                    for i in range(-1, -4, -1):
                        if eye_count_history[i] < 2:
                            break
                    else:
                        if config.debug_flag:
                            dprintnl("Heuristical playout cut!")
                        status = 1
                        break
            
##            if len(move_list)==1 and cboard.liberties_n(origin, 3) > 2:
##                self.make_move(PASS_MOVE)
##                move_list.append(PASS_MOVE)
                

        #update statistics
        for key, move in positions_seen.items():
            stat = position_statistics.get(key, {})
            stat_this_move = stat.get(move, [0, 0])
            stat_this_move[status] = stat_this_move[status] + 1
            stat[move] = stat_this_move
            position_statistics[key] = stat
            
        while len(self.move_history) > inital_move_count:
            self.undo_move()

        if status:
            status = TACTICALLY_LIVE
        else:
            status = TACTICALLY_DEAD
        #if config.debug_flag:
        #    dprintnl(status)

        return status, move_list

    def do_n_playouts(self, pos, position_statistics, no, negate_score = False):
        live_count = 0
        dead_count = 0
        for i in range(config.playout_alpha_beta_games):
            status, move_list = self.do_block_playout(pos, position_statistics, use_random=True)
            if status==TACTICALLY_LIVE:
                live_count = live_count + 1
            else:
                dead_count = dead_count + 1
            if config.debug_flag:
                if 0:
                    initial_move_count = len(self.move_history)
                    for move in move_list:
                        self.make_move(move)
                    fp = open("out/%s_%i.sgf" % (move_as_string(pos), i), "w")
                    fp.write(str(self))
                    fp.close()
                    while len(self.move_history) > initial_move_count:
                        self.undo_move()
                dprintnl(move_as_string(pos), i, status, move_list_as_string(move_list))
        score = 2.0 * live_count / no - 1.0
        if negate_score:
            score = -score
        return score

    def do_alpha_beta_block_playout(self, pos, position_statistics, depth, alpha, beta, negate_score):
        if depth <= 0:
            return self.do_n_playouts(pos, position_statistics, config.playout_alpha_beta_games, negate_score), [PASS_MOVE]
        old_debug = config.debug_flag
        config.debug_flag = False
        move_score_list = self.generate_local_move(pos, position_statistics,
                                                   use_random = False, return_all_moves = True)
        config.debug_flag = old_debug
        best_score = WORST_SCORE
        best_move = [PASS_MOVE]
        for tmp_score, move in move_score_list:
            if self.make_move(move):
                if config.debug_flag:
                    dprintnl(move_as_string(pos), depth, move_as_string(move), alpha, beta, ":")
                score, result_moves = self.do_alpha_beta_block_playout(pos, position_statistics,
                                                                       depth-1, -beta, -alpha, not negate_score)
                score = -score
                if config.debug_flag:
                    dprintnl("->", move_as_string(pos), depth, move_as_string(move),
                             score, move_list_as_string(result_moves), alpha, beta)
##                if score < 0:
##                    score = -1
##                elif score > 0:
##                    score = 1
                self.undo_move()
                if score > best_score:
                    best_score = score
                    best_move = [move] + result_moves
                    if score >= alpha:
                        alpha = score
                        if config.debug_flag:
                            dprintnl("new alpha", alpha)
                    if score >= beta:
                        if config.debug_flag:
                            dprintnl("beta cut")
                            dprintnl()
                        break #return score, best_move
                if config.debug_flag:
                    dprintnl()
        if best_score == WORST_SCORE:
            return self.do_n_playouts(pos, position_statistics, config.playout_alpha_beta_games, negate_score), [PASS_MOVE]
        return best_score, best_move

    def alpha_beta_block_playout(self, pos, position_statistics, negate_score):
        result, moves = self.do_alpha_beta_block_playout(pos, position_statistics,
                                                  config.playout_alpha_beta_depth, -1, 1, negate_score)
        if negate_score:
            result = -result
        if result >= 0:
            status = TACTICALLY_LIVE
        else:
            status = TACTICALLY_DEAD
        return status, result, moves

    def monte_carlo_score(self, pos, count):
        cb = self.current_board
        old_debug = config.debug_flag
        config.debug_flag = False
        move_score_list = self.generate_local_move(pos, {},
                                                   use_random = False, return_all_moves = True)
        config.debug_flag = old_debug
        if cb.side==cb.goban[pos]:
            def calc_score(pos=pos, count=count, cb=cb):
                return 2 * c_board.test_block(pos, color2ccolor[cb.side], count) - count
        else:
            def calc_score(pos=pos, count=count, cb=cb):
                return count - 2 * c_board.test_block(pos, color2ccolor[cb.side], count)
        best_score = calc_score()
        best_move = PASS_MOVE
        if config.debug_flag:
            dprintnl(move_as_string(best_move), best_score)
        for local_score, move in move_score_list:
            if self.make_move(move):
                score = calc_score()
                if config.debug_flag:
                    dprintsp(move_as_string(move), score, local_score)
                if score > best_score:
                    if config.debug_flag:
                        dprintnl("new")
                    best_move = move
                    best_score = score
                else:
                    if config.debug_flag:
                        dprintnl()
                self.undo_move()
        if config.debug_flag:
            dprintnl("best:", move_as_string(best_move), best_score)
        return best_score, best_move

    def monte_carlo_status(self, pos):
        score, move = self.monte_carlo_score(pos, config.monte_carlo_games)
        if score > 0:
            status = TACTICALLY_LIVE
        else:
            status = TACTICALLY_DEAD
        return status, [move]

    def block_playout_status_live_or_death(self, pos, reading_type="death", position_statistics = {}):
        cboard = self.current_board
        block = cboard.blocks[pos]
        origin_color = block.color
        self.current_reading_type = "playout " + reading_type
        self.current_shadow_origin = pos
        shadow_key = self.current_reading_type, pos
        if shadow_key in self.reading_shadow:
            self.last_shadow = self.reading_shadow[shadow_key]
            result = self.reading_shadow[shadow_key][pos]
            self.current_reading_type = None
            self.current_shadow_origin = NO_MOVE
            return result
        
        time0 = time.time()
        node_count0 = self.node_count
        saved_block_status_dict = cboard.save_block_status()
        if reading_type=="death":
            pass_needed = cboard.side == origin_color
        else:
            pass_needed = cboard.side != origin_color
        if pass_needed:
            self.make_move(PASS_MOVE)
        if config.monte_carlo_games:
            status, moves = self.monte_carlo_status(pos)
        elif config.playout_alpha_beta:
            status, moves = self.alpha_beta_block_playout(pos, position_statistics)
        else:
            status, moves = self.do_block_playout(pos, position_statistics)
        if pass_needed:
            self.undo_move()
        cboard.restore_block_status(saved_block_status_dict)
        if config.debug_flag:
            dprintnl(self.current_reading_type, move_as_string(pos), status, move_list_as_string(moves), self.node_count-node_count0, "%.3fs" % (time.time() - time0,))
        result = status, moves
        self.create_shadow(cboard.blocks[pos].stones)
        self.create_shadow(cboard.blocks[pos].neighbour)
        shadow = self.reading_shadow[shadow_key]
        shadow[pos] = result
        self.create_shadow_goban(shadow)
        self.current_reading_type = None
        self.current_shadow_origin = NO_MOVE
        return result
        

    def block_playout_status(self, pos, position_statistics = {}):
        #attack_status, attack_move_list = self.block_playout_status_live_or_death(pos, "death", position_statistics)
        #defend_status, defend_move_list = self.block_playout_status_live_or_death(pos, "live", position_statistics)
        attack_status, attack_move_list = self.block_playout_status_live_or_death(pos, "death", {})
        attack_move = attack_move_list[0]
        if attack_status==TACTICALLY_LIVE:
            result = TACTICALLY_LIVE, attack_move, PASS_MOVE
        else:
            defend_status, defend_move_list = self.block_playout_status_live_or_death(pos, "live", {})
            defend_move = defend_move_list[0]
            if defend_status==TACTICALLY_LIVE:
                result = TACTICALLY_CRITICAL, attack_move, defend_move
            else:
                result = TACTICALLY_DEAD, attack_move, defend_move
        if config.debug_flag:
            dprintnl("playout", move_as_string(pos), result[0], move_list_as_string(result[1:3]))
        return result

    def time_usage_ok(self, count):
        time1 = time.time()
        return time1 - self.time0 < config.time_per_move_limit and count < config.games_per_move_limit

    def c_color(self):
        return color2ccolor[self.current_board.side]

    def see_uct_move(self, count, count2):
        #if config.debug_flag:
        #    result = c_board.get_result_table(self.c_color()) 
        #    score = result[0] / float(sum(result))
        #    dprintnl("root %.6f %s" % (score, result))
        if config.debug_flag:
            start_len = len(self.move_history)
            swap = False
            while True:
                result = c_board.get_result_table(self.c_color())
                if not result:
                    break
                if swap:
                    result = result[1], result[0]
                dprintsp(result, result[0] / float(sum(result)))
                swap = not swap
                best_score = -1000
                best_move = PASS_MOVE
                for move in self.list_moves():
                    self.make_move(move)
                    result = c_board.get_result_table(self.c_color())
                    if result:
                        result = result[1], result[0]
                        score = result[0] / float(sum(result))
                        if move==PASS_MOVE:
                            #force cleanup and do not pass unless forced
                            score -= 0.2
                        if score > best_score:
                            best_score = score
                            best_move = move
                        #if len(self.move_history)==2:
                        #    print "?", score, result, move_as_string(move)
                    self.undo_move()
                self.make_move(best_move)
                dprintsp("|", move_as_string(best_move))
                if self.has_2_passes():
                    break
            dprintnl()
            while start_len < len(self.move_history):
                self.undo_move()

        #get best move
        move_results = []
        for move in self.list_moves():
            self.make_move(move)
            result = c_board.get_result_table(self.c_color())
            if result:
                result = result[1], result[0]
                score = result[0] / float(sum(result))
                #if move==PASS_MOVE:
                #    #force cleanup and do not pass unless forced
                #    score -= 0.2
                #if move==PASS_MOVE:
                #    #prefer PASS move among do nothing moves
                #    score += 0.000001
                move_results.append((score, result, move))
            self.undo_move()
        move_results.sort()
        move_results.reverse()
        if config.debug_flag:
            i = 0
            for score, result, move in move_results:
                i += 1
                dprintnl("%i %.6f %s %s" % (i, score, result, move_as_string(move)))
            dprintnl("current c score: %.1f" % (c_board.score_board()))
        self.disp_time_used(count, count2)
        if config.debug_flag:
            c_result = c_board.uct_top_win_ratio_move(self.c_color())
            if c_result:
                win_count, lost_count = c_result[1:]
                score = win_count / float(win_count + lost_count)
                dprintnl("c:", move_as_string(c_result[0]), score, win_count, lost_count)
            dprintnl()
        return move_results

    def change_endgame_settings(self, previous_endgame_state, new_endgame_state, komi, games_count, nodes_count):
        move_results = self.see_uct_move(games_count, nodes_count)
        c_board.clear_result_table()
        if config.debug_flag:
            dprintnl("endgame state:", previous_endgame_state, "->", new_endgame_state, "with komi:", komi)
            dprintnl()
        return move_results

    def select_uct_move(self, remove_opponent_dead=False, pass_allowed=True, pos=None):
        saved_moved_file = "saved_move.dat"
        #if os.path.exists(saved_moved_file):
        #    earlier_moves = eval(open(saved_moved_file).read())
        #    if earlier_moves[:-1]==self.move_history:
        #        move = earlier_moves[-1]
        #        if config.debug_flag:
        #            dprintnl("using stored move:", move_as_string(move))
        #            return move
        self.time0 = time.time()
        white_score, black_score = self.current_board.unconditional_score(WHITE+BLACK)
        if white_score + black_score==self.size**2:
            if config.debug_flag:
                dprintnl("All is unconditionally decided, using old select_scored_move")
            flag = config.use_tactical_reading
            config.use_tactical_reading = False
            move = self.select_scored_move(remove_opponent_dead, pass_allowed)
            config.use_tactical_reading = flag
            return move
        
        next_status_report = 10000
        games_count = 0
        nodes_count = 0
        start_nodes = c_board.get_trymove_counter()
        status_done = False

        #nice endgame related stuff
        our_moves = self.list_moves()
        self.make_move(PASS_MOVE)
        opponent_moves = self.list_moves()
        self.undo_move()
        effective_komi = actual_komi = self.komi
        if self.current_board.side==BLACK:
            bigger_score_direction = 1
        else:
            bigger_score_direction = -1
        endgame_state = "none"
        color_reversed = False
        current_moves = our_moves
        win_limit = config.uct_result_sure
        lost_limit = 1.0 - win_limit

        total_games_estimate = min(config.time_per_move_limit * config.games_per_second_estimate, config.games_per_move_limit)
        komi_total_limit = max(100, total_games_estimate // 30)
        komi_move_limit = max(10, total_games_estimate // 1000)
        if config.debug_flag:
            dprintnl("total_games_estimate:", total_games_estimate, "komi_total_limit:", komi_total_limit, "komi_move_limit:", komi_move_limit)
        while self.time_usage_ok(games_count):
            if pos:
                c_board.uct_capture(pos, self.c_color(), config.uct_count)
            else:
                c_board.uct_game(self.c_color(), config.uct_count)
            status_done = False
            nodes_count = c_board.get_trymove_counter() - start_nodes
            games_count += config.uct_count

            result_enough = False
            result = c_board.get_result_table(self.c_color())
            c_result = c_board.uct_top_win_ratio_move(self.c_color())
            if result and c_result:
                total_count = sum(result)
                move, win_count, lost_count = c_result
                move_total_count = win_count + lost_count
                score = win_count / float(move_total_count)
                if move in current_moves and move_total_count >= komi_move_limit and total_count >= komi_total_limit:
                    result_enough = True
            if config.uct_enable_nice_endgame and result_enough:
                #if config.debug_flag:
                #    dprintnl("endgame_state?:", move_as_string(move), score, win_count, lost_count)
                previous_endgame_state = endgame_state
                if endgame_state=="none":
                    if score >= win_limit:
                        endgame_state = "try more"
                        effective_komi += bigger_score_direction
                        self.set_komi(effective_komi)
                        move_results = self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        status_done = True
                    elif score <= lost_limit:
                        endgame_state = "try less"
                        effective_komi -= bigger_score_direction
                        self.set_komi(effective_komi)
                        move_results = self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        status_done = True
                    #else: do nothing, game has not been resolved to either direction
                elif endgame_state=="try more":
                    if score >= win_limit:
                        endgame_state = "try more"
                        effective_komi += bigger_score_direction
                        self.set_komi(effective_komi)
                        move_results = self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        status_done = True
                    else: #it was too big, we want to keep surely won game ... but previous one was ok
                        endgame_state = "try pass"
                        effective_komi -= bigger_score_direction
                        self.set_komi(effective_komi)
                        self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        self.make_move(PASS_MOVE)
                        color_reversed = True
                        status_done = True
                elif endgame_state=="try less":
                    if score <= lost_limit:
                        endgame_state = "try less"
                        effective_komi -= bigger_score_direction
                        self.set_komi(effective_komi)
                        move_results = self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        status_done = True
                    else: #foudn right one, not anymore surely lost game
                        endgame_state = "try pass"
                        self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        self.make_move(PASS_MOVE)
                        color_reversed = True
                        status_done = True
                elif endgame_state=="try pass":
                    if score <= lost_limit: #pass ok?
                        endgame_state = "pass"
                        self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        move_results =[(score, (win_count, lost_count), PASS_MOVE)]
                        status_done = True
                        break
                    else:
                        endgame_state = "keep this"
                        self.change_endgame_settings(previous_endgame_state, endgame_state, effective_komi, games_count, nodes_count)
                        self.undo_move()
                        color_reversed = False
                        status_done = True

            if not status_done and games_count >= next_status_report:
                move_results_tmp = self.see_uct_move(games_count, nodes_count)
                #don't want to pollute with invalid results ...
                if endgame_state == "none":
                    move_results = move_results_tmp
                elif endgame_state == "keep this" and result_enough:
                    move_results = move_results_tmp
                if next_status_report < 100000:
                    next_status_report *= 10
                else:
                    next_status_report += 100000
                status_done = True
        self.set_komi(actual_komi)
        if color_reversed:
            self.undo_move()
        if not status_done:
            move_results = self.see_uct_move(games_count, nodes_count)
        if move_results:
            score, result, move = move_results[0]
            #if score < 0.01:
            #    move = RESIGN_MOVE
            fp = open(saved_moved_file, "w")
            fp.write(str(self.move_history + [move]))
            fp.close()
            return move
        if config.debug_flag:
            dprintnl("no move, return PASS")
        return PASS_MOVE
        
    def uct_ld_score_moves(self, remove_opponent_dead=False, pass_allowed=True, pos=None):
        #config.debug_output = open("ld_score.log", "a")
        score_dict = {}
        config.time_per_move_limit = 100000000
        config.games_per_move_limit = 10000
        cboard = self.current_board
        if config.debug_flag:
            dprintnl(cboard)
        side0 = cboard.side
        pos_lst = []
        for block in cboard.iterate_blocks(BLACK+WHITE):
            pos = block.get_origin()
            pos_lst.append(pos)
        for pos in pos_lst:
            block_color = cboard.goban[pos]
            score_opponent = 0.0
            score_our = {}
            for color_switch in (False, True):
                if not color_switch:
                    if config.debug_flag:
                        dprintnl("test:", move_as_string(pos), cboard.side)
                else:
                    self.make_move(PASS_MOVE)
                    if config.debug_flag:
                        dprintnl("test opposite:", move_as_string(pos), cboard.side)
                c_board.clear_result_table()
                c_board.set_random_seed(1)
                self.select_uct_move(pos=pos)
                for move in self.list_moves():
                    if config.debug_flag:
                        dprintnl(move_as_string(pos), "move:", move_as_string(move))
                    self.make_move(move)
                    result = c_board.get_result_table(self.c_color())
                    self.undo_move()
                    score = result[1] / float(sum(result))
                    if cboard.side==side0:
                        score_our[move] = score
                    else:
                        score_opponent = max(score, score_opponent)
                if color_switch:
                    self.undo_move()
            if config.debug_flag:
                dprintnl("summary:")
                dprintnl(score_opponent, max(score_our.values()))
            score_our_lst = []
            for m, value in score_our.items():
                score_our_lst.append((value, m))
            score_our_lst.sort()
            score_our_lst = score_our_lst[-10:]
            if config.debug_flag:
                dprintnl(score_our_lst)
            for score, move in score_our_lst:
                if block_color==side0: #defend
                    score_diff = score - (1 - score_opponent)
                else:
                    score_diff = score_opponent - (1 - score)
                if config.debug_flag:
                    dprintnl("score diff:", score_diff, move_as_string(move), score)
                score_diff *= cboard.blocks[pos].size()
                score_dict[move] = score_dict.get(move, 0.0) + score_diff
            if config.debug_flag:
                dprintnl("endof", move_as_string(pos))
                dprintnl()
        move_values = []
        for move in score_dict:
            move_values.append((score_dict[move], move))
        move_values.sort()
        move_values.reverse()
        if config.debug_flag:
            for score, move in move_values:
                dprintnl(score, move_as_string(move))
        #for score, move in move_values[:5]:
        #    print score, move_as_string(move)
        #config.debug_output.flush()
        if move_values:
            return move_values[0][1]
        if config.debug_flag:
            dprintnl("no move, return PASS")
        return PASS_MOVE
