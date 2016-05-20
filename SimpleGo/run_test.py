import time, random, sys
import utils
reload(utils)
import board_analysis
reload(board_analysis)
import board
reload(board)
import game_search
reload(game_search)
import game_experimental
reload(game_experimental)
import game
reload(game)
import simple_go
reload(simple_go)
import load_sgf
reload(load_sgf)
import time_settings
reload(time_settings)
import config
import const
sm = simple_go.string_as_move
from utils import *

class Logger:
    def __init__(self):
        self.fp = open("run_test.out", "w")

    def __getattr__(self, name):
        return getattr(self.fp, name)

    def write(self, s):
        sys.stderr.write(s)
        self.fp.write(s)
        self.fp.flush()
        
def thread_dict_strength(dict):
    sum = 0.0
    for thread in dict.values():
        sum = sum + thread.strength()
    return sum

def compare_thread_dict(dict1, dict2):
    sum1 = thread_dict_strength(dict1)
    sum2 = thread_dict_strength(dict2)
    return cmp(sum1, sum2)

def test_thread(file):
    g = load_sgf.load_file(file)
    g.current_board.calculate_threads()
    block_list = list(g.current_board.iterate_blocks(simple_go.WHITE+simple_go.BLACK))
    block_list.sort(lambda b1,b2:cmp(b1.strength_sum, b2.strength_sum))
    block_list.reverse()
    most_block_strength = 0.0
    for block in block_list:
        orig = simple_go.move_as_string(block.get_origin(), g.size)
        print
        print "="*60
        if block.strength_sum >= most_block_strength:
            print "!!!",
            most_block_strength = block.strength_sum
        print orig, block.strength_sum
        thread_dict_list = map(lambda (k,v): (thread_dict_strength(v),k,v), block.threads.items())
        thread_dict_list.sort()
        thread_dict_list.reverse()
        most_strength = 0.0
        for strength, key, thread_dict in thread_dict_list:
            if strength >= most_strength:
                print "!!",
                most_strength = strength
            pos1 = simple_go.move_as_string(key, g.size)
            print pos1, strength
            thread_list = map(lambda (k,v): (v,k), thread_dict.items())
            thread_list.sort()
            thread_list.reverse()
            most_liberty_strength = 0.0
            for thread, key2 in thread_list:
                pos2 = simple_go.move_as_string(key2, g.size)
                strength = thread.strength()
                if strength >= most_liberty_strength:
                    most_liberty_strength = strength
                    print "!",
                print pos1, pos2, strength
    return g


def test_thread2():
    g = load_sgf.load_file("lib_dist/goseigen0.sgf")
    g.undo_move()
    g.undo_move()
    #g.undo_move()
    print g.current_board
    print g.current_board.score_position()
    return g

def test_thread3():
    g = simple_go.Game(19)
    g.make_move((16,16))
    print g.current_board
    g.current_board.score_position()


def test_thread4():
    #g = load_sgf.load_file("lib_dist/basic_positional_judgement.sgf")
    #g = load_sgf.load_file("lib_dist/2_stones.sgf")
    #g = load_sgf.load_file("lib_dist/3stones.sgf")
    #g = load_sgf.load_file("lib_dist/2_1stones.sgf")
    #g = load_sgf.load_file("lib_dist/2_1_cut_stones.sgf")
    #g = load_sgf.load_file("lib_dist/handicap2.sgf")
    #g = load_sgf.load_file("lib_dist/thread_cash_vs_influence.sgf")
    #g = load_sgf.load_file("lib_dist/distance_zero_color_test.sgf")
    g = load_sgf.load_file("lib_dist/distance_zero_color_test2.sgf")
    print g.current_board
    print g.current_board.score_position()
    return g


def test_thread5():
    g = simple_go.Game(19)
    g.make_move((17,16))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move((15,17))
    print g.current_board
    print g.current_board.score_position()
    g.undo_move()
    g.make_move((17,14))
    print g.current_board
    print g.current_board.score_position()
    
def test_thread6():
    g = simple_go.Game(15)
    g.make_move(simple_go.string_as_move("L12",15))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("N12",15))
    print g.current_board
    print g.current_board.score_position()

    g = simple_go.Game(15)
    g.make_move(simple_go.string_as_move("D6",15))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("C4",15))
    print g.current_board
    print g.current_board.score_position()

def test_thread7():
    g = simple_go.Game(15)
    g.make_move(simple_go.string_as_move("N12",15))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("L12",15))
    print g.current_board
    print g.current_board.score_position()

    g = simple_go.Game(15)
    g.make_move(simple_go.string_as_move("N12",15))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("N10",15))
    print g.current_board
    print g.current_board.score_position()

def test_thread8():
    g = simple_go.Game(15)
    g.make_move(simple_go.string_as_move("G8",15))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("G9",15))
    g.make_move(simple_go.string_as_move("G11",15))
    g.make_move(simple_go.string_as_move("G10",15))
    print g.current_board
    print g.current_board.score_position()

    g = simple_go.Game(15)
    g.make_move(simple_go.string_as_move("G8",15))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("G9",15))
    g.make_move(simple_go.string_as_move("H9",15))
    g.make_move(simple_go.string_as_move("G10",15))
    print g.current_board
    print g.current_board.score_position()


def test_thread9():
    g = simple_go.Game(19)
    g.make_move(simple_go.string_as_move("J10", 19))
    g.make_move(simple_go.string_as_move("K11", 19))
    g.make_move(simple_go.string_as_move("L10", 19))
    g.make_move(simple_go.string_as_move("K9", 19))
    print g.current_board
    print g.current_board.score_position()
    move = g.generate_move()
    g.make_move(move)
    fp = open("tmp.sgf", "w")
    fp.write(str(g))
    fp.close()
    return g

def test_search_2_1_liberty():
    g = load_sgf.load_file("lib_dist/2_1_tactics.sgf")
    depth = 1
    while 1:
        g.node_count = 0
        t0 = time.time()
        score, variation = g.search_2_1_liberty(depth)
        t1 = time.time()
        print depth, g.node_count, t1-t0, score, variation
        depth = depth + 1


def test_search(size):
    g = simple_go.Game(size)
    depth = 1
    while depth<=20:
        g.node_count = 0
        t0 = time.time()
        score, variation = g.search(depth)
        t1 = time.time()
        print depth, g.node_count, t1-t0, score, variation
        depth = depth + 1

def test_oxygen():
    #g = simple_go.Game(3)
    #g.make_move((2,2))
    #g = simple_go.Game(9)
    #g.make_move((5,5))
    #g.make_move((1,1))
    g = load_sgf.load_file("lib_dist/oxygen.sgf")
    d = g.current_board.oxygen_influence()
    for k in d:
        if d[k] > 0.1:
            print simple_go.move_as_string(k, g.size), d[k]
    return d
    

def test_different_positions(size):
    g = simple_go.Game(size)
    g.find_different_positions()
    print "%ix%i %i %i" % (size, size, g.diff_positions_max_depth, len(g.different_positions))
    return g

def test_ko():
    g = simple_go.Game(5)
    g.make_move((1,2)); print g.current_board; print g.current_board.ko_flag
    g.make_move((2,2)); print g.current_board; print g.current_board.ko_flag
    g.make_move((2,1)); print g.current_board; print g.current_board.ko_flag
    g.make_move((1,3)); print g.current_board; print g.current_board.ko_flag
    g.make_move((3,2)); print g.current_board; print g.current_board.ko_flag
    g.make_move((3,3)); print g.current_board; print g.current_board.ko_flag
    g.make_move((2,3)); print g.current_board; print g.current_board.ko_flag
    print "-"*60
    g.undo_move()
    g.make_move((4,2)); print g.current_board; print g.current_board.ko_flag
    g.make_move((2,4)); print g.current_board; print g.current_board.ko_flag
    g.make_move((2,3)); print g.current_board; print g.current_board.ko_flag
    

def test_move_history_symmetry():
    g = simple_go.Game(4)
    g.make_move((2,1))
    print g.symmetry_canonical_game_history()
    return g

def test_block_status():
    g = load_sgf.load_file("lib_dist/2_1_tactics.sgf")
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #('tactically critical', (2, 2), (4, 3))
    #node_count 14
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 114
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 18
    #lambda with shadow and special generator for n==1:
    #1 1.0 B2 18 15
    #(1.0, (2, 2)): node_count 18
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 1.0 B2 12 10
    #(1.0, (2, 2)), node_count 12

    print "="*60

    g.make_move((2,2))
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #('tactically dead', (3, 1), (-1, -1))
    #node_count 3
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 2
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 2
    #lambda with shadow and special generator for n==1:
    #(1.0, (-1, -1)): node_count 2
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #(1.0, (-1, -1)), node_count 2

    print "="*60

    g.undo_move()
    g.make_move(simple_go.PASS_MOVE)
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #('tactically critical', (2, 2), (4, 3))
    #node_count 16
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 115
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 19
    #lambda with shadow and special generator for n==1:
    #1 1.0 B2 18 15
    #(1.0, (2, 2)): node_count 19
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    ##1 1.0 B2 12 10
    #(1.0, (2, 2)), node_count 13
    
    print "="*60

    g.undo_move()
    g.make_move(simple_go.PASS_MOVE)
    g.make_move((1,2))
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 6
    #lambda without shadow and no special generator for n==1:
    #0.0: node_count 194
    #lambda without shadow and special generator for n==1:
    #1 0.0 B2 26 15
    #2 0.0 C1 8336 18
    #...

    
    #lambda with shadow and special generator for n==1:
    #1 0.0 B2 26 15
    #2 1.0 B1 233 15
    #(1.0, (2, 1)): node_count 259
    #fixed bug
    #1 0.0 B2 26 15
    #2 0.0 B2 673 19
    #3 0.0 B2 892657 19
    #above + self.shadow_only_neighbour
    #1 0.0 B2 26 11
    #2 0.0 B2 405 16
    #3 0.0 B2 123246 16
    #... self.node_count: 3094548
    #with cache:
    #1 0.0 B2 26 11
    #2 0.0 B2 279 10
    #3 0.0 B2 2888 10
    #4 1.0 C1 166745 17
    #(1.0, (3, 1)): node_count 169938
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 B2 24 10
    #2 0.0 B1 201 8
    #... self.node_count==316145

    g.make_move((2,1))
    g.make_move((2,2))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 PASS 62 6
    #4 1.0 B4 1027 17
    #(1.0, (2, 4)): node_count 1097
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move

    g.undo_move()
    g.undo_move()
    g.make_move((3, 1))
    g.make_move((2,2))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 PASS 86 12
    #4 1.0 B4 141692 9
    #(1.0, (2, 4)): node_count 141786
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    
    g.make_move((2, 4))
    g.make_move((3,4))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 68 13
    #3 0.0 B1 3622 15
    #4 1.0 D3 65031 9
    #(1.0, (4, 3)): node_count 68721
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move

    g.make_move((4, 3))
    g.make_move((1,4))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status((3,2))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 20 12
    #3 0.0 B1 814 10
    #4 0.0 A5 7053 12
    #5 0.0 B1 3965 12
    #6 0.0 A5 201212 12
    #7 0.0 B1 4012 9
    #8 0.0 B1 11057 9
    #9 0.0 B1 83 9
    #10 0.0 B1 83 9
    #11 0.0 B1 83 9
    #...
    #100 0.0 B1 83 9
    #(0.0, (2, 1)): node_count 235769
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move

    return g

def test_ladder_block_status():
    g = load_sgf.load_file("kgs/ladder_test.sgf")
    node_count0 = g.node_count
    #print g.block_tactic_status((2,3))
    print "node_count", g.node_count-node_count0
    #('tactically critical', (2, 4), (2, 4))
    #node_count 6
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 1
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 1
    #lambda with shadow and special generator for n==1:
    #(1.0, (-1, -1)): node_count 1
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #(1.0, (-1, -1)), node_count 1

    print "="*60

    node_count0 = g.node_count
    #print g.block_tactic_status((6,3))
    print "node_count", g.node_count-node_count0
    #('tactically dead', (6, 4), (-1, -1))
    #node_count 11
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 2
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 2
    #lambda with shadow and special generator for n==1:
    #(1.0, (-1, -1)): node_count 2
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #(1.0, (-1, -1)), node_count 2

    print "="*60

    g.make_move((6,4))
    node_count0 = g.node_count
    print g.block_tactic_status((6,3))
    print "node_count", g.node_count-node_count0
    #('tactically critical', (6, 5), (5, 4))
    #node_count 38
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 586
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 30
    #lambda with shadow and special generator for n==1:
    #1 1.0 F5 30 23
    #(1.0, (6, 5)): node_count 30
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 1.0 F5 18 17
    #(1.0, (6, 5)), node_count 18

    return g

def test_net_block_status():
    #need iterative deepening it seems!
    g = load_sgf.load_file("kgs/net.sgf")
    node_count0 = g.node_count
    print g.block_tactic_status((3,3)), "node_count", g.node_count-node_count0
    #v0.2.3:
    #node_limit: 100000
    #1 0.0 D3 60 12
    #2 1.0 D4 11521 13

    #PN search:
    #node_limit: 100000
    #1 False PASS 106 17
    #2 True D4 6453 13

    #PN search with lazy child generation
    #node_limit: 100000
    #1 False PASS 126 15
    #2 True D4 187 13
    #try defence: D4
    #node_limit: 50000
    #1 False PASS 14 8
    #2 False PASS 502 17
    #('tactically critical', (4, 4), (4, 4)) node_count 50317

    #added lazy change board: pn_change_board
    #node_limit: 100000
    #1 False PASS 82 15
    #2 True D4 173 13
    #try defence: D4
    #node_limit: 50000
    #1 False PASS 14 8
    #2 False PASS 420 17
    #('tactically critical', (4, 4), (4, 4)) node_count 50259

    #use alpha-beta for lambda1 and above for lambda2>=
    #node_limit: 5000
    #1 0.0 D3 60 12
    #2 True D4 92 12
    #try defence: D4
    #node_limit: 2500
    #1 0.0 D3 12 8
    #2 False PASS 336 16
    #('tactically critical', (4, 4), (4, 4)) node_count 2658

    print "="*60

    g = load_sgf.load_file("kgs/net2.sgf")
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("R3", g.size)), "node_count", g.node_count-node_count0
    #node_limit: 100000
    #1 0.0 R4 448 12
    #2 ...failed

    #PN search:
    #1 False PASS 1742 20
    #2 ..failed
    
    #PN search with lazy child generation
    #node_limit: 100000
    #1 False PASS 2042 59
    #2 True Q4 2303 14
    #try defence: Q4
    #node_limit: 50000
    #1 False PASS 14 8
    #('tactically critical', (16, 4), (16, 4)) node_count 54349

    #added lazy change board: pn_change_board
    #node_limit: 100000
    #1 False PASS 818 59
    #2 True Q4 1269 14
    #try defence: Q4
    #node_limit: 50000
    #1 False PASS 14 8
    #2 False PASS 44441 33
    #('tactically critical', (16, 4), (16, 4)) node_count 52090

    #use alpha-beta for lambda1 and above for lambda2>=
    #node_limit: 5000
    #1 0.0 R4 448 12
    #2 True Q4 92 14
    #try defence: Q4
    #node_limit: 2500
    #1 0.0 R4 12 8
    #('tactically critical', (16, 4), (16, 4)) node_count 3044

    return g


def test_ladder_block_status2():
    g = load_sgf.load_file("test_tactics/13x13_game21.sgf")
    while len(g.move_history)>52:
        g.undo_move()

    #config.debug_tactics = True
    node_count0 = g.node_count
    print g.block_tactic_status((6,3))
    print "node_count", g.node_count-node_count0

    print "="*60
    g.undo_move()
    node_count0 = g.node_count
    print g.block_tactic_status((6,3))
    print "node_count", g.node_count-node_count0

    print "="*60
    g.make_move((7,1))
    node_count0 = g.node_count
    print g.block_tactic_status((6,3))
    print "node_count", g.node_count-node_count0


def test_ladder_block_status3():
    g = load_sgf.load_file("kgs/masterdo_crazy_ladder_problem.sgf")
    #config.debug_tactics = True
    node_count0 = g.node_count
    print g.block_tactic_status((12,2))
    print "node_count", g.node_count-node_count0
    #('tactically critical', (13, 2), (12, 3))
    #node_count 1623
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 201658
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 1278
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 1.0 N2 706 263
    #(1.0, (13, 2)), node_count 706

    #PN search with lazy child generation
    #added lazy change board: pn_change_board
    #node_limit: 10000
    #1 True N2 9535 251
    #try defence: N2
    #node_limit: 5000
    #1 False PASS 0 5
    #2 False PASS 0 9
    #result: ('tactically critical', (13, 2), (13, 2)), node_count 14564

    #v0.2.3:
    #1 1.0 N2 5906 10

    #PN lambda cache and lazy (dis)proof numbers for potentially needed moves: only look for them if proof depends on them
    #1 True N2 6119 10

def test_whole_board_ladder():
    g = load_sgf.load_file("kgs/big_ladder.sgf")
    #config.debug_tactics = True
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("R3", g.size))
    print "node_count", g.node_count-node_count0
    #('tactically critical', (17, 5), (17, 5))
    #node_count 113
    #lambda without shadow and no special generator for n==1
    #1.0: node_count 43848
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 252
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 1.0 R5 180 95
    #(1.0, (17, 5)), node_count 180

    print "="*60
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("C17", g.size))
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("R3", g.size))
    print "node_count", g.node_count-node_count0
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 104
    #lambda without shadow and no special generator for n==1:
    #0.0: node_count 53570
    #lambda without shadow and special generator for n==1:
    #0.0: node_count 312
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 Q4 312 84
    #... self.node_count==20413


def test_ladder_block_status4():
    g = load_sgf.load_file("test_tactics/19x19_game41.sgf")
    while len(g.move_history)>201:
        g.undo_move()
    #config.debug_tactics = True
    node_count0 = g.node_count
    print g.block_tactic_status((9,16))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 J17 12 8
    #2 0.0 H17 583 11
    #... self.node_count==14787
    return g


def test_critical_scoring():
    g = load_sgf.load_file("test_tactics/5x5_tactical_game4.sgf")
    while len(g.move_history)>10:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()
    
    g = load_sgf.load_file("test_tactics/13x13_game15.sgf")
    while len(g.move_history)>90:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    g = load_sgf.load_file("test_tactics/13x13_game21.sgf")
    while len(g.move_history)>51:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    g = load_sgf.load_file("kgs/minue622-SimpleBot_tactics.sgf")
    while len(g.move_history)>48:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    g = load_sgf.load_file("test_tactics/19x19_game36.sgf")
    while len(g.move_history)>187:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    return g

    while len(g.move_history)>85:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    g = load_sgf.load_file("kgs/blubb-SimpleBot-tactics-3.sgf")
    while len(g.move_history)>40:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    g = load_sgf.load_file("test_tactics/19x19_game41.sgf")
    while len(g.move_history)>200:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    return g

def improved_tactical_reading():
    g = load_sgf.load_file("kgs/blubb-SimpleBot-tactics-2.sgf")
    while len(g.move_history)>92:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    g = load_sgf.load_file("kgs/masterdo-SimpleBot-tactics-ha2_2.sgf")
    while len(g.move_history)>42:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    g = load_sgf.load_file("kgs/masterdo-SimpleBot_tactics_ha2.sgf")
    while len(g.move_history)>40:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    while len(g.move_history)>36:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    while len(g.move_history)>34:
        g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    while len(g.move_history)>33:
        g.undo_move()

    print g.str_current_position()
    print g.generate_move()
    return g


def test_bug_block_status():
    g = load_sgf.load_file("test_tactics/9x9_game16.sgf")
    while len(g.move_history)>19:
        g.undo_move()
    print g.current_board
    node_count0 = g.node_count
    print g.block_tactic_status((2,3))
    print "node_count", g.node_count-node_count0

def test_bug_block_status2():
    g = load_sgf.load_file("test_tactics_0_1_6/02_handicap_4_or_5/gtpBalancer070.sgf")
    while len(g.move_history)>16+11:
        g.undo_move()
    print g.current_board
    move = g.generate_move()
    g.make_move(move)
    print g.current_board
    print g

def connection_test():
    g = load_sgf.load_file("kgs/simple_connection.sgf")
    print g.current_board
    print g.block_connection_status((2,2), (3,3))
    print g.block_connection_status((3,3), (4,4))
    g.form_chains()
    return g

def test_play_out():
    g = load_sgf.load_file("test_tactics/7x7_game14.sgf")
    #while len(g.move_history)>14:
    while len(g.move_history)>13:
        g.undo_move()
    #print "score now:", g.score_position()
    #score = g.critical_move_playout()
    #print "score:", score
    print g.current_board
    print g.generate_move()
    return g

def test_pass_in_playout():
    g = load_sgf.load_file("play/aloriless_tactics2/game005.sgf")
    while g.move_history[-1]!=(9,1):
        g.undo_move()
    g.undo_move()
    return g.generate_move()

def test_bonus():
    g = load_sgf.load_file("test_tactics/13x13_game26.sgf")
    while len(g.move_history)>31:
        g.undo_move()
    print g.current_board
    return g.generate_move()
    
def test_big_ladder():
    for use_cache in False, True:
        g = load_sgf.load_file("test_tactics/19x19_game30.sgf")
        while len(g.move_history)>126: g.undo_move()
        print g.current_board
        node_count0 = g.node_count
        config.use_shadow_cache = use_cache
        g.generate_move()
        print use_cache, "node_count", g.node_count-node_count0
    return g

def test_global_critical_bonus():
    g = load_sgf.load_file("kgs/tour_2005-10-02_CrazyStone-SimpleBot.sgf")
    while len(g.move_history)>100: g.undo_move()
    print g.str_current_position()
    print g.generate_move()
    
    while len(g.move_history)>50: g.undo_move()
    print g.str_current_position()
    print g.generate_move()
    
    while len(g.move_history)>46: g.undo_move()
    print g.str_current_position()
    print g.generate_move()
    
    g = load_sgf.load_file("kgs/tour_2005-10-02_antbot19-SimpleBot.sgf")
    while len(g.move_history)>324: g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    while len(g.move_history)>232: g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    while len(g.move_history)>150: g.undo_move()
    print g.str_current_position()
    print g.generate_move()

    while len(g.move_history)>94: g.undo_move()
    print g.str_current_position()
    print g.generate_move()
    
    return g
    

def test_speed():
    t0 = time.time()
    g = load_sgf.load_file("test_tactics/19x19_game41.sgf")
    config.use_shadow_cache = False
    while len(g.move_history):
        print g.str_current_position()
        print len(g.move_history), g.node_count
        g.undo_move()
    t1 = time.time()
    print t1-t0
    #342 moves in game
    #56.4261548519s for test
    #19633 nodes
    #348 nodes/s
    #6.1 moves/s

    #no shadow:
    #103.487010956s for test (some other tasks also occssionally)
    #27941 nodes
    #270 nodes/s
    #3.3 moves/s

def test_tactical_game_end():
    g = load_sgf.load_file("kgs/test_tactical_game_end.sgf")
    print g.str_current_position()
    print "dead", g.move_list_as_string(g.final_status_list("dead"))
    g.generate_move()
    g.generate_move(remove_opponent_dead=True)

    print "="*60
    g.undo_move()
    g.undo_move()
    print g.str_current_position()
    print "dead", g.move_list_as_string(g.final_status_list("dead"))
    g.generate_move()
    g.generate_move(remove_opponent_dead=True)

    print "="*60
    g.undo_move()
    print g.str_current_position()
    print "dead", g.move_list_as_string(g.final_status_list("dead"))
    g.generate_move()
    g.generate_move(remove_opponent_dead=True)

    print "="*60
    g.undo_move()
    print g.str_current_position()
    print "dead", g.move_list_as_string(g.final_status_list("dead"))
    g.generate_move()
    g.generate_move(remove_opponent_dead=True)
    
    print "="*60
    g = load_sgf.load_file("kgs/seki.sgf")
    print g.str_current_position()
    print "dead", g.move_list_as_string(g.final_status_list("dead"))
    g.generate_move()
    g.generate_move(remove_opponent_dead=True)

    print "="*60
    g = load_sgf.load_file("kgs/dead_test.sgf")
    print g.str_current_position()
    print "dead", g.move_list_as_string(g.final_status_list("dead"))
    g.generate_move()
    g.generate_move(remove_opponent_dead=True)

def handicap_test():
    g = simple_go.Game(5)
    g.current_board.calculate_distance_to_stones_or_edge()
    return g

def test_3_liberties():
    g = load_sgf.load_file("kgs/test_antonchan-SimpleBot.sgf")
    print "loaded"
    nodes0 = 0
    #print g.str_current_position()
    print "total nodes:", g.node_count-nodes0

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("S2", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 T2 33 10
    #(1.0, (19, 2)): node_count 34
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 S1 21 9
    #(1.0, (18, 1)), node_count 22
    
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("M5", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 M4 33 13
    #(1.0, (12, 4)): node_count 34
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 M4 14 13
    #(1.0, (12, 4)), node_count 15

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("L3", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 M4 300 20
    #(1.0, (12, 4)): node_count 309
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 0.0 PASS 112 15
    #4 1.0 M1 681 14
    #(1.0, (12, 1)), node_count 802

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("G2", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 H1 44 14
    #(1.0, (8, 1)): node_count 45
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 G1 46 13
    #(1.0, (7, 1)), node_count 47

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("B2", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 1.0 C1 176 10
    #(1.0, (3, 1)): node_count 185
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 1.0 C1 153 12
    #(1.0, (3, 1)), node_count 162

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("B7", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 C7 84 15
    #(1.0, (3, 7)): node_count 85
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 B8 45 18
    #(1.0, (2, 8)), node_count 46

    print "="*60
    node_count0 = g.node_count
    #print g.block_tactic_status(simple_go.string_as_move("O5", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 10 5
    #3 0.0 PASS 20 10
    #4 0.0 PASS 182 10
    #5 0.0 PASS 1581 8
    #6 1.0 Q5 29166 11
    #(1.0, (16, 5)): node_count 30960
    #must be error!
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 10 5
    #3 0.0 PASS 22 10
    #4 0.0 PASS 192 13
    #... self.node_count==101516

    print "="*60
    node_count0 = g.node_count
    #print g.block_tactic_status(simple_go.string_as_move("K16", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 0.0 PASS 68 10
    #... self.node_count==307103
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 0.0 PASS 68 8
    #... self.node_count==47769

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("F16", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 G16 168 48
    #... self.node_count==72340  !!!
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 G16 168 48
    #2 1.0 F15 114705 68
    #(1.0, (6, 15)), node_count 114874

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("H18", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 J18 12851 22
    #(1.0, (9, 18)): node_count 12852
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 J18 504 14
    #(1.0, (9, 18)), node_count 505

    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("Q17", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 R17 12 8
    #2 1.0 R17 196 15
    #(1.0, (17, 17)): node_count 209
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 R17 12 8
    #2 1.0 R17 131 17
    #(1.0, (17, 17)), node_count 144
    return g

def test_9x9_ha9():
    g = simple_go.Game(9)
    g.place_free_handicap(9)
    #g.make_move(simple_go.string_as_move("B1", g.size))
    #g.make_move(simple_go.string_as_move("B2", g.size))
    #g.make_move(simple_go.string_as_move("C1", g.size))
    #g.make_move(simple_go.string_as_move("D2", g.size))
    #g.make_move(simple_go.string_as_move("D1", g.size))
    #g.make_move(simple_go.string_as_move("E1", g.size))
    #g.make_move(simple_go.string_as_move("F1", g.size))
    #g.make_move(simple_go.string_as_move("E2", g.size))
    node_count0 = g.node_count

    #import pdb; pdb.set_trace()
    #print g.block_tactic_status(simple_go.string_as_move("B1", g.size))
    #print "node_count", g.node_count-node_count0
    #return

    g = simple_go.Game(9)
    g.place_free_handicap(9)
    g.make_move(simple_go.string_as_move("B2", g.size))
    node_count0 = g.node_count

    #import pdb; pdb.set_trace()
    #print g.block_tactic_status(simple_go.string_as_move("B2", g.size))
    #print "node_count", g.node_count-node_count0
    #return
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 B3 584 13
    #(1.0, (2, 3)): node_count 592
    #+use cache find for lower n for move ordering
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #?
    #(1.0, (2, 3)), node_count 599
    #+sort moves: move_cache, adjacent liberties, total_liberties
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 C2 228 21
    #(1.0, (3, 2)), node_count 236
    #shape move ordering: quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 B1 354 5
    #4 1.0 B1 1185 9
    #(1.0, (2, 1)), node_count 1547

    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("D4", g.size))
    print "="*60
    node_count0 = g.node_count
    #print g.block_tactic_status(simple_go.string_as_move("D4", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 C4 72 22
    #(1.0, (3, 4)): node_count 80
    #+use cache find for lower n for move ordering
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 C4 72 22
    #(1.0, (3, 4)), node_count 80
    #+sort moves: move_cache, adjacent liberties, total_liberties
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 E4 50 22
    #(1.0, (5, 4)), node_count 58
    #shape move ordering: quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 E4 50 22
    #(1.0, (5, 4)), node_count 58
    
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("F8", g.size))
    print "="*60
    node_count0 = g.node_count
    #print g.block_tactic_status(simple_go.string_as_move("F8", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 G8 380 19
    #(1.0, (7, 8)): node_count 388
    #+use cache find for lower n for move ordering
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 G8 380 19
    #node_count 388
    #+sort moves: move_cache, adjacent liberties, total_liberties
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 F7 130 19
    #(1.0, (6, 7)), node_count 138
    #shape move ordering: quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 1.0 F9 259 22
    #(1.0, (6, 9)), node_count 267

    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("J4", g.size))
    print "="*60
    node_count0 = g.node_count
    #print g.block_tactic_status(simple_go.string_as_move("J4", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 H4 1688 20
    #(1.0, (8, 4)): node_count 1688
    #+use cache find for lower n for move ordering
    #1 0.0 PASS 0 0
    #2 1.0 H4 1426 20
    #node_count 1426
    #+sort moves: move_cache, adjacent liberties, total_liberties
    #1 0.0 PASS 0 0
    #2 1.0 H4 98 14
    #(1.0, (8, 4)), node_count 98
    #shape move ordering: quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 H4 155 20
    #(1.0, (8, 4)), node_count 155

    g = simple_go.Game(9)
    g.place_free_handicap(9)
    for move in ("A1", "B1", "C1", "D1", "E1", "B2", "C2", "D2", "E2", "D3", "D4", "E4"):
        g.make_move(simple_go.string_as_move(move, g.size))
        print "="*60
        node_count0 = g.node_count
        print g.block_tactic_status(simple_go.string_as_move(move, g.size))
        print "node_count", g.node_count-node_count0
        g.undo_move()
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #A1:
    #1 1.0 A2 36 16
    #(1.0, (1, 2)): node_count 36
    
    #B1:
    #1 0.0 PASS 0 0
    #2 1.0 B2 1052 10
    #(1.0, (2, 2)): node_count 1052

    #C1:
    #1 0.0 PASS 0 0
    #2 1.0 C2 654 12
    #(1.0, (3, 2)): node_count 654

    #D1:
    #1 0.0 PASS 0 0
    #2 1.0 D2 1071 21
    #(1.0, (4, 2)): node_count 1071

    #E1:
    #1 0.0 PASS 0 0
    #2 1.0 F1 224 23
    #(1.0, (6, 1)): node_count 224

    #B2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 B3 584 13
    #(1.0, (2, 3)): node_count 592

    #C2:
    #1 0.0 PASS 0 0
    #2 0.0 B2 267 12
    #3 1.0 D2 137810 15
    #(1.0, (4, 2)): node_count 138077

    #D2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 E2 277 20
    #(1.0, (5, 2)): node_count 285

    #E2:
    #1 0.0 PASS 0 0
    #2 0.0 F2 56 10
    #3 1.0 D2 1650 23
    #(1.0, (4, 2)): node_count 1706

    #D3:
    #1 0.0 D2 12 9
    #2 1.0 D4 277 17
    #(1.0, (4, 4)): node_count 289

    #D4:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 C4 72 22
    #(1.0, (3, 4)): node_count 80

    #E4:
    #1 0.0 F4 12 9
    #2 1.0 D4 74 22
    #(1.0, (4, 4)): node_count 86

    ##############################################
    #+use cache find for lower n for move ordering
    #A1:
    #1 1.0 A2 36 16
    #(1.0, (1, 2)), node_count 36

    #B1:
    #1 0.0 PASS 0 0
    #1 0.0 PASS 0 0
    #(1.0, (2, 2)), node_count 1021

    #C1:
    #1 0.0 PASS 0 0
    #2 1.0 C2 682 13
    #(1.0, (3, 2)), node_count 682

    #D1: 1 0.0 PASS 0 0
    #2 1.0 D2 1093 21
    #(1.0, (4, 2)), node_count 1093

    #E1:
    #1 0.0 PASS 0 0
    #2 1.0 F1 224 23
    #(1.0, (6, 1)), node_count 224

    #B2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 B3 591 13
    #(1.0, (2, 3)), node_count 599

    #C2:
    #1 0.0 PASS 0 0
    #2 0.0 B2 267 12
    #3 1.0 B2 1115 15
    #(1.0, (2, 2)), node_count 1382

    #D2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 E2 256 20
    #(1.0, (5, 2)), node_count 264

    #E2:
    #1 0.0 PASS 0 0
    #2 0.0 F2 56 10
    #3 1.0 F2 469 13
    #(1.0, (6, 2)), node_count 525

    #D3:
    #1 0.0 D2 12 9
    #2 1.0 D2 74 23
    #(1.0, (4, 2)), node_count 86

    #D4:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 C4 72 22
    #(1.0, (3, 4)), node_count 80

    #E4:
    #1 0.0 F4 12 9
    #2 1.0 F4 68 24
    #(1.0, (6, 4)), node_count 80

    ##############################################
    #+sort moves: move_cache, adjacent liberties, total_liberties
    #A1:
    #1 1.0 B1 18 14
    #(1.0, (2, 1)), node_count 18

    #B1:
    #1 0.0 PASS 0 0
    #2 1.0 B2 41 10
    #(1.0, (2, 2)), node_count 41

    #C1:
    #1 0.0 PASS 0 0
    #2 1.0 D1 140 11
    #(1.0, (4, 1)), node_count 140

    #D1:
    #1 0.0 PASS 0 0
    #2 1.0 D2 101 17
    #(1.0, (4, 2)), node_count 101

    #E1:
    #1 0.0 PASS 0 0
    #2 1.0 E2 263 20
    #(1.0, (5, 2)), node_count 263

    #B2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 C2 228 21
    #(1.0, (3, 2)), node_count 236

    #C2:
    #1 0.0 PASS 0 0
    #2 0.0 D2 56 10
    #3 1.0 D2 2945 16
    #(1.0, (4, 2)), node_count 3001
    #search_key()
    #3 1.0 D2 2815 16
    #(1.0, (4, 2)), node_count 2871

    #D2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 D3 180 21
    #(1.0, (4, 3)), node_count 188

    #E2:
    #1 0.0 PASS 0 0
    #2 0.0 D2 56 10
    #3 1.0 D2 869 16
    #(1.0, (4, 2)), node_count 925
    #search_key()
    #3 1.0 D2 1558 16
    #(1.0, (4, 2)), node_count 1614
    

    #D3:
    #1 0.0 D4 12 9
    #2 1.0 D4 140 20
    #(1.0, (4, 4)), node_count 152

    #D4:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 E4 50 22
    #(1.0, (5, 4)), node_count 58

    #E4:
    #1 0.0 D4 12 9
    #2 1.0 D4 62 24
    #(1.0, (4, 4)), node_count 74
    
    ##############################################
    #shape move ordering: quick_score_move
    #A1:
    #1 1.0 A2 26 16
    #(1.0, (1, 2)), node_count 26

    #B1:
    #1 0.0 PASS 0 0
    #2 1.0 B2 41 10
    #(1.0, (2, 2)), node_count 41

    #C1:
    #1 0.0 PASS 0 0
    #2 1.0 C2 154 25
    #(1.0, (3, 2)), node_count 154

    #D1:
    #1 0.0 PASS 0 0
    #2 1.0 D2 155 20
    #(1.0, (4, 2)), node_count 155

    #E1:
    #1 0.0 PASS 0 0
    #2 1.0 E2 273 19
    #(1.0, (5, 2)), node_count 273

    #B2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 B1 354 5
    #4 1.0 B1 1185 9
    #(1.0, (2, 1)), node_count 1547

    #C2:
    #1 0.0 PASS 0 0
    #2 0.0 D2 56 10
    #3 1.0 D2 406 16
    #(1.0, (4, 2)), node_count 462

    #D2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 1.0 D1 271 22
    #(1.0, (4, 1)), node_count 279

    #E2:
    #1 0.0 PASS 0 0
    #2 0.0 F2 56 10
    #3 1.0 F2 299 16
    #(1.0, (6, 2)), node_count 355

    #D3:
    #1 0.0 D4 12 9
    #2 1.0 D4 120 20
    #(1.0, (4, 4)), node_count 132
    
    #D4:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 1.0 E4 50 22
    #(1.0, (5, 4)), node_count 58

    #E4:
    #1 0.0 F4 12 9
    #2 1.0 F4 62 24
    #(1.0, (6, 4)), node_count 74

    ##############################################
    #v0.2.3
    #node_limit: 10000 (defense also done with 5000 node limit)
    
    #A1:
    #1 1.0 A2 26 7
    #try defence: A2
    #1 0.0 PASS 0 3
    #2 1.0 B2 393 14
    #try defence: B1
    #1 0.0 PASS 0 3
    #2 1.0 B2 351 12
    #try defence: B2
    #1 0.0 B1 12 6
    #2 ...
    #('tactically critical', (1, 2), (2, 2)), node_count 5775
    
    #B1:
    #1 0.0 PASS 0 3
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10005

    #C1:
    #1 0.0 PASS 0 3
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10004

    #D1:
    #1 0.0 PASS 0 3
    #2 1.0 D2 1304 12
    #('tactically critical', (4, 2), (4, 2)), node_count 6308

    #E1:
    #1 0.0 PASS 0 3
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10002

    #B2:
    #1 0.0 PASS 0 4
    #2 0.0 PASS 0 4
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10002

    #C2:
    #1 0.0 PASS 0 3
    #2 0.0 D2 217 19
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10002

    #D2:
    #1 0.0 PASS 0 4
    #2 0.0 PASS 0 4
    #3 1.0 C2 7180 15
    #('tactically critical', (3, 2), (3, 2)), node_count 12188

    #E2:
    #1 0.0 PASS 0 3
    #2 0.0 F2 219 19
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10001

    #D3:
    #1 0.0 D4 12 9
    #2 1.0 D4 341 13
    #('tactically critical', (4, 4), (4, 4)), node_count 5364

    #D4:
    #1 0.0 PASS 0 4
    #2 0.0 PASS 0 4
    #3 1.0 C4 261 21
    #('tactically critical', (3, 4), (3, 4)), node_count 5266

    #E4:
    #1 0.0 F4 12 9
    #2 1.0 F4 117 14
    #try defence: F4
    #1 0.0 PASS 0 4
    #2 0.0 PASS 0 8
    #('tactically critical', (6, 4), (6, 4)), node_count 5145

    ##############################################
    #PN search with lazy child generation
    #added lazy change board: pn_change_board
    #use alpha-beta for lambda1 and PN for lambda2>=
    #node_limit: 10000 (defense also done with 5000 node limit)
    
    #A1:
    #1 1.0 A2 26 7
    #try defence: A2
    #1 0.0 PASS 0 3
    #2 True B2 873 23
    #try defence: B1
    #1 0.0 PASS 0 3
    #2 True B2 824 23
    #try defence: B2
    #1 0.0 B1 12 6
    #2 False PASS 277 10
    #3 ...
    #('tactically critical', (1, 2), (2, 2)), node_count 6734

    #B1:
    #1 0.0 PASS 0 3
    #2 True B2 3824 29
    #('tactically critical', (2, 2), (2, 2)), node_count 8831

    #C1:
    #1 0.0 PASS 0 3
    #2 True B1 2786 20
    #('tactically critical', (2, 1), (2, 1)), node_count 7795

    #D1:
    #1 0.0 PASS 0 3
    #2 True D2 2364 20
    #('tactically critical', (4, 2), (4, 2)), node_count 7377

    #E1:
    #1 0.0 PASS 0 3
    #2 True E2 8430 17
    #('tactically critical', (5, 2), (5, 2)), node_count 13439

    #B2:
    #1 0.0 PASS 0 4
    #2 False PASS 0 4
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10001

    #C2:
    #1 0.0 PASS 0 3
    #2 False PASS 219 19
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10001

    #D2:
    #1 0.0 PASS 0 4
    #2 False PASS 0 4
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10010

    #E2:
    #1 0.0 PASS 0 3
    #2 False PASS 221 19
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10002

    #D3:
    #1 0.0 D4 12 9
    #2 True D2 919 20
    #('tactically critical', (4, 2), (4, 2)), node_count 5934

    #D4:
    #1 0.0 PASS 0 4
    #2 False PASS 0 4
    #3 True C4 266 21
    #('tactically critical', (3, 4), (3, 4)), node_count 5271

    #E4:
    #1 0.0 F4 12 9
    #2 True D4 779 20
    #try defence: D4
    #1 0.0 PASS 0 4
    #2 False PASS 0 8
    #3 True F4 1893 22
    #try defence: F4
    #1 0.0 PASS 0 4
    #2 False PASS 0 8
    #3 True D4 1846 22
    #try defence: C4
    #1 0.0 F4 14 9
    #2 True F4 349 18
    #try defence: G4
    #1 0.0 D4 12 9
    #2 True D4 341 18
    #try defence: D3
    #1 0.0 F4 16 15
    #2 True F4 653 17
    #try defence: D5
    #1 0.0 F4 16 15
    #2 True F4 908 17
    #try defence: F3
    #1 0.0 D4 14 15
    #2 True D4 366 17
    #try defence: F5
    #1 0.0 D4 14 15
    #2 True D4 498 17
    #try defence: B4
    #1 0.0 F4 12 9
    #2 True D4 720 21
    #try defence: D2
    #1 0.0 F4 12 9
    #2 True D4 618 21
    #try defence: F2
    #1 0.0 F4 12 9
    #2 True D4 685 21
    #try defence: H4
    #1 0.0 F4 12 9
    #2 True D4 788 20
    #try defence: E2
    #1 0.0 F4 14 14
    #2 True D4 346 17
    #try defence: E6
    #1 0.0 F4 14 14
    #2 True D4 411 18
    #('tactically dead', (4, 4), (-1, -1)), node_count 11390

    ##############################################
    #PN search with lazy child generation
    #added lazy change board: pn_change_board
    #use alpha-beta for lambda1 and PN for lambda2>=
    #node_limit: 10000 (defense also done with 5000 node limit)
    #lambda cache
    
    #A1:
    #1 1.0 A2 26 7
    #try defence: A2
    #1 0.0 PASS 0 3
    #2 True B2 825 23
    #try defence: B1
    #1 0.0 PASS 0 3
    #2 True B2 775 23
    #try defence: B2
    #1 0.0 B1 12 6
    #2 False PASS 261 10
    #('tactically critical', (1, 2), (2, 2)), node_count 6634

    #B1:
    #1 0.0 PASS 0 3
    #2 True B2 3573 29
    #('tactically critical', (2, 2), (2, 2)), node_count 8579

    #C1:
    #1 0.0 PASS 0 3
    #2 True B1 2548 20
    #('tactically critical', (2, 1), (2, 1)), node_count 7551

    #D1:
    #1 0.0 PASS 0 3
    #2 True D2 2146 20
    #('tactically critical', (4, 2), (4, 2)), node_count 7150

    #E1:
    #1 0.0 PASS 0 3
    #2 True E2 7469 26
    #('tactically critical', (5, 2), (5, 2)), node_count 12477

    #B2:
    #1 0.0 PASS 0 4
    #2 False PASS 0 4
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10004

    #C2:
    #1 0.0 PASS 0 3
    #2 False PASS 199 19
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10002

    #D2:
    #1 0.0 PASS 0 4
    #2 False PASS 0 4
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10003

    #E2:
    #1 0.0 PASS 0 3
    #2 False PASS 205 19
    #('tactically alive', (-1, -1), (-1, -1)), node_count 10003

    #D3:
    #1 0.0 D4 12 9
    #2 True D2 847 23
    #('tactically critical', (4, 2), (4, 2)), node_count 5871

    #D4:
    #1 0.0 PASS 0 4
    #2 False PASS 0 4
    #3 True C4 253 21
    #('tactically critical', (3, 4), (3, 4)), node_count 5259

    #E4:
    #1 0.0 F4 12 9
    #2 True D4 693 20
    #try defence: D4
    #1 0.0 PASS 0 4
    #2 False PASS 0 8
    #3 True F4 1694 32
    #try defence: F4
    #1 0.0 PASS 0 4
    #2 False PASS 0 8
    #3 True D4 1674 32
    #try defence: C4
    #1 0.0 F4 14 9
    #2 True F4 336 36
    #try defence: G4
    #1 0.0 D4 12 9
    #2 True D4 333 25
    #try defence: D3
    #1 0.0 F4 16 15
    #2 True F4 588 30
    #try defence: D5
    #1 0.0 F4 16 15
    #2 True F4 854 32
    #try defence: F3
    #1 0.0 D4 14 15
    #2 True D4 303 30
    #try defence: F5
    #1 0.0 D4 14 15
    #2 True D4 446 32
    #try defence: B4
    #1 0.0 F4 12 9
    #2 True D4 622 26
    #try defence: D2
    #1 0.0 F4 12 9
    #2 True D4 595 21
    #try defence: F2
    #1 0.0 F4 12 9
    #2 True D4 650 19
    #try defence: H4
    #1 0.0 F4 12 9
    #2 True D4 675 20
    #try defence: E2
    #1 0.0 F4 14 14
    #2 True D4 320 28
    #try defence: E6
    #1 0.0 F4 14 14
    #2 True D4 384 31
    #('tactically dead', (4, 4), (-1, -1)), node_count 10356

    g = simple_go.Game(9)
    g.place_free_handicap(9)
    for move in g.iterate_moves():
        if move==simple_go.PASS_MOVE:
            continue
        g.make_move(move)
        print "="*60
        node_count0 = g.node_count
        t0 = time.time()
        print g.block_tactic_status(move)
        t1 = time.time()
        print g.move_as_string(move), "node_count", g.node_count-node_count0, "%.3fs" % (t1-t0,)
        g.undo_move()
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #A1 node_count 36 0.032s
    #A2 node_count 396 0.513s
    #A3 node_count 853 0.870s
    #A4 node_count 409 0.335s
    #A5 node_count 756 0.704s
    #A6 node_count 329 0.264s
    #A7 node_count 182 0.171s
    #A8 node_count 420 0.433s
    #A9 node_count 36 0.032s
    #B1 node_count 1052 1.000s
    #B2 node_count 592 0.440s
    #B3 node_count 929890 977.904s
    #B4 node_count 410 2.317s
    #B5 node_count 3367 11.078s
    #B6 node_count 764 0.638s
    #B7 node_count 9422 21.330s
    #B8:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 B9 662 12
    #... self.node_count==4598701


    ##############################################
    #+use cache find for lower n for move ordering
    #A1 node_count 36 0.078s
    #A2 node_count 496 0.756s
    #A3 node_count 928 1.100s
    #A4 node_count 409 0.492s
    #A5 node_count 758 1.809s
    #A6 node_count 333 0.388s
    #A7 node_count 182 0.223s
    #A8 node_count 324 1.420s
    #A9 node_count 36 0.064s
    #B1 node_count 1021 1.360s
    #B2 node_count 599 0.656s
    #B3 node_count 1052 2.329s
    #B4 node_count 410 0.505s
    #B5 node_count 1404 3.405s
    #B6 node_count 761 0.774s
    #B7 node_count 516 1.502s
    #B8:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 B9 689 12
    #...
    #B9 node_count 800 2.008s
    #C1 node_count 682 1.416s
    #C2 node_count 1382 7.374s
    #C4 node_count 186 0.475s
    #C6 node_count 74 0.347s
    #C8 node_count 38207 100.134s
    #C9 node_count 679 1.663s
    #D1 node_count 1093 2.896s
    #D2 node_count 264 0.683s
    #D3 node_count 86 0.293s
    #D4 node_count 80 0.119s
    #D5 node_count 86 0.334s
    #D6 node_count 80 0.377s
    #D7 node_count 86 0.264s
    #D8 node_count 996 1.751s
    #D9 node_count 746 1.506s
    #E1 node_count 224 0.551s
    #E2 node_count 525 1.143s
    #E4 node_count 80 0.421s
    #E6 node_count 86 0.470s
    #E8 node_count 1251 2.421s
    #E9 node_count 197 0.486s
    #F1 node_count 155 0.448s
    #F2 node_count 274 1.167s
    #F3 node_count 156 0.307s
    #F4 node_count 80 0.355s
    #F5 node_count 86 0.292s
    #F6 node_count 80 0.261s
    #F7 node_count 196 0.590s
    #F8 node_count 388 0.954s
    #F9 node_count 1407 2.442s
    #G1 node_count 292 0.763s
    #G2 node_count 1310 3.305s
    #G4 node_count 86 0.329s
    #G6 node_count 162 0.483s
    #G8:
    #1 0.0 PASS 0 0
    #2 0.0 H8 103 10
    #... 

    ##############################################
    #+sort moves: move_cache, adjacent liberties, total_liberties
    #A1 node_count 18 0.157s
    #A2 node_count 41 0.122s
    #A3 node_count 133 0.535s
    #A4 node_count 98 0.277s
    #A5 node_count 137 0.334s
    #A6 node_count 96 0.275s
    #A7 node_count 126 0.678s
    #A8 node_count 41 0.247s
    #A9 node_count 26 0.197s
    #B1 node_count 41 0.120s
    #B2 node_count 236 0.777s
    #B3 node_count 4424 8.635s  search_key(): B3 node_count 3315 2.757s
    #B4 node_count 222 0.573s
    #B5 node_count 832 1.936s  search_key(): B5 node_count 836 0.878s
    #B6 node_count 254 0.721s
    #B7:
    #1 0.0 PASS 0 0
    #2 0.0 B6 56 10
    #gets stuck here with and without search_key()

    ##############################################
    #shape move ordering: quick_score_move
    #A1 node_count 26 0.425s
    #A2 node_count 41 0.118s
    #A3 node_count 154 0.231s
    #A4 node_count 155 0.326s
    #A5 node_count 273 0.364s
    #A6 node_count 102 0.171s
    #A7 node_count 134 0.185s
    #A8 node_count 41 0.079s
    #A9 node_count 26 0.053s
    #B1 node_count 41 0.082s
    #B2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 B1 354 5
    #4 1.0 B1 1185 9
    #(1.0, (2, 1))
    #B2 node_count 1547 1.918s
    #B3:
    #1 0.0 PASS 0 0
    #2 0.0 B4 56 10
    #3 1.0 B4 1625 16
    #(1.0, (2, 4))
    #B3 node_count 1681 1.801s
    #B4 node_count 279 0.320s
    #B5 node_count 355 0.445s
    #B6 node_count 267 0.263s
    #B7:
    #1 0.0 PASS 0 0
    #2 0.0 B8 56 10
    #3 1.0 B8 359 11
    #(1.0, (2, 8))
    #B7 node_count 415 0.470s
    #B8:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 B9 354 5
    #4 1.0 B9 1185 9
    #(1.0, (2, 9))
    #B8 node_count 1547 1.756s
    #B9 node_count 41 0.076s
    #C1 node_count 154 0.249s
    #C2 node_count 462 0.502s
    #C4 node_count 132 0.198s
    #C6 node_count 144 0.190s
    #C8 node_count 462 0.783s
    #C9 node_count 154 0.198s
    #D1 node_count 155 0.209s
    #D2 node_count 279 0.311s
    #D3 node_count 132 0.313s
    #D4 node_count 58 0.123s
    #D5 node_count 74 0.439s
    #D6 node_count 58 0.101s
    #D7 node_count 74 0.144s
    #D8 node_count 279 0.301s
    #D9 node_count 155 0.199s
    #E1 node_count 273 0.338s
    #E2 node_count 355 0.443s
    #E4 node_count 74 0.186s
    #E6 node_count 74 0.492s
    #E8 node_count 355 0.500s
    #E9 node_count 273 0.334s
    #F1 node_count 102 0.184s
    #F2 node_count 267 0.355s
    #F3 node_count 144 0.193s
    #F4 node_count 58 0.105s
    #F5 node_count 74 0.154s
    #F6 node_count 58 0.098s
    #F7 node_count 74 0.407s
    #F8 node_count 267 0.368s
    #F9 node_count 102 0.132s
    #G1 node_count 134 0.169s
    #G2 node_count 415 0.476s
    #G4 node_count 74 0.482s
    #G6 node_count 74 0.142s
    #G8 node_count 415 0.484s
    #G9 node_count 134 0.179s
    #H1 node_count 41 0.077s
    #H2:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 J2 354 5
    #4 1.0 J2 1185 9
    #(1.0, (9, 2))
    #H2 node_count 1547 1.732s
    #H3 node_count 462 0.486s
    #H4 node_count 279 0.316s
    #H5 node_count 355 0.446s
    #H6 node_count 267 0.465s
    #H7 node_count 415 0.486s
    #H8:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 4
    #3 0.0 J8 354 5
    #4 1.0 J8 1185 9
    #(1.0, (9, 8))
    #H8 node_count 1547 1.428s
    #H9 node_count 41 0.086s
    #J1 node_count 26 0.059s
    #J2 node_count 41 0.172s
    #J3 node_count 154 0.193s
    #J4 node_count 155 0.179s
    #J5 node_count 273 0.383s
    #J6 node_count 102 0.132s
    #J7 node_count 134 0.505s
    #J8 node_count 41 0.076s
    #J9 node_count 26 0.055s
    
def test_9x9_ha9_defend():
    g = simple_go.Game(9)
    g.place_free_handicap(9)
    g.make_move(simple_go.string_as_move("B2", g.size))
    node_count0 = g.node_count
    #import pdb; pdb.set_trace()
    print g.block_tactic_status(simple_go.string_as_move("B2", g.size)), "node_count", g.node_count-node_count0

    defend_moves = g.reading_shadow[simple_go.string_as_move("B2", g.size)].keys()
    g.make_move(simple_go.PASS_MOVE)
    for move in defend_moves:
        if g.make_move(move):
            print "-"*60
            print "try defence:", g.move_as_string(move)

            node_count0 = g.node_count
            print g.block_tactic_status(simple_go.string_as_move("B2", g.size)), "node_count", g.node_count-node_count0
            g.undo_move()

def really_deep_1_2_tactics():
    g = load_sgf.load_file("kgs/very_slow_move_gen_v_0_2_1.sgf")
    g.make_move(simple_go.string_as_move("G18", g.size))
    
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("S8", g.size))
    print "node_count", g.node_count-node_count0
    #('tactically critical', (18, 9), (19, 9))
    #node_count 7075
    #lambda without shadow and no special generator for n==1:
    #1.0: node_count 29442
    #lambda without shadow and special generator for n==1:
    #1.0: node_count 1614
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 1.0 S9 1606 151
    #(1.0, (18, 9)): node_count 1606
    #2.3s: 694 nodes/s
    return g

def test_lambda():
    g = load_sgf.load_file("kgs/SimpleBot-carlicos_tactics_test.sgf")
    while len(g.move_history)>69: g.undo_move()
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("H3", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 0.0 PASS 68 15
    #4 0.0 H4 4627 15
    #5 1.0 J4 20825 20
    #(1.0, (9, 4)): node_count 25529
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 0.0 PASS 58 12
    #4 0.0 PASS 367 9
    #5 1.0 J4 1407 12
    #(1.0, (9, 4)): node_count 1841
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 0.0 PASS 56 12
    #4 0.0 H4 2553 12
    #5 1.0 D4 4188 9
    #(1.0, (4, 4)), node_count 6806
    #+target liberties always included, also after it has expanded by connecting
    #1 0.0 PASS 0 0
    #2 0.0 PASS 8 5
    #3 0.0 PASS 112 7
    #4 1.0 J4 1477 12
    #(1.0, (9, 4)), node_count 1598

    while len(g.move_history)>52: g.undo_move()
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("E8", g.size))
    print "node_count", g.node_count-node_count0
    #1-2 liberty code:
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 0
    #above + self.current_shadow_origin==pos: if len(liberties)>=5 or (len(liberties)>=4 and depth>=2) or (len(liberties)>=3 and depth>=5):
    #('tactically dead', (6, 9), (-1, -1))
    #node_count 25
    #lambda without shadow and no special generator for n==1:
    #1 0.0 66
    #2 1.0 3402
    #1.0: node_count 3468
    #lambda without shadow and special generator for n==1:
    #1 0.0 0
    #2 1.0 254
    #1.0: node_count 254
    #lambda with shadow and special generator for n==1:
    #1 0.0 PASS 0 0
    #2 1.0 F9 16 60
    #(1.0, (6, 9)): node_count 16
    #above + self.shadow_only_neighbour
    #1 0.0 PASS 0 0
    #2 1.0 F9 16 11
    #(1.0, (6, 9)): node_count 16
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 F9 16 11
    #(1.0, (6, 9)): node_count 16
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 D9 14 12
    #(1.0, (4, 9)), node_count 14
    #+target liberties always included, also after it has expanded by connecting
    #-"-
    #g.block_tactic_status_sgf(simple_go.string_as_move("E8", g.size))
    #return

    print "="*60
    node_count0 = g.node_count
    #print g.block_tactic_status_sgf(simple_go.string_as_move("H8", g.size))
    print g.block_tactic_status(simple_go.string_as_move("H8", g.size))
    print "node_count", g.node_count-node_count0
    #1-2 liberty code:
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 0
    #above + self.current_shadow_origin==pos: if len(liberties)>=5 or (len(liberties)>=4 and depth>=2) or (len(liberties)>=3 and depth>=5):
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 78
    #lambda without shadow and no special generator for n==1:
    #1 0.0 66
    #2 1.0 47808
    #1.0: node_count 47874
    #lambda without shadow and special generator for n==1:
    #1 0.0 0
    #2 1.0 2978
    #1.0: node_count 2978
    #lambda with shadow and special generator for n==1:
    #1 0.0 PASS 0 0
    #2 1.0 J7 74 61
    #(1.0, (9, 7)): node_count 74
    #above + self.shadow_only_neighbour
    #1 0.0 PASS 0 0
    #2 1.0 J7 74 12
    #(1.0, (9, 7)): node_count 74
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 J7 66 10
    #(1.0, (9, 7)): node_count 66
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 H9 46 14
    #(1.0, (8, 9)), node_count 46
    #+target liberties always included, also after it has expanded by connecting
    #-"-
    
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("A8", g.size))
    print "node_count", g.node_count-node_count0
    #1-2 liberty code:
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 2
    #above + self.current_shadow_origin==pos: if len(liberties)>=5 or (len(liberties)>=4 and depth>=2) or (len(liberties)>=3 and depth>=5):
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 6
    #lambda without shadow and no special generator for n==1:
    #1 0.0 144
    #2 1.0 5098
    #1.0: node_count 5242
    #lambda without shadow and special generator for n==1:
    #1 0.0 6
    #2 1.0 278
    #1.0: node_count 284
    #lambda with shadow and special generator for n==1:
    #1 0.0 A9 6 62
    #2 1.0 C9 84 64
    #(1.0, (3, 9)): node_count 90
    #above + self.shadow_only_neighbour
    #1 0.0 A9 6 9
    #2 1.0 C9 16 11
    #(1.0, (3, 9)): node_count 22
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 A9 6 9
    #2 1.0 C9 16 11
    #(1.0, (3, 9)): node_count 22
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 A9 6 9
    #2 1.0 C9 38 11
    #(1.0, (3, 9)), node_count 44
    #+target liberties always included, also after it has expanded by connecting
    #-"-
    
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("B2", g.size))
    print "node_count", g.node_count-node_count0
    #1-2 liberty code:
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 0
    #above + self.current_shadow_origin==pos: if len(liberties)>=5 or (len(liberties)>=4 and depth>=2) or (len(liberties)>=3 and depth>=5):
    #('tactically dead', (3, 1), (-1, -1))
    #node_count 79
    #lambda without shadow and no special generator for n==1:
    #1 0.0 66
    #2 1.0 3194
    #1.0: node_count 3260
    #lambda without shadow and special generator for n==1:
    #1 0.0 0
    #2 1.0 254
    #1.0: node_count 254
    #lambda with shadow and special generator for n==1:
    #1 0.0 PASS 0 0
    #2 1.0 C1 13 59
    #(1.0, (3, 1)): node_count 13
    #above + self.shadow_only_neighbour
    #1 0.0 PASS 0 0
    #2 1.0 C1 13 8
    #(1.0, (3, 1)): node_count 13
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 C1 13 8
    #(1.0, (3, 1)): node_count 13
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 A2 22 16
    #(1.0, (1, 2)), node_count 22
    #+target liberties always included, also after it has expanded by connecting
    #-"-
    
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("D2", g.size))
    print "node_count", g.node_count-node_count0
    #1-2 liberty code:
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 0
    #above + self.current_shadow_origin==pos: if len(liberties)>=5 or (len(liberties)>=4 and depth>=2) or (len(liberties)>=3 and depth>=5):
    #('tactically critical', (5, 1), (6, 2))
    #node_count 317
    #lambda without shadow and no special generator for n==1:
    #not calculated..
    #lambda without shadow and special generator for n==1:
    #1 0.0 0
    #2 1.0 61014
    #1.0: node_count 61014
    #lambda with shadow and special generator for n==1:
    #1 0.0 PASS 0 0
    #2 1.0 E1 125 66
    #(1.0, (5, 1)): node_count 125
    #above + self.shadow_only_neighbour
    #1 0.0 PASS 0 0
    #2 1.0 E1 125 16
    #(1.0, (5, 1)): node_count 125
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 E1 111 16
    #(1.0, (5, 1)): node_count 111
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 1.0 D1 63 18
    #(1.0, (4, 1)), node_count 63
    #+target liberties always included, also after it has expanded by connecting
    #-"-
    
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("H3", g.size))
    print "node_count", g.node_count-node_count0
    #1-2 liberty code:
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 0
    #above + self.current_shadow_origin==pos: if len(liberties)>=5 or (len(liberties)>=4 and depth>=2) or (len(liberties)>=3 and depth>=5):
    #('tactically alive', (-1, -1), (-1, -1))
    #node_count 210
    #lambda without shadow and no special generator for n==1:
    #
    #lambda without shadow and special generator for n==1:
    #1 0.0 0
    #2 0.0 148
    #3 ? self.node_cont = 12267233
    #lambda with shadow and special generator for n==1:
    #1 0.0 PASS 0 0
    #2 0.0 PASS 88 65
    #...
    #above + self.shadow_only_neighbour
    #1 0.0 PASS 0 0
    #2 0.0 PASS 88 20
    #3 1.0 H2 313120 17
    #(1.0, (8, 2)): node_count 313208
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 0.0 PASS 60 11
    #3 1.0 H2 19313 23
    #(1.0, (8, 2)): node_count 19373
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #1 0.0 PASS 0 0
    #2 0.0 PASS 58 11
    #... self.node_count==374420
    #+target liberties always included, also after it has expanded by connecting
    #1 0.0 PASS 0 0
    #2 0.0 PASS 58 11
    #3 1.0 H2 11037 12
    #(1.0, (8, 2)), node_count 11095

    g.make_move((8,2))
    g.make_move((9,6))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("H3", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1:
    #above + self.shadow_only_neighbour
    #1 0.0 H4 26 12
    #2 0.0 H4 2467 13
    #3 1.0 J3 8866 29
    #(1.0, (9, 3)): node_count 11359
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 H4 26 12
    #2 0.0 H4 1285 11
    #3 1.0 J3 119 27
    #(1.0, (9, 3)): node_count 1430
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #+target liberties always included, also after it has expanded by connecting
    #1 0.0 H4 24 11
    #2 1.0 J3 669 24
    #(1.0, (9, 3)), node_count 693

    g.make_move((9,3))
    g.make_move((8,4))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("H3", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1:
    #above + self.shadow_only_neighbour
    #1 0.0 PASS 0 0
    #2 1.0 J4 91 23
    #(1.0, (9, 4)): node_count 91
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 PASS 0 0
    #2 1.0 J4 65 18
    #(1.0, (9, 4)): node_count 65
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #+target liberties always included, also after it has expanded by connecting
    #1 0.0 PASS 0 0
    #2 1.0 J4 95 18
    #(1.0, (9, 4)), node_count 95

    g.make_move((9,4))
    g.make_move((9,5))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("H3", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1:
    #above + self.shadow_only_neighbour
    #1 0.0 J7 40 19
    #2 1.0 J2 1688 21
    #(1.0, (9, 2)): node_count 1728
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 0.0 J7 40 19
    #2 1.0 J2 1152 8
    #(1.0, (9, 2)): node_count 1192
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #+target liberties always included, also after it has expanded by connecting
    ##1 0.0 J7 70 19
    #2 1.0 J2 226 18
    #(1.0, (9, 2)), node_count 296

    g.make_move((9,2))
    g.make_move((7,2))
    print "="*60
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("H3", g.size))
    print "node_count", g.node_count-node_count0
    #lambda with shadow and special generator for n==1:
    #above + self.shadow_only_neighbour
    #1 1.0 D4 12 13
    #(1.0, (4, 4)): node_count 12
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache
    #1 1.0 D4 12 13
    #(1.0, (4, 4)): node_count 12
    #lambda with shadow and special generator for n==1 + self.shadow_only_neighbour + cache + quick_score_move
    #+target liberties always included, also after it has expanded by connecting
    #1 1.0 D4 12 13
    #(1.0, (4, 4)), node_count 12

    return g

def analyse_end_blocks_at_end(g, color):
    origin_list = []
    for block in g.current_board.iterate_blocks(color):
        origin_list.append(block.get_origin())

    for origin in origin_list:
        node_count0 = g.node_count
        print g.block_tactic_status(origin)
        print "node_count", g.node_count-node_count0
        

def game_end_dead_status():
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_2_1_19x19_ha9_whole_board.sgf")
    while len(g.move_history)>294:
        g.undo_move()

    #Good test for inverse search: 
##    node_count0 = g.node_count
##    print g.block_tactic_status(simple_go.string_as_move("L2", g.size))
##    print "node_count", g.node_count-node_count0
##    return -1

##    node_count0 = g.node_count
##    print g.block_tactic_status(simple_go.string_as_move("G4", g.size))
##    print "node_count", g.node_count-node_count0
##    return -1

    while len(g.move_history)>280:
        g.undo_move()

    #analyse_end_blocks_at_end(g, simple_go.BLACK)

    g = load_sgf.load_file("kgs/Pento-SimpleBot_mod.sgf")

    #Even better test for inverse search:  E6/C18/G18/E8/M18/M6/L9/H19
##    node_count0 = g.node_count
##    print g.block_tactic_status(simple_go.string_as_move("E6", g.size))
##    print "node_count", g.node_count-node_count0
##    return -1

    analyse_end_blocks_at_end(g, simple_go.BLACK)

def test_lambda2():
    #Inverse search tests
    g = load_sgf.load_file("test_tactics/5x5_lambda_50W.sgf")
    while len(g.move_history)>7:
        g.undo_move()

    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("D3", g.size)), "node_count", g.node_count-node_count0
    print "="*60

    g = load_sgf.load_file("test_tactics/7x7_lambda_51W.sgf")
    while len(g.move_history)>19:
        g.undo_move()

    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("D6", g.size)), "node_count", g.node_count-node_count0

    

    return g

def load_file_at_count(file, count=1000):
    g = load_sgf.load_file(file)
    while len(g.move_history)>count:
        g.undo_move()
    return g

def test_file_move_count(file, count, pos):
    g = load_file_at_count(file, count)

    print file, count, pos
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move(pos, g.size)), "node_count", g.node_count-node_count0
    print "="*60

    return g

def test_file_move_count_move_generation(file, count=1000000):
    g = load_file_at_count(file, count)
    print file, count
    print g.current_board
    print g.str_current_position()
    print g.generate_move()
    return g

def test_inversion():
    file = "kgs/false_eye_chain.sgf"
    file = "kgs/inverted_search.sgf"
    g = test_file_move_count(file, 1000, "A3")
    g = test_file_move_count(file, 1000, "A9")
    g = test_file_move_count(file, 1000, "A11")
    g = test_file_move_count(file, 1000, "Q15")
    g = test_file_move_count(file, 1000, "J13")
    g = test_file_move_count(file, 1000, "N4")

    g = test_file_move_count("test_tactics/19x19_lambda_i_60W.sgf", 192, "J7")

def test_double_attack():
    g = test_file_move_count("test_tactics/13x13_lambda_i_59W.sgf", 3, "K2")
    #if J2 move made..
    g.generate_move()
    
def test_capture_dead():
##    g = load_sgf.load_file("test_tactics/13x13_lambda_d_61W.sgf")
##    while len(g.move_history)>47:
##        g.undo_move()
##    print g.str_current_position()
##    print g.generate_move()

    g = load_sgf.load_file("kgs/dead_stones.sgf")
    print g.str_current_position()
    print g.generate_move()
    return g

def why_not_save():
    g = load_sgf.load_file("kgs/SimpleBot-Jarcys_got_lucky.sgf")
    while len(g.move_history)>35:
        g.undo_move()

    #print g.str_current_position()
    #print g.generate_move()

    g.make_move(simple_go.string_as_move("G8", 9))

    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("F8", g.size)), "node_count", g.node_count-node_count0

    return g

def self_kill():
    file = "kgs/RQC-SimpleBot_self_kill.sgf"
##    g = test_file_move_count(file, 167, "J1")
    g = load_sgf.load_file(file)
    while len(g.move_history)>166:
        g.undo_move()

    print g.current_board
    print g.str_current_position()
    print g.generate_move()
    return g

def broken():
    g = load_sgf.load_file("kgs/broken.sgf")
    #while len(g.move_history)>106:
    #    g.undo_move()
    print g.current_board
    print g.str_current_position()
    print g.generate_move()
    return g

def inside_unconditionally_alive_and_still_fails_to_see_dead():
    g = test_file_move_count("kgs/Berra-SimpleBot.sgf", 335, "P10")
    return g

def big_dead():
    file = "kgs/big_dead.sgf"
    config.lambda_limit = 100
    g = test_file_move_count(file, 1000, "R1")
    g = test_file_move_count(file, 1000, "A1")
    g = test_file_move_count(file, 1000, "T4")
    g = test_file_move_count(file, 1000, "A19")

    g = test_file_move_count(file, 1000, "A3")
    g = test_file_move_count(file, 1000, "A17")
    return g

def many_things_to_test():
    #first one
    #g = test_file_move_count("kgs/RQC-SimpleBot-2.sgf", 12, "D18")
    file = "kgs/SimpleBot-cunimb_many_things_to_fix_french.sgf"
    #g = test_file_move_count(file, 105, "E5")
    #g = test_file_move_count(file, 91, "E5")
    g = test_file_move_count(file, 316, "K17")
    return g

def test_sgf_trace():
    config.sgf_trace_tactics = False
##    file = "kgs/RQC-SimpleBot-2.sgf"
##    count = 12+1
##    pos = "D18"
##    g = load_sgf.load_file(file)
##    while len(g.move_history)>count:
##        g.undo_move()

##    print file, count, pos
##    node_count0 = g.node_count
##    print g.block_tactic_status_sgf(simple_go.string_as_move(pos, g.size)), "node_count", g.node_count-node_count0
##    print "="*60


    g = simple_go.Game(9)
    g.place_free_handicap(9)
    g.make_move(simple_go.string_as_move("B2", g.size))
    node_count0 = g.node_count
    #import pdb; pdb.set_trace()
    print g.block_tactic_status_sgf(simple_go.string_as_move("B2", g.size)), "node_count", g.node_count-node_count0


    return g


def unconditional_endgame_test():
    #config.use_unconditional_search
    g = test_file_move_count("run_test/minue622-SimpleBot_v0_2_2_mod.sgf", 316+8, "H2")
    print g.current_board
    move = g.generate_move()
    print g.make_move(move)
    print g.make_move((5,15))
    move = g.generate_move()
    print g.make_move(move)
    return g

def test_shape_rescue():
    #config.try_to_find_better_defense
    g = test_file_move_count("run_test/shape_rescue.sgf", 1000, "F2")
    print g.str_current_position()
    print g.generate_move()
    #g.make_move((5,3))
    #print g.str_current_position()
    return g

def slow_reading_problem():
    g = load_file_at_count("kgs/Aloriless-SimpleBot_v0_2_3_testX_19x19_ha9.sgf", 242+8)
    g.make_move(simple_go.string_as_move("L6"))
    node_count0 = g.node_count
    print g.block_tactic_status(simple_go.string_as_move("L6", g.size)), "node_count", g.node_count-node_count0
    return g

def test_coord_conv(move, size):
    print move, size
    sgf = utils.move_as_sgf(move, size)
    print sgf
    print load_sgf.sgf2tuple(size, sgf)

def test_1_line_weird_move():
    #g = test_file_move_count_move_generation("kgs/1_line_weird_move_214.sgf", 214+2)
    #g = test_file_move_count_move_generation("kgs/1_line_weird_move.sgf", 214+2)
    #g = test_file_move_count_move_generation("kgs/SimpleBot-hungtieu_weird_1_line_save.sgf", 1000)
    g = test_file_move_count_move_generation("kgs/1_line_weird_move_SimpleBot-jaywalk.sgf", 72+5)
    return g

def test_weird_saving_move():
    #g = test_file_move_count_move_generation("kgs/long_thinking_time.sgf", 14)
    #g = test_file_move_count_move_generation("kgs/why_not_save_SimpleBot-kimling.sgf", 183)
    #g = test_file_move_count_move_generation("kgs/why_not_save_SimpleBot-kimling.sgf", 207)
    g = test_file_move_count_move_generation("kgs/why_not_save_SimpleBot-kimling.sgf", 287)

def test_allowing_escape():
    #SimpleBot-Ped_why_allow_escape.sgf : allowed laddered group to escape with ladder breaker
    g = test_file_move_count_move_generation("kgs/SimpleBot-Ped_why_allow_escape.sgf", 161)
    return g

def test_slow_move_generation():
    g = test_file_move_count_move_generation("kgs/long_thinking_time.sgf", 73+1)
##    g = load_file_at_count("kgs/long_thinking_time.sgf", 73+1)
##    print g.make_move(simple_go.string_as_move("G12"))
##    config.debug_tactics = True
##    node_count0 = g.node_count
##    print g.block_tactic_status(simple_go.string_as_move("F13", g.size)), "node_count", g.node_count-node_count0
    return g

def test_broken_atari_defense():
    g = test_file_move_count_move_generation("kgs/broken_atari_defense.sgf")
    print "="*60
    #g = test_file_move_count_move_generation("kgs/why_not_save_SimpleBot-kimling.sgf", 183)

def test_futile_end_moves():
    g = load_file_at_count("kgs/zalgo0361-SimpleBot.sgf", 356+8)
    g.make_move(simple_go.string_as_move("J19"))
    g.make_move(simple_go.string_as_move("O13"))
    g.make_move(simple_go.string_as_move("L19"))
    g.make_move(simple_go.string_as_move("P13"))
    g.make_move(simple_go.string_as_move("O15"))
    g.make_move(simple_go.string_as_move("N14"))
    print g.current_board
    print g.str_current_position()
    print g.generate_move()
    return g
    
#very_slow.sgf
#long_thinking_time.sgf (also includes weird saving try move)
#ok: tactic_test_SimpleBot-jaywalk.sgf move 63 group N7

def self_kill2():
    g = test_file_move_count_move_generation("kgs/SimpleBot-suuri_blunder.sgf", 315)
    
def bad_shape_save():
    g = test_file_move_count_move_generation("kgs/bad_shape_save_SimpleBot-bernd77.sgf", 53)

def too_many_nodes():
    #g = test_file_move_count("kgs/too_many_nodes.sgf", 1000, "A3")
    #g = load_sgf.load_file("kgs/too_many_nodes.sgf")
    #print g.block_tactic_status_sgf(simple_go.string_as_move("A2"))
    g = test_file_move_count("kgs/too_many_nodes2.sgf", 1000, "G7")
    #g = load_sgf.load_file("kgs/too_many_nodes2.sgf")
    #print g.block_tactic_status_sgf(simple_go.string_as_move("G7"))
    return g

def try_move(move):
    g = load_sgf.load_file("kgs/too_many_nodes.sgf")
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(string_as_move(move))
    print g.block_tactic_status(simple_go.string_as_move("A3"))
    g.undo_move()
    return g

def lambda_cache_bug():
    test_file_move_count("kgs/lambda_cache_bug.sgf", 1000, "P13")
    

def simple_danger_group():
    for block, move in (("S16", "T18"), ("A18", "B19"), ("A2", "B1")):
        g = test_file_move_count("kgs/simple_danger_group.sgf", 1000, block)
        g.make_move(simple_go.string_as_move(move))
        print g.block_tactic_status(simple_go.string_as_move(block))
        
def simple_danger_group2():
    for block, move in (("S16", "S19"), ("B18", "A18"), ("B2", "A2")):
        g = test_file_move_count("kgs/simple_danger_group2.sgf", 1000, block)
        g.make_move(simple_go.string_as_move(move))
        print g.block_tactic_status(simple_go.string_as_move(block))
        


def danger_rating_from_game():
    g = load_file_at_count("kgs/danger_rating_from_game.sgf")
    print g.current_board
    print g.str_current_position()

    print "="*60

    g = load_file_at_count("kgs/danger_rating_from_game.sgf")
    g.make_move(simple_go.string_as_move("F14"))
    print g.current_board
    print g.str_current_position()
    return g

def simple_ld_problem():
    g = load_file_at_count("kgs/simple_ld_problem.sgf")
    g = load_file_at_count("kgs/simple_ld_problem_unconditional.sgf")
    #g.make_move(simple_go.string_as_move("P18"))
    #print g.block_tactic_status(simple_go.string_as_move("O19"))
    print g.block_tactic_status(simple_go.string_as_move("Q18"))
    return
    for move in ("PASS", "P18", "P19", "O18"):
        print "="*60
        print "try move:", move
        g.make_move(simple_go.string_as_move(move))
        for block in ("O19", "Q19", "N17"):
            print g.block_tactic_status(simple_go.string_as_move(block))
        g.undo_move()
    
def test_danger(move_no=1000):
    #g = load_file_at_count("kgs/test_danger.sgf", 253+4)
    #g = load_file_at_count("kgs/test_danger.sgf", move_no+4)
    g = load_file_at_count("kgs/amni-SimpleBot.sgf", 352+8)
    node_count0 = g.node_count
    print g.current_board
    print g.str_current_position()
    print "total node_count:", g.node_count - node_count0
    #print g.generate_move()
    return g

def test_inside_dead():
    g = load_sgf.load_file("kgs/inside_dead.sgf")
    print g.current_board
    print g.str_current_position()
    print g.generate_move()
    print simple_go.move_list_as_string(g.final_status_list("dead"))
    print "="*60
    g.make_move(simple_go.string_as_move("S19"))
    print g.current_board
    print g.str_current_position()
    print g.generate_move()
    print simple_go.move_list_as_string(g.final_status_list("dead"))
    return g

def double_threat_fix():
    """if same move saves agaist both threats in double threat: not double threat"""
    g = load_sgf.load_file("kgs/double_threat_fix.sgf")
    print g.block_tactic_status(simple_go.string_as_move("G6"))

    print "="*60
    
    g.make_move(simple_go.string_as_move("H5"))
    g.make_move(simple_go.string_as_move("H6"))
    print g.block_tactic_status(simple_go.string_as_move("G6"))
    
def test_simple_life_and_death():
    config.lambda_node_limit = 100
    config.lambda_slow_node_limit = 100
    #g = load_sgf.load_file("kgs/first_ld_problems.sgf")
    g = load_sgf.load_file("kgs/first_ld_problems_mod.sgf")
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("F4"))
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("C4"))
    #print g.all_block_tactic_status(simple_go.string_as_move("B5"))
    
    #return
    print g.current_board
    print g.str_current_position()
    print g.make_move(g.generate_move())
    print g
    return
    
    #for move in ("PASS", "A6", "C5", "A7", "A8", "B6", "C9", "PASS", "B4", "PASS", "C4"):
    #    g.make_move(simple_go.string_as_move(move))
    #g.block_tactic_status(simple_go.string_as_move("B5"))
    
    print g.current_board.as_string_with_unconditional_status()
    #print g.current_board.find_eye_points()
    print g.block_life_and_death_status(simple_go.string_as_move("A2"))
    print "="*60
    print g.block_life_and_death_status(simple_go.string_as_move("H8"))
    print "="*60
    #print g.block_life_and_death_status(simple_go.string_as_move("H1"))
    print "="*60
    print g.block_life_and_death_status(simple_go.string_as_move("B8"))
    print "="*60
    print g.block_life_and_death_status(simple_go.string_as_move("B5"))

    #print g.str_current_position()
    #print g.block_life_and_death_status(simple_go.string_as_move("A2"))
    #print g.generate_move()

    g = load_file_at_count("kgs/simple_ld_problem.sgf")
    g = load_file_at_count("kgs/simple_ld_problem_unconditional.sgf")
    print g.current_board.as_string_with_unconditional_status()
    print g.block_life_and_death_status(simple_go.string_as_move("Q18"))
    

    g = load_sgf.load_file("kgs/second_ld_problems.sgf")
##    print "="*60
##    print g.block_tactic_status(simple_go.string_as_move("A3"))

##    print "="*60
##    print g.block_tactic_status(simple_go.string_as_move("E3"))

##    print "="*60
##    print g.block_tactic_status(simple_go.string_as_move("A6"))
    
    print g.current_board.as_string_with_unconditional_status()
    print "="*60
    print g.block_life_and_death_status(simple_go.string_as_move("A3"))

    print "="*60
    print g.block_life_and_death_status(simple_go.string_as_move("E3"))

    print "="*60
    print g.block_life_and_death_status(simple_go.string_as_move("A6"))

def solve_ld(file, pos):
    pos = simple_go.string_as_move(pos)
    g = load_sgf.load_file(file)
    #print g.current_board.as_string_with_unconditional_status()
    #print g.block_life_and_death_status(pos, reading_type="death")
    #print g.block_life_and_death_status(pos, reading_type="life")
    #print g.block_life_and_death_status(pos)
    #print g.block_capture_tactic_status(pos)
    #print g.block_tactic_status(pos)
    print g.all_block_tactic_status(pos)
    
def test_beginner_life_and_death():
    #solve_ld("kgs/first_ld_problems.sgf", "A2")
    #solve_ld("kgs/first_ld_problems.sgf", "H8")
    #solve_ld("kgs/first_ld_problems.sgf", "H1")
    #solve_ld("kgs/first_ld_problems.sgf", "B8")
    #solve_ld("kgs/first_ld_problems.sgf", "B5")
    #solve_ld("kgs/simple_ld_problem.sgf", "S19")
    #solve_ld("kgs/simple_ld_problem.sgf", "R17")
    #solve_ld("kgs/simple_ld_problem.sgf", "T15")
    #solve_ld("kgs/simple_ld_problem.sgf", "P14")
    #solve_ld("kgs/simple_ld_problem.sgf", "L12")
    #solve_ld("kgs/simple_ld_problem.sgf", "G16")
    #solve_ld("kgs/simple_ld_problem.sgf", "F19")
    #solve_ld("kgs/simple_ld_problem.sgf", "B17")
    #solve_ld("kgs/simple_ld_problem_unconditional.sgf", "Q18")
    #solve_ld("kgs/second_ld_problems.sgf", "A3")
    #solve_ld("kgs/second_ld_problems.sgf", "E3")
    #solve_ld("kgs/second_ld_problems.sgf", "A6")
    #solve_ld("kgs/beginner_ld2.sgf", "A7")
    #solve_ld("kgs/beginner_ld6.sgf", "A8")
    #solve_ld("kgs/beginner_ld6.sgf", "A2")
    #solve_ld("kgs/beginner_ld6_2.sgf", "A8")
    #solve_ld("kgs/beginner_ld6_2.sgf", "A2")
    #solve_ld("kgs/beginner_ld9.sgf", "B1")
    #solve_ld("kgs/beginner_ld9_2.sgf", "B1")
    #solve_ld("kgs/beginner_ld11.sgf", "E2")
    #solve_ld("kgs/tour2005-12-04_SimpleBot-CrazyStone_ld.sgf", "M7")
    #solve_ld("kgs/bienvenue-PyBot_ld_test1.sgf", "B2")
    #solve_ld("kgs/bienvenue-PyBot_ld_test2.sgf", "B4")
    solve_ld("kgs/Aloriless-SimpleBot_v0_3_0_test_ld.sgf", "C3")
    solve_ld("kgs/Aloriless-SimpleBot_v0_3_0_test_ld.sgf", "G2")
    solve_ld("kgs/Aloriless-SimpleBot_v0_3_0_test_ld.sgf", "F1")

def surround_ld_test():
    g = load_sgf.load_file("kgs/erislover-SimpleBot_2006-01-03_2_ld.sgf")
    g = load_sgf.load_file("kgs/surround_test.sgf")
    g = load_sgf.load_file("kgs/PyBot-mechacolo2_ld.sgf")
    g = load_sgf.load_file("kgs/bienvenue-PyBot_ld_test3.sgf")
    #print g.current_board.as_string_with_unconditional_status()
    #g.current_board.assumed_unconditional_alive_list = map(simple_go.string_as_move, ("B11", "B8", "A7", "A12", "D15"))
    #print g.current_board.as_string_with_unconditional_status()
    #g.make_move(simple_go.string_as_move("PASS"))
    #g.make_move(simple_go.string_as_move("C9"))
    #print g.current_board.as_string_with_unconditional_status()
    #return
    #for pos in ("B9", "B11", "B8", "A7", "A12"):
    config.lambda_node_limit = 100
    config.lambda_slow_node_limit = 3
    config.debug_tactics = False
    print g.current_board
    print g.str_current_position()
    #for pos in ("B9",):
    #    print "="*60
    #    print g.all_block_tactic_status(simple_go.string_as_move(pos))
    return g

def caching_bug():
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_3_0_test_bug.sgf")
    print g.undo_move()
    print g.generate_move()

def heuristical_dead_move_generation():
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_3_0_test_ld.sgf")
    g.make_move(simple_go.PASS_MOVE)
    g.make_move(simple_go.string_as_move("D6"))
    print g.current_board
    move = g.generate_move()
    print g.make_move(move)
    print g.make_move(simple_go.string_as_move("D1"))
    g.generate_move()
    return g

def heuristical_chain_dead_extension():
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_heuristical_chain_dead_extension.sgf")
    move = g.generate_move()
    return g

def caching_bug2():
    config.lambda_node_limit = 100
    config.lambda_slow_node_limit = 3
    config.debug_tactics = True
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_3_0_test5_cache.sgf")
    for i in range(5):
        print g.undo_move()

    print g.make_move(simple_go.string_as_move("R6"))
    print g.generate_move()
    
    print "="*60

    print g.make_move(simple_go.string_as_move("P5"))
    print g.make_move(simple_go.string_as_move("M6"))
    print g.generate_move()

    print "="*60
    
    print g.make_move(simple_go.string_as_move("S6"))
    print g.make_move(simple_go.string_as_move("R5"))
    print g.generate_move()

def heuristical_move():
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_3_0_test6_heuristic.sgf")
    print g.current_board
    print g.generate_move()

def critical_problem():
    g = load_sgf.load_file("kgs/SimpleBot-aradzi-2_critical_problem.sgf")
    print g.current_board
    print g.generate_move()
    
def capture_critical2heuristic():
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_3_0_test9_capture_critical2heuristic.sgf")
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_3_0_test9_capture_critical2heuristic-2.sgf")
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_v0_3_0_test9_capture_critical2heuristic-3.sgf")
    print g.current_board
    print g.generate_move()

def big_dead_and_big_one_eye():
##    g = load_sgf.load_file("kgs/big_dead_and_big_one_eye.sgf")
##    print g.current_board
##    config.lambda_node_limit = 100
##    config.lambda_slow_node_limit = 3
##    config.debug_tactics = True
##    stop()
##    print g.all_block_tactic_status(simple_go.string_as_move("A9"))
##    config.lambda_slow_node_limit = 100
##    print g.block_tactic_status(simple_go.string_as_move("A7"))

    g = load_sgf.load_file("kgs/big_dead_and_big_one_eye2.sgf")
    config.lambda_node_limit = 100
    config.lambda_slow_node_limit = 10000
    config.debug_tactics = True
    print g.block_tactic_status(simple_go.string_as_move("A9"))

def edge_and_middle_death():
##    g = load_sgf.load_file("kgs/broken_heuristic.sgf")
##    config.lambda_slow_node_limit = 100
##    config.debug_tactics = True
##    print g.heuristical_dead_analysis(simple_go.string_as_move("P15"))

    #g = load_sgf.load_file("kgs/small_surround_test.sgf")
    #g = load_sgf.load_file("kgs/small_surround_test2.sgf")

    #g = load_sgf.load_file("kgs/need_connection1.sgf")
    #print g.block_cut_status(simple_go.string_as_move_list("S16"), simple_go.string_as_move_list("T16 T17 T15"))
    #g = load_sgf.load_file("kgs/need_connection0.sgf")
    #g = load_sgf.load_file("kgs/need_connection.sgf")
    #print g.heuristical_dead_analysis(simple_go.string_as_move("B12"))

    g = load_sgf.load_file("kgs/SimpleBot-DL_connection.sgf")
    #print g.block_cut_status(simple_go.string_as_move_list("Q18"), simple_go.string_as_move_list("Q19 R19 P19 S19"))
    #print g.block_cut_status(simple_go.string_as_move_list("N17"), simple_go.string_as_move_list("N19 O19"))
    #print g.block_cut_status(simple_go.string_as_move_list("S16"), simple_go.string_as_move_list("T16 T17 T15"))
    
    print g.str_current_position()
    #print g.block_connection_status(simple_go.string_as_move("J2"), simple_go.string_as_move("L2"))
    #print g.block_connection_status(simple_go.string_as_move("S1"), simple_go.string_as_move("S4"))
    #print g.block_connection_status((simple_go.string_as_move("Q11"), simple_go.string_as_move("R12")))
    #g.current_shadow_origin = PASS_MOVE
    #g.make_move(simple_go.string_as_move("Q12"))
    #print g.block_connection_status((simple_go.string_as_move("Q11"), simple_go.string_as_move("R12")))
    #print g.block_connection_status((simple_go.string_as_move("L5"), simple_go.string_as_move("M4")))
    #print g.block_connection_status((simple_go.string_as_move("J4"), simple_go.string_as_move("M4")))
    #SimpleBot-DL.sgf -> SimpleBot-DL_connection.sgf
    #SimpleBot-sadtr.sgf -> SimpleBot-sadtr_connection.sgf
    
def chain_bug():
    g = load_sgf.load_file("kgs/SimpleBot-RubyDinner_bug.sgf")
    print g.current_board
    print g.generate_move()

def cache_color_bug():
    g = load_sgf.load_file("kgs/eyeful-SimpleBot-9x9_ha5_bug.sgf")
    moves2play = g.move_history[-26:]
    for i in range(26):
        g.undo_move()
    for i in range(0, len(moves2play), 2):
        print "<"*60
        print g.current_board
        g.generate_move()
        for move in moves2play[i:i+2]:
            print "move:", simple_go.move_as_string(move)
            print g.make_move(move)
        print ">"*60
    print "="*60
    print g.generate_move()

def why_capture_fail():
    g = load_sgf.load_file("kgs/why_capture_fail2.sgf")
    print g.generate_move()

def why_bad_shape():
    g = load_sgf.load_file("kgs/inferior_defense.sgf")
    print g.generate_move()

#Shape score: O1 0.0111111111111
#Shape score: O2 0.0694444444444
#Shape score: N2 1.0
#(O2, 9.56944444444) (N2, 1.0) (O1, 0.0111111111111)
#! (O1, 10.5111111111, tactically unknown, 287) (N2, 10.5, 110) (O2, 9.56944444444, tactically unknown, 305)

def key_error():
    g = simple_go.Game(19)
    g.make_move(sm("Q4"))
    g.make_move(sm("PASS"))
    g.make_move(sm("N4"))
    wait_move = False
    for line in open("error/key_error.log"):
        if wait_move:
            move = line.split()[1]
            g.make_move(sm(move))
            wait_move = False
        if line[:8]==">genmove":
            wait_move = True
        if line[:5]==">play":
            move = line.split()[2].upper()
            g.make_move(sm(move))

    print g.current_board
    print g.generate_move()


def death_failure():
    g = load_sgf.load_file("kgs/death_failure.sgf")
    print g.generate_move()
    #g.block_life_and_death_status(sm("N1"))
    
    
def time_usage_test():
    load_sgf.test_time_usage("kgs/time_usage_test.sgf", simple_go.BLACK)
    
def test_adjust():
    t = time_settings.Timekeeper()
    for i in range(20):
        t.statistics.add_data(10)
    config.time_per_move_limit = 5
    for i in range(15):
        print "ok: tpm limit " + str(config.time_per_move_limit) + " interval: " + str(t.statistics.confidence_interval(2)) + " config: " + str(config.lambda_node_limit) + " "  + str(config.capture_lambda1_factor_limit) + " " + str(config.min_capture_lambda1_nodes) + " " + str(config.lambda_slow_node_limit) + " " + str(config.lambda_connection_node_limit) + " " + str(config.other_lambda1_factor_limit) + " " + str(config.use_danger_increase) + " " + str(config.use_big_block_life_death_increase)
        print t._adjust_node_limit()

    config.time_per_move_limit = 15

    for i in range(15):
        print "ok: tpm limit " + str(config.time_per_move_limit) + " interval: " + str(t.statistics.confidence_interval(2)) + " config: " + str(config.lambda_node_limit) + " "  + str(config.capture_lambda1_factor_limit) + " " + str(config.min_capture_lambda1_nodes) + " " + str(config.lambda_slow_node_limit) + " " + str(config.lambda_connection_node_limit) + " " + str(config.other_lambda1_factor_limit) + " " + str(config.use_danger_increase) + " " + str(config.use_big_block_life_death_increase)
        print t._adjust_node_limit()
        #utils.stop()

def test_dead_pruning():
    #config.try_to_find_alive_move
    g = load_sgf.load_file("run_test/PyBot-IOS-time-loss.sgf")
    move_2, move_1 = g.move_history[-2:]
    g.undo_move()
    g.undo_move()
    g.generate_move()
    print "="*60
    g.make_move(move_2)
    g.make_move(move_1)
    g.generate_move()
    return g

def test_adjust2(time = 720, stones = 32):
    reload(config)
    config.manage_time = True
    t = time_settings.Timekeeper()
    #t.set_boardsize(9)
    t.set_boardsize(19)
    t.kgs_set_time(["absolute", 780])
    for i in range(5):
        time_left = 770 - i*10
        print i, time_left
        t.time_left(["black", time_left, 37-i])
    t.time_left(["black", time, stones])
    #0: 400 10 2000 8 40 2 True True True True True 4.84023159496
    #1: 200 10 2000 4 20 2 True True True True True 4.53982855838
    #2: 200 5 2000 4 20 1 True True True True True 4.24004977211
    #3: 100 5 2000 2 10 1 True True True True True 3.94151143263
    #4: 100 2 2000 2 10 1 True True True True True 3.59549622183
    #5: 100 2 2000 2 10 1 False True True True True 3.35410843915
    #6: 100 2 2000 2 10 1 False False True True True 3.33041377335
    #7: 100 2 2000 2 10 1 False False False True True 3.32551566336
    #8: 50 2 1000 1 5 1 False False False True True 3.04453976039
    #9: 25 1 1000 1 2 1 False False False True True 3.04336227802
    #10: 25 1 500 1 2 1 False False False True True 2.78175537465
    #11: 25 1 500 1 2 1 False False False False True 2.70329137812
    #12: 1 1 1 1 1 1 False False False False True 0.698970004336
    #13: 1 1 1 1 1 1 False False False False True 0.698970004336
    return t

def test_time_management():
    reload(config)
    config.manage_time = True
    t = time_settings.Timekeeper()
    t.set_boardsize(9)
    t.kgs_set_time(["absolute", 300])
    t.time_left(["black", 298, 0])
    t.time_left(["black", 298, 0])
    t.time_left(["black", 293, 0])
    t.time_left(["black", 288, 0])
    t.time_left(["black", 271, 0])
    t.time_left(["black", 271, 0])
    t.time_left(["black", 271, 0])
    t.time_left(["black", 270, 0])
    t.time_left(["black", 270, 0])
    t.time_left(["black", 270, 0])
    t.time_left(["black", 269, 0])
    t.time_left(["black", 269, 0])
    t.time_left(["black", 268, 0])
    t.time_left(["black", 268, 0])
    t.time_left(["black", 267, 0])
    t.time_left(["black", 262, 0])
    t.time_left(["black", 257, 0])
    t.time_left(["black", 251, 0])
    t.time_left(["black", 246, 0])
    t.time_left(["black", 241, 0])
    t.time_left(["black", 237, 0])
    t.time_left(["black", 206, 0])
    t.time_left(["black", 205, 0])
    t.time_left(["black", 205, 0])
    t.time_left(["black", 204, 0])
    t.time_left(["black", 204, 0])
    t.time_left(["black", 203, 0])
    t.time_left(["black", 203, 0])
    t.time_left(["black", 202, 0])
    t.time_left(["black", 202, 0])
    t.time_left(["black", 201, 0])
    t.time_left(["black", 197, 0])
    t.time_left(["black", 193, 0])
    t.time_left(["black", 185, 0])
    t.time_left(["black", 182, 0])
    t.time_left(["black", 182, 0])

def eye_score_test():
    #for origin in simple_go.string_as_move_list("C3 H2 B8 E7"):
    #    g = load_sgf.load_file("kgs/eye_score_test.sgf")
    #for origin in simple_go.string_as_move_list("M8"):
        #g = load_sgf.load_file("kgs/eye_score_test2.sgf")
    for origin in simple_go.string_as_move_list("C4"):
        g = load_sgf.load_file("kgs/nakade_point.sgf")
        print "-"*60
        print simple_go.move_as_string(origin)
        cboard = g.current_board
        origin_color = cboard.goban[origin]
        #if cboard.side!=origin_color:
        #    g.make_move(simple_go.PASS_MOVE)
        #print cboard
        while cboard.goban[origin]==origin_color:
            move_list = g.list_moves()
            for block in cboard.iterate_blocks(simple_go.WHITE+simple_go.BLACK):
                block.status = simple_go.UNCONDITIONAL_LIVE
            d = {}
            best_score = 0
            best_move = simple_go.PASS_MOVE
            for move in move_list:
                if move==simple_go.PASS_MOVE:
                    continue
                score = cboard.eye_score_move(move, origin)
                if score:
                    d[move] = score
                    if score > best_score:
                        best_score = score
                        best_move = move
            if best_move==simple_go.PASS_MOVE:
                break
            g.label_dict = d
            print g.make_move(best_move)
            #g.make_move(simple_go.PASS_MOVE)
            print " ", simple_go.move_as_string(best_move)
        #print cboard.as_sgf_with_labels(d)
        print g

def connection_scoring_test():
    g = load_sgf.load_file("kgs/connection_scoring.sgf")
    cboard = g.current_board
    for pair in ("Q4 Q6", "C8 C11", "C4 E4", "C14 C16", "L4 L6", "Q10 P11", "J15 K16", "P15 Q16", "C4 C8", "C11 C14", "O9 P11", "D16 E17"):
        print pair
        pos1, pos2 = simple_go.string_as_move_list(pair)
        print cboard.connection_score(pos1, pos2)
    return g

def connection_scoring2_test():
    g = load_sgf.load_file("kgs/connection_scoring2.sgf")
    cboard = g.current_board
##    for pair in ("Q4 Q6", "C11 C8", "C4 E4", "D16 C14", "L4 L6", "P11 Q10", "J15 K16", "P15 Q16", "C4 C8", "C11 C14", "P11 O9", "D16 E17"):
##        print pair
##        pos1, pos2 = simple_go.string_as_move_list(pair)
##        print cboard.connection_score_move(pos1, pos2)
    origin1 = sm("C8")
    origin2 = sm("C14")
    #origin1 = sm("R4")
    #origin2 = sm("Q6")
    d = {}
    best_move = simple_go.PASS_MOVE
    best_score = 1000.0
    for move in g.list_moves():
        print move_as_string(move)
        if move==simple_go.PASS_MOVE:
            continue
        score1 = cboard.connection_score_move(move, origin1)
        score2 = cboard.connection_score_move(move, origin2)
        score = score1 + score2
        if score < best_score:
            best_score = score
            best_move = move
        score = int(10*score)
        if score!=200:
            d[move] = score
    orignal_score = cboard.connection_score(origin1, origin2)
    print cboard.as_sgf_with_labels(d)
    print best_score, simple_go.move_as_string(best_move)
    print orignal_score
    return g

def statistics2tree(g, tree, position_statistics, final_status_positions):
    key = g.search_key()
    best_move = simple_go.PASS_MOVE
    best_score = None
    if key in final_status_positions:
        best_score, count = final_status_positions[key]
        if best_score==0:
            best_score = -1
        if g.current_board.side==simple_go.WHITE:
            best_score = -best_score
        best_score = count * best_score
        #print "?????", best_score
    if key not in position_statistics:
        return best_score, best_move
    stat = position_statistics[key]
    pos_score_sum = 0
    neg_score_sum = 0
    for move in stat:
        if g.make_move(move):
            stat2 = stat[move]
            tree.counts.append("%s %s" % (simple_go.move_as_string(move), tuple(stat2[:2])))
            node = game_search.SearchNode()
            node.move = move
            node.counts = ["%s" % (tuple(stat2[:2]),)]
            node.color = const.other_side[g.current_board.side]
            tree.children.append(node)
            score, move2 = statistics2tree(g, node, position_statistics, final_status_positions)
            node.counts[0] = node.counts[0] + " <" + simple_go.move_as_string(move2) + ":" + str(score) + ">"
            if score!=None:
                score = -score
                if score > 0:
                    pos_score_sum = pos_score_sum + score
                else:
                    neg_score_sum = neg_score_sum + score
                if len(stat2)==3:
                    stat2.append(score)
                else:
                    stat2[3] = score
                tree.counts[-1] = tree.counts[-1] + " " + str(score)
                if best_score==None or score > best_score:
                    best_score = score
                    best_move = move
            g.undo_move()
        else:
            utils.dprintnl("Could not make move", simple_go.move_as_string(move), "in statistics2tree")
    if best_score!=None:
        if best_score > 0:
            best_score = pos_score_sum
        else:
            best_score = neg_score_sum
    return best_score, best_move

def test_local_move_generation(only_one_move = True, file_name = "kgs/all_static_test2.sgf", move_list_string = "A15 C3 O1 R17 R11 K11", repeat_count = 1, play_count = 1, defense=True):
    config.debug_flag = only_one_move
    if repeat_count > 1:
        config.debug_flag = False
    if move_list_string:
        move_list = simple_go.string_as_move_list(move_list_string)
    else:
        move_list = []
        g = load_sgf.load_file(file_name)
        for block in g.current_board.iterate_blocks(simple_go.BLACK+simple_go.WHITE):
            move_list.append(block.get_origin())
    config.debug_output = Logger()
    for origin in move_list:
        total_stat = [0, 0]
        total_nodes = 0
        move_stat = {}
        play_t0 = time.time()
        position_statistics = {}
        final_status_positions = {}
        random_state = random.getstate()
        random.seed(1)
        g = load_sgf.load_file(file_name)
        origin_color = g.current_board.goban[origin]
        if defense:
            pass_needed = g.current_board.side != origin_color
        else:
            pass_needed = g.current_board.side == origin_color
        if pass_needed:
            g.make_move(simple_go.PASS_MOVE)
        initial_move_count = len(g.move_history)
        random.setstate(random_state)
        origin_str = simple_go.move_as_string(origin)
        dprintnl(origin_str)
        dprintnl(g.current_board)
        for i in range(play_count):
            while len(g.move_history) > initial_move_count:
                g.undo_move()
            first_move = None

            #update statistics
            tree = game_search.SearchNode()
            tree.counts = total_stat[:]
            best_score, best_move = statistics2tree(g, tree, position_statistics, final_status_positions)
            dprintnl("Total stat:", tree.counts, simple_go.move_as_string(best_move), best_score)
            dprintnl("="*60)

            t0_start = time.time()
            positions_seen = {}
            #g.generate_local_move(origin)
            while True:
                t0 = time.time()
                for j in range(repeat_count):
                    move = g.generate_local_move(origin, position_statistics)
                t1 = time.time()
                key_after_move = None
                positions_seen[g.search_key()] = move
                if not first_move:
                    first_move = simple_go.move_as_string(move)
                if move==simple_go.PASS_MOVE:
                    if g.current_board.side==origin_color:
                        dprintnl(first_move, "Dies with PASS")
                        status = 0
                    else:
                        dprintnl(first_move, "Lives with PASS")
                        status = 1
                    break
                dprintnl(" %i: %s %.3fs %s" % (len(g.move_history) - initial_move_count,
                                             simple_go.move_as_string(move), t1-t0,
                                             g.search_dict[PASS_MOVE][1]))
                result = g.make_move(move)
                if result:
                    key_after_move = g.search_key()
                total_nodes = total_nodes + 1
                live_status = g.current_board.block_unconditional_status(origin)
                if not result or g.current_board.goban[origin]==simple_go.EMPTY or live_status:
                    if live_status:
                        dprintnl(first_move, "Lives")
                        status = 1
                    else:
                        dprintnl(first_move, "Dies")
                        status = 0
                    break
                if config.debug_flag:
                    dprintnl("-"*60)
                if only_one_move:
                    break
            #store result to final position, increase counts if seen more than once
            key = g.search_key()
            lst = final_status_positions.get(key, [status, 0])
            lst[1] = lst[1] + 1
            final_status_positions[key] = lst
            
            t1_end = time.time()
            dprintnl("%i: Total time: %.3fs" % (i+1, t1_end-t0_start))

            total_stat[status] = total_stat[status] + 1
            
            counts = move_stat.get(first_move, [0, 0])
            counts[status] = counts[status] + 1
            move_stat[first_move] = counts
            #dprintsp("Total stat:", total_stat)
            #for move in move_stat:
            #    dprintsp(move, move_stat[move], " ")
            #dprintnl()

            for key, move in positions_seen.items():
                stat = position_statistics.get(key, {})
                stat_this_move = stat.get(move, [0, 0, key_after_move])
                stat_this_move[status] = stat_this_move[status] + 1
                stat[move] = stat_this_move
                position_statistics[key] = stat
            
            if i==play_count-1:
                fp = open("tmp%s.sgf" % origin_str, "w")
                fp.write(str(g))
                fp.close()
            #print g

        play_t1 = time.time()
        dprintnl("Total play time: %.3fs, nodes: %i" % (play_t1 - play_t0, total_nodes))

        random.seed(1)
        g = load_sgf.load_file(file_name)
        origin_color = g.current_board.goban[origin]
        if pass_needed:
            g.make_move(simple_go.PASS_MOVE)
        tree = game_search.SearchNode()
        tree.counts = total_stat
        best_score, best_move = statistics2tree(g, tree, position_statistics, final_status_positions)
        dprintnl("Total stat:", tree.counts, simple_go.move_as_string(best_move), best_score)
        #print final_status_positions
        fp = open("tmpTree.sgf", "w")
        fp.write(g.tree2sgf(tree))
        fp.close()
        
        #R17 with 100 iterations:
        #Run 1         : S18 [0, 4]   T17 [1, 17]   T18 [36, 42]
        #Run 2  80.683s: S18 [0, 4]   T17 [1, 16]   T18 [30, 49]
        #Run 3 110.644s: S18 [0, 4]   T17 [1, 14]   T18 [29, 52]
        #Run 4  83.255s:              T17 [1, 18]   T18 [35, 46]
        #Run 5 71.441s:               T17 [0, 18]   T18 [38, 44]

        #Learning:
        #Run 6 172.736s, nodes: 2829, T17 [15, 84]   T18 [0, 1]  

        #O1 with 100 iterations:
        #Run 1 522.722s: L6 [2, 0]   L7 [25, 0]   M7 [1, 0]   K6 [20, 0]   K5 [1, 0]   O6 [1, 0]   O5 [9, 40]   N5 [1, 0]

        #A15 with 100 iterations:
        #Run 1 56.021s, nodes: 1352   B17 [6, 94]

        #kgs/simple_ld3.sgf Q13
        #Run 1 with 100 iterations: 39.786s, nodes: 744   S13 [5, 0]   T14 [11, 0]   T15 [13, 20]   T16 [9, 0]   T10 [8, 0]   T11 [16, 7]   T12 [10, 1]
        #Run 2 with 1000 iterations: 149.236s, nodes: 4524  S13 [5, 0]   T14 [11, 0]   T15 [13, 920]   T16 [9, 0]   T10 [8, 0]   T11 [16, 7]   T12 [10, 1]
        #        T15 Dies with PASS
        #        96: Total time: 0.106s
        #        S13 [5, 0]   T14 [11, 0]   T15 [13, 16]   T16 [9, 0]   T10 [8, 0]   T11 [16, 7]   T12 [10, 1]

        #crazy_stone_ld_local_read_attack.sgf R7
        #Run 1 with 100 iteratiosn: 332.275s, nodes: 4149  All [61, 39]   R5  [2, 2]   R6 [2, 0]   S8 [23, 16]   Q5 [1, 0]   P5 [1, 0]   T6 [1, 0]   T5 [3, 0]   S6 [2, 1]   S5 [23, 19]   O5 [3, 1]
        
        #crazy_stone_ld_local_read_attack2.sgf R7
        #Run 1 with 100 iterations: 212.930s, nodes: 2609 All [45, 55]   N9 [7, 6]   T5 [11, 11]   S5 [27, 38]

        #beginner_ld10.sgf J4
        #Run 1 with 100 iterations: 105.724s, nodes: 2811  Total stat: [63, 37] M5 [4, 2]   J6 [1, 0]   H1 [3, 1]   J1 [3, 0]   J2 [2, 0]   H5 [9, 8]   L6 [18, 15]   L7 [7, 4]   L5 [1, 0]   M1 [1, 1]   L3 [0, 2]   K5 [3, 1]   M2 [1, 0]   O5 [3, 1]   N5 [4, 1]   N6 [3, 1]
        #Run 2 with 10000 iterations: 15184.682s, nodes: 385350  Total stat: [5716, 4284] M5 [2860, 2770]   J6 [143, 54]   H1 [157, 68]   J1 [275, 184]   J2 [312, 222]   H5 [193, 104]   L6 [154, 64]   L7 [379, 289]   L5 [162, 73]   M1 [99, 11]   L3 [98, 10]   K5 [147, 57]   M2 [155, 67]   O5 [188, 97]   N5 [172, 82]   N6 [222, 132]   
    return g

def test_simple_unconditional():
    g = load_sgf.load_file("kgs/unconditional_local_read_test.sgf")
    print g.current_board
    for origin in simple_go.string_as_move_list("A2 G6 R18 T19 M11 G1 A12 S2 R1 S7 T11 F18 A5 A8 N4 O6"):
        print "="*60
        print simple_go.move_as_string(origin)
        print g.current_board.block_unconditional_status(origin)

def test_playout_movegen(file_name = "kgs/play_out_test.sgf"):
    g = load_sgf.load_file(file_name)
    print g.current_board
    print g.generate_move()
    print "="*60
    print g.generate_move()
    return g

def play_game(adjust_count, count, size):
    import play_gtp
    total_move_count = 0
    total_time = 0.0
    prefix = "game%i_%ix%i_" % (adjust_count, size, size)
    for i in range(count):
        config.debug_output = play_gtp.Logger(prefix + "%04i.log")
        t0 = time.time()
        g = simple_go.Game(size)
        while not g.has_2_passes():
            move = g.generate_move()
            g.make_move(move)
        t1 = time.time()
        time_now = t1-t0
        total_time = total_time + time_now
        move_count = len(g.move_history)
        total_move_count = total_move_count + move_count
        n = i + 1
        s = "%i: now: %.3fs/game %.6fs/move %i moves  total: %.3fs %.3fs/game %.6fs/move %i moves" % (n,
            time_now, time_now / move_count, move_count,
            total_time, total_time / n, total_time / total_move_count, total_move_count)
        utils.dprintnl(s)
        print s
        sgf_name = play_gtp.get_next_filename(prefix + "%04i.sgf")
        fp = open(sgf_name, "w")
        fp.write(str(g))
        fp.close()
    return total_time / total_move_count

def play_all_adjusts(size):
    import play_gtp
    t = time_settings.Timekeeper()
    fp = open("%i_timing.txt" % size, "w")
    for i in range(t.different_adjust_levels):
        s = t._config_as_string()
        utils.dprintnl(s)
        print s
        result = play_game(i, 1, size)
        fp.write("%.6f\n" % result)
        t._do_adjust(False)
    fp.close()
        
def play_all_sizes():
    import play_gtp
    #for size in (2, 3, 5):
    for size in (9, 13, 19):
        utils.dprintnl("size:", size)
        print "size:", size
        reload(config)
        play_all_adjusts(size)
        
def show_all_adjusts():
    t = time_settings.Timekeeper()
    t.set_boardsize(13)
    t.timing_data = {}
    print t._config_as_string(), t.adjustments_made
    s_lst = [[], []]
    for undo in (False, True):
        for i in range(t.different_adjust_levels):
            print "-"*60
            t._do_adjust(undo)
            s = t._config_as_string()
            print s, t.adjustments_made
            s_lst[undo].append(s)
    s_lst[0].reverse()
    print "="*60
    for i in range(len(s_lst)):
        if s_lst[0][i] != s_lst[1][i]:
            print i, ":"
            print s_lst[0][i]
            print s_lst[1][i]
            print "-"*60

def test_block_in_file(file, count, pos):
    g = load_file_at_count(file, count)

    print file, count, pos
    node_count0 = g.node_count
    result = g.block_capture_tactic_status(simple_go.string_as_move(pos, g.size))
    print result, "node_count", g.node_count-node_count0
    print "="*60
    return result

def test_attack_move(file, count, pos, move):
    mode, attack, defend = test_block_in_file(file, count, pos)
    #if mode==simple_go.TACTICALLY_CRITICAL:
    if mode==simple_go.TACTICALLY_DEAD:
        if simple_go.move_as_string(attack)==move:
            return True
    return False

def elementary_test():
    problems = [(1, "L10", "K10"),
                (2, "H11", "H13"),
                (3, "M12", "M13"),
                (4, "K11", "J11"),
                (5, "K11", "J12"),
                (6, "H11", "K13"),
                (7, "F11", "H13"),
                (8, "G10", "G12"),
                (9, "G10", "F10"),
                (10, "J10", "H11"),
                (11, "L11", "M13"),
                (12, "H10", "H12"),
                (13, "J11", "K10"),
                (14, "H11", "H10"),
                (15, "H10", "J12"),
                (16, "H10", "G9"),
                (17, "K11", "M12"),
                (18, "K10", "L13"),
                (19, "K9", "H9"),
                (20, "K11", "J12"),
                (21, "G12", "J12"),
                (22, "H12", "H13"),
                (23, "J9", "G11"),
                (24, "G12", "M13"),
                (25, "J11", "M13"),
                (26, "J12", "G13"),
                (27, "J8", "J10"),
                (28, "G11", "J13"),
                (29, "J11", "J13"),
                (30, "L11", "N12"),
                ]
    ok_count = 0
    total_count = 0
    t0 = time.time()
    for no, pos, solution in problems: #(problems[-1],):
        file_name = "kgs/elementary_tesuji_%i.sgf" % no
        result = test_attack_move(file_name, 10000, pos, solution)
        total_count = total_count + 1
        if result:
            ok_count = ok_count + 1
        t = time.time() - t0
        print "So far:", ok_count, total_count, 100.0*ok_count/total_count, t / 60.0
        

def test_playout_alpha_beta(file_name = "kgs/all_static_test2.sgf", move_list_string = "A15 C3 O1 R17 R11 K11", defense=True):
    if move_list_string:
        move_list = simple_go.string_as_move_list(move_list_string)
    else:
        move_list = []
        g = load_sgf.load_file(file_name)
        for block in g.current_board.iterate_blocks(simple_go.BLACK+simple_go.WHITE):
            move_list.append(block.get_origin())
    config.debug_output = Logger()
    for origin in move_list:
        total_nodes = 0
        play_t0 = time.time()
        #random_state = random.getstate()
        random.seed(1)
        g = load_sgf.load_file(file_name)
        origin_color = g.current_board.goban[origin]
        if defense:
            pass_needed = g.current_board.side != origin_color
        else:
            pass_needed = g.current_board.side == origin_color
        if pass_needed:
            g.make_move(simple_go.PASS_MOVE)
        initial_move_count = len(g.move_history)
        #random.setstate(random_state)
        origin_str = simple_go.move_as_string(origin)
        dprintnl(origin_str)
        dprintnl(g.current_board)
        nodes0 = g.node_count
        status = g.alpha_beta_block_playout(origin, {}, not defense)
        print status[0], status[1], utils.move_list_as_string(status[2])
##        status, moves = g.alpha_beta_block_playout(origin, {})
##        print status, moves[:2]
##        no = 0
##        for result, move_list in moves[2]:
##            print no, result, utils.move_list_as_string(move_list)
##            for move in move_list:
##                g.make_move(move)
##            fp = open("out/%s_%i.sgf" % (origin_str, no), "w")
##            fp.write(str(g))
##            fp.close()
##            while len(g.move_history) > initial_move_count:
##                g.undo_move()
##            no = no + 1
        total_nodes = total_nodes + g.node_count - nodes0
        play_t1 = time.time()
        dprintnl("Total play time: %.3fs, nodes: %i" % (play_t1 - play_t0, total_nodes))

def test_b3_both():
    print '>>> test_playout_alpha_beta("kgs/minue622-long20_local_read.sgf", "B3")'
    test_playout_alpha_beta("kgs/minue622-long20_local_read.sgf", "B3")
    print ">>>"
    print '>>> test_playout_alpha_beta("kgs/minue622-long20_local_read.sgf", "B3", defense=False)'
    test_playout_alpha_beta("kgs/minue622-long20_local_read.sgf", "B3", defense=False)
    
