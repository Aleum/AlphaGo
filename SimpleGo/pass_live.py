import sys
import simple_go
from utils import *

start_no = long(sys.argv[1])
end_no = long(sys.argv[2])

fp = open("pass_live.log", "w")

whole_board_flag = False

if whole_board_flag:
    #size = 3
    #limit = 3

    size = 6
    limit = 12
else:
    #size = 2
    #limit = 2

    #size = 3
    #limit = 3

    #size = 4
    #limit = 5

    #size = 5
    #limit = 7

    size = 6
    limit = 11

bits = size**2

if whole_board_flag:
    win_condition = size**2 #whole board win
else:
    win_condition = 1

if not end_no:
    end_no = 2**bits

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()
    fp.write(s)
    fp.flush()

write("Running with size %i with stone limit at %i\n" % (size, limit))
write("from position %s to position %s\n" % (start_no, end_no))
write("Result to screen and to pass_live.log\n")
write("Win condition: %i points\n\n" % win_condition)

best_bit_win = {}
for i in range(limit+1):
    best_bit_win[i] = 1

def create_board(size):
    simple_board = []
    for y in range(size):
        simple_board.append([0]*size)
    return simple_board

def ref1(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-x][y]

def ref2(b2, b1, x, y, size=size):
    b2[x][y] = b1[x][size-1-y]

def ref3(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-x][size-1-y]

def ref4(b2, b1, x, y, size=size):
    b2[x][y] = b1[y][x]

def ref5(b2, b1, x, y, size=size):
    b2[x][y] = b1[y][size-1-x]

def ref6(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-y][x]

def ref7(b2, b1, x, y, size=size):
    b2[x][y] = b1[size-1-y][size-1-x]

def iterate_bit_goban(no, bits=bits):
    x = 1
    y = 1
    for i in xrange(bits):
        if (1L<<i) & no:
            yield x,y
        x += 1
        if x>size:
            x = 1
            y += 1

def binary_str(no):
    s = ""
    while no:
        s = str(no%2) + s
        no = no / 2
    return s

simple_board2 = create_board(size)
no = start_no
while no<=end_no and no<2**bits:
    bit_count = 0
    for i in xrange(bits):
        if (1L<<i) & no:
            bit_count += 1
    if no%1000==0:
        sys.stderr.write("%i\r" % no)
    #print "?", binary_str(no), bit_count
    if bit_count > limit:
        i = 0
        while not ((1L<<i) & no):
            i += 1
        if i > 0:
            #print "skip by", (2**i - 1)
            no += (2**i - 1)
    #print "!", binary_str(no), bit_count
    if bit_count<=limit:
        simple_board = create_board(size)
        for x,y in iterate_bit_goban(no):
            simple_board[x-1][y-1] = 1
        for reflection_function in ref1, ref2, ref3, ref4, ref5, ref6, ref7:
            for x in range(size):
                for y in range(size):
                    reflection_function(simple_board2, simple_board, x, y)
            if simple_board2 < simple_board:
                break
        else:
            b = simple_go.Board(size)
            for x,y in iterate_bit_goban(no):
                b.add_stone(simple_go.BLACK, (x, y))
            score = b.unconditional_score(simple_go.BLACK)
            if score>=best_bit_win[bit_count]:
                write("no: %i, bits: %i, score: %i\n%s\n" % (no, bit_count, score, b))
                best_bit_win[bit_count] = score
    no = no + 1

fp.close()
