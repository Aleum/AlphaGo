import string, sys
from pprint import pprint
from simple_go import *
from scored_move import ScoredMove
import load_sgf
import c_board

KILLED = "killed"
LIVES = "lives"

def counts2ratio(counts):
    count_sum = sum(counts)
    ratio = float(counts[0]) / count_sum
    return ratio

def find_lib_count_and_stone(cboard, block):
    lib_count = 0
    stone = PASS_MOVE
    block_liberties = cboard.block_liberties(block)
    if block_liberties==1:
        lib_count = 0
        for stone in block.stones:
            for pos2 in cboard.iterate_neighbour(stone):
                if cboard.goban[pos2]==EMPTY:
                    lib_count = 1
                    break
            if lib_count:
                break
    elif block_liberties==2:
        for stone in block.stones:
            lib_count = 0
            for pos2 in cboard.iterate_neighbour(stone):
                if cboard.goban[pos2]==EMPTY:
                    lib_count = lib_count + 1
            if lib_count==2:
                break
        if lib_count==1:
            lib_count = 0
    return lib_count, stone

class FastRandomGame(Game):
    def __init__(self, size):
        Game.__init__(self, size)
        self.full_init_fast_select_random_no_eye_fill_move()

    def generate_move(self, remove_opponent_dead=False, pass_allowed=True):
        return self.fast_select_random_no_eye_fill_move()

class BGame(Game):
    def __init__(self, size, pattern_statistics = {}):
        Game.__init__(self, size)
        self.full_init_fast_select_random_no_eye_fill_move()
        self.pattern_statistics = pattern_statistics

    def generate_move(self, remove_opponent_dead=False, pass_allowed=True):
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
        move_values = []
        self.search_dict = {}
        if selected_move==PASS_MOVE and move_list:
            pattern_move_scores = {}
            #'tactical' pattern reading
            for block in cboard.iterate_blocks(BLACK+WHITE):
                lib_count, stone = find_lib_count_and_stone(cboard, block)
                if lib_count:
                    pattern = get_pattern(cboard, stone)
                    if pattern in self.pattern_statistics:
                        pattern_result = self.pattern_statistics[pattern]
                        opponent = other_side[cboard.side]
                        #find best opponent result
                        opponent_best_score = 0.0
                        opponent_best_move = PASS_MOVE
                        our_best_score = 0.0
                        our_best_move = PASS_MOVE
                        default_score = counts2ratio(pattern_result.counts)
                        for (color, move), counts in pattern_result.moves.items():
                            if move==None:
                                continue
                            move = stone[0] + move[0], stone[1] + move[1]
                            ratio = counts2ratio(counts)
                            if color==opponent:
                                if block.color==cboard.side:
                                    score = default_score - ratio
                                else:
                                    score = ratio - default_score
                                if score > opponent_best_score:
                                    opponent_best_score = score
                                    opponent_best_move = move
                            else:
                                if block.color==cboard.side:
                                    score = ratio - default_score
                                else:
                                    score = default_score - ratio
                                pattern_move_scores[move] = pattern_move_scores.get(move, 0.0) + score
                                if score > our_best_score:
                                    our_best_score = score
                                    our_best_move = move
                        if opponent_best_score > 0.0 and our_best_score > 0.0:
                            pattern_move_scores[our_best_move] = pattern_move_scores.get(our_best_move, 0.0) + opponent_best_score

            for move in move_list:
                side_colors = {}
                for pos in cboard.iterate_neighbour(move):
                    side_colors[cboard.goban[pos]] = True
                if len(side_colors)>1 or side_colors.keys()[0]==EMPTY:
                    if self.legal_move(move):
                        score = pattern_move_scores.get(move, 0.0)
                        smove = ScoredMove(move, score)
                        move_values.append(smove)
            if move_values:
                move_values.sort()
                move_values.reverse()
                selected_move = move_values[0].move
                move_list = self.available_moves[cboard.side] = []
                for smove in move_values[1:]:
                    move_list.append(smove.move)

            for smove in move_values:
                self.search_dict[smove.move] = smove.score, str(smove)

        if config.debug_flag:
            dprintnl(cboard)
            dprintnl("selected move:", move_as_string(selected_move))
            dprintsp("!")
            for smove in move_values:
                dprintsp(smove)
            dprintnl()

        return selected_move
    

    def probabilistic_alpha_beta(self, pos, depth, alpha=-1.1, beta=1.1):
        cboard = self.current_board
        if cboard.goban[pos]==EMPTY:
            return -1.0, []
        if depth==0:
            return 0.0, []

        best_score = WORST_SCORE
        best_move = [PASS_MOVE]
        move_list = self.list_moves()
        for move in move_list:
            if random.random() > 0.1:
                continue
            self.make_move(move)
            score, result_moves = self.probabilistic_alpha_beta(pos, depth-1, -beta, -alpha)
            score = -score
            if config.debug_flag:
                dprintnl("->", move_as_string(pos), depth, move_as_string(move),
                         score, move_list_as_string(result_moves), alpha, beta)
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
            best_score = 0.0
        return best_score, best_move
                
        

def get_pattern(cboard, pos):
    pattern = [((0, 0), cboard.goban[pos])]
    for pos2 in cboard.iterate_neighbour_and_diagonal_neighbour(pos):
        pattern_pos2 = (pos2[0] - pos[0], pos2[1] - pos[1])
        pattern.append((pattern_pos2, cboard.goban[pos2]))
    return tuple(pattern)

def pattern2str(pattern):
    s = ""
    for y in range(1, -1-1, -1):
        for x in range(-1, 1+1):
            for pos, color in pattern:
                if (x, y) == pos:
                    s = s + color
                    break
            else:
                s = s + const.EDGE
        s = s + "\n"
    return s

class PatternResults:
    def __init__(self, counts = None, moves = None):
        if counts==None:
            self.counts = [0, 0]
        else:
            self.counts = counts
        if moves==None:
            self.moves = {}
        else:
            self.moves = moves

    def add_result(self, result, move_list):
        if result==LIVES:
            self.counts[0] = self.counts[0] + 1
        else:
            self.counts[1] = self.counts[1] + 1
        if len(move_list)==1:
            start = 0
        else:
            start = 1
        for color_move in move_list[start:]:
            count_list = self.moves.get(color_move, [0, 0])
            if result==LIVES:
                count_list[0] = count_list[0] + 1
            else:
                count_list[1] = count_list[1] + 1
            self.moves[color_move] = count_list

    def __str__(self):
        count_sum = sum(self.counts)
        ratio = float(self.counts[0]) / count_sum
        s = "%s %s %s" % (count_sum, ratio, self.counts)
        move_results = []
        for color_move, counts in self.moves.items():
            count_sum = sum(counts)
            ratio = float(counts[0]) / count_sum
            move_results.append((ratio, count_sum, counts, color_move))
        move_results.sort()
        for ratio, count_sum, counts, color_move in move_results:
            if color_move[1]==None:
                move = PASS_MOVE
            else:
                move = color_move[1][0] + 2, color_move[1][1] + 2
            s = s + "  <%s %s %s %s %s>" % (ratio, count_sum, counts, color_move[0], move_as_string(move))
        return s + "\n"

    def __repr__(self):
        return "PatternResults(%s, %s)" % (repr(self.counts), repr(self.moves))

def FastRandomFactory():
    g = FastRandomGame(9)
    return g

def play_game(pattern_statistics, seed, game_factory=FastRandomFactory):
    sys.stderr.write("%i\r" % seed)
    random.seed(seed)
    #print seed,
    g = game_factory()
    cboard = g.current_board
    track_list = []
    results = []
    board_str = []
    while not g.has_2_passes():
        #print cboard
        new_track_list = []
        for problem in track_list:
            move_no, pos, color, pattern, moves = problem
            result = None
            if cboard.goban[pos]!=color:
                result = KILLED
##            elif cboard.liberties(pos) > 2:
##                result = LIVES
            else:
                new_track_list.append(problem)
            if result:
                results.append((problem, result, len(g.move_history)))
                pattern_results = pattern_statistics.get(pattern, PatternResults())
                pattern_results.add_result(result, moves)
                pattern_statistics[pattern] = pattern_results
        track_list = new_track_list
        #print "2 libs:",
        for block in cboard.iterate_blocks(BLACK+WHITE):
            lib_count, stone = find_lib_count_and_stone(cboard, block)
            if lib_count:
                #print move_as_string(stone)
                pattern = get_pattern(cboard, stone)
                new_problem = [len(g.move_history), stone, block.color, pattern, [(cboard.side, None)]]
                for problem in track_list:
                    if problem[1:-1]==new_problem[1:-1]:
                        break
                else:
                    track_list.append(new_problem)
                    if pattern2str(pattern)=="O..\nOX.\n.O.\n":
                        print "-"*60
                        print move_list_as_string(g.move_history)
                        pattern_pos_list = []
                        for pos, color in pattern:
                            pattern_pos_list.append((pos[0] + stone[0], pos[1] + stone[1]))
                        print cboard.pattern_str(pattern_pos_list)
                        print seed, len(g.move_history), move_as_string(stone)
        #print
        board_str.append(str(cboard))
        #move = g.select_brown_move()
        move = g.generate_move()
        for problem in track_list:
            move_no, pos, color, pattern, moves = problem
            pattern_now = get_pattern(cboard, pos)
            if pattern==pattern_now and move in cboard.iterate_neighbour_and_diagonal_neighbour(pos):
                pattern_move = move[0] - pos[0], move[1] - pos[1]
                moves.append((cboard.side, pattern_move))
        #print move_as_string(move),
        sys.stdout.flush()
        g.make_move(move)
        
    for problem in track_list:
        move_no, pos, color, pattern, moves = problem
        result = LIVES
        results.append((problem, result, len(g.move_history)))
        pattern_results = pattern_statistics.get(pattern, PatternResults())
        pattern_results.add_result(result, moves)
        pattern_statistics[pattern] = pattern_results

    #print
    #print len(track_list)
    #print track_list
    #pprint(results)
    results.sort()
    #pprint(results)

    #print "="*60

    if 0:
        for (move_no, pos, color, pattern), result, result_move in results:
            print board_str[move_no]
            print move_as_string(pos), color
            print pattern
            print result
            print move_list_as_string(g.move_history[move_no: result_move])
            print board_str[result_move]
            print "-"*60

    #print g

def test_2_liberties(save_interval, game_factory=FastRandomFactory):
    pattern_statistics = {}
    seed = 1
    save_count = 0
    while True:
        for i in range(save_interval):
            play_game(pattern_statistics, seed, game_factory)
            seed = seed + 1

        pattern_list = []
        for pattern, result in pattern_statistics.items():
            ratio = float(result.counts[0]) / sum(result.counts)
            pattern_list.append([sum(result.counts), ratio, pattern])
        pattern_list.sort()
        save_count = save_count + 1
        
        print save_count, " " * len(str(save_interval))
        fp = open("2lib_stat%03i.log" % save_count, "w")
        for count_both, ratio, pattern in pattern_list:
            fp.write(pattern2str(pattern))
            fp.write("%s\n\n" % pattern_statistics[pattern])
        fp.close()

        for i in range(len(pattern_list)):
            pattern_list[i][0], pattern_list[i][1] = pattern_list[i][1], pattern_list[i][0]
        pattern_list.sort()

        fp1 = open("2lib_stat_ratio%03i.log" % save_count, "w")
        fp2 = open("2lib_stat_ratio_common%03i.log" % save_count, "w")
        for ratio, count_both, pattern in pattern_list:
            fp1.write(pattern2str(pattern))
            fp1.write("%s\n\n" % pattern_statistics[pattern])
            if count_both >= 10:
                fp2.write(pattern2str(pattern))
                fp2.write("%s\n\n" % pattern_statistics[pattern])
        fp1.close()
        fp2.close()

        fp = open("2lib_stat_ratio%03i.dat" % save_count, "w")
        fp.write(repr(pattern_statistics))
        fp.close()

def test_pattern_in_play(pattern_file, seed=1):
    s = open(pattern_file).read()
    pattern_statistics = eval(s)
    random.seed(seed)
    g = BGame(9, pattern_statistics)
    while not g.has_2_passes():
        move = g.generate_move()
        g.make_move(move)
    print g
    return g


class PatternGameFactory:
    def __init__(self, pattern_file):
        s = open(pattern_file).read()
        self.pattern_statistics = eval(s)

    def __call__(self):
        g = BGame(9, self.pattern_statistics)
        return g
    

def test_2_liberties_pattern(save_interval):
    config.debug_flag = False
    game_factory = PatternGameFactory("2lib_stat_input.dat")
    test_2_liberties(save_interval, game_factory)
    
def test_ladder_alpha_beta(name = "kgs/simple_ladders2.sgf", pos_str = "C3", depth = 1, seed = 1):
    random.seed(seed)
    g = load_sgf.load_file(name, game_class = BGame)
    pos = string_as_move(pos_str)
    block_color = g.current_board.goban[pos]
    if g.current_board.side==block_color:
        g.make_move(PASS_MOVE)
    print g.current_board
    print pos_str
    #g.probabilistic_alpha_beta(string_as_move(pos), 80)
    nodes0 = g.node_count
    score, moves = g.probabilistic_alpha_beta(pos, depth)
    nodes1 = g.node_count
    print score, move_list_as_string(moves), nodes1-nodes0

class RandomGame(Game):
    def generate_move(self, remove_opponent_dead=False, pass_allowed=True):
        return self.select_random_move()

def RandomFactory():
    g = RandomGame(9)
    return g

def test_2_liberties_random(save_interval):
    config.debug_flag = False
    test_2_liberties(save_interval, RandomFactory)

def play_game_python(g, pos):
    cboard = g.current_board
    while not g.has_2_passes():
        if cboard.goban[pos]==EMPTY:
            return 0
        move = g.generate_move()
        g.make_move(move)
    return 1

def play_game_c(g, pos):
    cboard = g.current_board
    if cboard.goban[pos]==EMPTY:
        return 0
    result = c_board.test_block(pos, color2ccolor[cboard.side], 1)
    return result

play_game = play_game_c

def invert_probability(prob_lst):
    result = []
    for prob in prob_lst:
        result.append(1-prob)
    return result

def new_bayesian_prob(priors, theories, measurement):
    if measurement:
        theories = invert_probability(theories)
    combined = 0.0
    for i in range(len(priors)):
        combined = combined + theories[i] * priors[i]
    posteriors = []
    for i in range(len(priors)):
        posteriors.append(priors[i] * theories[i] / combined)
    return posteriors

def make_random_generator(kill_probability):
    while True:
        no = random.random()
        if no <= kill_probability:
            yield 0
        else:
            yield 1

def test_theories(priors, theories, generator, count, seed=1):
    random.seed(seed)
    total_measurement = 0
    for i in range(count):
        measurement = generator.next()
        total_measurement = total_measurement + measurement
        priors = new_bayesian_prob(priors, theories, measurement)
        #print i+1, measurement, priors
    print count, total_measurement, priors
    
"""
examples:

test_theories([0.05, 0.05, 0.7, 0.2], [0.999, 0.001, 0.5, 0.75], make_random_generator(0.75), count)
count total_measurements posteriors
1 0 [0.090818181818181812, 9.0909090909090904e-05, 0.63636363636363624, 0.27272727272727276]
10 3 [4.5107342941610679e-08, 4.5288224290534587e-20, 0.62103618754726775, 0.37896376734538928]
100 27 [5.5250940886130806e-57, 5.7853177878677316e-195, 6.5642861864238607e-05, 0.99993435713813583]
1000 265 [0.0, 0.0, 7.7614254325074074e-50, 1.0]

test_theories([0.05, 0.05, 0.7, 0.2], [0.999, 0.001, 0.5, 0.75], make_random_generator(0.99), count)
count total_measurements posteriors
1 0 [0.090818181818181812, 9.0909090909090904e-05, 0.63636363636363624, 0.27272727272727276]
10 0 [0.80558860218089012, 8.1368897338292454e-31, 0.011124653932969672, 0.18328674388614011]
100 1 [0.99999999952784813, 1.1030168671472459e-294, 1.2193970350435909e-26, 4.7215189947644984e-10]
1000 8 [1.0, 0.0, 3.525072483678562e-276, 1.8940394702024934e-104]

"""

class MovePattern:
    def __init__(self, move):
        self.move = move
        self.theories = [0.99, 0.9, 0.7, 0.6, 0.5, 0.4, 0.3, 0.1, 0.01]
        self.priors = [1.0 / len(self.theories)] * len(self.theories)
        self.total_count = 0
        self.result_sum = 0

    def apply_result(self, result):
        self.total_count += 1
        self.result_sum += result
        self.priors = new_bayesian_prob(self.priors, self.theories, result)

    def best_theory(self):
        best_theory = self.theories[0]
        best_priori = self.priors[0]
        for i in range(1, len(self.theories)):
            if self.priors[i] > best_priori:
                best_theory = self.theories[i]
                best_priori = self.priors[i]
        return best_theory, best_priori

    def __cmp__(self, other):
        return cmp(self.move, other.move)

    def __hash__(self):
        return hash(self.move)

    def __str__(self):
        data_str = ""
        max_prior = max(self.priors)
        for i in range(len(self.priors)):
            if self.priors[i]==max_prior:
                bracket_left = "["
                bracket_right = "]"
            else:
                bracket_left = "("
                bracket_right = ")"
            data_str += " %s%.3f: %.3f%s" % (bracket_left, self.theories[i], self.priors[i], bracket_right)
        return "MovePattern(%s): (%s/%s)%s" % (move_as_string(self.move), self.result_sum, self.total_count, data_str)


def test_simple_atari(count):
    random.seed(1)
    c_board.set_random_seed(1)
    g = load_sgf.load_file("kgs/simple_atari0.sgf", game_class = RandomGame)
    print g.current_board
    move_list = g.list_moves()
    pattern_dict = {}
    for move in move_list:
        pattern = MovePattern(move)
        pattern_dict[move] = pattern
        #print len(pattern_dict), pattern
    for seed in range(1, count+1):
        best_score = None
        for move in move_list:
            pattern = pattern_dict[move]
            score = pattern.best_theory()
            if score > best_score:
                best_score = score
                best_patterns = [pattern]
            elif score == best_score:
                best_patterns.append(pattern)
##        print len(best_patterns), "%.3f: %.3f" % best_score,
##        for pattern in best_patterns:
##            print move_as_string(pattern.move),
##        print
        pattern = random.choice(best_patterns)
        pattern = pattern_dict[random.choice(pattern_dict.keys())]
        move = pattern.move
        start_len = len(g.move_history)
        g.make_move(move)
        result = play_game(g, string_as_move("A1"))
        #print g.current_board
        while len(g.move_history) > start_len:
            g.undo_move()
        pattern.apply_result(result)
##        print seed, result, "%.3f: %.3f" % pattern.best_theory(), str(pattern)
##        print

    result_lst = []
    print "-"*60
    for move in move_list:
        pattern = pattern_dict[move]
        if pattern.total_count:
            result_lst.append((pattern.best_theory(), pattern))
    result_lst.sort()
    for score, pattern in result_lst:
        print str(pattern)

def test_same(move_str):
    g = load_sgf.load_file("kgs/simple_atari0.sgf", game_class = RandomGame)
    cboard = g.current_board
    print cboard
    g.make_move(string_as_move(move_str))
    result_sum = 0
    for i in range(1000):
        result_sum += play_game_c(g, string_as_move("A1"))
    print move_str, result_sum
