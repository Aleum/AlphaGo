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

#Modified to translate few commands between gtp1 and gtp2

import popen2
import sys
import string
import time
import os
import traceback
import utils
import simple_go
import config
config.debug_flag = False

debug = 1

def log(s):
    fp = open("game1.log", "a")
    fp.write(s)
    fp.close()

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
        # total number of gtpa-logfiles
        for i in range(1000):
            log_name = "gtpa%03i.log" % i
            if not os.path.exists(log_name):
                break
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
        # total number of gtpb-logfiles
        for i in range(1000):
            log_name = "gtpb%03i.log" % i
            if not os.path.exists(log_name):
                break
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

    def __init__(self, command):
        self.engine_command = command
        self.engine = GTP_connection(self.engine_command)
        self.master = GTP_controller(sys.stdin, sys.stdout)
        # total number of gtpc-logfiles
        for i in range(1000):
            log_name = "gtpc%03i.log" % i
            if not os.path.exists(log_name):
                break
        self.log_fp = open(log_name, "w")
        self.size = 19

    def ok(self, result=None):
        if result==None: result = ""
        return "= " + result + "\n\n"

    def boardsize(self, size):
        self.size = size
        self.engine.exec_cmd("quit")
        self.engine = GTP_connection(self.engine_command)
        return self.engine.exec_cmd("boardsize " + str(size))

    def genmove(self, color):
        if string.lower(color[0])=="b":
            return self.engine.exec_cmd("genmove_black")
        else:
            return self.engine.exec_cmd("genmove_white")

    def play(self, color, move):
        if string.lower(color[0])=="b":
            return self.engine.exec_cmd("black " + move)
        else:
            return self.engine.exec_cmd("white " + move)

    def place_free_handicap(self, count):
        result = utils.handicap_list(self.size, count)
        if result:
            for move in result:
                self.play("black", move)
        else:
            return "? unknown handicap\n\n"
        return self.ok(string.join(result))

    def set_free_handicap(self, stones):
        for stone in stones:
            self.play("black", stone)
        return self.ok()

    def list_commands(self):
        return """= genmove
play
list_commands
place_free_handicap
set_free_handicap
""" + self.engine.exec_cmd("help")[2:]
        
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
        if cmd=="genmove":
            result = self.genmove(cmd_lst[1])
        elif cmd=="list_commands":
            result = self.list_commands()
        elif cmd=="play":
            result = self.play(cmd_lst[1], cmd_lst[2])
        elif cmd=="place_free_handicap":
            result = self.place_free_handicap(int(cmd_lst[1]))
        elif cmd=="set_free_handicap":
            result = self.set_free_handicap(cmd_lst[1:])
        elif cmd=="boardsize":
            result = self.boardsize(int(cmd_lst[1]))
        else:
            self.log_fp.write("Command passed unchanged:" + cmd_line)
            self.log_fp.flush()
            result = self.engine.exec_cmd(cmd_line)
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
    if len(sys.argv)<2:
        print 'Usage: %s "gnugo gtp1 program name with arguments"' % sys.argv[0]
        sys.exit(1)
    player = GTP_player(sys.argv[1])
    player.loop()
    
