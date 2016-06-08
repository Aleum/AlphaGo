# -*- coding: ms949 -*-

import simple_go
import cgos_opening_tree
import version

import popen2
import sys
import string
import time
import random
import os
import traceback
import config
import getopt
import time_settings
import load_sgf

from jobmgr import *
from network import *
import argparse

debug = 1

def get_next_filename(pattern):
    i = 1
    while True:
        name = pattern % i
        if not os.path.exists(name):
            break
        i = i + 1
    return name
    

class Logger:
    def __init__(self, name = "minigo%04i.log"):
        
        log_name = get_next_filename(name)
        self.fp = open(log_name, "w")

    def __getattr__(self, name):
        return getattr(self.fp, name)

    def write(self, s):
        
        self.fp.write(s)
        self.fp.flush()
        
config.debug_output = Logger()

def log(s):
    config.debug_output.write(s)
##    fp = open("game2.log", "a")
##    fp.write(s)
##    fp.close()

def parse_options(player):
    try:
        options, args = getopt.getopt(sys.argv[1:], "h", player.get_cmd_options())
        player.handle_options(options)
    except getopt.GetoptError:
        print "Invalid option"
        player.help_with_cmd_options()
        sys.exit(2)
    

def coords_to_sgf(size, board_coords):
    global debug
    
    board_coords = string.lower(board_coords)
    if board_coords == "pass":
        return ""
    letter = board_coords[0]
    digits = board_coords[1:]
    if letter > "i":
        sgffirst = chr(ord(letter) - 1)
    else:
        sgffirst = letter
    sgfsecond = chr(ord("a") + int(size) - int(digits))
    return sgffirst + sgfsecond
        
def sgf_to_coords(size, sgf_coords):
    #print sgf_coords
    if len(sgf_coords)==0: return "PASS"
    letter = string.upper(sgf_coords[0])
    if letter>="I":
        letter = chr(ord(letter)+1)
    digit = str(ord('a') + int(size) - ord(sgf_coords[1]))
    return letter+digit


class GTP_controller:

    #
    # Class members:
    #   outfile         File to write to
    #   infile          File to read from

    def __init__(self, infile, outfile):
        self.infile  = infile
        self.outfile = outfile
        
        log_name = get_next_filename("gtpb%04i.log")
        self.log_fp = open(log_name, "w")

    def get_cmd(self):
        global debug
        result = ""
        while 1:
            line = self.infile.readline()
            if not line: break
            if self.log_fp:
                self.log_fp.write(">" + line)
                self.log_fp.flush()
            if line=="\n": continue
            result = result + line
            break
        return result
        

    def set_result(self, result):
        global debug
        if debug:
            self.log_fp.write("<"+result)
            self.log_fp.flush()
        self.outfile.write(result)
        self.outfile.flush()
        


class GTP_player:

    # Class members:
    #    slave          GTP_connection
    #    master         GTP_controller

    def __init__(self):
        #if config.use_opening_library:
        #    self.opening_tree = {}
        #    for color in "WB":
        #        self.opening_tree[color + "0"] = cgos_opening_tree.OpeningTree("opening%s_0.dat" % color, None)
        #        self.opening_tree[color] = cgos_opening_tree.OpeningTree("opening%s.dat" % color, None)
        self.engine = simple_go.Game(9)
        self.master = GTP_controller(sys.stdin, sys.stdout)
        self.version = version.number
        #self.name = version.name + version.message
        self.name = version.name
        self.komi = 0.0
        self.handicap = 0
        self.capture_all_dead = False
        log_name = get_next_filename("gtpc%04i.log")
        self.log_fp = open(log_name, "w")
        self.clock = None
        self.move_generated = False
        
        komi = 6.5
        self.engine.set_komi(komi)
        
        # note formatting: follow newline with tab
        self.cmd_options = {"help" : "Can also use '-h'. Displays this message.",
                            "message=" : "Message robot gives on new games\n\tQuotes required for spaces.",
                            "node_limit=" : "Positive integer\n\tSpecifies the normal depth of the search for a 9x9 game.",
                            "manage_time" : "If passed to program, uses time management.",
                            "capture_all_dead" : "If passed to program, will capture all dead before passing"}
        
        self.mode = None
        self.randomcount = 0
        
        print 'ready to setting '
        
        #jobmgr, network 설정.
        self.m_network = network()
        self.m_network.init2()
        
        self.engine.network = self.m_network
        
        self.m_jobmgr = jobmgr2(self.mode)
        
        print 'setting is done'

    def get_cmd_options(self):
        return self.cmd_options.keys()
    
    def help_with_cmd_options(self):
        result = "\n\n"
        for i in self.cmd_options.keys():
            result = result + "--" + string.strip(i, "=") + "\n\t" + self.cmd_options[i] + "\n\n"
        self.master.set_result(result)
    
    def handle_options(self, options):
        for opt, arg in options:
            if opt == "--message":
                self.name = version.name + " " + arg
            if opt == "--node_limit":
                try:
                    newval = string.atoi(arg)
                    config.lambda_node_limit_baseline = newval
                except string.atoi_error:
                    self.master.set_result("\n" + opt + " given is not a number, default used.\n\n")
            if opt == "-h" or opt == "--help":
                self.help_with_cmd_options()
            if opt == "--manage_time":
                config.manage_time = True
            if opt == "--capture_all_dead":
                self.capture_all_dead = True

    def ok(self, result=None):
        if result==None: result = ""
        return "= " + result + "\n\n"

    def error(self, msg):
        return "? " + msg + "\n\n"

    def set_handicap(self, handicap):
        self.handicap = handicap
        self.engine.set_komi(self.komi + self.handicap)        

    def save_sgf(self, prefix):
        sgf_name = get_next_filename(prefix + "%04i.sgf")
        fp = open(sgf_name, "w")
        fp.write(str(self.engine))
        fp.close()

    def boardsize(self, size):
        if size > 9:
            return self.error("Too big size")
        #if size > simple_go.max_size:
        #    return self.error("Too big size")
        
        # clock must be initialized before the engine
        #    otherwise the engine will override any lambda node limit settings
        if config.lambda_node_limit_baseline > 0:
            config.lambda_node_limit = int(config.lambda_node_limit_baseline * 81.0 / (size*size)) - size + 9
        if self.clock is None:
            self.clock = time_settings.Timekeeper()
        else:
            self.clock.set_boardsize(size)

        if len(self.engine.move_history):
            self.save_sgf("size")
        self.engine = simple_go.Game(size)
        
        self.engine.network = self.m_network
        
        self.set_handicap(0.0)
##        if size<=9:
##            #config.debug_tactics = True
##            config.lambda_node_limit = 100
##        elif size<=13:
##            config.lambda_node_limit = 75
##        else:
##            config.lambda_node_limit = 50
        log("="*60 + "\n")
        log("boardsize: %s\n" % size)
        if os.path.exists("break.flag"):
            sys.exit(1)
        self.move_generated = False
        return self.ok("")

    def clear_board(self):
        config.debug_output = Logger()
        return self.boardsize(self.engine.size)

    def check_side2move(self, color):
        if (self.engine.current_board.side==simple_go.BLACK) != (string.upper(color[0])=="B"):
            if self.handicap==0:
                handicap_change = 2
            else:
                handicap_change = 1
            if string.upper(color[0])=="B":
                self.set_handicap(self.handicap + handicap_change)
            else:
                self.set_handicap(self.handicap - handicap_change)
            self.engine.make_move(simple_go.PASS_MOVE)

    def genmove_plain(self, color, remove_opponent_dead=False, pass_allowed=True):
        if config.always_remove_opponent_dead:
            remove_opponent_dead = True
        self.check_side2move(color)
        if config.use_opening_library and not self.engine.opening_tree:
            opening_file = cgos_opening_tree.find_opening_from_web(string.upper(color[0]))
            log("Using opening file: %s\n" % opening_file)
            #self.engine.opening_tree0 = self.opening_tree[string.upper(color[0]) + "0"]
            #self.engine.opening_tree0.game = self.engine
            #self.engine.opening_tree = self.opening_tree[string.upper(color[0])]
            self.engine.opening_tree = cgos_opening_tree.OpeningTree(opening_file, self.engine)
            if self.engine.opening_tree.hash_tree:
                log("Opening file OK\n")
            #self.engine.opening_tree.game = self.engine
        #old code
        #move = self.engine.generate_move(remove_opponent_dead, pass_allowed)
        '''
        move = ()
        move = RESIGN_MOVE
        move = string.lower(simple_go.move_as_string(move, self.engine.size))
        return move
        '''
        
        #print self.engine.move_history
		
        if self.engine.is_end(by_score=True) == True:
            print 'resign:'
            move = ()
            move = RESIGN_MOVE
            move = string.lower(simple_go.move_as_string(move, self.engine.size))
            return move
		
        move = ()
        
        if self.randomcount > len(self.engine.move_history):
            #print 'action by randomcount:'
            move = self.engine.generate_move(remove_opponent_dead, pass_allowed)
        else:
            move = self.m_jobmgr.genmove(self.engine)
            
#         movescore = self.engine.score_move(move)
        
        #print self.engine.move_history
        #print 'move : ' + str(move[0]) + ',' + str(move[1]) + ' movescore : ' + str(movescore)
        
        self.move_generated = True
        
        #print 'genmove 100 : ' + str(move[0]) + ',' + str(move[1])
        move = string.lower(simple_go.move_as_string(move, self.engine.size))
        #print 'genmove 101 : ' + str(move[0]) + ',' + str(move[1])
        self.play_plain(color, move)
        ##print 'genmove 102'
        return move

    def genmove(self, color):
        if os.path.exists("resign.flag"):
            os.remove("resign.flag")
            return self.ok("resign")
        return self.ok(self.genmove_plain(color, remove_opponent_dead=self.capture_all_dead, pass_allowed=True))

    def play_plain(self, color, move):
        #print 'play_plain called'
        self.check_side2move(color)
        self.engine.make_move(simple_go.string_as_move(string.upper(move), self.engine.size))
        if self.engine.play_randomly_initialization_done:
            self.engine.update_fast_random_status()
        log("move made: %s %s\n" % (color, move))
        log(str(self.engine.current_board))
        log("-"*60 + "\n")
        #log(str(self.engine.current_board))
##        self.engine.score_position()
##        log(self.engine.current_board.as_string_with_unconditional_status(analyze=False))
##        log("move: " + move + "\n")
##        log("score: %s unconditional score: W:%i B:%i\n" % (
##            self.final_score_as_string(),
##            self.engine.current_board.unconditional_score(simple_go.WHITE),
##            self.engine.current_board.unconditional_score(simple_go.BLACK)))
##        self.save_sgf("game")

    def play(self, color, move):
        return self.ok(self.play_plain(color, move))

    def place_free_handicap(self, count):
        self.set_handicap(count)
        result = []
        for move in self.engine.place_free_handicap(count):
            move = simple_go.move_as_string(move, self.engine.size)
            result.append(move)
        return self.ok(string.join(result))

    def set_free_handicap(self, stones):
        self.set_handicap(len(stones))
        for i in range(len(stones)):
            if i: self.play_plain("white", "PASS")
            self.play_plain("black", stones[i])
        return self.ok("")

    def final_status_list(self, status):
        self.save_sgf("status")
        self.clock.reset()
        lst = self.engine.final_status_list(status)
        str_lst = []
        for pos in lst:
            str_lst.append(simple_go.move_as_string(pos, self.engine.size))
        return self.ok(string.join(str_lst, "\n"))

    def final_score_as_string(self):
        score = self.engine.current_board.score_position()
        if self.engine.current_board.side==simple_go.BLACK:
            score = -score
        score = score + self.komi + self.handicap
        if score>=0:
            result = "W+%.1f" % score
        else:
            result = "B+%.1f" % -score
        return result

    def final_score(self):
        self.save_sgf("score")
        return self.ok(self.final_score_as_string())

    def genmove_cleanup(self, color):
        return self.ok(self.genmove_plain(color, remove_opponent_dead=True))

    def showboard(self):
        return self.ok(str(self.engine.current_board))

    def mobile_showboard(self, prompt="..."):
        result = self.showboard()
        if self.engine.size > 13:
            lines = string.split(result, "\n")
            result0 = string.join(lines[:-16], "\n")
            result = string.join(lines[-16:], "\n")
            self.master.outfile.write(result0)
            self.master.outfile.flush()
            raw_input(prompt)
        if self.engine.size > 9:
            result = result[:-3] + " "
        self.master.outfile.write(result)
        self.master.outfile.flush()
        return ""

    def save(self):
        fp = open("tmp.sgf", "w")
        fp.write(str(self.engine))
        fp.close()
        return self.ok()

    def load(self):
        self.engine = load_sgf.load_file("tmp.sgf")
        return self.ok()

    def p(self, color, move):
        try:
            self.play(color, move)
        except:
            traceback.print_exc(None, self.master.outfile)
            return self.error("Illegal move")
        if string.lower(color[0])=="b":
            ocolor = "white"
        else:
            ocolor = "black"
        result = self.genmove(ocolor)
        self.save()
        result = result[:-2] + " "
        self.mobile_showboard(result)
        return result

    def undo(self):
        if self.engine.undo_move():
            return self.ok()
        return self.error("no moves")

    def list_commands(self):
        result = string.join(("list_commands",
                              "boardsize",
                              "name",
                              "version",
                              "quit",
                              "clear_board",
                              "place_free_handicap",
                              "fixed_handicap",
                              "set_free_handicap",
                              "play",
                              "final_status_list",
                              "kgs-genmove_cleanup",
                              "showboard",
                              "protocol_version",
                              "komi",
                              "final_score",
                              "kgs-time_settings",
                              "time_settings",
                              "time_left",
                              ), "\n")
        return self.ok(result)
        
    def relay_cmd_and_reply(self):
        cmd_line = self.master.get_cmd()
        if not cmd_line: return 0
        cmd_lst = string.split(cmd_line)
        cmd = cmd_lst[0]     #Ctrl-C cancelling shows "list index out of range" error here in the log (keep this comment)
        if cmd and cmd[0] in string.digits:
            reply_no = cmd
            cmd_lst = cmd_lst[1:]
            if not cmd_lst: return 0
            cmd = cmd_lst[0]
        else:
            reply_no = ""
        if cmd=="version":                              
            result = "= " + self.version + "\n\n"
        elif cmd=="name":
            result = "= " + self.name + "\n\n"
        elif cmd=="protocol_version":
            result = "= 2\n\n"
        elif cmd=="komi":
            self.komi = float(cmd_lst[1])
            self.engine.set_komi(self.komi + self.handicap)
            result = "=\n\n"
        elif cmd=="genmove_white":
            result = self.genmove("white")
        elif cmd=="genmove_black":
            result = self.genmove("black")
        elif cmd=="genmove":
            result = self.genmove(cmd_lst[1])
        elif cmd=="boardsize":
            result = self.boardsize(int(cmd_lst[1]))
        elif cmd=="list_commands":
            result = self.list_commands()
        elif cmd=="play":
            result = self.play(cmd_lst[1], cmd_lst[2])
        elif cmd=="clear_board":
            result = self.clear_board()
        elif cmd=="place_free_handicap":
            result = self.place_free_handicap(int(cmd_lst[1]))
        elif cmd=="fixed_handicap":
            result = self.place_free_handicap(int(cmd_lst[1]))
        elif cmd=="set_free_handicap":
            result = self.set_free_handicap(cmd_lst[1:])
        elif cmd=="final_status_list":
            result = self.final_status_list(cmd_lst[1])
        elif cmd=="kgs-genmove_cleanup":
            result = self.genmove_cleanup(cmd_lst[1])
        elif cmd=="showboard":
            result = self.showboard()
        elif cmd=="-":
            result = self.mobile_showboard()
        elif cmd=="gb":
            result = self.genmove("black")
        elif cmd=="gw":
            result = self.genmove("white")
        elif cmd=="pb":
            result = self.play("black", cmd_lst[1])
        elif cmd=="pw":
            result = self.play("white", cmd_lst[1])
        elif cmd=="save":
            result = self.save()
        elif cmd=="load":
            result = self.load()
        elif cmd=="und":
            result = self.undo()
        elif cmd=="p":
            result = self.p("black", cmd_lst[1])
        elif cmd=="final_score":
            result = self.final_score()
        elif cmd=="time_left":
            if self.move_generated:
                result = self.ok(self.clock.time_left(cmd_lst[1:]))
            else:
                result = self.ok()
        elif cmd=="kgs-time_settings":
            result = self.ok(self.clock.kgs_set_time(cmd_lst[1:]))
        elif cmd=="time_settings":
            result = self.ok(self.clock.set_time(cmd_lst[1:]))
        elif cmd=="quit":
            result = "=\n\n"
        else:
            self.log_fp.write("Unhandled command:" + cmd_line)
            self.log_fp.flush()
            result = self.error("Unknown command")
        if reply_no:
            result = result[0] + reply_no + result[1:]
        self.master.set_result(result)
        return cmd!="quit"
    
    def loop(self):
        try:
            while self.relay_cmd_and_reply():
                pass
        except:
            self.log_fp.write("error : ")
            traceback.print_exc(None, self.log_fp)
            self.log_fp.flush()
            raise

'''
DL : default
SL : SL
RL : RL
FR : fast rollout
'''
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-mode', nargs=1, required=False, dest='mode')
    parser.add_argument('-randomcount', nargs=1, required=False, dest='randomcount')
    args = parser.parse_args()
    if args.mode is not None:
        if args.mode[0] is not None:
            mode = args.mode[0]
    else:
        mode = 'DL'
        
    if args.randomcount is not None:
        if args.randomcount[0] is not None:
            randomcount = int(args.randomcount[0])
    else:
        randomcount = 0
    
    print 'mode : ' + mode
        
    player = GTP_player()
    #parse_options(player)
    player.mode = mode
    player.name = player.name + '_' + mode
    player.randomcount = randomcount
    
    player.loop()
    
