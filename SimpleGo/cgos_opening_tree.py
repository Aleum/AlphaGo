import sys, random, time, re, pprint, os
cgos_dir = "cgos_web/"
sys.path.append(cgos_dir)
import load_sgf
from simple_go import *
import cPickle
try:
    from read_results import read_results
except:
    #no need for this when using only OpeningTree class, otherwise need to add read_results module
    pass


#opponent = "gnugo_3.7.4"
opponent = "CrazyStoneQuad"
opponent_color = "B"

class OpeningTree:
    def __init__(self, name, game):
        self.name = name
        self.load_tree(name)
        self.game = game

    def load_tree(self, name):
        if os.path.exists(name):
            fp = open(name)
            self.hash_tree = cPickle.load(fp)
            fp.close()
        else:
            self.hash_tree = {}

    def get_move(self):
        g = self.game
        if not g.move_history:
            middle = (g.size+1)//2
            return 1.0, 1.0, [0, 0], (middle, middle)
        key = g.search_key()
        cb = g.current_board
        ht = self.hash_tree
        if key not in ht:
            return
        d = ht[key]
        l = []
        for m in d:
            if len(d[m]) > 2:
                if cb.side==WHITE:
                    i1 = 0
                    i2 = 1
                else:
                    i1 = 1
                    i2 = 0
                score = (d[m][i1] + FUDGE) / (d[m][i2] + FUDGE)
                l.append((d[m][2], score, d[m][:2], m))
        if not l:
            return
        l.sort()
        m = l[-1][-1]
        if g.legal_move(m):
            return l[-1]

def find_opening_from_web(color):
    global opponent
    global opponent_color
    if color=="B":
        opponent_color = "W"
    else:
        opponent_color = "B"
    tmp_file = "cgos_9x9.txt"
    os.system("lynx -dump http://cgos.boardspace.net/9x9.html > " + tmp_file)
    pat = re.compile(r".* (\S+)\(.*\)\s+(\S+)\(.*\) - playing ...")
    for line in open(tmp_file):
        m = pat.match(line)
        if m:
            if color=="W":
                opponent = m.group(2)
                our_name = m.group(1)
            else:
                opponent = m.group(1)
                our_name = m.group(2)
            if our_name=="SimpleBot":
            #if our_name=="WeakBot50k":
                return opening_file("_pruned")
    return "None"

def opening_file(additional_info = ""):
    return cgos_dir + "opening/" + opponent_color + "_" + opponent + additional_info + ".dat"

def show_top_players():
    result_lst = read_results(cgos_dir)
    d = {}
    d_all = {}
    for result in result_lst:
        for color in ("W", "B"):
            name = result["P" + color]
            rating = result[color + "R"]
            m = re.match(r"(-?\d+)", rating)
            if m:
                rating = int(m.group(1))
                if rating >= 1600:
                    d[name] = d.get(name, 0) + 1
            d_all[name] = d_all.get(name, 0) + 1
    pprint.pprint(d)
    print sum(d.values()), sum(d_all.values())
    return d, d_all

def create_top():
    global opponent
    global opponent_color
    d, d_all = show_top_players()
    for name in d:
        for color in ("W", "B"):
            print name, color, d[name]
            opponent = name
            opponent_color = color
            create_tree()

def create_tree():
    result_lst = read_results(cgos_dir)
    hash_tree = {}
    i = 0
    for result in result_lst:
        if result["P" + opponent_color]==opponent:
            random.seed(1)
            g = load_sgf.load_file(cgos_dir + result["File"])
            cboard = g.current_board
            #print cboard
            print result
            black_won = result["RE"][0]=="B"
            next_move = PASS_MOVE
            while True:
                key = g.search_key()
                moves = hash_tree.get(key, {})
                counts = moves.get(next_move, [0, 0])
                counts[black_won] += 1
                moves[next_move] = counts
                hash_tree[key] = moves
                if len(g.move_history)==0:
                    break
                next_move = g.move_history[-1]
                g.undo_move()
            i += 1
            print i, len(hash_tree), len(hash_tree)/float(i)
            #print hash_tree
            #random.seed(1)
            #g = Game(9)
            #print hash_tree[g.search_key()]
            #break

    fp = open(opening_file(), "w")
    cPickle.dump(hash_tree, fp)

def load_tree():
    fp = open(opening_file())
    hash_tree = cPickle.load(fp)
    return hash_tree

def get_our_count_ind():
    if cb.side==WHITE:
        i1 = 0
        i2 = 1
    else:
        i1 = 1
        i2 = 0
    #if opponent_color=="W":
    #    i1, i2 = i2, i1
    return i1, i2
    

def lm():
    d = ht[g.search_key()]
    l = []
    for m in d:
        i1, i2 = get_our_count_ind()
        l.append(((d[m][i1] + FUDGE) / (d[m][i2] + FUDGE), m))
    l.sort()
    for s, m in l:
        print s, move_as_string(m), d[m]
    return l[-1][1]

def lm2():
    d = ht[g.search_key()]
    l = []
    for m in d:
        i1, i2 = get_our_count_ind()
        score = (d[m][i1] + FUDGE) / (d[m][i2] + FUDGE)
        l.append((d[m][2], score, m))
    l.sort()
    for s, s2, m in l:
        print s, s2, move_as_string(m), d[m]
    return l[-1][2]

def mm(m):
    print g.make_move(string_as_move(m))

FUDGE = 3.0
WORST_SCORE = 1E-6
def alphabeta(depth, alpha, beta, current_depth=0):
    best_score = WORST_SCORE
    best_move = (PASS_MOVE,)
    key = g.search_key()
    if key not in ht:
        return best_score, best_move
    d = ht[key]
    l = []
    for m in d:
        i1, i2 = get_our_count_ind()
        l.append(((d[m][i1] + FUDGE) / (d[m][i2] + FUDGE), m))
    if not l:
        return best_score, best_move
    l.sort()
    l.reverse()
    if depth==0 or (g.move_history and g.move_history[-1] == PASS_MOVE):
        return l[0][0], (l[0][1],)
    for s, m in l:
        if m==PASS_MOVE:
            continue
        if g.make_move(m):
            s2, m2 = alphabeta(depth - 1, 1.0/beta, 1.0/alpha, current_depth + 1)
            s2 = 1.0 / s2
            #print "    "*current_depth, current_depth, move_list_as_string(g.move_history), s2, move_list_as_string(m2), alpha, beta,
            g.undo_move()
            if s2 > best_score:
                #print "s2 > best_score",
                best_score = s2
                best_move = (m,) + m2
                if s2 >= alpha:
                    #print "s2 >= alpha", 
                    alpha = s2
                    if s2 >= beta:
                        #print "s2 >= beta"
                        break
            #print
    #print "    "*current_depth, current_depth, "return", move_list_as_string(g.move_history), best_score, move_list_as_string(best_move)
    return best_score, best_move

def ab(depth):
    nodes0 = g.node_count
    t0 = time.time()
    s, m = alphabeta(depth, WORST_SCORE, 1/WORST_SCORE)
    nodes = g.node_count - nodes0
    t = time.time() - t0
    print depth, s, move_list_as_string(m), nodes, t, nodes/t

def prune_move(move):
    key = g.search_key()
    d = ht[key]
    moves = g.move_history[:]
    counts = d[move]
    print move_as_string(move), counts
    del d[move]
    while g.undo_move():
        key2 = g.search_key()
        d2 = ht[key2]
        for m in g.list_moves():
            g.make_move(m)
            if key==g.search_key():
                print move_as_string(m), d2[m],
                d2[m][0] -= counts[0]
                d2[m][1] -= counts[1]
                print d2[m]
            g.undo_move()
        key = key2
    for m in moves:
        g.make_move(m)

def list_tree():
    key = g.search_key()
    if key not in ht:
        return
    d = ht[key]
    count = [0, 0]
    for result in d.values():
        count[0] += result[0]
        count[1] += result[1]
    fp = open("tmp.out", "a")
    s = "%s %s %s\n" % (count, move_list_as_string(g.move_history), d)
    fp.write(s)
    fp.close()
    if count[0]:
        print s[:-1]
    for m in d:
        if m==PASS_MOVE:
            continue
        if g.make_move(m):
            list_tree()
            g.undo_move()

def delete_tree():
    key = g.search_key()
    if key not in ht:
        return
    d = ht[key]
    del ht[key]
    count = [0, 0]
    for result in d.values():
        count[0] += result[0]
        count[1] += result[1]
    fp = open("tmp.out", "a")
    s = "%s %s %s\n" % (count, move_list_as_string(g.move_history), d)
    fp.write(s)
    fp.close()
    if count[0]:
        print s[:-1]
    for m in d:
        if m==PASS_MOVE:
            continue
        if g.make_move(m):
            delete_tree()
            g.undo_move()

def find_lost_branches(color, remove_flag=False):
    key = g.search_key()
    if key not in ht:
        return
    d = ht[key]
    delete_flag = g.current_board.side==color
    move_lst = d.keys()
    for m in move_lst:
        if m==PASS_MOVE:
            continue
        if g.make_move(m):
            counts = d[m]
            i1, i2 = get_our_count_ind()
            if delete_flag and counts[i2]==0:
                print move_list_as_string(g.move_history), counts
                if remove_flag:
                    delete_tree()
                g.undo_move()
                if remove_flag:
                    #prune_move(m)
                    del d[m]
            else:
                find_lost_branches(color, remove_flag)
                g.undo_move()

def minmax_tree(depth):
    if depth <= 3:
        print move_list_as_string(g.move_history)
    best_score = WORST_SCORE
    best_move = (PASS_MOVE,)
    key = g.search_key()
    if key not in ht:
        return best_score, best_move
    d = ht[key]
    l = []
    for m in d:
        i1, i2 = get_our_count_ind()
        l.append(((d[m][i1] + FUDGE) / (d[m][i2] + FUDGE), m))
    if not l:
        return best_score, best_move
    if g.has_2_passes():
        return l[0][0], (l[0][1],)
    for s, m in l:
        if g.make_move(m):
            if len(d[m])==2:
                s2, m2 = minmax_tree(depth + 1)
                if s2==WORST_SCORE:
                    s2 = s
                else:
                    s2 = 1.0 / s2
                d[m].append(s2)
            else:
                s2 = d[m][2]
                m2 = ()
            g.undo_move()
            if s2 > best_score:
                best_score = s2
                best_move = (m,) + m2
    return best_score, best_move
    
def minmax():
    nodes0 = g.node_count
    t0 = time.time()
    s, m = minmax_tree(0)
    nodes = g.node_count - nodes0
    t = time.time() - t0
    print s, move_list_as_string(m), nodes, t, nodes/t

def create_tree_from_minmax(color, less_flag, ht_new = None):
    if ht_new==None:
        ht_new = {}
    if g.has_2_passes():
        return
    key = g.search_key()
    if key not in ht:
        return
    d = ht[key]
    if g.current_board.side==color:
        l = []
        for m in d:
            if len(d[m]) > 2:
                i1, i2 = get_our_count_ind()
                score = (d[m][i1] + FUDGE) / (d[m][i2] + FUDGE)
                l.append((d[m][2], score, m))
        if l:
            l.sort()
            if less_flag:
                d2 = {}
                while l:
                    score, score2, m = l.pop()
                    if score <= 1.0:
                        break
                    if g.make_move(m):
                        d2[m] = d[m]
                        create_tree_from_minmax(color, less_flag, ht_new)
                        g.undo_move()
                if d2:
                    ht_new[key] = d2
            else:
                m = l[-1][2]
                if g.make_move(m):
                    ht_new[key] = {m: d[m]} #leave only top move
                    create_tree_from_minmax(color, less_flag, ht_new)
                    g.undo_move()
    else:
        ht_new[key] = d #leave all moves
        for m in d:
            if g.make_move(m):
                create_tree_from_minmax(color, less_flag, ht_new)
                g.undo_move()
    return ht_new

def create_pruned_tree(name, color, less_flag=False):
    while g.undo_move(): pass
    if color=="W":
        g.make_move((5,5))
    global opponent
    global opponent_color
    global ht
    opponent = name
    opponent_color = color
    ht = load_tree()
    minmax()
    if color=="W":
        color = BLACK
    else:
        color = WHITE
    ht_new = create_tree_from_minmax(color, less_flag)
    fp = open(opening_file("_pruned"), "w")
    cPickle.dump(ht_new, fp)
    fp.close()
    return ht_new

def list_create_pruned_tree(name_list):
    for name in name_list:
        for color in "WB":
            create_pruned_tree(name, color)

def combine_trees(name_list, color, output):
    global opponent
    global opponent_color
    hash_tree = {}
    for name in name_list:
        opponent = name
        opponent_color = color
        fp = open(opening_file("_pruned2"))
        ht2 = cPickle.load(fp)
        fp.close()
        add_count = 0
        for pos in ht2:
            if pos not in hash_tree:
                hash_tree[pos] = ht2[pos]
                add_count += 1
        print name, "added", add_count
    fp = open(output, "w")
    cPickle.dump(hash_tree, fp)
    fp.close()

if __name__=="__main__":
    #create_tree()
    #ht = load_tree()
    random.seed(1)
    g = Game(9)
    cb = g.current_board
