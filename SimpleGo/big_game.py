import string, random, sys, math
import config
from const import *
from utils import *

from block import Block
from eye import Eye
from gothread import Thread
from board import Board
from pos_cache import PositionCache
from game import Game
import play_gtp

def main(size):
    """Play game against itself on given size board.
       Make sgf and images of resulting game.
    """
    idiot_flag = True
    random.seed(2)
    g = Game(size)
    g.init_fast_select_random_no_eye_fill_move()
    for remove_opponent_dead in (False, True):
        g.undo_move()
        g.undo_move()
        while True:
            if idiot_flag:
                move = g.fast_select_random_no_eye_fill_move()
            else:
                move = g.generate_move(remove_opponent_dead=remove_opponent_dead)
            g.make_move(move)
            #if size<=max_size:
            #    print move_as_string(move)
            #print g.current_board
            if idiot_flag:
                lst_lst = g.move_history, g.atari_moves, g.available_moves[WHITE], g.available_moves[BLACK]
            else:
                lst_lst = g.move_history, g.available_moves
            for lst in lst_lst:
                sys.stderr.write("%i " % len(lst))
            if len(g.atari_moves) >= 2:
                sys.stderr.write("\n")
                if size<=max_size:
                    sys.stderr.write("%s\n" % g.move_list_as_string(g.atari_moves))
            else:
                sys.stderr.write("         \r")
            if g.has_2_passes():
                break
        #print g.move_history
        #print g.current_board.goban
        args = (size, size, remove_opponent_dead)
        fp = open("%ix%i_%s.sgf" % args, "w")
        fp.write(str(g))
        fp.close()
        fp = open("%ix%i_bw_%s.pgm" % args, "w")
        fp.write(g.as_image())
        fp.close()
        fp = open("%ix%i_color_%s.ppm" % args, "w")
        fp.write(g.as_color_image())
        fp.close()
    return g

if __name__=="__main__":
    #If this file is executed directly it will play game against itself.
    size = int(sys.argv[1])
    main(size)
