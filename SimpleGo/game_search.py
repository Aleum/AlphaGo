import string, random, sys, math, copy, time
import config
from const import *
from utils import *
from types import *

from chain import Chain
from board import Board
from pos_cache import *


class SearchAborted(Exception): pass

class SearchNode:
    """Store search results
    """
    def __init__(self):
        self.parent = None
        self.children = []
        self.move = None
        self.counts = []

class PNSearchNode(SearchNode):
    """Store proof number search results
       Also proof number tree is formed from these
    """
    def __init__(self, type):
        SearchNode.__init__(self)
        self.type = type
        self.move = PASS_MOVE
        self.expanded = False
        self.value = None
        self.proof = None
        self.disproof = None
        self.lambda_generator = None

class GameSearch:
    """Search and search related methods
    """
    def __init__(self):
        self.node_count = 0
        #reading shadow for caching local reads
        #reading shadow for each read, key is type of reading and origin of block
        self.reading_shadow = {}
        self.lambda_sorted_moves_history = {}
        #if PASS_MOVE: destroy shadows, other: create shadow for that block origin
        self.current_shadow_origin = PASS_MOVE
        self.shadow_only_neighbour = False
        #what points on goban have shadow
        #value is dictionary of origins of blocks that can be used to retrieve actual shadow from self.reading_shadow
        self.reading_shadow_goban = {}
        self.use_lambda = config.use_lambda
        if self.use_lambda:
            self.shadow_only_neighbour = True
        self.target_blocks = []

    def last_captures(self):
        """List of stones captured in previous move (usually empty)
        """
        captures = []
        if self.undo_history:
            for name, color, pos in self.undo_history[-1]:
                if name=="change_block_color":
                    captures = captures + self.current_board.blocks[pos].stones.keys()
        captures.sort()
        return captures
        
    def search_key(self):
        """Heuristics: make last capture relevant to current position.
            This handles ko and some other similar things.
        """
        captures = self.last_captures()
        return self.current_board.side, self.current_board.key(), tuple(captures)

    def check_shadow_consistency(self):
        """Debugging: use this to check shadow data consistency
        """
        for type_and_origin in self.reading_shadow:
            for pos in self.reading_shadow[type_and_origin]:
                if not self.reading_shadow_goban[pos][type_and_origin]:
                    raise KeyError, (pos, type_and_origin)
        for pos in self.reading_shadow_goban:
            for type_and_origin in self.reading_shadow_goban[pos]:
                if not self.reading_shadow[type_and_origin][pos]:
                    raise KeyError, (pos, type_and_origin)

    def create_shadow(self, shadow_dict):
        """Create shadow from given dictionary.
        """
        reading_type = self.current_reading_type
        if not reading_type:
            return
        origin = self.current_shadow_origin
        shadow_key = reading_type, origin
        if shadow_key not in self.reading_shadow:
            self.reading_shadow[shadow_key] = {}
        shadow = self.reading_shadow[shadow_key]
        for pos in shadow_dict:
            shadow[pos] = True
##            if not self.use_lambda:
##                if pos not in self.reading_shadow_goban:
##                    self.reading_shadow_goban[pos] = {}
##                self.reading_shadow_goban[pos][origin] = origin

    def create_shadow_goban(self, shadow_dict):
        """For all points in shadow_dict add 'pointer' to reading_shadow from reading_shadow_goban.
        """
        reading_type = self.current_reading_type
        origin = self.current_shadow_origin
        for pos in shadow_dict:
            if pos not in self.reading_shadow_goban:
                self.reading_shadow_goban[pos] = {}
            self.reading_shadow_goban[pos][reading_type, origin] = True

    def destroy_this_shadow_only(self, key):
        """Destroy shadow given in key and also remove pointers to it from reading_shadow_goban.
        """
        shadow = self.reading_shadow[key]
        del self.reading_shadow[key]
        for pos2 in shadow:
            if pos2 not in self.reading_shadow_goban:
                continue
            del self.reading_shadow_goban[pos2][key]
            if not self.reading_shadow_goban[pos2]:
                del self.reading_shadow_goban[pos2]
        

    def destroy_shadow(self, shadow_dict):
        """Destroy all shadows in all points listed in shadow_dict.
        """
        for pos in shadow_dict:
            if pos in self.reading_shadow_goban:
                key_list = self.reading_shadow_goban[pos].keys()
                for key in key_list:
                    self.destroy_this_shadow_only(key)

    def update_shadow(self, move):
        """Destroy all shadows that this move effects.
        """
        if self.current_shadow_origin==NO_MOVE or move==PASS_MOVE:
            return
        #collect shadow intersections
        cboard = self.current_board
        shadow_dict = {}
        shadow_dict[move] = True
        for pos in cboard.iterate_neighbour(move):
            block = cboard.blocks[pos]
            if block.color in (WHITE, BLACK) and not self.shadow_only_neighbour:
                shadow_dict.update(block.stones)
                shadow_dict.update(block.neighbour)
            else:
                shadow_dict[pos] = True
        if self.current_shadow_origin==PASS_MOVE:
            self.destroy_shadow(shadow_dict)
        else:
            self.create_shadow(shadow_dict)

    def all_block_tactic_status(self, pos):
        """Normal tactical and heuristical tactical analysis
           Heuristical analysis is done only if normal tactical gives unknown or critical result.
        """
        cboard = self.current_board
        block = cboard.blocks[pos]
        origin = block.get_origin()
        if config.debug_flag and origin!=pos:
            dprintnl(move_as_string(pos), "--origin->", move_as_string(origin))
        result = self.block_tactic_status(origin)
        block.status = result[0]
        if config.use_life_and_death and result[0] in (TACTICALLY_UNKNOWN, TACTICALLY_CRITICAL):
                result_dict = self.heuristical_dead_analysis(origin)
                if origin in result_dict:
                    result = result_dict[origin]
        return result

    def block_tactic_status(self, pos):
        """Capture, life and death tactical status.
           Life&death is only done if capture gives unknown result.
        """
        cboard = self.current_board
        block = cboard.blocks[pos]
        origin = block.get_origin()
##        if origin in self.reading_shadow:
##            try:
##                result0 = self.reading_shadow[origin][origin]
##                try:
##                    a, b, c = result0
##                    if config.use_shadow_cache:
##                        return result0
##                except TypeError:
##                    result0 = None
##            except KeyError:
##                result0 = None
##        else:
##            result0 = None

        status, attack_move, defend_move = self.block_capture_tactic_status(pos)
##        all_reading_shadow = self.reading_shadow.get(origin, {})
        if config.use_life_and_death and status==TACTICALLY_UNKNOWN:
            status, attack_move, defend_move = self.block_life_and_death_status(pos)
        if config.use_playout_reading and status==TACTICALLY_UNKNOWN:
            status, attack_move, defend_move = self.block_playout_status(pos)
##            (status, attack_move, defend_move), ld_shadow = self.block_life_and_death_status(pos)
##            all_reading_shadow.update(ld_shadow)
        #if origin in self.reading_shadow:
        #    del self.reading_shadow[origin]
        result = status, attack_move, defend_move
##        self.reading_shadow[origin] = all_reading_shadow
##        self.reading_shadow[origin][origin] = result
        if config.debug_flag:
            dprintnl("all", move_as_string(pos), result[0], move_list_as_string(result[1:3]))
        self.current_shadow_origin = PASS_MOVE
        return result

    def block_life_and_death_status(self, pos):
        """Do both life and death reading.
           If both life and death result -> critical
           If life result, then see if there is move that invalidates life result -> unknown
           If only dead result -> dead
           Otherwise unknown.
        """
        cboard = self.current_board
        block = cboard.blocks[pos]
        block_color = cboard.blocks[pos].color
        origin = block.get_origin()
##        combined_shadow = {}
        life_result = self.block_life_or_death_status(pos, "life")
##        combined_shadow.update(shadow = self.reading_shadow.get(origin, {}))
        death_result = self.block_life_or_death_status(pos, "death")
        death_shadow_moves = self.last_shadow.keys()
##        combined_shadow.update(shadow = self.reading_shadow.get(origin, {}))
        attack_move = death_result[1]
        defense_move = life_result[1]
        if life_result[0] >= 1.0:
            if death_result[0] >= 1.0:
                status = TACTICALLY_CRITICAL
            else:
                if defense_move==PASS_MOVE:
                    result = life_result
                else:
                    result = self.block_life_or_death_defense(origin, defense_move, [defense_move], "life")
                if result[0] >= 1.0:
                    status = TACTICALLY_LIVE
                else:
                    status = TACTICALLY_UNKNOWN
                    attack_move = result[1]
        else:
            if death_result[0] >= 1.0:
                status = TACTICALLY_DEAD
                result = self.block_life_or_death_defense(origin, attack_move, death_shadow_moves)
                if result[0] < 1.0:
                    defense_move = result[1]
                    status = TACTICALLY_CRITICAL
            else:
                status = TACTICALLY_UNKNOWN
        result = status, attack_move, defense_move
        if config.debug_flag:
            dprintnl("l&d", move_as_string(pos), result[0], move_list_as_string(result[1:3]))
        return result #, combined_shadow

    def block_life_or_death_status(self, pos, reading_type="death", defense_move=PASS_MOVE):
        """analyse life or death status for block
           reading_type: "death" or "life"
           If enabled, bigger blocks get more reading.
        """
        cboard = self.current_board
        self.life_death_reading_type = reading_type
        self.current_reading_type = reading_type
        if defense_move!=PASS_MOVE:
            self.current_reading_type = self.current_reading_type + " " + move_as_string(defense_move)
        if cboard.assumed_unconditional_alive_list:
            self.current_reading_type = self.current_reading_type + " " + move_list_as_string(cboard.assumed_unconditional_alive_list)
        saved_block_status_dict = cboard.save_block_status()
        block = cboard.blocks[pos]
        block_color = cboard.blocks[pos].color
        origin = block.get_origin()
        if reading_type=="death":
            self.defender_color = block_color
        else:
            self.defender_color = other_side[block_color]
        self.current_shadow_origin_color = block_color
        if config.debug_tactics:
            dprintnl(self.move_as_string(origin), reading_type)
            dprintnl(self.current_board.as_string_with_unconditional_status())
        #setup search for life&death search
        time0 = time.time()
        node_count0 = self.node_count
        self.lambda0 = self.life_death_connection_cut_lambda0
        self.goal_achieved = self.unconditional_status
        self.find_relevant_moves = self.find_relevant_eye_moves
        original_default_nodes = config.lambda_node_limit
        if block.size() < 3 or not config.use_big_block_life_death_increase:
            config.lambda_node_limit = config.lambda_slow_node_limit 
        elif block.size() < 6:
            config.lambda_node_limit = config.lambda_slow_node_limit * 2
        else:
            config.lambda_node_limit = config.lambda_slow_node_limit * 5
        original_slow_limit = config.lambda_node_limit
        self.lambda_search_cache = {}
        self.lambda_shadow = None
        self.next_lambda_recursion = 0
        result = self.lambda_search(origin)
        if config.debug_tactics:
            self.print_pn_statistics()
        config.lambda_node_limit = original_default_nodes
        cboard.restore_block_status(saved_block_status_dict)
        #if origin in self.reading_shadow:
        #    del self.reading_shadow[origin]
        if config.debug_flag:
            if result[0] >= 1.0 and reading_type=="death":
                dprintnl("!"*60)
            if defense_move!=PASS_MOVE:
                defense_string = "defense " + move_as_string(defense_move)
            else:
                defense_string = ""
            if self.node_count-node_count0==0:
                dprintsp("(")
            dprintnl(reading_type, move_as_string(pos), result[0], move_list_as_string(result[1:3]), self.node_count-node_count0, original_slow_limit, defense_string, "%.3fs" % (time.time() - time0,))
        return result

    def block_life_or_death_defense(self, pos, attack_move, death_shadow_moves, reading_type="death"):
        """Try to find move that spoils earlier life/death result.
        """
        cboard = self.current_board
        block = cboard.blocks[pos]
        block_color = cboard.blocks[pos].color
        origin = block.get_origin()
        result = [1.0, attack_move]
        move_list = self.lambda_sort_move_candidates(death_shadow_moves, [], attack_move)
        if reading_type=="death":
            defender_color = block_color
        else:
            defender_color = other_side[block_color]
        if defender_color==other_side[cboard.side]:
            pass_made = True
            self.make_move(PASS_MOVE)
        else:
            pass_made = False
        defense_move = PASS_MOVE
        for move in move_list:
            if self.make_move(move):
                if config.debug_tactics:
                    dprintnl(reading_type + " try defence:", self.move_as_string(move))
##                backup_shadow = self.reading_shadow[origin]
                result = self.block_life_or_death_status(pos, reading_type, defense_move=move)
##                self.reading_shadow[origin] = backup_shadow
                self.undo_move()
                if result[0]<1.0:
                    if config.debug_tactics:
                        dprintnl("found defence:", self.move_as_string(move))
                    defense_move = move
                    break
        if pass_made:
            self.undo_move()
        return result[0], defense_move

    def block_connection_status(self, pos1, pos2):
        """analyse connection status for block1 and block2
        """
        cboard = self.current_board
        reading_type = "connection"
        self.current_reading_type = reading_type + move_list_as_string((pos1, pos2))
        saved_block_status_dict = cboard.save_block_status()
        block = cboard.blocks[pos1]
        block_color = cboard.blocks[pos1].color
        self.defender_color = other_side[block_color]
        self.current_shadow_origin_color = block_color
        if config.debug_tactics:
            dprintnl(move_list_as_string((pos1, pos2)), reading_type)
            dprintnl(self.current_board)
        #setup search for life&death search
        time0 = time.time()
        node_count0 = self.node_count
        self.lambda0 = self.life_death_connection_cut_lambda0
        self.goal_achieved = self.connection_status
        self.find_relevant_moves = self.find_connection_moves
        original_default_nodes = config.lambda_node_limit
        config.lambda_node_limit = config.lambda_connection_node_limit
        original_connection_limit = config.lambda_node_limit
        self.lambda_search_cache = {}
        self.lambda_shadow = None
        self.next_lambda_recursion = 0
        self.connection_pos2 = pos2
        result = self.lambda_search(pos1)
        if config.debug_tactics:
            self.print_pn_statistics()
        if result[0]>=1.0:
            connect_move = result[1]
            moves = self.lambda_sort_move_candidates(self.last_shadow.keys(), [], connect_move)
            if block_color==cboard.side:
                pass_made = True
                self.make_move(PASS_MOVE)
            else:
                pass_made = False
            for cut_move in moves:
                if self.make_move(cut_move):
                    if config.debug_tactics:
                        dprintnl("try cut:", self.move_as_string(cut_move))
                    self.current_reading_type = "cut " + move_list_as_string((pos1, pos2, cut_move))
                    result = self.lambda_search(pos1)
                    self.undo_move()
                    if result[0]<1.0:
                        break
            if pass_made:
                self.undo_move()
            if result[0]>=1.0:
                result = TACTICALLY_LIVE, connect_move, PASS_MOVE
            else:
                result = TACTICALLY_CRITICAL, connect_move, cut_move
        else:
            result = TACTICALLY_UNKNOWN, result[1], PASS_MOVE
        
        config.lambda_node_limit = original_default_nodes
        cboard.restore_block_status(saved_block_status_dict)
        #if origin in self.reading_shadow:
        #    del self.reading_shadow[origin]
        if config.debug_flag:
            if self.node_count-node_count0==0:
                dprintsp("(")
            dprintnl(reading_type, move_list_as_string((pos1, pos2)), result[0], move_list_as_string(result[1:3]), self.node_count-node_count0, original_connection_limit, "%.3fs" % (time.time() - time0,))
        return result

    def block_cut_status(self, origin_blocks, cutting_points):
        """analyse cutting status for origin_blocks using cutting_points
           seems to be too inefficient to be useful :-(
           will just use more limited static miai analysis for now
        """
        cboard = self.current_board
        reading_type = "cut"
        str_args = move_list_as_string(origin_blocks) + " : " + move_list_as_string(cutting_points)
        base_current_reading_type = reading_type + str_args
        saved_block_status_dict = cboard.save_block_status()
        pos1 = origin_blocks[0]
        block = cboard.blocks[pos1]
        block_color = cboard.blocks[pos1].color
        self.defender_color = other_side[block_color]
        self.current_shadow_origin_color = block_color
        if config.debug_tactics:
            dprintnl(str_args, reading_type)
            dprintnl(self.current_board)
        #setup search for life&death search
        time0 = time.time()
        node_count0 = self.node_count
        self.lambda0 = self.life_death_connection_cut_lambda0
        self.origin_blocks = origin_blocks
        self.goal_achieved = self.cut_status
        self.cutting_points = cutting_points
        self.find_relevant_moves = self.find_cut_moves
        original_default_nodes = config.lambda_node_limit
        config.lambda_node_limit = config.lambda_connection_node_limit
        original_connection_limit = config.lambda_node_limit
        self.lambda_search_cache = {}
        self.lambda_shadow = None
        self.next_lambda_recursion = 0
        result = [0.0, PASS_MOVE]
        for connect_move in cutting_points:
            if block_color==cboard.side:
                pass_made = True
                self.make_move(PASS_MOVE)
            else:
                pass_made = False
            if self.make_move(connect_move):
                if config.debug_tactics:
                    dprintnl("try connect:", self.move_as_string(connect_move))
                self.current_reading_type = base_current_reading_type + " : " + move_as_string(connect_move)
                result = self.lambda_search(pos1)
                self.undo_move()
                if config.debug_tactics:
                    self.print_pn_statistics()
                if result[0]<1.0:
                    break
            if pass_made:
                self.undo_move()
        if result[0]>=1.0:
            result = TACTICALLY_LIVE, result[1], PASS_MOVE
        else:
            result = TACTICALLY_UNKNOWN, result[1], PASS_MOVE
        
        config.lambda_node_limit = original_default_nodes
        cboard.restore_block_status(saved_block_status_dict)
        #if origin in self.reading_shadow:
        #    del self.reading_shadow[origin]
        if config.debug_flag:
            if self.node_count-node_count0==0:
                dprintsp("(")
            dprintnl(reading_type, str_args, result[0], move_list_as_string(result[1:3]), self.node_count-node_count0, original_connection_limit, "%.3fs" % (time.time() - time0,))
        return result

    def count_chain_liberties(self, chain):
        """How many liberties this chain has total?
        """
        cboard = self.current_board
        liberties_dict = {}
        for block in chain.blocks.values():
            for liberty in cboard.list_block_liberties(block):
                liberties_dict[liberty] = True
        chain.liberty_count = len(liberties_dict)

    def common_dead_neighbour(self, block1, block2):
        """If there a shared dead neighbour?
        """
        cboard = self.current_board
        for block3 in cboard.iterate_neighbour_blocks(block1):
            if block3.color==other_side[block1.color] and block3.status==TACTICALLY_DEAD:
                for block4 in cboard.iterate_neighbour_blocks(block2):
                    if block4==block3:
                        return True
        return False

    def form_chains_tactical(self):
        """blocks are connected if:
           1) 2 or more common liberties
           2) shared dead block
           3) 1 common liberty and tactical search says they are connected
        """
        self.chains = []
        cboard = self.current_board
        for block in cboard.iterate_blocks(BLACK+WHITE):
            if not hasattr(block, "status"):
                block.status = TACTICALLY_UNKNOWN
            block.chain = None
        for color in (BLACK, WHITE):
            block_origin_list = []
            for block in cboard.iterate_blocks(color):
                block_origin_list.append(block.get_origin())

            for origin1 in block_origin_list:
                block1 = cboard.blocks[origin1]
                if block1.chain: continue
                chain = Chain()
                self.chains.append(chain)
                chain.add_block(block1)
                block_added = True
                while block_added:
                    block_added = False
                    for origin2 in block_origin_list:
                        block2 = cboard.blocks[origin2]
                        if block2.chain or block2.color!=block1.color:
                            continue
                        for origin3 in chain.blocks.keys():
                            block3 = cboard.blocks[origin3]
                            common_liberty_count = len(cboard.block_connection_status(origin2, origin3))
                            if common_liberty_count>=2 or self.common_dead_neighbour(block2, block3):
                                chain.add_block(block2)
                                block_added = True
                                break
                            elif common_liberty_count==1:
                                result = self.block_connection_status(origin2, origin3)
                                self.refresh_all_chain_pointers()
                                block1 = cboard.blocks[origin1]
                                block2 = cboard.blocks[origin2]
                                #self.check_chains(require_complete = False)
                                if result[0]==TACTICALLY_LIVE:
                                    chain.add_block(block2)
                                    block_added = True
                                    break

    def chain_propagate_live_status(self, chain):
        """propagate UNCONDITIONALLY_LIVE, TACTICALLY_LIVE status to connected TACTICALLY_UNKNOWN blocks"""
        has_live_block = False
        chain.has_unknown_block = False
        for block in chain.blocks.values():
            if block.status==UNCONDITIONAL_UNKNOWN:
                block.status = TACTICALLY_UNKNOWN
            if block.status in (UNCONDITIONAL_LIVE, TACTICALLY_LIVE):
                has_live_block = True
            elif block.status in (TACTICALLY_UNKNOWN, TACTICALLY_CRITICAL):
                chain.has_unknown_block = True
        if has_live_block:
            for block in chain.blocks.values():
                if block.status == TACTICALLY_UNKNOWN:
                    block.status = TACTICALLY_LIVE
            chain.has_unknown_block = False

    def add_cutting_moves(self, target_origin, surrounding_origins):
        """Go trough all potential cutting points where there are 2 alternative cuts (miai cut)
           Play move in one that is farther from target_origin.
        """
        cboard = self.current_board
        cut_color = cboard.goban[surrounding_origins[0]]
        surround_lib_dict = {}
        for pos in surrounding_origins:
            block = cboard.blocks[pos]
            for lib in cboard.list_block_liberties(block):
                surround_lib_dict[lib] = True
        for pos in surround_lib_dict:
            if cboard.goban[pos]!=EMPTY:
                continue
            for pos2 in cboard.iterate_neighbour(pos):
                if pos not in surround_lib_dict:
                    continue
                if cboard.goban[pos2]!=EMPTY:
                    continue
                x1, y1 = pos
                x2, y2 = pos2
                ok = False
                if x1==x2:
                    if x1==1:
                        ok = cboard.goban[x1+1, y1]==cboard.goban[x2+1, y2]==cut_color
                    elif x1==cboard.size:
                        ok = cboard.goban[x1-1, y1]==cboard.goban[x2-1, y2]==cut_color
                    else:
                        ok = cboard.goban[x1+1, y1]==cboard.goban[x2+1, y2]==cut_color and \
                             cboard.goban[x1-1, y1]==cboard.goban[x2-1, y2]==cut_color
                else:
                    if y1==1:
                        ok = cboard.goban[x1, y1+1]==cboard.goban[x2, y2+1]==cut_color
                    elif y1==cboard.size:
                        ok = cboard.goban[x1, y1-1]==cboard.goban[x2, y2-1]==cut_color
                    else:
                        ok = cboard.goban[x1, y1+1]==cboard.goban[x2, y2+1]==cut_color and \
                             cboard.goban[x1, y1-1]==cboard.goban[x2, y2-1]==cut_color
                if not ok:
                    continue
                if cboard.side!=cut_color:
                    self.make_move(PASS_MOVE)
                if taxi_distance(pos, target_origin) < taxi_distance(pos2, target_origin):
                    move = pos2
                else:
                    move = pos
##                print cboard
##                print move_as_string(move)
                self.make_move(move)
##                print cboard
##                stop()
    
    def refresh_all_chain_pointers(self):
        """Recreate all pointers based on block origins.
           Used when searches spoils chain<->block pointers.
        """
        cboard = self.current_board
        for block in cboard.iterate_blocks(BLACK+WHITE):
            block.chain = None
        for chain in self.chains:
            for origin in chain.blocks:
                block = cboard.blocks[origin]
                chain.blocks[origin] = block
                block.chain = chain

    def chains_as_sgf(self):
        """For debugging: each chain gets unique label letter.
        """
        current_letter = "a"
        label_dict = {}
        for chain in self.chains:
            for block in chain.blocks.values():
                for stone in block.stones:
                    label_dict[stone] = current_letter
            current_letter = chr(ord(current_letter) + 1)
            if current_letter > "z":
                current_letter = "A"
        return self.current_board.as_sgf_with_labels(label_dict)

    def check_chains(self, require_complete=True):
        """Debugging: check that chain<->block pointers are ok.
        """
        cboard = self.current_board
        for chain in self.chains:
            for origin in chain.blocks:
                if cboard.blocks[origin]!=chain.blocks[origin]:
                    raise ValueError, "not pointing to right block"
        for block in cboard.iterate_blocks(BLACK+WHITE):
            if not block.chain:
                if require_complete:
                    raise ValueError, "no chain for block"
                else:
                    continue
            for chain in self.chains:
                if block.get_origin() in chain.blocks:
                    break
            else:
                raise ValueError, "block not found in any chains"

    def heuristical_dead_analysis(self, one_block_pos = PASS_MOVE):
        """
           1) normal analysis
           2) store block status
           3) connection analysis
           4) propagate UNCONDITIONALLY_LIVE, TACTICALLY_LIVE status to connected TACTICALLY_UNKNOWN blocks
           5) count total liberties for all chains (combine liberties to dict and count size)
           6) go trough all chains that are TACTICALLY_UNKNOWN
           7) reset assumed_unconditional_alive_list
           8) search for neighbour opponent chains
           9) add all TACTICALLY_LIVE blocks to assumed_unconditional_alive_list
           10) if opponent chain has 2 more liberties, add all TACTICALLY_UNKNOWN to assumed_unconditional_alive_list
           11) if miai cuts, make move to make cut so that don't need to do it during search
           12) do death analysis for biggest inside block
           13) if there was result, then do search for smaller blocks also
           14) add result to result_list
           15) restore block status
           16) set block status from result_list
        """
        if config.debug_flag:
            dprintnl("")
            dprintnl("START HEURISTICAL ANALYSIS")
        cboard = self.current_board
        if one_block_pos==PASS_MOVE:
            one_block_pos = None
        else:
            one_block_pos = cboard.blocks[one_block_pos].get_origin()
        saved_block_status_dict = cboard.save_block_status()
        self.form_chains_tactical()
        if (config.debug_flag and not one_block_pos) or config.debug_tactics:
            dprintnl(self.chains_as_sgf())
        #self.check_chains()
        for chain in self.chains:
            self.chain_propagate_live_status(chain)
            self.count_chain_liberties(chain)
        result_dict = {}
        for chain in self.chains:
            if one_block_pos:
                if one_block_pos not in chain.blocks:
                    continue
            elif not chain.has_unknown_block:
                continue
            cboard.assumed_unconditional_alive_list = []
            #search for neighbour opponent chains
            neighbour_chains = {}
            for block in chain.blocks.values():
                for block2 in cboard.iterate_neighbour_blocks(block):
                    if block2.color==EMPTY:
                        continue
                    chain2 = block2.chain
                    chain2_origin = chain2.get_origin()
                    neighbour_chains[chain2_origin] = chain2
            # add all TACTICALLY_LIVE blocks to assumed_unconditional_alive_list
            # if opponent chain has 2 more liberties, add all TACTICALLY_UNKNOWN to assumed_unconditional_alive_list
            for chain2 in neighbour_chains.values():
                liberty_count_ok = chain2.liberty_count >= chain.liberty_count + 2
                for block2 in chain2.blocks.values():
                    if block2.status==TACTICALLY_LIVE or \
                       (block2.status==TACTICALLY_UNKNOWN and liberty_count_ok):
                        cboard.assumed_unconditional_alive_list.append(block2.get_origin())
                        cboard.assumed_unconditional_alive_color = block2.color
            blocks_todo = {}
            if one_block_pos:
                blocks_todo[one_block_pos] = True
            else:
                for origin, block in chain.blocks.items():
                    if block.status in (TACTICALLY_UNKNOWN, TACTICALLY_CRITICAL):
                        blocks_todo[origin] = True
            
            while blocks_todo:
                biggest_block = None
                for origin in blocks_todo:
                    block = cboard.blocks[origin]
                    if biggest_block==None or block.size() > biggest_block.size():
                        biggest_block = block
                origin = biggest_block.get_origin()
                del blocks_todo[origin]
                if cboard.assumed_unconditional_alive_list:
                    saved_block_status_dict2 = cboard.save_block_status()
                    #do death analysis for biggest inside block
                    node_count0 = self.node_count
                    current_history_len = len(self.move_history)
                    self.current_shadow_origin = NO_MOVE
                    self.add_cutting_moves(origin, cboard.assumed_unconditional_alive_list)
##                    if move_as_string(origin)=="N1":
##                        print "?!?!?!"
##                        print cboard
##                        stop()
                    if cboard.goban[origin]==EMPTY:
                        result_dict[origin] = TACTICALLY_DEAD, PASS_MOVE, PASS_MOVE
                    else:
                        death_result = self.block_life_or_death_status(origin, "death")
                        death_shadow_moves = self.last_shadow.keys()
                        if death_result[0] >= 1.0:
                            if death_result[0] >= 1.0:
                                dprintnl("?"*60)
                            attack_move = death_result[1]
                            result = self.block_life_or_death_defense(origin, attack_move, death_shadow_moves)
                            if result[0] < 1.0:
                                defend_move = result[1]
                                status = TACTICALLY_CRITICAL
                            else:
                                defend_move = PASS_MOVE
                                status = TACTICALLY_DEAD
                            result_dict[origin] = status, attack_move, defend_move
                            if self.node_count-node_count0==0:
                                dprintsp("(")
                            if config.debug_flag:
                                dprintnl("heuristical death", move_as_string(origin), status, move_as_string(attack_move), move_as_string(defend_move), self.node_count-node_count0)
                        else:
                            if self.node_count-node_count0==0:
                                dprintsp("(")
                            if config.debug_flag:
                                dprintnl("heuristical death", move_as_string(origin), TACTICALLY_UNKNOWN, self.node_count-node_count0)
                    self.current_shadow_origin = NO_MOVE
                    while len(self.move_history) > current_history_len:
                        self.undo_move()
                    cboard.restore_block_status(saved_block_status_dict2)
                    self.refresh_all_chain_pointers()
                else:
                    blocks_todo = {}
        cboard.assumed_unconditional_alive_list = []
        cboard.restore_block_status(saved_block_status_dict)
        self.current_shadow_origin = PASS_MOVE
        return result_dict

    def search_log2tree(self, search_log):
        root_node = node = SearchNode()
        color = self.current_board.side
        for entry, node_count in search_log:
            node.counts.append(node_count)
            if entry==UNDO_MOVE:
                node = node.parent
            else:
                parent = node
                node = SearchNode()
                node.move = entry
                node.color = color
                node.parent = parent
                parent.children.append(node)
            color = other_side[color]
        return root_node

    def sgf_trace(self, move):
        if config.sgf_trace_tactics: # and not self.next_lambda_recursion:
            self.search_log.append((move, self.node_count))

    def tree2sgf(self, tree):
        if tree.move==None:
            s = ["(;GM[1]SZ[%i]RU[Chinese]" % self.size]
            for i in range(len(self.move_history)):
                if i%2:
                    color = ";W"
                else:
                    color = ";B"
                move = self.move_history[i]
                sgf = move_as_sgf(move, self.size)
                if move==PASS_MOVE:
                    s.append("%s[%s]" % (color, sgf))
                else:
                    s.append("%s[%s]CR[%s]" % (color, sgf, sgf))
        else:
            if tree.color==WHITE:
                color = ";W"
            else:
                color = ";B"
            sgf = move_as_sgf(tree.move, self.size)
            if tree.move==PASS_MOVE:
                cr = ""
            else:
                cr = "CR[%s]" % sgf
            s = ["%s[%s]%s" % (color, sgf, cr)]
        #number following moves
        i = 1
        slabel = ["LB"]
        slabel_dict = {}
        scomment = ["C["]
        for node in tree.children:
            if node.move!=PASS_MOVE:
                sgf_move = move_as_sgf(node.move, self.size)
                if sgf_move in slabel_dict:
                    sgf = slabel_dict[sgf_move][:-1] + ","+str(i) + "]"
                else:
                    sgf = "[%s:%s]" % (sgf_move, i)
                slabel_dict[sgf_move] = sgf
            else:
                scomment.append("PASS:%s\n" % i)
            i = i + 1
        scomment.append("Counts: %s\n" % (tuple(tree.counts),))
        if slabel_dict:
            slabel = slabel + slabel_dict.values()
            s.append(string.join(slabel, ""))
        if len(scomment)>1:
            scomment.append("]")
            s.append(string.join(scomment, ""))
        #add child nodes
        if tree.children:
            if len(tree.children)==1:
                s.append(self.tree2sgf(tree.children[0]))
            else:
                for node in tree.children:
                    s.append("(" + self.tree2sgf(node) + ")")
        if tree.move==None:
            s.append(")")
        return string.join(s, "\n")

    def block_capture_tactic_status_sgf(self, pos):
        old_sgf_trace_tactics = config.sgf_trace_tactics
        config.sgf_trace_tactics = True
        self.search_log = []
        result = self.block_capture_tactic_status(pos)
        tree = self.search_log2tree(self.search_log)
        sgf_trace_fp = open("lambda_search.sgf", "w")
        sgf_trace_fp.write(self.tree2sgf(tree))
        sgf_trace_fp.close()
        config.sgf_trace_tactics = old_sgf_trace_tactics
        return result

    def block_capture_tactic_status(self, pos):
        cboard = self.current_board
        block = cboard.blocks[pos]
        block_color = cboard.blocks[pos].color
        origin = block.get_origin()
        liberties = cboard.list_block_liberties(block)
        if 0 and origin in self.reading_shadow:
            if self.use_lambda:
                result0, self.block_extra_result = self.reading_shadow[origin][origin]
            else:
                result0 = self.reading_shadow[origin][origin]
            if config.use_shadow_cache:
                return result0
        else:
            result0 = None
        time0 = time.time()
        self.current_reading_type = "capture"
        node_count0 = self.node_count
        #backup_reading_shadow = copy.deepcopy(self.reading_shadow)
        #backup_reading_shadow_goban = copy.deepcopy(self.reading_shadow_goban)
        self.defender_color = self.current_shadow_origin_color = block_color
        if config.debug_tactics:
            dprintnl(self.move_as_string(origin), "capture")
            dprintnl(self.current_board)
            
        if self.use_lambda:
            self.lambda0 = self.capture_lambda0
            self.goal_achieved = self.captured
            self.find_relevant_moves = self.find_relevant_liberties
            self.block_extra_result = None
            #result = self.lambda_n(origin, 1, 10001)
            self.lambda_shadow = None
            self.next_lambda_recursion = 0
            self.alpha_beta_search_cache = {}
            self.lambda_search_cache = {}
            original_default_nodes = config.lambda_node_limit
            #config.lambda_node_limit = default_nodes
            result = self.lambda_search(origin)
            default_nodes = self.danger_limit
            #default_nodes = self.danger_limit
            current_danger = self.pn_danger_ratio()
            if config.debug_tactics:
                self.print_pn_statistics()
            if result[0]>=1.0:
                attack_move = result[1]
                moves = self.lambda_sort_move_candidates(self.last_shadow.keys(), liberties, attack_move)
                #moves = [] #???????????????????????????????????????????
                if config.sgf_trace_tactics:
                    moves = []
                if block_color==other_side[cboard.side]:
                    pass_made = True
                    self.make_move(PASS_MOVE)
                else:
                    pass_made = False
                for defend_move in moves:
                    if self.make_move(defend_move):
                        is_atari_move = ""
                        block2 = cboard.blocks[defend_move]
                        if cboard.block_liberties(block2)==1:
                            is_atari_move = "atari"
                        else:
                            for block3 in cboard.iterate_neighbour_blocks(block2):
                                if block3.color==cboard.side and cboard.block_liberties(block3)==1:
                                    is_atari_move = "atari"
                        if is_atari_move:
                            config.lambda_node_limit = default_nodes * 2
                        else:
                            config.lambda_node_limit = default_nodes / 2
                        if config.debug_tactics:
                            dprintnl("try defence:", is_atari_move, self.move_as_string(defend_move))
##                        backup_shadow = self.reading_shadow[origin]
                        self.current_reading_type = "capture defense " + move_list_as_string((origin, defend_move))
                        result = self.lambda_search(origin)
##                        self.reading_shadow[origin] = backup_shadow
                        self.undo_move()
                        if result[0]<1.0:
                            break
                if pass_made:
                    self.undo_move()
                if result[0]>=1.0:
                    result = TACTICALLY_DEAD, attack_move, PASS_MOVE
                else:
                    result = TACTICALLY_CRITICAL, attack_move, defend_move
            else:
                config.lambda_node_limit = default_nodes / 5
                #check double threats...
                if block_color==cboard.side:
                    pass_made = True
                    self.make_move(PASS_MOVE)
                else:
                    pass_made = False
                for pos2 in liberties:
                    search_this = False
                    for pos3 in cboard.iterate_neighbour(pos2):
                        block2 = cboard.blocks[pos3]
                        origin2 = block2.get_origin()
                        if origin2!=origin and block2.color==block_color:
                            search_this = True
                            break
                    if search_this and not config.sgf_trace_tactics:
                        if self.make_move(pos2):
                            #in case of ko initial reading from cache might have missed this
                            if cboard.goban[origin]==EMPTY:
                                self.undo_move()
                                result = TACTICALLY_CRITICAL, pos2, pos2
                                break
                                
##                            backup_shadow0 = self.reading_shadow.get(pos2)
                            backup_current_shadow_origin_color = self.current_shadow_origin_color
                            self.defender_color = self.current_shadow_origin_color = cboard.goban[pos2]
                            self.current_reading_type = "capture double check " + self.move_as_string(pos2)
                            result0 = self.lambda_search(pos2)
                            self.defender_color = self.current_shadow_origin_color = backup_current_shadow_origin_color
##                            if backup_shadow0:
##                                self.reading_shadow[pos2] = backup_shadow0
##                            elif pos2 in self.reading_shadow:
##                                del self.reading_shadow[self.current_reading_type, pos2]
                            if result0[0]>=1.0:
                                if config.debug_tactics:
                                    dprintnl("can't do double attack at:", self.move_as_string(pos2))
                                self.undo_move()
                            else:
                                if config.debug_tactics:
                                    dprintnl("try double attack:", self.move_as_string(pos2))
##                                backup_shadow = self.reading_shadow[origin]
                                self.current_reading_type = "capture double attack1 " + self.move_as_string(origin)
                                result1 = self.lambda_search(origin)
                                if result1[0]>=1.0:
                                    if config.debug_tactics:
                                        dprintnl(self.move_as_string(origin), "was now critical, try:", self.move_as_string(origin2))
##                                    backup_shadow2 = self.reading_shadow.get(origin2)
                                    self.current_reading_type = "capture double attack2 " + self.move_as_string(origin2)
                                    result2 = self.lambda_search(origin2)
                                    if result1[0]>=1.0:
                                        if config.debug_tactics:
                                            dprintnl(self.move_as_string(origin2), "was also critical, try find common saving move")
                                        block2 = cboard.blocks[origin]
                                        attack_as_defense_moves_to_analyse = []
                                        for block3 in cboard.iterate_neighbour_blocks(block):
                                            if block3.color == other_side[block2.color]:
                                                liberties3 = cboard.list_block_liberties(block3)
                                                if len(liberties3)==1 and liberties3[0] not in attack_as_defense_moves_to_analyse:
                                                    attack_as_defense_moves_to_analyse.append(liberties3[0])
                                        for move2 in attack_as_defense_moves_to_analyse:
                                            if self.make_move(move2):
                                                if config.debug_tactics:
                                                    dprintnl("group1:", self.move_as_string(origin), "try capture defense:", self.move_as_string(move2))
                                                self.current_reading_type = "capture double defend1 " + self.move_as_string(origin)
                                                result1_2 = self.lambda_search(origin)
                                                if config.debug_tactics:
                                                    dprintnl("group2:", self.move_as_string(origin2), "try capture defense", self.move_as_string(move2))
                                                self.current_reading_type = "capture double defend2 " + self.move_as_string(origin2)
                                                result2_2 = self.lambda_search(origin2)
                                                self.undo_move()
                                                if result1_2[0] < 1.0 and result2_2[0] < 1.0:
                                                    if config.debug_tactics:
                                                        dprintnl(self.move_as_string(move2), "saves both")
                                                    result1 = result1_2
                                                    result2 = result2_2
                                                else:
                                                    if config.debug_tactics:
                                                        dprintnl(self.move_as_string(move2), "doesn't work")
##                                    if backup_shadow2:
##                                        self.reading_shadow[origin2] = backup_shadow2
##                                    elif origin2 in self.reading_shadow:
##                                        del self.reading_shadow[self.current_reading_type, origin2]
##                                self.reading_shadow[origin] = backup_shadow
                                self.undo_move()
                                if result1[0]>=1.0 and result2[0]>=1.0:
                                    result = TACTICALLY_CRITICAL, pos2, pos2
                                    break
                else: #no adjacent double attacks found
                    if 0 and current_danger>=0.3:
                        config.lambda_node_limit = default_nodes
                        moves = self.lambda_sort_move_candidates(self.last_shadow.keys(), liberties, result[1])
                        increase_move = PASS_MOVE
                        best_increase = 0
                        for attack_move in moves[:config.danger_move_limit]:
                            if self.make_move(attack_move):
                                if config.debug_tactics:
                                    dprintnl("try danger increase:", move_as_string(attack_move))
##                                backup_shadow = self.reading_shadow[origin]
                                result = self.lambda_search(origin)
##                                self.reading_shadow[origin] = backup_shadow
                                self.undo_move()
                                danger_difference = self.pn_danger_ratio() - current_danger
                                if config.debug_tactics:
                                    dprintnl("danger_difference:", danger_difference)
                                if danger_difference > best_increase:
                                    best_increase = danger_difference
                                    increase_move = attack_move
                        self.make_move(PASS_MOVE)
                        best_decrease = 0
                        decrease_move = PASS_MOVE
                        for defend_move in moves[:config.danger_move_limit]:
                            if self.make_move(defend_move):
                                if config.debug_tactics:
                                    dprintnl("try danger decrease:", move_as_string(defend_move))
##                                backup_shadow = self.reading_shadow[origin]
                                result = self.lambda_search(origin)
##                                self.reading_shadow[origin] = backup_shadow
                                self.undo_move()
                                danger_difference = current_danger - self.pn_danger_ratio()
                                if config.debug_tactics:
                                    dprintnl("danger_difference:", danger_difference)
                                if danger_difference > best_decrease:
                                    best_decrease = danger_difference
                                    decrease_move = defend_move
                        self.undo_move() #undo PASS
                        self.block_extra_result = current_danger, best_increase, increase_move, best_decrease, decrease_move
                    result = TACTICALLY_UNKNOWN, result[1], PASS_MOVE
                if pass_made:
                    self.undo_move()

            #shadow = copy.deepcopy(self.reading_shadow.get(origin, {}))
            #self.reading_shadow = copy.deepcopy(backup_reading_shadow)
            #self.reading_shadow_goban = copy.deepcopy(backup_reading_shadow_goban)
            config.lambda_node_limit = original_default_nodes
            if config.debug_tactics:
                dprintnl("result:", result)
                dprintnl("extra result:", self.block_extra_result)
##            shadow = self.reading_shadow.get(origin, {})
##            if shadow:
##                self.create_shadow(cboard.blocks[origin].stones)
##                self.create_shadow(cboard.blocks[origin].neighbour)
##                self.reading_shadow[origin][origin] = result, self.block_extra_result
##                self.create_shadow_goban(shadow)
##                if config.debug_tactics:
##                    dprintnl("shadow:", self.reading_shadow[origin])
##                    dprintnl(self.current_board.as_sgf_with_labels(self.reading_shadow[origin]))
##            #self.check_shadow_consistency()
##        else:
##            self.create_shadow(block.stones)
##            self.create_shadow(block.neighbour)
##            result = self.block_tactic_status_recursive(origin)
##            self.reading_shadow[origin][origin] = result
##            if result0 and result0!=result:
##                #import pdb; pdb.set_trace()
##                result = self.block_tactic_status_recursive(origin)
        if config.debug_flag and self.use_lambda:
            if self.block_extra_result:
                er = self.block_extra_result
                extra_result_string = "%.3f %.3f %s %.3f %s" % (er[0], er[1], move_as_string(er[2]), er[3], move_as_string(er[4]))
            else:
                extra_result_string = ""
            if self.node_count-node_count0==0:
                dprintsp("(")
            dprintnl("capture", move_as_string(pos), result[0],
                     move_list_as_string(result[1:3]), extra_result_string,
                     self.node_count-node_count0, default_nodes, "%.3fs" % (time.time() - time0,))
        return result

    def unconditional_status(self, pos, n):
        cboard = self.current_board
        if self.life_death_reading_type=="death":
            dead_result = 1.0
            live_result = 0.0
        else:
            dead_result = 0.0
            live_result = 1.0
        if cboard.goban[pos]!=self.current_shadow_origin_color:
            return dead_result
        #if assumption doesn't hold, then heuristical dead search will return with True
        for pos2 in cboard.assumed_unconditional_alive_list:
            if cboard.goban[pos2]!=cboard.assumed_unconditional_alive_color:
                return live_result
        cboard.analyze_unconditional_status()
        block = cboard.blocks[pos]
        if block.status==UNCONDITIONAL_LIVE:
            return live_result
        if block.status==UNCONDITIONAL_DEAD:
            return dead_result
        return 0.5

    def connection_status(self, pos1, n):
        pos2 = self.connection_pos2
        cboard = self.current_board
        if cboard.goban[pos1]!=self.current_shadow_origin_color:
            return 0.0
        if cboard.goban[pos2]!=self.current_shadow_origin_color:
            return 0.0
        if cboard.blocks[pos1]==cboard.blocks[pos2]:
            return 1.0
        return 0.5

    def cut_status(self, pos, n):
        cboard = self.current_board
        origin_origins = []
        for pos in self.origin_blocks:
            if cboard.goban[pos]!=self.current_shadow_origin_color:
                return 0.0
            origin_origins.append(cboard.blocks[pos].get_origin())
        for pos in self.cutting_points:
            if cboard.goban[pos]==self.current_shadow_origin_color:
               pos_origin = cboard.blocks[pos].get_origin()
               if pos_origin in origin_origins:
                   return 1.0
        return 0.5

    def captured(self, pos, n):
        """
           n==1
       false         false         false
    ------------------------------------------
     . O O B . X . . O O S O X . . O O B . X .
     . O X O O X . . O X O O X . . O X . . X .
     . O X X X X . . O X X X X . . O X X X X .

       false         true
    ----------------------------
     . X X . B O . . X X O S O .
     . X O B B O . . X O S S O .
     . X O O O O . . X O O O O .

           n==2
       false         false         false
    ------------------------------------------
     . . O B . . X . . O S O . X . O O B . X X
     . O X . O X X . O X O O X X . O X . . X X
     . O X X X X . . O X X X X . . O X X X X .

       false         true
    ----------------------------
     . X X . B O . . X X O S O .
     . X O . B O . . X O O S O .
     . X O O O O . . X O O O O .

        """
        #temporary hack
        if self.current_board.goban[pos]!=self.current_shadow_origin_color:
            return 1.0
        if self.current_board.liberties(pos) > n+1:
            return 0.0
        return 0.5

    def lambda_search(self, pos):
        #self.check_shadow_consistency()
        cboard = self.current_board
        self.pn_statistics = {}
        self.current_shadow_origin = pos
        shadow_key = self.current_reading_type, pos
        if shadow_key in self.reading_shadow:
            self.last_shadow = self.reading_shadow[shadow_key]
            result = self.reading_shadow[shadow_key][pos]
            self.current_reading_type = None
            self.current_shadow_origin = NO_MOVE
            return result
        
        self.lambda_search_start_node_count = self.node_count
        self.lambda_search_start_history_len = len(self.move_history)
        self.danger_limit = config.lambda_node_limit
        self.lambda1_done = False
        if config.debug_tactics:
            dprintnl("node_limit:", config.lambda_node_limit)
        try:
            if 1:
                result = self.lambda_n(pos, config.lambda_limit, config.lambda_depth_limit, root_node=True)
            else:
                for n in range(1, config.lambda_limit+1):
                    for d in range(3, n*2+1+1, 2):
                        result = self.lambda_n(pos, n, d, root_node=True)
                        if result[0] != 0.5:
                            break
                    if result[0] != 0.5:
                        break
            shadow = self.reading_shadow.get(shadow_key, {})
            if shadow_key in self.reading_shadow:
                del self.reading_shadow[shadow_key]
        except SearchAborted:
            shadow = self.lambda_shadow
            while len(self.move_history) > self.lambda_search_start_history_len:
                self.undo_move()
            result = -1.0, PASS_MOVE

        if shadow:
            self.create_shadow(cboard.blocks[pos].stones)
            self.create_shadow(cboard.blocks[pos].neighbour)
            self.create_shadow(shadow)
            shadow = self.reading_shadow[shadow_key]
            shadow[pos] = result
            self.create_shadow_goban(shadow)
            if config.debug_tactics:
                dprintnl("shadow:", shadow)
                dprintnl(cboard.as_sgf_with_labels(shadow))
        elif shadow_key in self.reading_shadow:
            del self.reading_shadow[shadow_key]
        #self.check_shadow_consistency()
##        if self.current_reading_type=='cut K16 N15 M15':
##            self.ok_reading_shadow = copy.deepcopy(shadow)
##            stop()
        self.last_shadow = shadow
        self.current_reading_type = None
        self.current_shadow_origin = NO_MOVE
        
        return result

    def find_lambda_search_cache(self, pos, n):
        real_key = self.search_key(), pos, n
        #for i in range(n, -1, -1):
        for i in (n,):
            key = self.search_key(), pos, i
            cache_pos = self.lambda_search_cache.get(key)
            if cache_pos:
                return i, real_key, cache_pos
        return n, real_key, cache_pos

    def lambda_n(self, pos, n, d, root_node=False):
        """based on http://www.t-t.dk/go/cg2000/code20s.html code
           Procedure trying out trees of lambda-order 0,1,2,...,n, all with depth=d.
           Note that the attacker moves first (other side than pos color)
        """
        if config.debug_tactics>1:
            dprintnl(self.current_board)
            dprintnl("lambda_n: start: ", pos, n, d)
        if d%2==0:
            raise ValueError, "lambda must be called with uneven d"
        cboard = self.current_board
        move = PASS_MOVE
        if d<0:
            return 0.5, move
        result = self.goal_achieved(pos, n)
        if result != 0.5:
            return result, move
        result = 0.5

        found_n, key, cache_pos = self.find_lambda_search_cache(pos, n)
        if cache_pos:
            if found_n==n or cache_pos.score==1.0:
                self.lambda_shadow = copy.copy(cache_pos.shadow)
                return cache_pos.score, cache_pos.move

        if self.defender_color==cboard.side:
            pass_made = True
            self.make_move(PASS_MOVE)
        else:
            pass_made = False

        lambda_shadow_backup = self.lambda_shadow
        self.lambda_shadow = {}
        shadow_key = self.current_reading_type, pos

        for i in range(0, n+1):
            if shadow_key in self.reading_shadow:
                #self.destroy_this_shadow_only(pos)
                del self.reading_shadow[shadow_key]
            if i==0:
                result, move = self.lambda0(pos)
                self.lambda_shadow = {}
                if self.current_reading_type[:7]!="capture" and shadow_key in self.reading_shadow:
                    self.lambda_shadow.update(self.reading_shadow[shadow_key])
                if self.current_reading_type[:3]!="cut":
                    for lib in self.find_relevant_liberties(pos, i):
                        self.lambda_shadow[lib] = True
                self.reading_shadow[shadow_key] = self.lambda_shadow
            else:
                node_count0 = self.node_count
                #if not self.next_lambda_recursion:
                #    import pdb; pdb.set_trace()
                if True or i==1:
                    if config.use_pn_search: # and i>1:
                        node = PNSearchNode(PN_OR)
                        node.color = other_side[cboard.side]
                        result, move = self.pn_lambda_search(pos, i, node)
                    else:
                        result, move = self.lambda_alphabeta(pos, i, d, 0.75, 0.75)
                else:
                    result = 0.5
                    for d2 in range(i*2+1, d+1, 2):
                        result, move = self.lambda_alphabeta(pos, i, d2, 0.75, 0.75)
                        print "??", i, d, d2, result, self.move_as_string(move), self.node_count-self.lambda_search_start_node_count
                        if result==-1000000000:
                            result, move = self.lambda_alphabeta(pos, i, d2, 0.75, 0.75)
                            print "???", i, d, d2, result, self.move_as_string(move), self.node_count-self.lambda_search_start_node_count
                            stop()
                            result, move = self.lambda_alphabeta(pos, i, d2, 0.75, 0.75)
                        if result!=0.5:
                            break
                    if result==0.5 and d>1000:
                        result = 0.0
                #if not self.next_lambda_recursion:
                #    import pdb; pdb.set_trace()
                self.lambda_shadow = self.reading_shadow.get(shadow_key, {})
                for lib in self.find_relevant_liberties(pos, i):
                    self.lambda_shadow[lib] = True
                if root_node:
                    if i==1:
                        self.lambda1_done = True
                    if config.debug_tactics:
                        if n<config.lambda_limit:
                            dprintsp(n, d)
                        dprintnl(i, result, self.move_as_string(move), self.node_count-node_count0, len(self.lambda_shadow))
                        dprintnl(self.lambda_shadow)


            if result>=1.0:
                break

        self.lambda_shadow = lambda_shadow_backup

        if pass_made:
            self.undo_move()

        self.lambda_search_cache[key] = LambdaPositionCache(key, result, move, self.lambda_shadow, n)

        return result, move

    def life_death_connection_cut_lambda0(self, pos):
        """Lambda{0} is quite special, so it has its own method
           Note that the attacker moves first (other side than pos color)
        """
        result_move = PASS_MOVE
        cboard = self.current_board
        move_dict = self.find_relevant_moves(pos, 0)
        liberties = cboard.list_block_liberties(cboard.blocks[pos])
        if len(liberties)==1:
            move_dict[liberties[0]] = True
        #move_dict = liberties
        if self.defender_color==cboard.side:
            pass_made = True
            self.make_move(PASS_MOVE)
        else:
            pass_made = False
        result = 0.0
        for move in move_dict:
            if self.make_move(move):
                #self.sgf_trace(move)
                result = self.goal_achieved(pos, 1)
                self.undo_move()
                if result>=1.0:
                    result_move = move
                    break
                else:
                    result = 0.0
                #self.sgf_trace(UNDO_MOVE)
        if pass_made:
            self.undo_move()
        return result, result_move

    def capture_lambda0(self, pos):
        """Lambda{0} is quite special, so it has its own method
           Note that the attacker moves first (other side than pos color)
        """
        move = PASS_MOVE
        cboard = self.current_board
        liberties = cboard.list_block_liberties(cboard.blocks[pos])
        if len(liberties)>1:
            return 0.0, move
        block_color = cboard.blocks[pos].color
        if block_color==cboard.side:
            pass_made = True
            self.make_move(PASS_MOVE)
        else:
            pass_made = False
        result = 0.0
        if self.make_move(liberties[0]):
            #self.sgf_trace(move)
            result = self.goal_achieved(pos, 1)
            if result>=1.0:
                move = liberties[0]
            else:
                result = 0.0
            self.undo_move()
            #self.sgf_trace(UNDO_MOVE)
        if pass_made:
            self.undo_move()
        return result, move

    def find_alpha_beta_search_cache(self, n):
        for i in range(n, 1-1, -1):
            key = i, self.search_key()
            cache_pos = self.alpha_beta_search_cache.get(key)
            if cache_pos:
                return i, key, cache_pos
        return n, key, cache_pos

    def lambda_alphabeta(self, pos, n, d, alpha, beta):
        """Fail-soft alpha-beta"""
        #Game ends if eval()!=0.5, or if the remaining depth<=0
        #if(eval()!=0.5f || d<=0)return eval()*moveColor;
        result = self.goal_achieved(pos, n)
        if result != 0.5 or d <= 0:
            if self.current_board.side==self.defender_color:
                result = -result
            return result, PASS_MOVE
        #if result or d<=0: return result, PASS_MOVE
        #?result = 0.0

        if self.node_count - self.lambda_search_start_node_count > config.lambda_node_limit \
           and self.lambda1_done:
            raise SearchAborted
##        if self.node_count > 30000:
##            while self.move_history:
##                print self.move_as_string(self.move_history[-1])
##                print self.current_board
##                move_count = len(self.move_history)
##                if self.lambda_sorted_moves_history.has_key(move_count-1):
##                    for score, move in self.lambda_sorted_moves_history[move_count-1]:
##                        print -score, self.move_as_string(move),
##                    print
##                self.undo_move()
##            raise Foo

        #see if its cached...
        found_n, key, cache_pos = self.find_alpha_beta_search_cache(n)
        cache_result = None
        if cache_pos:
            self.lambda_shadow.update(cache_pos.shadow)
            cache_move = cache_pos.move
            if found_n==n and d<=cache_pos.depth:
                if cache_pos.flag==EXACTSCORE:
                    #cache_result = cache_pos.score, cache_move
                    return cache_pos.score, cache_move
                elif cache_pos.flag== UPPERBOUND:
                    beta = min(beta, cache_pos.score)
                elif cache_pos.flag==LOWERBOUND :
                    alpha = cache_pos.score
                if alpha >= beta:
                    #cache_result = cache_pos.score, cache_move
                    #save_alpha_beta = alpha, beta
                    return cache_pos.score, cache_move
        else:
            cache_move = PASS_MOVE
        
        best_score = WORST_SCORE
        best_move = PASS_MOVE
        #Counts the number of siblings (successive moves)
        siblings = 0
        savealpha = alpha
        #Lambda-trees are made of lambda-moves
        for move, sub_result in self.next_lambda_move(pos, n, d, cache_move):
            if move==NO_MOVE:
                break
            siblings = siblings + 1
            self.make_move(move)
            #self.sgf_trace(move)
            #if n==2 and self.move_as_string(move)=="B1" and self.current_board.side==WHITE:
            #    import pdb; pdb.set_trace()
            score, result_move = self.lambda_alphabeta(pos, n, d-1, -beta, -alpha)
            score = -score
            #if not self.next_lambda_recursion:
            if config.debug_tactics>1:
                dprintnl("lambda_alphabeta:")
                dprintnl(self.current_board)
                dprintnl(self.next_lambda_recursion, self.node_count, n, d, score, best_score, alpha, beta)
                dprintnl(">", self.move_list_as_string(self.move_history[self.lambda_search_start_history_len:]), self.move_as_string(result_move))
                #if score==-1.0:
                #    stop()
                #    self.lambda_alphabeta(pos, n, d-1, -beta, -alpha)
            self.undo_move()
            #self.sgf_trace(UNDO_MOVE)
            if score>=best_score:
                best_score = score
                best_move = move
                if score>=alpha:
                    alpha = score
                if score>=beta:
                    break #return score, best_move
        #if the node has no siblings
        if siblings==0:
            if self.current_board.side==self.defender_color:
                best_score = -sub_result
            else:
                best_score = sub_result

##            #Lambda-search: 1 is returned if moveColor==-1 (defender to move),
##            #0 is returned if moveColor==1 (attacker to move)
##            if self.current_board.side==self.defender_color:
##                best_score = -1.0
##            else:
##                best_score = 0.0
##            #return moveColor*(1-moveColor)/2; ???

        self.alpha_beta_search_cache[key] = AlphaBetaPositionCache(key, best_score, best_move, d, savealpha, beta, self.lambda_shadow)
##        if cache_result and cache_result!=(best_score, best_move):
##            stop()
        return best_score, best_move

    def lambda_sort_move_candidates(self, moves, liberties, cache_move):
        cboard = self.current_board
        move_values = []
        for move in moves:
            score = cboard.quick_score_move(move)
            if move in liberties:
                score = score + 2
            else:
                for lib in liberties:
                    if cboard.are_adjacent_points(lib, move):
                        score = score + 1
            if move==cache_move:
                score = score + 10
            move_values.append((-score, move))
                    
        move_values.sort()
        self.lambda_sorted_moves_history[len(self.move_history)] = move_values
        moves = []
        for nscore, move in move_values:
            moves.append(move)
        return moves

    def find_relevant_liberties(self, pos, n):
        cboard = self.current_board
        #block = cboard.blocks[pos]
        #liberties = cboard.list_block_liberties(block)
        relevant_blocks = {pos: 0}
        while True:
            new_relevant_blocks = copy.copy(relevant_blocks)
            for origin in relevant_blocks:
                block = cboard.blocks[origin]
                m = relevant_blocks[origin] + 1
                for block2 in cboard.iterate_neighbour_blocks(block):
                    if block2.color==EMPTY:
                        #this should handle false eye cases
                        if block2.size() < n - m + 3:
                            for block3 in cboard.iterate_neighbour_blocks(block2):
                                origin3 = block3.get_origin()
                                if block3.color!=EMPTY and origin3 not in relevant_blocks:
                                    liberties = cboard.list_block_liberties(block3)
                                    for pos2 in block2.stones:
                                        if pos2 not in liberties:
                                            liberties.append(pos2)
                                    for pos2 in cboard.list_block_liberties(block):
                                        if pos2 not in liberties:
                                            liberties.append(pos2)
                                    if len(liberties) < n - m + 3:
                                        new_relevant_blocks[origin3] = m
                    else:
                        origin2 = block2.get_origin()
                        if origin2 not in relevant_blocks:
                            #use for now real liberties instead of quasi_liberties
                            liberties = cboard.list_block_liberties(block2)
                            if len(liberties) < n - m + 3:
                                new_relevant_blocks[origin2] = m
                            
            if relevant_blocks == new_relevant_blocks:
                break
            relevant_blocks = copy.copy(new_relevant_blocks)
            
        liberties_dict = {}
        for origin in relevant_blocks:
            block = cboard.blocks[origin]
            for lib in cboard.list_block_liberties(block):
                liberties_dict[lib] = True
        liberties = liberties_dict.keys()
        return liberties

    def find_relevant_eye_moves(self, pos0, n):
        cboard = self.current_board
        liberties_list = self.find_relevant_liberties(pos0, n)
        cboard.analyze_unconditional_status()
        raw_candidate_dict = {}
        move_candidates_dict = {}
        for pos in liberties_list:
            raw_candidate_dict[pos] = True
            pos2_count = 0
            pos2_empty_count = 0
            for pos2 in cboard.iterate_neighbour(pos):
                pos2_count = pos2_count + 1
                if cboard.goban[pos2]==EMPTY:
                    raw_candidate_dict[pos2] = True
                    pos2_empty_count = pos2_empty_count + 1
                elif cboard.goban[pos2]==self.current_shadow_origin_color:
                    if cboard.blocks[pos0]!=cboard.blocks[pos2]:
                        #solid connection moves always candidates
                        move_candidates_dict[pos] = True
            #'connection' to edge should also be considered if not already connected there
##            if pos2_count==3 and pos2_empty_count==2:
##                stop() # wrong group... should be for surrounding group
##                move_candidates_dict[pos] = True
        eye_dict = {}
        other_color = other_side[self.current_shadow_origin_color]
        for pos in raw_candidate_dict:
            if cboard.analyse_eye_point(pos, other_color):
                eye_dict[pos] = True
        for pos in eye_dict:
            for pos2 in cboard.iterate_neighbour_and_diagonal_neighbour(pos):
                if pos2 in raw_candidate_dict:
                    move_candidates_dict[pos2] = True
##        if move_as_string(pos0)=="B5":
##            print move_list_as_string(liberties_list)
##            print move_list_as_string(raw_candidate_dict.keys())
##            print move_list_as_string(eye_dict.keys())
##            print move_list_as_string(move_candidates_dict.keys())
##            stop()
        return move_candidates_dict

    def find_connection_moves(self, pos1, n):
        pos2 = self.connection_pos2
        common_liberties = self.current_board.block_connection_status(pos1, pos2)
        move_dict = {}
        for lib in common_liberties:
            move_dict[lib] = True
        return move_dict

    def find_cut_moves(self, pos0, n):
        move_dict = {}
        for pos in self.cutting_points:
            move_dict[pos] = True
        return move_dict

    def useful_atari_extension(self, move):
        cboard = self.current_board
        for pos in cboard.iterate_neighbour(move):
            if cboard.liberties(pos)==1:
                if self.make_move(move):
                    liberties = cboard.liberties(move)
                    self.undo_move()
                    if liberties>1:
                        return True
                return False #either move fails or not enough liberties
        return False
        
  
    def next_lambda_move(self, pos, n, d, cache_move):
        """Method for generating lambda-moves"""
        cboard = self.current_board
        liberties = self.find_relevant_moves(pos, n)
        
        moves = self.lambda_shadow.keys()
        #moves = self.list_moves()[1:]
        iterator = self.iterate_moves
        if not moves:
            moves = liberties
        for lib in liberties:
            if lib not in moves:
                moves.append(lib)
        iterator = moves.__iter__

        moves = self.lambda_sort_move_candidates(moves, liberties, cache_move)
        moves.append(PASS_MOVE)

##        if config.sgf_trace_tactics:
##            if not self.sgf_search_tree:
##                node = SearchNode()
##                self.sgf_current_node = self.sgf_search_tree = node
##            else:
##                node = self.sgf_current_node
##            depth = len(self.move_history) - self.lambda_search_start_history_len
##            stop()
##            while len(self.sgf_search_tree) <= depth:
##                self.sgf_search_tree.append([])
##            node.move = PASS_MOVE
##            self.sgf_search_tree[depth].append(node)
##            node.shadow = copy.copy(moves)
##            node.moves = []
##            node.comment = "n=%i\nnodes=%i\n" % (n, self.node_count-self.lambda_search_start_node_count)
                
        
        if config.debug_tactics>1:
            dprintsp( "lambda move candidates:")
            for move in moves:
                dprintsp(self.move_as_string(move))
            dprintnl()

        iterator = moves.__iter__

        best = WORST_SCORE
        worst = BEST_SCORE

        for move in iterator():
            self.pn_resources_available()
            if self.useful_atari_extension(move):
                #Makes atari extension without seeing if its lambda n-1 move
                yield move, 0.5
            elif self.current_board.side==other_side[self.defender_color]:
                #Makes an attacker's move
                if self.make_move(move):
##                    print cboard
##                    print move_as_string(move)
##                    print move_list_as_string(moves)
##                    print cboard.as_sgf_with_labels(self.lambda_shadow)
##                    stop()
                    #Makes a lambda-search of lambda-order n-1 to depth d-2
                    self.next_lambda_recursion = self.next_lambda_recursion + 1
                    result, result_move = self.lambda_n(pos, n-1, d-2)
                    self.next_lambda_recursion = self.next_lambda_recursion - 1
                    self.undo_move()
                    #If the lambda-search returns value<1, this is a lambda-move for the attacker
                    if result>=1:
##                        if config.sgf_trace_tactics:
##                            node.moves.append(move)
                        yield move, result
                    best = max(best, result)
            else:
                #Makes a defender's move
                if self.make_move(move):
                    #Makes a lambda-search of lambda-order n-1 to depth d-1
                    self.next_lambda_recursion = self.next_lambda_recursion + 1
                    result, result_move = self.lambda_n(pos, n-1, d-1)
                    self.next_lambda_recursion = self.next_lambda_recursion - 1
                    self.undo_move()
                    #If the lambda-search returns value<1, this is a lambda-move for the defender
                    if result<1:
##                        if config.sgf_trace_tactics:
##                            node.moves.append(move)
                        yield move, result
                    worst = min(worst, result)

        if self.current_board.side==self.defender_color:
            result = worst
        else:
            result = best
        yield NO_MOVE, result


    ################################################################################
    #proof number as defined by http://web.archive.org/web/20041010123059/http://www.cs.vu.nl/~victor/thesis.html
    def pn_resources_available(self):
        danger = self.pn_danger_ratio()
        if danger<=0.0 or not config.use_danger_increase:
            limit = config.lambda_node_limit
        elif danger<0.3:
            limit = config.lambda_node_limit * 2
        elif danger<0.7:
            limit = config.lambda_node_limit * 4
        else:
            limit = config.lambda_node_limit * 8
        if limit > self.danger_limit: #increase limit
            self.danger_limit = limit
        else: #never decrease limit even if ratio drops
            limit = self.danger_limit
        #if self.node_count - self.lambda_search_start_node_count > 100000:
        #    stop()
        if not self.lambda1_done:
            if self.goal_achieved == self.captured:
                limit = config.capture_lambda1_factor_limit * limit
                if limit < config.min_capture_lambda1_nodes:
                    limit = config.min_capture_lambda1_nodes
            else:
                limit = config.other_lambda1_factor_limit * limit
        if self.node_count - self.lambda_search_start_node_count > limit:
            raise SearchAborted

##        if self.node_count - self.lambda_search_start_node_count > limit \
##           and self.lambda1_done:
##            raise SearchAborted

##        if not hasattr(self, "next_search_print"):
##            self.next_search_print = self.node_count + 1000
##        if self.node_count > self.next_search_print:
##            print self.current_board
##            print self.node_count
##            self.next_search_print = self.node_count + 1000
        return True

    def print_pn_tree_branch(self, depth, node, current_node):
        if node==current_node:
            marker = "*"
        else:
            marker = " "
        self.print_count = self.print_count + 1
        print "    "*depth, marker, move_as_string(node.move), node.type, node.value, node.proof, node.disproof, node.lambda_generator
        for child in node.children:
            self.print_pn_tree_branch(depth+1, child, current_node)

    def print_pn_tree(self, node):
        current_node = node
        while node.parent:
            node = node.parent

        self.print_count = 0
        self.print_pn_tree_branch(0, node, current_node)
        print "tree leaves:", self.print_count

    def pn_evaluate(self, pos, n, node):
        node.value = self.goal_achieved(pos, n)
    
    def pn_lambda_search(self, pos, n, root):
        #if config.debug_tactics:
        #    self.tmp_root_board = copy.deepcopy(self.current_board)
        #    #stop()
        self.pn_evaluate(pos, n, root)
        self.pn_set_proof_and_disproof_numbers(pos, n, root)
        last_most_proving_node = current_node = root
        self.virtual_board_change_history = []
        start_node_count = last_node_count = self.node_count
        while root.proof and root.disproof and self.pn_resources_available():
            most_proving_node, need_more_expansion = self.pn_select_most_proving(current_node)
            if 0 and n==2:
                print
                print "="*60
                print "nodes:", self.node_count - last_node_count, self.node_count - start_node_count
                print len(self.virtual_board_change_history), move_list_as_string(self.virtual_board_change_history)
                self.print_pn_tree(most_proving_node)
                old_root_move = root.move
                root.move = None
                sgf_trace_fp = open("pn_search.sgf", "w")
                sgf_trace_fp.write(self.tree2sgf(root))
                sgf_trace_fp.close()
                root.move = old_root_move
                stop()
            self.virtual_board_change_history = []
            last_node_count = self.node_count
            self.pn_change_board(last_most_proving_node, most_proving_node)
            last_most_proving_node = most_proving_node
            if need_more_expansion:
                self.pn_expand_more(pos, n, most_proving_node)
            else:
                self.pn_expand_node(pos, n, most_proving_node)
            current_node = self.pn_update_ancestors(pos, n, most_proving_node)
        self.pn_change_board(last_most_proving_node, root)
        move = PASS_MOVE
        if root.proof==0:
            root.value = True
            for child in root.children:
                if child.proof==0:
                    move = child.move
                    break
        elif root.disproof==0:
            root.value = False
        else:
            root.value = PN_UNKNOWN
        if 0 and n==2 or hasattr(self, "stop"):
            self.print_pn_tree(root)
            old_root_move = root.move
            root.move = None
            sgf_trace_fp = open("pn_search.sgf", "w")
            sgf_trace_fp.write(self.tree2sgf(root))
            sgf_trace_fp.close()
            root.move = old_root_move
            stop()
        return root.value, move

    def pn_debug_info(self, msg, node):
        dprintnl("proof number search problem:", msg)
        dprintnl(self.current_board)
        dprintnl(self.print_pn_tree(node))

    def print_pn_statistics(self):
        keys = self.pn_statistics.keys()
        keys.sort()
        for key in keys:
            dprintnl(key, self.pn_statistics[key])
        for n in range(1, config.lambda_limit+1):
            key1 = n, False
            key2 = n, True
            if key1 in self.pn_statistics or key2 in self.pn_statistics:
                v1 = self.pn_statistics.get(key1, 0)
                v2 = self.pn_statistics.get(key2, 0)
                v3 = self.pn_statistics.get((n, 0.5), 0)
                dprintnl(n, 100.0 * v2 / (v1+v2), 100.0 * v2 / (v1+v2+v3), 100.0 * v1 / (v1+v2+v3))

    def pn_danger_ratio(self):
        v1 = self.pn_statistics.get((1, False), 0)
        v2 = self.pn_statistics.get((1, True), 0)
        if not v2:
            return 0.0
        return float(v2) / (v1+v2)

    def pn_change_board(self, from_node, to_node):
        path1 = []
        node = from_node
        while node:
            path1.append(node)
            node = node.parent
        path1.reverse()

        path2 = []
        node = to_node
        while node:
            path2.append(node)
            node = node.parent
        path2.reverse()
        
        while path1 and path2 and path1[0]==path2[0]:
            del path1[0]
            del path2[0]

        while path1:
            self.undo_move()
            path1.pop()

        for node in path2:
            self.make_move(node.move)

    def pn_update_ancestors(self, pos, n, node):
        changed = True
        undo_needed = False
        while node and changed:
            old_proof = node.proof
            old_disproof = node.disproof
            self.pn_set_proof_and_disproof_numbers(pos, n, node)
            changed = (old_proof != node.proof) or (old_disproof != node.disproof)
            previous_node = node
            node = node.parent
            if undo_needed:
                self.virtual_board_change_history.append(UNDO_MOVE)
                #self.undo_move()
            else:
                undo_needed = True
        return previous_node

    def pn_select_most_proving(self, node):
        while node.expanded:
            expand_lambda = False
            if node.type==PN_OR:
                i = 0
                while node.children[i].proof != node.proof:
                    i = i+1
                    if i>=len(node.children):
                        expand_lambda = True
                        break
            elif node.type==PN_AND:
                i = 0
                while node.children[i].disproof != node.disproof:
                    i = i+1
                    if i>=len(node.children):
                        expand_lambda = True
                        break
            if expand_lambda:
                return node, True
            node = node.children[i]
            self.virtual_board_change_history.append(node.move)
            #self.make_move(node.move)
        return node, False

    def pn_set_proof_and_disproof_numbers(self, pos, n, node):
        if node.expanded:
            if node.lambda_generator:
                node.proof = node.disproof = 1
                if node.type==PN_AND:
                    for child in node.children:
                        node.proof = node.proof + child.proof
                    for child in node.children:
                        node.disproof = min(node.disproof, child.disproof)
                elif node.type==PN_OR:
                    for child in node.children:
                        node.proof = min(node.proof, child.proof)
                    for child in node.children:
                        node.disproof = node.disproof + child.disproof
            else:
                if node.type==PN_AND:
                    node.proof = 0
                    for child in node.children:
                        node.proof = node.proof + child.proof
                    node.disproof = node.children[0].disproof
                    for child in node.children:
                        node.disproof = min(node.disproof, child.disproof)
                elif node.type==PN_OR:
                    node.proof = node.children[0].proof
                    for child in node.children:
                        node.proof = min(node.proof, child.proof)
                    node.disproof = 0
                    for child in node.children:
                        node.disproof = node.disproof + child.disproof
        else:
            if node.value==False:
                node.proof = PN_INF
                node.disproof = 0
            elif node.value==True:
                node.proof = 0
                node.disproof = PN_INF
            elif node.value==PN_UNKNOWN:
                node.proof = 1
                node.disproof = 1
            self.pn_statistics[n, node.value] = self.pn_statistics.get((n, node.value), 0) + 1

    def pn_eval_child(self, pos, n, child):
        self.make_move(child.move)
        self.pn_evaluate(pos, n, child)
        self.undo_move()
        self.pn_set_proof_and_disproof_numbers(pos, n, child)

    def pn_create_child_node(self, pos, n, node, move):
        if node.type==PN_OR:
            type2 = PN_AND
        else:
            type2 = PN_OR
        child = PNSearchNode(type2)
        child.color = self.current_board.side
        child.move = move
        child.parent = node
        node.children.append(child)
        self.pn_eval_child(pos, n, child)

    def pn_generate_one_child(self, pos, n, node):
        node.children = []
        siblings = 0
        if self.current_board.side==other_side[self.defender_color]:
            d = config.lambda_depth_limit
        else:
            d = config.lambda_depth_limit - 1
        node.lambda_generator = self.next_lambda_move(pos, n, d, NO_MOVE)
        move, sub_result = node.lambda_generator.next()
        if move!=NO_MOVE:
            siblings = siblings + 1
            self.pn_create_child_node(pos, n, node, move)
        else:
            node.lambda_generator = None
        if siblings==0:
            #if self.current_board.side==self.self.defender_color:
            #    result = -sub_result
            #else:
            #    result = sub_result
            result = sub_result
            #result = abs(sub_result)
            #if sub_result!=1.0 and sub_result!=0.0:
            #    stop()
            tested = False
            if self.current_board.side==self.defender_color:
                if sub_result==1.0 or sub_result==1000000000:
                    tested = True
            if self.current_board.side!=self.defender_color:
                if sub_result==0.0 or sub_result==-1000000000:
                    tested = True
            if not tested:
                self.pn_debug_info("untested result: %s %s" % (self.current_board.side==self.defender_color, sub_result), node)
                stop()
            if result>=1.0:
                node.value = True
            elif result<=0.0:
                node.value = False
            else:
                self.pn_debug_info("result not in range: %s %s" % (self.current_board.side==self.defender_color, sub_result), node)
                stop()
                raise ValueError, "how did this happen?"
        else:
            node.expanded = True

    def pn_expand_node(self, pos, n, node):
        self.pn_generate_one_child(pos, n, node)

    def pn_expand_more(self, pos, n, node):
        move, sub_result = node.lambda_generator.next()
        if move!=NO_MOVE:
            self.pn_create_child_node(pos, n, node, move)
        else:
            node.lambda_generator = None
        
