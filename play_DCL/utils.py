import string
from const import *
import config

def number2string(no):
    if no<len(x_coords_string):
        return x_coords_string[no]
    else:
        a,b = divmod(no, len(x_coords_string))
        return number2string(a-1) + number2string(b)
    

def move_as_string(move, board_size = 1):
    """convert move tuple to string
       example: (2, 3) -> B3
    """
    if move==PASS_MOVE: return "PASS"
    elif move==UNDO_MOVE: return "UNDO"
    elif move==NO_MOVE: return "NONE"
    elif move==RESIGN_MOVE: return "RESIGN"
    x, y = move
    return number2string(x-1) + str(y)
    #return x_coords_string[x-1] + str(y)

def string_as_move(m, size = 1):
    """convert string to move tuple
       example: B3 -> (2, 3)
    """
    if m=="PASS": return PASS_MOVE
    elif m=="UNDO": return UNDO_MOVE
    elif m=="NONE": return NO_MOVE
    elif m=="RESIGN": return RESIGN_MOVE
    x = string.find(x_coords_string, m[0]) + 1
    y = int(m[1:])
    return x,y

def string_as_move_list(str):
    #return map(string_as_move, string.split(str))
    moves = []
    for s in string.split(str):
        moves.append(string_as_move(s))
    return moves

def move_list_as_string(m_lst, size = 1):
    s_lst = []
    for m in m_lst:
        s_lst.append(move_as_string(m, size))
    return string.join(s_lst)

def single_number2sgf(no):
    if no >= 26:
        return chr(ord("A") + no - 26)
    else:
        return chr(ord("a") + no)

def number2sgf(no):
    if no<52:
        return single_number2sgf(no)
    else:
        a,b = divmod(no, 52)
        return number2sgf(a) + number2sgf(b)

def move_as_sgf(move, board_size):
    if move==PASS_MOVE: return ""
    sgf1 = number2sgf(move[0] - 1)
    sgf2 = number2sgf(board_size - move[1])
    sgfsize = len(number2sgf(board_size - 1))
    sgf1 = "a"*(sgfsize - len(sgf1)) + sgf1
    sgf2 = "a"*(sgfsize - len(sgf2)) + sgf2
    return sgf1 + sgf2

def union_list(lst1, lst2):
    """union of arguments
       works with both list and dictionary
    """
    common = []
    for pos in lst1:
        if pos in lst2:
            common.append(pos)
    return common

union_dict = union_list

def list2dict(lst, default_value=True):
    return {}.fromkeys(lst, default_value)

def taxi_distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x2-x1) + abs(y2-y1)

def ref_coords0((x, y), size):
    return x, y

def ref_coords1((x, y), size):
    return size+1-x, y

def ref_coords2((x, y), size):
    return x, size+1-y

def ref_coords3((x, y), size):
    return size+1-x, size+1-y

def ref_coords4((x, y), size):
    return y, x

def ref_coords5((x, y), size):
    return y, size+1-x

def ref_coords6((x, y), size):
    return size+1-y, x

def ref_coords7((x, y), size):
    return size+1-y, size+1-x

all_ref_coords = (ref_coords0, ref_coords1, ref_coords2, ref_coords3, ref_coords4, ref_coords5, ref_coords6, ref_coords7)

def goban2ref_board(board):
    simple_board = []
    for y in range(board.size):
        simple_board.append([" "]*board.size)
    for pos in board.iterate_goban():
        x, y = pos[0]-1, pos[1]-1
        simple_board[x][y] = board.goban[pos]
    return simple_board

def handicap_list(size, count):
    if size in (9, 13, 19) and 2<=count<=9:
        handicap_as_string = {9: {2: "G7 C3",
                                  3: "C7 G7 C3",
                                  4: "C7 G7 C3 G3",
                                  5: "C7 G7 E5 C3 G3",
                                  6: "C7 G7 C5 G5 C3 G3",
                                  7: "C7 G7 C5 E5 G5 C3 G3",
                                  8: "C7 E7 G7 C5 G5 C3 E3 G3",
                                  9: "C7 E7 G7 C5 E5 G5 C3 E3 G3"},
                              13: {2: "K10 D4",
                                   3: "D10 K10 D4",
                                   4: "D10 K10 D4 K4",
                                   5: "D10 K10 G7 D4 K4",
                                   6: "D10 K10 D7 K7 D4 K4",
                                   7: "D10 K10 D7 G7 K7 D4 K4",
                                   8: "D10 G10 K10 D7 K7 D4 G4 K4",
                                   9: "D10 G10 K10 D7 G7 K7 D4 G4 K4"},
                              19: {2: "Q16 D4",
                                   3: "D16 Q16 D4",
                                   4: "D16 Q16 D4 Q4",
                                   5: "D16 Q16 K10 D4 Q4",
                                   6: "D16 Q16 D10 Q10 D4 Q4",
                                   7: "D16 Q16 D10 K10 Q10 D4 Q4",
                                   8: "D16 K16 Q16 D10 Q10 D4 K4 Q4",
                                   9: "D16 K16 Q16 D10 K10 Q10 D4 K4 Q4"}}
        return string.split(handicap_as_string[size][count])
    else:
        return []


def shape_score(stone_count, liberties_count):
    return stone_count * liberties_count / (stone_count*2+2.0)

def deb():
    import pdb; pdb.pm()

def stop():
    import pdb; pdb.set_trace()

def dprintnl(*lst):
    """similar to print statement, but output goes to debug file (which by default is sys.stderr): adds newline"""
    s_lst = map(str, lst)
    config.debug_output.write(string.join(s_lst) + "\n")

def dprintsp(*lst):
    """similar to print statement, but output goes to debug file (which by default is sys.stderr): adds spoace"""
    s_lst = map(str, lst)
    config.debug_output.write(string.join(s_lst) + " ")
