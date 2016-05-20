import sys, string, time
import load_sgf, utils, const
use_c = False
if use_c:
    import cpatterns

"""
Any pattern allowed, for example:
(((0, 0), '.'), ((0, 1), '.'), ((1, 3), 'O'), ((2, 2), 'X')) 30432 0.0%

Diagram of above:
.
.
  X
 O

Anything is allowed in empty space.


This code needs documentation and refactoring.
Its otherwise unfinished too :-(
"""

class Patterns:
    def __init__(self, size = 19):
        self.size = size
        self.pos_lst = []
        for y in range(0, size + 2):
            for x in range(0, size + 2):
##                if not 1 <= x <= size and not 1 <= y <= size:
##                    continue
                self.pos_lst.append((x, y))
        print len(self.pos_lst)

        self.pattern1_dict = {}
        self.pattern2_dict = {}
        self.pattern3_dict = {}
        self.pattern4_dict = {}
        self.pattern5_dict = {}
        self.pattern6_dict = {}
        self.pattern7_dict = {}

    def update_pattern1(self, cboard):
        if use_c:
            cpatterns.update(self.board2string(cboard), self.size, 1)
            return
        for pos in self.pos_lst:
            value = cboard.get_goban(pos)
            self.pattern1_dict[value] = self.pattern1_dict.get(value, 0) + 1

    def update_pattern2(self, cboard):
        if use_c:
            cpatterns.update(self.board2string(cboard), self.size, 2)
            return
        for pos1 in self.pos_lst:
            #print pos1,
            #sys.stdout.flush()
            value1 = cboard.get_goban(pos1)
            for pos2 in self.pos_lst:
                if pos1==pos2:
                    continue
                value2 = cboard.get_goban(pos2)
                pattern = ((pos1, value1), (pos2, value2))
                pattern = self.normalize_pattern(pattern)
                self.pattern2_dict[pattern] = self.pattern2_dict.get(pattern, 0) + 1
        #print

    def update_pattern3(self, cboard):
        if use_c:
            t0 = time.time()
            cpatterns.update(self.board2string(cboard), self.size, 3)
            print time.time() - t0
            return
        for pos1 in self.pos_lst:
            #print pos1,
            #sys.stdout.flush()
            value1 = cboard.get_goban(pos1)
            for pos2 in self.pos_lst:
                if pos1==pos2:
                    continue
                value2 = cboard.get_goban(pos2)
                for pos3 in self.pos_lst:
                    if pos3 in (pos2, pos1):
                        continue
                    value3 = cboard.get_goban(pos3)
                    pattern = ((pos1, value1), (pos2, value2), (pos3, value3))
                    pattern = self.normalize_pattern(pattern)
                    self.pattern3_dict[pattern] = self.pattern3_dict.get(pattern, 0) + 1
        #print

    def update_pattern4(self, cboard):
        if use_c:
            t0 = time.time()
            cpatterns.update(self.board2string(cboard), self.size, 4)
            print time.time() - t0
            return
        else:
            raise ValueError, "not defined for Python currently"
        
    def update_pattern5(self, cboard):
        if use_c:
            t0 = time.time()
            cpatterns.update(self.board2string(cboard), self.size, 5)
            print time.time() - t0
            return
        else:
            raise ValueError, "not defined for Python currently"
        
    def update_pattern6(self, cboard):
        if use_c:
            t0 = time.time()
            cpatterns.update(self.board2string(cboard), self.size, 6)
            print time.time() - t0
            return
        else:
            raise ValueError, "not defined for Python currently"
        
    def update_pattern7(self, cboard):
        if use_c:
            t0 = time.time()
            cpatterns.update(self.board2string(cboard), self.size, 7)
            print time.time() - t0
            return
        else:
            raise ValueError, "not defined for Python currently"
        
    def board2string(self, cboard):
        s_lst = []
        for pos in self.pos_lst:
            value = cboard.get_goban(pos)
            s_lst.append(value)
        return string.join(s_lst, "")

    def minimize(self, pattern0):
        min_x = self.size + 2
        min_y = self.size + 2
        for pos, value in pattern0:
            min_x = min(min_x, pos[0])
            min_y = min(min_y, pos[1])
        pattern = []
        for i in range(len(pattern0)):
            (x, y), value = pattern0[i]
            x = x - min_x
            y = y - min_y
            pattern.append(((x, y), value))
        return tuple(pattern)

    def box_size(self, pattern):
        size = -1
        for (x, y), value in pattern:
            size = max(size, x, y)
        return size + 1

    def sort_pattern(self, pattern):
        pattern = list(pattern)
        pattern.sort()
        return tuple(pattern)

    def normalize_pattern(self, pattern0):
        best_pattern = None
        all_mirrors = []
        pattern1 = self.minimize(pattern0)
        pattern1 = self.sort_pattern(pattern1)
        #size = self.box_size(pattern1)
        #for value_mirror in (False, True):
        #    for normalize_color in (False, True):
        for value_mirror in (False, ):
            for normalize_color in (False, True):
                for ref in utils.all_ref_coords:
                    pattern = []
                    min_x = self.size + 2
                    min_y = self.size + 2
                    for pos, value in pattern1:
                        #pos = ref(pos, size - 2)
                        pos = ref(pos, self.size)
                        pattern.append((pos, value))
                        min_x = min(min_x, pos[0])
                        min_y = min(min_y, pos[1])
                    for i in range(len(pattern)):
                        (x, y), value = pattern[i]
                        x = x - min_x
                        y = y - min_y
                        if normalize_color:
                            if value==const.BLACK:
                                value = const.WHITE
                            elif value==const.WHITE:
                                value = const.BLACK
                        pattern[i] = (x, y), value
                    pattern = self.sort_pattern(pattern)
                    if value_mirror:
                        pattern = list(pattern)
                        (x0, y0), value0 = pattern[0]
                        (x1, y1), value1 = pattern[1]
                        pattern = ((x0, y0), value1), ((x1, y1), value0)
                        pattern = tuple(pattern)
                    all_mirrors.append((pattern, ref, normalize_color, value_mirror))
                    if best_pattern == None or pattern < best_pattern:
                        if value_mirror:
                            import pdb; pdb.set_trace()
                        best_pattern = pattern
        #if best_pattern in ((((0, 0), '.'), ((0, 1), 'O')),
        #                    (((0, 0), '.'), ((1, 2), 'O'))):
        #    print pattern0, best_pattern
        return best_pattern

    def print_statistics(self, pattern_dict = None, print_image = False):
        if use_c:
            #pattern_dict = cpatterns.dump(self.size, 50)
            pattern_dict = cpatterns.dump(self.size, 1000000000)
            #pattern_dict = self.pattern1_dict
        total_count = sum(pattern_dict.values())
        lst = []
        for value, count in pattern_dict.items():
            lst.append((count, value))
        lst.sort()
        lst.reverse()
        for count, value in lst:
            print "%s %i %.1f%%" % (value, count, 100.0 * count / total_count)
            if print_image:
                print pattern_as_image(value)

def pattern_as_image(pattern):
    s = []
    screen = {}
    max_x = -1
    max_y = -1
    for (x, y), color in pattern:
        screen[x, y] = color
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    for y in range(max_y+1):
        for x in range(max_x+1):
            s.append(screen.get((x,y), " "))
        s.append("\n")
    return string.join(s, "")



def analyse_patterns(positions, pattern_method):
    for cboard in positions():
        pattern_method(cboard)

file_names = "test/patterns/Mei-1981-%i.sgf"

def one_position(file_name = file_names % 1):
    g = load_sgf.load_file(file_name)
    yield g.current_board

def one_game(file_name = file_names % 1):
    g = load_sgf.load_file(file_name)
    cboard = g.current_board
    while True:
        print "#", file_name, len(g.move_history)
        sys.stdout.flush()
        yield cboard
        if not g.undo_move():
            break

def all_games(dummy_file_name = None):
    for i in range(1, 4+1):
        file_name = file_names % i
        for cboard in one_game(file_name):
            yield cboard

def count_patterns():
    for positions in (one_position, one_game, all_games):
        p = Patterns()
        print positions.__name__
        analyse_patterns(positions, p.update_pattern1)
        p.print_statistics(p.pattern1_dict)
        print
        sys.stdout.flush()
        analyse_patterns(positions, p.update_pattern2)
        p.print_statistics(p.pattern2_dict)
        print
##        sys.stdout.flush()
##        analyse_patterns(positions, p.update_pattern3)
##        p.print_statistics(p.pattern3_dict)
##        print
        print "-"*60
        sys.stdout.flush()
    return p

def count_patterns_file(size, file_name, how_many = one_position):
    print_image = False
    p = Patterns(size)
    analyse_patterns(lambda :how_many(file_name), p.update_pattern1)
    p.print_statistics(p.pattern1_dict, print_image)
    print "-"*60
    analyse_patterns(lambda :how_many(file_name), p.update_pattern2)
    p.print_statistics(p.pattern2_dict, print_image)
    print "-"*60
    analyse_patterns(lambda :how_many(file_name), p.update_pattern3)
    p.print_statistics(p.pattern3_dict, print_image)
    print "-"*60
    analyse_patterns(lambda :how_many(file_name), p.update_pattern4)
    p.print_statistics(p.pattern4_dict, print_image)
    print "-"*60
    analyse_patterns(lambda :how_many(file_name), p.update_pattern5)
    p.print_statistics(p.pattern5_dict, print_image)
    print "-"*60
    analyse_patterns(lambda :how_many(file_name), p.update_pattern6)
    p.print_statistics(p.pattern6_dict, print_image)
    print "-"*60
    analyse_patterns(lambda :how_many(file_name), p.update_pattern7)
    p.print_statistics(p.pattern7_dict, print_image)

def all_adjacent(pattern):
    add_lst = []
    for pos, value in pattern:
        add_lst.append(pos)

    seen_dict = {}
    seen_dict[add_lst.pop()] = True

    while add_lst:
        found = None
        for x, y in add_lst:
            for pos2 in ((x,y+1), (x+1,y), (x,y-1), (x-1,y)):
                if pos2 in seen_dict:
                    found = x, y
                    break
            if found:
                break
        if not found:
            return False
        add_lst.remove(found)
        seen_dict[found] = True

    return True

def make_1_adjacent_group(add_lst):
    add_lst = add_lst[:]
    seen_dict = {}
    seen_dict[add_lst.pop()] = True

    while add_lst:
        found = None
        for x, y in add_lst:
            for pos2 in ((x,y+1), (x+1,y), (x,y-1), (x-1,y)):
                if pos2 in seen_dict:
                    found = x, y
                    break
            if found:
                break
        if not found:
            break
        add_lst.remove(found)
        seen_dict[found] = True

    return seen_dict.keys(), add_lst

def adjacent_group_count(pattern):
    add_lst = []
    for pos, value in pattern:
        add_lst.append(pos)

    group_count = 0
    while add_lst:
        group, add_lst = make_1_adjacent_group(add_lst)
        group_count = group_count + 1
    return group_count

def stone_count(pattern):
    stone_count = 0
    for pos, value in pattern:
        if value in (const.BLACK, const.WHITE):
            stone_count = stone_count + 1
    return stone_count


def has_stone(pattern):
    for pos, value in pattern:
        if value in (const.BLACK, const.WHITE):
            return True
    return False

#changed this constant in const.EDGE, for now keeping compatibility with old
NONSTANDARD_EDGE = "-"
def non_edge_count(pattern):
    count = 0
    for pos, value in pattern:
        if value != NONSTANDARD_EDGE:
            count = count + 1
    return count

def write_sorted(file_name, out_lst, as_image, total_count4):
    fp = open(file_name, "w")
    out_lst.sort()
    out_lst.reverse()
    for count, pattern in out_lst:
        fp.write("%s %i %.1f%%\n" % (pattern, count, 100.0 * count / total_count4))
        if as_image:
            fp.write(pattern_as_image(pattern) + "\n")
    fp.close()

def print_c_pattern_output(file_name, filter_func = lambda count,pattern:True):
    count_dict = {}
    count_dict2 = {}
    count_dict3 = {}
    count_dict4 = {}
    count_dict5 = {}
    count_flag = False
    out_lst = []
    #out_lst2 = []
    total_count4 = 0
    for line in open(file_name):
        if count_flag:
            count = eval(line)
            #print pattern, count
            #print pattern_as_image(pattern)
            #print adjacent_group_count(pattern), stone_count(pattern), non_edge_count(pattern)
            plen = len(pattern)
            count_dict[plen] = count_dict.get(plen, 0) + 1
            incr = 10
            current = 10
            while count > current:
                current += incr
                if str(current)[0]=='1':
                    incr *= 10
            key2 = plen, current
            count_dict2[key2] = count_dict2.get(key2, 0) + 1
            count_dict3[key2] = count_dict3.get(key2, 0) + count
            key3 = plen, current, adjacent_group_count(pattern), stone_count(pattern), non_edge_count(pattern)
            count_dict4[key3] = count_dict4.get(key3, 0) + 1
            count_dict5[key3] = count_dict5.get(key3, 0) + count
            #ok = filter_func(count, pattern)
            #if ok:
            #    count_dict4[key2] = count_dict4.get(key2, 0) + 1
            #    count_dict5[key2] = count_dict5.get(key2, 0) + count
            count_flag = False
            if plen==7:
                total_count4 += count
                out_lst.append((count, pattern))
            #    if ok and len(out_lst) <= 1000000:
            #        out_lst.append((count, pattern))
            #    #if count >= 10000:
            #    #    out_lst.append((count, pattern))
            #    #if all_adjacent(pattern):
            #    #    out_lst2.append((count, pattern))
        if line[0]=='(':
            pattern = eval(line)
            count_flag = True
        if len(out_lst)==1000000:
            break
    print count_dict
    print count_dict2
    print count_dict3
    print count_dict4
    print count_dict5
    write_sorted("tmp.out", out_lst, True, total_count4)
    #write_sorted("tmp2.out", out_lst2, True, total_count4)

def print_ordered_statistics(dict):
    keys = dict.keys()
    keys.sort()
    total_sum = {}
    for key in keys:
        total_sum[key[0]] = total_sum.get(key[0], 0) + dict[key]
    last_key0 = None
    for key in keys:
        if key[0]!=last_key0:
            current_sum = 0.0
            last_key0 = key[0]
            print
        current_sum += dict[key]
        print "%s %s %.2f%% %i %.2f%%" % (key, dict[key],
                                100.0 * dict[key] / total_sum[key[0]],
                                current_sum,
                                100.0 * current_sum / total_sum[key[0]])

def read_c_pattern_statistics(file_name):
    fp = open(file_name)
    count_dict = eval(fp.readline())
    count_dict2 = eval(fp.readline())
    count_dict3 = eval(fp.readline())
    count_dict4 = eval(fp.readline())
    count_dict5 = eval(fp.readline())
    return count_dict, count_dict2, count_dict3, count_dict4, count_dict5

def print_c_pattern_statistics(file_name):
    count_dict, count_dict2, count_dict3, count_dict4, count_dict5 = read_c_pattern_statistics(file_name)
    print count_dict
    print
    print_ordered_statistics(count_dict2)
    print
    print_ordered_statistics(count_dict3)
    print
    print_ordered_statistics(count_dict4)
    print
    print_ordered_statistics(count_dict5)
    print

def print_c_pattern_statistics2(file_name):
    count_dict, count_dict2, count_dict3, count_dict4, count_dict5 = read_c_pattern_statistics(file_name)
    d = count_dict4
    d2 = {}
    for key in d.keys():
        size, pattern_count, blocks, stones, no_edge = key
        key2 = size, blocks, stones, no_edge
        key2 = (size, blocks), -pattern_count
        key2 = size, blocks
        d2[key2] = d2.get(key2, 0) + d[key]
    print_ordered_statistics(d2)

if __name__=="__main__":
    p = count_patterns()
    #p = count_patterns_file(9, "test/patterns/11113.sgf")
    #p = count_patterns_file(9, "test/patterns/11113.sgf", one_game)
    #p = count_patterns_file(9, "test/patterns/Mei-1981-1.sgf", one_game)

    #print_c_pattern_output(sys.argv[1], lambda count,pattern:has_stone(pattern))
    #print_c_pattern_statistics(sys.argv[1])
    #print_c_pattern_statistics2(sys.argv[1])
    pass
