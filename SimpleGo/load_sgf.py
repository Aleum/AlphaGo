import string, simple_go, re, sys, time

def sgf_to_coords(size, sgf_coords):
    #print sgf_coords
    if len(sgf_coords)==0: return "PASS"
    letter = string.upper(sgf_coords[0])
    if letter>="I":
        letter = chr(ord(letter)+1)
    digit = str(ord('a') + int(size) - ord(sgf_coords[1]))
    return letter+digit

#def sgf2tuple(size, move):
#    coords = sgf_to_coords(size, move)
#    return simple_go.string_as_move(coords, size)

def sgf2number(sgf):
    no = 0
    #print "-"*60
    #print sgf
    while len(sgf)>0:
        ch = sgf[0]
        sgf = sgf[1:]
        if 'a'<=ch<='z':
            no = 52 * no + ord(ch)-ord('a')
        else:
            no = 52 * no + ord(ch)-ord('A') + 26
        #print ch,sgf,no
    return no

def sgf2tuple(size, move):
    if len(move)==0:
        return simple_go.PASS_MOVE
    coordsize = len(move)/2
    no1 = sgf2number(move[:coordsize])
    no2 = sgf2number(move[coordsize:])
    return no1+1, size-no2

def load_file(name, game_class = simple_go.Game):
    s = open(name).read()
    parts = string.split(s, ";")
    header = parts[1]
    moves = parts[2:]
    sz = re.match(r".*SZ\[(\d+)\].*", header, re.DOTALL)
    if sz:
        g = game_class(int(sz.group(1)))
    else:
        raise ValueError, "no size tag"
    komi = re.match(r".*KM\[([\d\.]+)\].*", header, re.DOTALL)
    if komi:
        komi = float(komi.group(1))
        g.set_komi(komi)
    ha = re.match(r".*AB(.*?)P.*", header, re.DOTALL)
    if ha:
        for move in string.split(ha.group(1)[1:-1], "]["):
            if g.current_board.side==simple_go.WHITE:
                g.make_move(simple_go.PASS_MOVE)
            if not g.make_move(sgf2tuple(g.size, move)):
                raise ValueError, move
    for move_str in moves:
        m = re.match(r".*?(\w+)\[(.*?)\](.*)", move_str, re.DOTALL)
        if m:
            color = m.group(1)
            move = m.group(2)
            rest = m.group(3)
            if color in ("B", "W"):
                if (g.current_board.side==simple_go.BLACK) != (string.upper(color[0])=="B"):
                    g.make_move(simple_go.PASS_MOVE)
                if not g.make_move(sgf2tuple(g.size, move)):
                    raise ValueError, move
            elif color in ("AW", "AB"):
                while move and color in ("AW", "AB"):
                    if (g.current_board.side==simple_go.BLACK) != (string.upper(color[1])=="B"):
                        g.make_move(simple_go.PASS_MOVE)
                    if not g.make_move(sgf2tuple(g.size, move)):
                        raise ValueError, move
                    m = re.match(r"\[(.*?)\](.*)", rest, re.DOTALL)
                    if m:
                        move = m.group(1)
                        rest = m.group(2)
                    else:
                        m = re.match(r"(\w+)\[(.*?)\](.*)", rest, re.DOTALL)
                        if m:
                            color = m.group(1)
                            move = m.group(2)
                            rest = m.group(3)
                        else:
                            move = None
    return g

def test_time_usage(file_name, color):
    g = load_file(file_name)
    moves = g.move_history[:]
    while g.undo_move():
        pass
    t0 = time.time()
    for move in moves:
        move_no = len(g.move_history) + 1
        if g.current_board.side==simple_go.BLACK:
            print "Black to move"
        else:
            print "White to move"
        print "Current move:", move_no, simple_go.move_as_string(move)
        if g.current_board.side==color:
            print "Generated move:", move_no, simple_go.move_as_string(g.generate_move())
        g.make_move(move)
        print
        print "="*60
        print
    t1 = time.time()
    print "Total time usage:", t1-t0

if __name__=="__main__":
    g = load_file(sys.argv[1])
