# -*- coding: cp1252 -*-
#! /usr/bin/env python

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This program is distributed with GNU Go, a Go program.        #
#                                                               #
# Write gnugo@gnu.org or see http://www.gnu.org/software/gnugo/ #
# for more information.                                         #
#                                                               #
# Copyright 1999, 2000, 2001, 2002, 2003 and 2004               #
# by the Free Software Foundation.                              #
#                                                               #
# This program is free software; you can redistribute it and/or #
# modify it under the terms of the GNU General Public License   #
# as published by the Free Software Foundation - version 2.     #
#                                                               #
# This program is distributed in the hope that it will be       #
# useful, but WITHOUT ANY WARRANTY; without even the implied    #
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR       #
# PURPOSE.  See the GNU General Public License in file COPYING  #
# for more details.                                             #
#                                                               #
# You should have received a copy of the GNU General Public     #
# License along with this program; if not, write to the Free    #
# Software Foundation, Inc., 59 Temple Place - Suite 330,       #
# Boston, MA 02111, USA.                                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# some comments (like above) and
# lots of code copied from twogtp.py from gnugo-3.6-pre4
# additions/changes by Aloril 2004

# minor changes by Blubb Fallo 2004

# Alori modified to work with simple_go.py

# Aloril again modified to work with very simple implementation of gtp
# together with better implementation of gtp like GNU Go 3.6.
# Need only boardsize, komi, reg_genmove, play and gtp_play commands from simple gtp implementation.

import popen2
import sys
import string
import time
import os
import traceback
import utils
import simple_go
import config
from play_gtp import get_next_filename, Logger, log
config.debug_flag = False

debug = 1

##def log(s):
##    fp = open("game1.log", "a")
##    fp.write(s)
##    fp.close()

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


class GTP_connection:

    #
    # Class members:
    #   outfile         File to write to
    #   infile          File to read from

    def __init__(self, command):
        try:
            infile, outfile = popen2.popen2(command)
        except:
            print "popen2 failed"
            sys.exit(1)
        self.infile  = infile
        self.outfile = outfile
        log_name = get_next_filename("gtpa%04i.log")
        self.log_fp = open(log_name, "w")
        self.log_fp.write(command+"\n")
        self.log_fp.flush()
        
    def exec_cmd(self, cmd):
        if cmd[-1]!="\n":
            cmd = cmd + "\n\n"
        self.outfile.write(cmd)
        self.outfile.flush()
        if self.log_fp:
            self.log_fp.write("Time: %f\n" % time.time())
            self.log_fp.write(cmd + "\n\n")
            self.log_fp.flush()
        result = ""
        while 1:
            line = self.infile.readline()
            if not line: break
            if not result and line=="\n": continue
            if self.log_fp:
                self.log_fp.write(line)
                self.log_fp.flush()
            result = result + line
            if line=="\n": break

        return result
        


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

    def __init__(self, command1, command2, name, version):
        self.engine_command = command1
        self.engine = GTP_connection(self.engine_command)
        self.simple_engine = simple_go.Game(19)
        self.slave = GTP_connection(command2)
        self.master = GTP_controller(sys.stdin, sys.stdout)
        self.version = version
        self.name = name
        self.time_delay = False
        self.time = 600
        # total number of gtpc-logfiles
        log_name = get_next_filename("gtpc%04i.log")
        self.log_fp = open(log_name, "w")
        self.size = 19

    def ok(self, result=None):
        if result==None: result = ""
        return "= " + result + "\n\n"

    def save_sgf(self, prefix):
        sgf_name = get_next_filename(prefix + "%04i.sgf")
        fp = open(sgf_name, "w")
        fp.write(str(self.simple_engine))
        fp.close()

    def boardsize(self, size):
        if size<9 or size>19:
            return "? unacceptable size\n\n"
        self.size = size
        self.engine.exec_cmd("quit")
        self.engine = GTP_connection(self.engine_command)
        result = self.engine.exec_cmd("boardsize " + str(size))
        if result[0]=="?":
            return result
        result = self.engine.exec_cmd("clear_board")
        self.slave.exec_cmd("boardsize " + str(size))
        self.slave.exec_cmd("clear_board")
        if len(self.simple_engine.move_history):
            self.save_sgf("size")
        self.simple_engine = simple_go.Game(size)
        if os.path.exists("break.flag"):
            sys.exit(1)
        return self.ok()

    def clear_board(self):
        return self.boardsize(self.size)

    def time_settings(self, parameters):
        self.time = int(parameters[0])

    def time_left(self, parameters):
        self.time = int(parameters[1])

    def play_gg(self, color, move):
        result = self.slave.exec_cmd("play " + color + " " + move)
        log("gg result: " + str(result) + "\n")
        return result

    def genmove_plain(self, color, pass_allowed=1):
        t0 = time.time()
        move = self.engine.exec_cmd("reg_genmove " + color)
        if move[0]=="=": move = move[2:]
        while move and move[-1]=="\n": move = move[:-1]
        if string.upper(move[:4])=="PASS" or move[:2]=="??":
            move = self.slave.exec_cmd("reg_genmove " + color)
            if move[0]=="=": move = move[2:]
            while move and move[-1]=="\n": move = move[:-1]
            log("overruled pass with: " + move + "\n")
        result = self.play_plain(color, move)
        if result[0]=="?":
            move = self.slave.exec_cmd("reg_genmove " + color)
            if move[0]=="=": move = move[2:]
            while move and move[-1]=="\n": move = move[:-1]
            log("overruled illegal move with gnugo3.6: " + move + "\n")
            result = self.play_plain(color, move)
            if result[0]=="?":
                move = self.simple_engine.generate_move()
                move = simple_go.move_as_string(move, self.size)
                log("overruled illegal move with simplego: " + move + "\n")
                self.play_plain(color, move)
        time_used = time.time() - t0
        time_per_move = self.time / 30.0
        time_not_yet_used = time_per_move - time_used
        self.log_fp.write("Time left: %.2f\n" % self.time)
        self.log_fp.write("Time used: %.2f\n" % time_used)
        self.log_fp.write("Time/move: %.2f\n" % time_per_move)
        self.log_fp.write("Unused time: %.2f\n" % time_not_yet_used)
        self.log_fp.flush()
        if self.time_delay and time_not_yet_used > 0.0:
            self.log_fp.write("Sleeping: %.2f\n" % time_not_yet_used)
            self.log_fp.flush()
            time.sleep(time_not_yet_used)
        return move

    def genmove(self, color):
        return self.ok(self.genmove_plain(color))

    def play_plain(self, color, move):
        if (self.simple_engine.current_board.side==simple_go.BLACK) != (string.upper(color[0])=="B"):
            self.simple_engine.make_move(simple_go.PASS_MOVE)
        move2 = simple_go.string_as_move(string.upper(move), self.size)
        if not self.simple_engine.make_move(move2):
            return "? illegal move: maybe super-ko"
        result = self.play_gg(color, move)
        if result[0]=="?":
            return result
        self.engine.exec_cmd("play " + color + " " + move)
        log("move: " + move + "\n")
        return result

    def play(self, color, move):
        return self.play_plain(color, move)

    def place_free_handicap(self, count):
        result = utils.handicap_list(self.size, count)
        if result:
            for move in result:
                self.play_plain("black", move)
        else:
            for i in range(count):
                if i: self.play_plain("white", "PASS")
                result.append(self.genmove_plain("black", pass_allowed=0))
        return self.ok(string.join(result))

    def set_free_handicap(self, stones):
        for i in range(len(stones)):
            if i: self.play_plain("white", "PASS")
            self.play_plain("black", stones[i])
        return self.ok()

    def showboard(self):
        return self.ok(self.slave.exec_cmd("showboard"))

    def list_commands(self):
        result = string.join(("list_commands",
                              "boardsize",
                              "name",
                              "version",
                              "quit",
                              "clear_board",
                              "place_free_handicap",
                              "set_free_handicap",
                              "play",
                              "final_status_list",
                              "kgs-genmove_cleanup",
                              "showboard",
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
        elif cmd=="set_free_handicap":
            result = self.set_free_handicap(cmd_lst[1:])
        elif cmd=="showboard":
            result = self.showboard()
        elif cmd=="kgs-genmove_cleanup":
            result = self.slave.exec_cmd(cmd_line)
            self.slave.exec_cmd("undo\n")
            self.play_plain(cmd_lst[1], result[2:-2])
        elif cmd=="kgs-time_settings":
            self.time_settings(cmd_lst[2:])
            self.slave.exec_cmd(cmd_line)
            result = self.ok()
        elif cmd=="time_settings":
            self.time_settings(cmd_lst[1:])
            self.slave.exec_cmd(cmd_line)
            result = self.ok()
        elif cmd=="time_left":
            self.time_left(cmd_lst[1:])
            self.slave.exec_cmd(cmd_line)
            result = self.ok()
        else:
            self.log_fp.write("Unhandled command:" + cmd_line)
            self.log_fp.flush()
            result = self.slave.exec_cmd(cmd_line)
        if reply_no:
            result = result[0] + reply_no + result[1:]
        self.master.set_result(result)
        return cmd!="quit"
    def loop(self):
        try:
            while self.relay_cmd_and_reply():
                pass
        except:
            traceback.print_exc(None, self.log_fp)
            self.log_fp.flush()
            raise

if __name__=="__main__":
    if len(sys.argv)<5:
        print 'Usage: %s "simple gtp program name with arguments" "gnugo gtp program name with arguments" "name" "version"' % sys.argv[0]
        sys.exit(1)
    player = GTP_player(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    if len(sys.argv)>=6 and sys.argv[5]=="--time_delay":
        player.time_delay = True
    player.loop()
    
