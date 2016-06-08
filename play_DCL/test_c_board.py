import time
import c_board
from simple_go import *
import load_sgf
from pprint import pprint
import math

CEMPTY = 0
CWHITE = 1
CBLACK = 2

color2ccolor = {BLACK: CBLACK, WHITE: CWHITE, EMPTY: CEMPTY}

class CGame(Game):
    def __init__(self, size):
        c_board.clear_board(size)
        Game.__init__(self, size)

    def c_color(self):
        return color2ccolor[self.current_board.side]
    
##    def make_move(self, move):
##        color = self.c_color()
##        res = Game.make_move(self, move)
##        if res:
##            c_board.make_move(move, color)
##        return res
            
##    def undo_move(self):
##        if self.move_history:
##            move = self.move_history[-1]
##            if move!=PASS_MOVE:
##                c_board.undo_move()
##        return Game.undo_move(self)

    def monte_carlo_local_moves(self, pos, count, local_moves = True):
        cb = self.current_board
        old_debug = config.debug_flag
        config.debug_flag = False
        if local_moves:
            move_score_list = self.generate_local_move(pos, {},
                                                       use_random = False, return_all_moves = True)
        else:
            move_score_list = []
            for move in self.iterate_moves():
                move_score_list.append((0, move))
        config.debug_flag = old_debug
        if cb.side==cb.goban[pos]:
            def calc_score(pos=pos, count=count, cb=cb):
                return 2 * c_board.test_block(pos, color2ccolor[cb.side], count) - count
        else:
            def calc_score(pos=pos, count=count, cb=cb):
                return count - 2 * c_board.test_block(pos, color2ccolor[cb.side], count)
        best_score = calc_score()
        best_move = PASS_MOVE
        print move_as_string(best_move), best_score
        for local_score, move in move_score_list:
            if self.make_move(move):
                score = calc_score()
                print move_as_string(move), score, local_score,
                if score > best_score:
                    print "new"
                    best_move = move
                    best_score = score
                else:
                    print
                self.undo_move()
        return best_score, best_move

    def select_random_move(self):
        """return randomly selected move from all legal moves
        """
        moves = self.list_moves()
        return moves[c_board.rand()%len(moves)]

def test_n(n):
    #on empty 9x9 board tengen:
    #moves, time, moves/s
    #10000000 1.12345790863 8901090.03923
    #100000000 13.0292351246 7675047.61744

    #make move in first empty position
    #games, time, games/s (each 200 moves + 200 undo)
    #10000 1.0918431282 9158.82487299
    #100000 20.221198082 4945.30539658

    #random moves, no checking for new available empty positions
    #games, time, games/s, moves, moves/s
    #100000 4.22188186646 23686.1198781 8515668 2017031.3309

    #random moves, after capture do init_available();
    #games, time, games/s, moves, moves/s
    #100000 8.87007284164 11273.8645765 12873983 1451395.40902

    #random moves, do init_available() at every move + captures
    #games, time, games/s, moves, moves/s
    #100000 15.042181015 6647.97211921 13141933 873672.041766

    #random moves, pass move also option at frequency of 1/'estimate of available moves' , after capture do init_available();
    #games, time, games/s, moves, moves/s
    #10000 0.666018009186 15014.6090077 1122653 1685619.58463
    #100000 7.72982311249 12936.9066465 11184983 1446990.80913


    t0 = time.time()
    #c_board.test(4, 4, n)
    moves = c_board.test_game(n)
    t1 = time.time()
    t = t1-t0
    if t==0.0:
        t = 1E-300
    print n, t, n/t, moves, moves/t

def test_all_moves(n):
    res = []
    for i in range(1, 5+1):
        for j in range(1, 5+1):
            if i <= j:
                move = i, j
                c_board.make_move(move, CBLACK)
                count = c_board.test_game(n)
                print move, count
                res.append((count, move_as_string(move)))
                c_board.undo_move()
    res.sort()
    pprint(res)
    

def test_all_moves2(n):
    res = []
    for i in range(1, 9+1):
        for j in range(1, 9+1):
            move = i, j
            c_board.make_move(move, CBLACK)
            count = c_board.test_game(n)
            print move, count
            res.append((count, move_as_string(move)))
            c_board.undo_move()
    count = c_board.test_game(n)
    print PASS_MOVE, count
    res.append((count, move_as_string(PASS_MOVE)))
    res.sort()
    pprint(res)
    
def test_all_moves3(n):
    t0 = time.time()
    res = []
    g = Game(9)
    for m1 in g.iterate_moves():
        g.make_move(m1)
        c_board.make_move(m1, CBLACK)
        for m2 in g.iterate_moves():
            g.make_move(m2)
            c_board.make_move(m2, CBLACK)
            count = c_board.test_game(n)
            moves = move_list_as_string([m1, m2])
            res.append((count, moves))
            print len(res), moves, count
            if m2!=PASS_MOVE:
                c_board.undo_move()
            g.undo_move()
        if m2!=PASS_MOVE:
            c_board.undo_move()
        g.undo_move()
    res.sort()
    pprint(res)
    t1 = time.time()
    print t1-t0

def compare_results(all_results):
    for i in range(len(all_results[0])):
        print i,
        for j in range(len(all_results)):
            results = all_results[j]
            count, moves = results[i]
            if i:
                prev_count = all_results[j][i-1][0]
            else:
                prev_count = count
            norm_moves = move_list_as_string(normalize_moves(string_as_move_list(moves), 9))
            add = count - prev_count
            print (count, add, moves, norm_moves),
        print

def normalize_moves(moves, size):
    best_moves = None
    for ref in all_ref_coords:
        moves2 = []
        for m in moves:
            if m==PASS_MOVE:
                moves2.append(m)
            else:
                moves2.append(ref(m, size))
        moves2.sort()
        if best_moves==None or moves2 < best_moves:
            best_moves = moves2
    return tuple(best_moves)

def test_all_moves4(n, size=9):
    t0 = time.time()
    res = []
    seen_patterns = {}
    g = CGame(size)
    for m1 in g.iterate_moves():
        g.make_move(m1)
        g.make_move(PASS_MOVE)
        for m2 in g.iterate_moves():
            moves_tuple = normalize_moves([m1, m2], size)
            if moves_tuple not in seen_patterns:
                seen_patterns[moves_tuple] = True
                g.make_move(m2)
                count = c_board.test_game(n)
                moves = move_list_as_string(moves_tuple)
                res.append((count, moves))
                print len(res), moves, count
                g.undo_move()
        g.undo_move()
        g.undo_move()
    res.sort()
    pprint(res)
    t1 = time.time()
    print t1-t0

def test_block_capture(name, pos_str, n):
    pos = string_as_move(pos_str)
    g = load_sgf.load_file(name, game_class = CGame)
    print g.current_board
    print pos_str, n
    t0 = time.time()
    res1 = c_board.test_block(pos, CWHITE, n)
    print "White:", res1
    res2 = c_board.test_block(pos, CBLACK, n)
    print "Black:", res2
    print "Diff:", res2-res1
    t1 = time.time()
    print "Time:", t1-t0
    
def test_block_capture_local_moves(name, pos_str, n, local_moves = True):
    t0_all = time.time()
    pos = string_as_move(pos_str)
    g = load_sgf.load_file(name, game_class = CGame)
    block_color = g.current_board.goban[pos]
    if g.current_board.side==block_color:
        g.make_move(PASS_MOVE)
    pass_count = 0
    while pass_count < 2:
        print g.current_board
        print pos_str, n
        t0 = time.time()
        score, move = g.monte_carlo_local_moves(pos, n, local_moves)
        t1 = time.time()
        if pass_count==0:
            print "Attack",
        else:
            print "Defend",
        print "result:", move_as_string(move), score
        print "Time:", t1-t0
        g.make_move(PASS_MOVE)
        pass_count = pass_count + 1
    t1_all = time.time()
    print "Total time:", t1_all-t0_all

def play_random_game(seed=0, size=9):
    g = CGame(size)
    c_board.set_random_seed(seed)
    while not g.has_2_passes():
        move = g.select_random_move()
        g.make_move(move)
    print g
    print g.current_board

def test_ladder(n, name = "kgs/simple_ladders2.sgf"):
    for pos_str, moves_string in (("C3", "D3 C4 C5 D4 E4 D5 D6 E5 F5 E6 E7 F6 G6 F7 F8 G7 H7 G8 H8 G9 F9 H9 J9"),
                              ("G3", "F3 G4 G5 F4 E4 F5 F6 E5 D5 E6 E7 D6 C6 D7 D8 C7 PASS")):
        print "="*60
        g = load_sgf.load_file(name, game_class = CGame)
        pos = string_as_move(pos_str)
        block_color = g.current_board.goban[pos]
        if g.current_board.side==block_color:
            g.make_move(PASS_MOVE)

        for move in string_as_move_list(moves_string):
            color = g.current_board.side
            print g.current_board
            score, move2 = g.monte_carlo_local_moves(pos, n)
            g.make_move(move)
            print color, move_as_string(move), score, move_as_string(move2)
            print "-"*60

def test_c_ladder_alpha_beta(name = "kgs/simple_ladders2.sgf", pos_str = "C3", depth = 1, seed = 1, undo_count = 0, limit = 0, print_pos = True):
    c_board.set_random_seed(seed)
    g = load_sgf.load_file(name, game_class = CGame)
    undo_count0 = undo_count
    while undo_count:
        g.undo_move()
        undo_count = undo_count - 1
    pos = string_as_move(pos_str)
    block_color = g.current_board.goban[pos]
    if g.current_board.side==block_color:
        g.make_move(PASS_MOVE)
    if print_pos:
        print g.current_board
        print pos_str
    #g.probabilistic_alpha_beta(string_as_move(pos), 80)
    nodes0 = c_board.get_trymove_counter()
    t0 = time.time()
    score = c_board.alpha_beta_search_random(pos, g.c_color(), depth, -2, 2, limit)
    t1 = time.time()
    nodes1 = c_board.get_trymove_counter()
    moves = []
    t_used = t1-t0
    t_used = round(t_used, int(-math.log10(t_used) + 2))
    nodes_s = (nodes1-nodes0)/(t1-t0)
    if nodes_s >= 1000000:
        nodes_s = "%sM" % round(nodes_s/1000000., 1)
    else:
        nodes_s = "%sK" % round(nodes_s/1000.)
        if nodes_s >= 10000:
            nodes_s = nodes_s.replace(".0", "")
    limit_s = str(limit/1000000.)
    limit_s = limit_s.replace(".0", "")
    s = "%-6s %-4s %-5s %-6s %-9s %-7s %s" % (limit_s, undo_count0, depth, score, nodes1-nodes0, t_used, nodes_s)
    print s
    return s, score

def test_show():
    g = CGame(8)
    g.make_move((2,1))
    print g.make_move((7,2))
    c_board.simple_showboard()
    
def test_ab(limit, seed=1, depth=7, undo_count=7):
    limit = int(limit * 1000000)
    return test_c_ladder_alpha_beta(name = "kgs/simple_ladder_full.sgf", pos_str = "C3", depth = depth, seed = seed, undo_count = undo_count, limit = limit, print_pos = False)

def test_ab2(limit, seed=1, undo_count=23, start=1):
    for depth in range(start, 100+1):
        test_ab(limit, seed, depth, undo_count)

def test_ab3(limit, count, depth, undo_count=23):
    t0 = time.time()
    nodes0 = c_board.get_trymove_counter()
    score_d = {}
    for seed in range(1, count+1):
        s, score = test_ab(limit, seed, depth, undo_count)
        score_d[score] = score_d.get(score, 0) + 1
        t1 = time.time()
        nodes1 = c_board.get_trymove_counter()
        print seed, score_d, t1-t0, float(nodes1-nodes0)/seed
    t1 = time.time()
    print score_d, t1-t0, float(nodes1-nodes0)/count
    
def test_uct(count=1, g=None):
    if not g:
        g = CGame(9)
    c_board.uct_game(g.c_color(), count)

def test_uct(count=1, g=None, pos=None):
    if not g:
        g = CGame(9)
    if pos:
        c_board.uct_capture(string_as_move(pos), g.c_color(), count)
    else:
        c_board.uct_game(g.c_color(), count)

def recursive_show_result_tree(g, swap):
    result = c_board.get_result_table(g.c_color())
    if result:
        if swap:
            result = result[1], result[0]
        movel_s = move_list_as_string(g.move_history)
        if g.move_history:
            move_s = move_as_string(g.move_history[-1])
        else:
            move_s = ""
        print " "*(len(movel_s) - len(move_s)), move_s, result
        for move in g.list_moves():
            g.make_move(move)
            recursive_show_result_tree(g, not swap)
            g.undo_move()

def show_result_tree():
    g = CGame(9)
    recursive_show_result_tree(g, False)

def recursive_show_main_line(g, swap):
    result = c_board.get_result_table(g.c_color())
    if result:
        if swap:
            result = result[1], result[0]
        movel_s = move_list_as_string(g.move_history)
        if g.move_history:
            move_s = move_as_string(g.move_history[-1])
        else:
            move_s = ""
        print " "*(len(movel_s) - len(move_s)), move_s, result
        for move in g.list_moves():
            g.make_move(move)
            recursive_show_main_line(g, not swap)
            g.undo_move()

def result2score(result):
    return result[0] / float(sum(result))

def show_main_line(g = None):
    if not g:
        g = CGame(9)
    start_len = len(g.move_history)
    swap = False
    while True:
        result = c_board.get_result_table(g.c_color())
        if not result:
            break
        if swap:
            result = result[1], result[0]
        print result, result2score(result), #score from root viewpoint
        swap = not swap
        best_score = -1000
        best_move = PASS_MOVE
        for move in g.list_moves():
            g.make_move(move)
            result = c_board.get_result_table(g.c_color())
            if result:
                result = result[1], result[0]
                score = result2score(result) #score from side to move viewpoint
                if score > best_score:
                    best_score = score
                    best_move = move
                #if len(g.move_history)==2:
                #    print "?", score, result, move_as_string(move)
            g.undo_move()
        if best_move==PASS_MOVE:
            break
        g.make_move(best_move)
        print "|", move_as_string(best_move),
    print
    while start_len < len(g.move_history):
        g.undo_move()
    move_results = []
    result0 = c_board.get_result_table(g.c_color())
    for move in g.list_moves():
        g.make_move(move)
        result = c_board.get_result_table(g.c_color())
        if result:
            result = result[1], result[0]
            score = result2score(result)
            if result0:
                score2 = uct_score(result0, result)
            else:
                score2 = 0.0
            move_results.append((score, result, score2, move))
        g.undo_move()
    move_results.sort()
    move_results.reverse()
    i = 0
    for  score, result, score2, move in move_results:
        i += 1
        ms = move_as_string(move)
        if 1: #i<=5: # or ms=="C5":
            print i, "%.6f %.6f" % (score, score2), result, ms
    while start_len < len(g.move_history):
        g.undo_move()
    if move_results:
        return move_results[0][2]
    return PASS_MOVE

def uct_score(result1, result2):
    t = float(sum(result1))
    n = float(sum(result2))
    v = result2[0] / n
    return v + math.sqrt((2*math.log(t))/(10*n))

t = test_uct
t2 = show_result_tree
t3 = show_main_line

def uct_search(count, g, pos=None):
    t0 = time.time()
    test_uct(count, g, pos)
    t1 = time.time()
    move = show_main_line(g)
    print sum(c_board.get_result_table(g.c_color())), t1-t0, count/(t1-t0)
##    if g.make_move(PASS_MOVE):
##        print "-"*60
##        show_main_line(g)
##        g.undo_move()
##    if g.make_move(string_as_move("D5")):
##        print "-"*60
##        show_main_line(g)
##        g.undo_move()
##    if g.make_move(string_as_move("D4")):
##        print "-"*60
##        show_main_line(g)
##        g.undo_move()
    return move

def o(): print g.make_move(uct_search(10000, g))

def test_pattern():
    c_board.set_random_seed(1)
    g = load_sgf.load_file("kgs/simple_ladder_full.sgf", game_class = CGame)
    for i in range(21):
        g.undo_move()
    print g.current_board
    #c_board.add_pattern_result_table(string_as_move("C5"), CBLACK, 3, 1)
    uct_search(1, g)
    print c_board.dump_pattern_result_table("patterns.dat")
##    s = "B:B9 W:E2 B:J7 W:B8 B:E5 W:G7 B:D8 W:A1 B:D2 W:A8 B:G6 W:G2 B:D4 W:B1 B:D6 W:J5 B:B2 W:D1 B:J6 W:H6 B:F3 W:C1 B:H3 W:E4 B:F6 W:G9 B:E3 W:G3 B:G4 W:D9 B:H8 W:F7 B:A5 W:A3 B:A9 W:F8 B:J4 W:E9 B:H7 W:B5 B:D7 W:E6 B:H9 W:C6 B:J9 W:B6 B:H2 W:H1 B:E8 W:J3 B:E7 W:A2 B:G5 W:H5 B:J1 W:C8 B:J2 W:F2 B:A6 W:F4 B:G8 W:F1 B:G1 W:C9 B:H4 W:C7 B:B7 W:J5 B:A4 W:C5 B:D5 W:A9 B:F5 W:F9 B:E4 W:H1 B:A7 W:H5 B:E1 W:B1 B:A2 W:A1 B:D1 B:H6 W:J5 B:C1 W:A1 B:B1 B:G1 W:E2 B:F1 W:G2 B:H5 W:G3 B:F2 W:G2 B:B9 W:A8 B:F9 W:C9 B:F8 W:G7 B:F7 W:C7 B:C8 W:B5 B:G3 W:C5 B:C3 W:D9 B:C4 W:A9 B:B8 W:A9 B:B6 B:A8 B:C6 W:C5 B:B5 B:E9 W:C9 B:D9"
##    for m in s.split():
##        m = string_as_move(m.split(":")[1])
##        if not g.make_move(m):
##            print "illegal move:", move_as_string(m)
##            break
##    print g.current_board
    return g

def decode_pattern_key(key):
    color = (key & 1) + 1
    piece = (key>>1) & 3
    liberties = (key>>3) + 1
    return color, piece, liberties

pattern_ind2xy = [(0,-1), (-1,0), (0,1), (1,0),
                  (-1,-1), (-1,1), (1,1), (1,-1),
                  (0,-2), (-2,0), (0,2), (2,0)]
def print_pattern(pattern_str):
    color2str = " WB"
    piece2str = EMPTY + WHITE + BLACK + EDGE
    size = 12
    screen = {}
    for x in range(-2, 2+1):
        for y in range(-2, 2+1):
            screen[x,y] = "  "
    l = map(int, pattern_str.split())
    for i in range(size):
        x, y = pattern_ind2xy[i]
        color, piece, liberties = decode_pattern_key(l[i])
        color = color2str[color]
        piece = piece2str[piece]
        if piece in WHITE+BLACK:
            liberties = str(liberties)
        else:
            liberties = " "
        screen[0,0] = color + " "
        screen[x,y] = piece + liberties
    for y in range(2, -2-1, -1):
        for x in range(-2, 2+1):
            print screen[x,y],
        print
    print l[size:], float(l[-2])/sum(l[-2:])
    print
    return screen

def load_patterns_sorted(filename = "patterns.dat"):
    pattern_lst = []
    for line in open(filename):
        l = line.split()
        n1 = int(l[-1])
        n2 = int(l[-2])
        #if n1 > 3*n2 or n2 > 3*n1:
        #if n1 > 3*n2:
        if 1:
            pattern_lst.append((n1+n2, line))
    pattern_lst.sort()
    pattern_lst.reverse()
    for count, line in pattern_lst[:10]:
        print_pattern(line)
    print len(pattern_lst)
    return pattern_lst

def move_pattern(pattern, direction):
    xd, yd = direction
    pattern2 = []
    for (x,y), value in pattern:
        pattern2.append(((x + xd, y + yd), value))
    return pattern2

def create_board_from_pattern(pattern_str):
    screen = print_pattern(pattern_str)
    pattern = screen.items()
    edge_move_amount = {}
    def ind2edge_move(n):
        if abs(n)==1:
            return 4*n
        return n*3/2
    for x, y in pattern_ind2xy:
        edge_move_amount[x, y] = ind2edge_move(x), ind2edge_move(y)
    max_move_sum = 0
    max_move = (0, 0)
    for pos, value in pattern:
        if value[0]!=EDGE:
            continue
        move = edge_move_amount[pos]
        move_sum = sum(map(abs, move))
        if move_sum > max_move_sum:
            max_move_sum = move_sum
            max_move = move
    pattern = move_pattern(pattern, max_move)
    bsize = 9
    mx = my = (bsize + 1)//2
    middle9x9 = mx, my
    pattern = move_pattern(pattern, middle9x9)
    g = Game(bsize)
    cb = g.current_board
    real_liberties = {}
    for pos, value in pattern:
        piece, liberties = value[0], value[1]
        if piece in WHITE+BLACK:
            if cb.side!=piece:
                g.make_move(PASS_MOVE)
            g.make_move(pos)
            real_liberties[pos] = int(liberties)
    return pattern, g, real_liberties

def show_pattern_moves(g):
    fudge = 100.0
    ml = []
    best_score = -1.0
    best_moves = []
    for move in g.list_moves():
        if move==PASS_MOVE:
            continue
        result = c_board.get_pattern_result_table(move, g.c_color())
        if result:
            score = result2score((result[0]+fudge, result[1]+fudge))
            if sum(result):
                score0 = result2score(result)
            else:
                score0 = 0.5
            if score >= best_score:
                if score > best_score:
                    best_score = score
                    best_moves = []
                best_moves.append(move)
            ml.append((score, score0, result, move))
            
    ml.sort()
    ml.reverse()
    for score, score0, result, move in ml[:10]:
        print score, score0, result, move_as_string(move)
    move = random.choice(best_moves)
    print len(best_moves), move_as_string(move)
    print g.make_move(move)


def t():
    g = load_sgf.load_file("uct_game.sgf", game_class = CGame)
    while len(g.move_history) > 58:
        g.undo_move()
    return g

def dump(name = "patterns.dat"):
    return c_board.dump_pattern_result_table(name)

def test_wrong_count():
    global g
    #g = load_sgf.load_file("../../kgs/Aloriless-SimpleBot_uct_brown_wrong_count.sgf")
    #g = load_sgf.load_file("kgs/Aloriless-SimpleBot_uct_weak_ha3_won.sgf")
    #g = load_sgf.load_file("kgs/Aloriless-SimpleBot_uct_shape_still_wrong_scoring.sgf")
    #g = load_sgf.load_file("kgs/Aloriless-SimpleBot_still_loses_trivially.sgf")
    g = load_sgf.load_file("kgs/Aloriless-SimpleBot_again_loses_trivially.sgf")
    c_board.set_komi(3.5)
    print c_board.score_board()
    
def mm(m):
    print g.make_move(string_as_move(m))

def test_komi(komi):
    config.time_per_move_limit = 100000000
    config.games_per_move_limit = 1000000
    print "."*60
    print "Komi:", komi
    #g = load_sgf.load_file("kgs/minue622-SimpleBot_1h_komi_analysis6.sgf"); g.make_move(PASS_MOVE)
    #g = Game(7)
    #g = load_sgf.load_file("kgs/Fomalhaut-SimpleBot_2006-08-06_tourn.sgf")
    #g = load_sgf.load_file("kgs/StoneCrazy-SimpleBot_2006-08-06_tour.sgf")
    #g = load_sgf.load_file("kgs/yose_test0.sgf")
    g = load_sgf.load_file("kgs/t.sgf")
    print g.current_board
    c_board.clear_result_table()
    g.set_komi(komi)
    c_board.set_random_seed(1)
    print g.generate_move()

def test_ld(filename, pos):
    config.time_per_move_limit = 100000000
    config.games_per_move_limit = 2**63
    g = load_sgf.load_file(filename)
    print g.current_board
    c_board.clear_result_table()
    c_board.set_random_seed(1)
    g.select_uct_move(pos=string_as_move(pos))

def test_ld_all_blocks(filename, colors):
    config.time_per_move_limit = 100000000
    config.games_per_move_limit = 100000
    g = load_sgf.load_file(filename)
    cb = g.current_board
    print cb
    pos_lst = []
    for block in cb.iterate_blocks(colors):
        pos = block.get_origin()
        pos_lst.append(pos)
    for pos in pos_lst:
        print "test:", move_as_string(pos), cb.side
        c_board.clear_result_table()
        c_board.set_random_seed(1)
        g.select_uct_move(pos=pos)
        g.make_move(PASS_MOVE)
        print "test opposite:", move_as_string(pos), cb.side
        c_board.clear_result_table()
        c_board.set_random_seed(1)
        g.select_uct_move(pos=pos)
        g.undo_move()


def ld_score_moves(filename = None, g = None):
    #config.debug_output = open("ld_score.log", "a")
    score_dict = {}
    config.time_per_move_limit = 100000000
    config.games_per_move_limit = 10000
    if filename:
        g = load_sgf.load_file(filename)
    cb = g.current_board
    dprintnl(cb)
    side0 = cb.side
    pos_lst = []
    for block in cb.iterate_blocks(BLACK+WHITE):
    #for block in cb.iterate_blocks(WHITE):
        pos = block.get_origin()
        pos_lst.append(pos)
    for pos in pos_lst:
        block_color = cb.goban[pos]
        score_opponent = 0.0
        score_our = {}
        for color_switch in (False, True):
            if not color_switch:
                dprintnl("test:", move_as_string(pos), cb.side)
            else:
                g.make_move(PASS_MOVE)
                dprintnl("test opposite:", move_as_string(pos), cb.side)
            c_board.clear_result_table()
            c_board.set_random_seed(1)
            g.select_uct_move(pos=pos)
            for move in g.list_moves():
                dprintnl(move_as_string(pos), "move:", move_as_string(move))
                g.make_move(move)
                result = c_board.get_result_table(g.c_color())
                g.undo_move()
                score = result[1] / float(sum(result))
                if cb.side==side0:
                    #dprintnl("defend:", score)
                    score_our[move] = score
                else:
                    #dprintnl("attack:", score)
                    score_opponent = max(score, score_opponent)
            if color_switch:
                g.undo_move()
        dprintnl("summary:")
        dprintnl(score_opponent, max(score_our.values()))
        #dprintnl(score_our)
        score_our_lst = []
        for m, value in score_our.items():
            score_our_lst.append((value, m))
        score_our_lst.sort()
        score_our_lst = score_our_lst[-10:]
        dprintnl(score_our_lst)
        for score, move in score_our_lst:
            if block_color==side0: #defend
                score_diff = score - (1 - score_opponent)
            else:
                score_diff = score_opponent - (1 - score)
            dprintnl("score diff:", score_diff, move_as_string(move), score)
            score_diff *= cb.blocks[pos].size()
            score_dict[move] = score_dict.get(move, 0.0) + score_diff
        dprintnl("endof", move_as_string(pos))
        dprintnl()
    move_values = []
    for move in score_dict:
        move_values.append((score_dict[move], move))
    move_values.sort()
    move_values.reverse()
    for score, move in move_values:
        dprintnl(score, move_as_string(move))
    #for score, move in move_values[:5]:
    #    print score, move_as_string(move)
    #config.debug_output.flush()
    if move_values:
        return move_values[0][1]
    return PASS_MOVE

def test_tromp_taylor_scoring():
    c_board.clear_result_table()
    c_board.set_random_seed(1)
    config.time_per_move_limit = 100000000
    config.games_per_move_limit = 10000
    g = load_sgf.load_file("kgs/tromp_taylor_scoring_error.sgf")
    g.undo_move()
    #g.undo_move()
    print g.current_board
    print g.make_move(g.generate_move())
    return g

def test_area_scoring():
    c_board.clear_result_table()
    c_board.set_random_seed(1)
    config.time_per_move_limit = 100000000
    config.games_per_move_limit = 100000
    g = load_sgf.load_file("kgs/endgame_test.sgf")
    g.set_komi(7.5)
    g.undo_move()
    #g.make_move(string_as_move("C1"))
    #g.make_move(string_as_move("G1"))
    #g.make_move(string_as_move("D5"))
    print g.current_board
    #g.generate_move()
    return g

def gm0():
    config.games_per_move_limit = 100000
    c_board.clear_result_table()
    print g.make_move(g.generate_move())
    g.undo_move()

def gm():
    print g.make_move(ld_score_moves(g=g))

if __name__=="__main__":
    #test_uct(1)
    #show_result_tree()
    c_board.set_random_seed(1)
    g = CGame(9)
    #fp = open("patterns.dat")
    #line = fp.readline()
    #pattern, g, real_liberties = create_board_from_pattern(line)
    #uct_search(1, g)
    #test_wrong_count()
    g = test_area_scoring()
    pass
