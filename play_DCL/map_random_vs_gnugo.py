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

# Aloril modified to work with simple_go.py

# Aloril later modified to map random games against gnugo

usage =  """

This program tries to find a game where random player wins
against GNU Go. Random player is defined as: random.choice(self.list_moves())
cgos_gnugo_check_seed1 is contains this:
/usr/local/bin/gnugo --mode gtp --chinese-rules --never-resign --capture-all-dead --seed 1

Usage:
start with command:
python -i map_random_vs_gnugo.py

At Python prompt use this method:
map_random(start, end, size=9)

Example:
map_random(0, 1000000, 9)

or

map_random(0, 10000000, 7)

or

map_random(0, 100000000, 5)

"""

import popen2
import sys
import string
import time
import os
import traceback
import random
import utils
import simple_go
import config
from play_gtp import get_next_filename, Logger, log

SUPER_KO = "superko violation"
ESTIMATED_WIN = "estimated win"
GAME_FINISHED = "game finished"
BLACK_POSITIVE = "black positive"
EDGE_HEURISTICS = "edge heuristics"
START_HEURISTICS = "start heuristics"

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


seen_chats = {}

class GTP_connection:

    #
    # Class members:
    #   outfile         File to write to
    #   infile          File to read from

    def __init__(self, command):
        self.init_done = False
        self.command = command
        self.command_log = []

    def real_init(self):
        command = self.command
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
        for i in range(0, len(self.command_log)-1, 2):
            cmd = self.command_log[i]
            reply = self.command_log[i+1]
            real_reply = self.real_exec_cmd(cmd)
            if reply!=real_reply:
                raise ValueError, "reply not same: %s: %s != %s" % (cmd, reply, real_reply)
        self.init_done = True
        
    def real_exec_cmd(self, cmd):
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

    def exec_cmd(self, cmd):
        #print "???"
        #print cmd
        self.command_log.append(cmd)
        key0 = tuple(self.command_log)
        key = (hash(key0), len(key0), hash(key0[-10:]), hash(key0[10:]))
        if key in seen_chats:
            reply = seen_chats[key]
            #print "<<<cache<<<"
            #print key
            #print ">>>cache>>>"
        else:
            if not self.init_done:
                self.real_init()
            reply = self.real_exec_cmd(cmd)
        #print "!!!"
        #print reply
        seen_chats[key] = reply
        self.command_log.append(reply)
        return reply

class Match:
    def __init__(self, size, command):
        self.engine_command = command
        self.engine = GTP_connection(command)
        self.estimate_engine = GTP_connection(command)
        self.boardsize(size)

    def boardsize(self, size):
        if size<5 or size>19:
            return "? unacceptable size\n\n"
        self.size = size
        self.engine.exec_cmd("quit")
        self.estimate_engine.exec_cmd("quit")
        self.engine = GTP_connection(self.engine_command)
        self.estimate_engine = GTP_connection(self.engine_command)
        #self.engine.exec_cmd("set_random_seed 1")
        #self.estimate_engine.exec_cmd("set_random_seed 1")
        result = self.engine.exec_cmd("boardsize " + str(size))
        if result[0]=="?":
            return result
        self.estimate_engine.exec_cmd("boardsize " + str(size))
        self.engine.exec_cmd("clear_board")
        self.estimate_engine.exec_cmd("clear_board")
        self.random_engine = simple_go.Game(size)

    def play(self, seed=1, print_flag = False):
        if self.size in (5, 7):
            random.seed(seed)
            self.random_engine.current_board.init_hash()
            if self.size==5 and int(random.random() * 26)!=13:
                return START_HEURISTICS
            if self.size==7:
                if int(random.random() * 50)!=25:
                    return START_HEURISTICS
                if int(random.random() * 48) not in (17, 18, 23, 24, 29, 30, 31):
                    return START_HEURISTICS
        random.seed(seed)
        self.boardsize(self.size)
        score = ""
        while not self.random_engine.has_2_passes():
            if self.random_engine.current_board.side==simple_go.BLACK:
                move_tuple = self.random_engine.select_random_move()
                self.random_engine.make_move(move_tuple)
                move = simple_go.move_as_string(move_tuple)
                edge_flag = False
                if self.size==5:
                    if len(self.random_engine.move_history) <= 1:
                        for coord in move_tuple:
                            if coord in (2, self.size-1):
                                edge_flag = True
                    if len(self.random_engine.move_history) <= 3:
                        if self.random_engine.current_board.pos_near_edge(move_tuple):
                            edge_flag = True
                    if len(self.random_engine.move_history) <= 7:
                        if move_tuple==simple_go.PASS_MOVE:
                            edge_flag = True
                else: # self.size >= 9:
                    if len(self.random_engine.move_history) <= 3:
                        for coord in move_tuple:
                            if coord in (2, self.size-1):
                                edge_flag = True
                    if len(self.random_engine.move_history) <= 7:
                        if self.random_engine.current_board.pos_near_edge(move_tuple):
                            edge_flag = True
                    if len(self.random_engine.move_history) <= 15:
                        if move_tuple==simple_go.PASS_MOVE:
                            edge_flag = True
                if edge_flag and not print_flag:
                    return EDGE_HEURISTICS
                result = self.engine.exec_cmd("play black " + move)
                if result[0]=="?":
                    raise ValueError, "engine didn't accept move"
                self.estimate_engine.exec_cmd("play black " + move)
            else:
                move = self.engine.exec_cmd("genmove white")
                move = move.split()[1]
                move_tuple = simple_go.string_as_move(move)
                if not self.random_engine.make_move(move_tuple):
                    return SUPER_KO
                self.estimate_engine.exec_cmd("play white " + move)
                #if len(self.random_engine.move_history)%8==0:
                score = self.estimate_engine.exec_cmd("estimate_score")
                if print_flag:
                    print score
            if print_flag:
                print move, len(self.random_engine.move_history)
                print self.random_engine.current_board
            else:
                score_lst = score.split()
                #if score[:8]=="= W+81.0":
                if self.size==5:
                    #if score:
                    #    print score, score_lst[1][0], float(score_lst[4][:-1])
                    if score and (score_lst[1][0]=="W" or abs(float(score_lst[4][:-1]))!=25):
                        return ESTIMATED_WIN
                elif self.size==7:
                    if score and score_lst[1][0]=="W" and float(score_lst[1][1:]) >= 10.0:
                        return ESTIMATED_WIN
                else:
                    if score and score_lst[1][0]=="W" and float(score_lst[1][1:]) >= 20.0:
                        return ESTIMATED_WIN
                    elif score[:3]=="= B" and len(self.random_engine.move_history) >= 20:
                        return BLACK_POSITIVE
        if print_flag:
            print self.random_engine
            print simple_go.move_list_as_string(self.random_engine.move_history)
        return GAME_FINISHED

def map_random(start, end, size=9):
    m = Match(size, "cgos_gnugo_check_seed1")
    fp = open("map_random_%ix%i_seed1.log" % (size, size), "a")
    for seed in xrange(start, end+1):
        t0 = time.time()
        result = m.play(seed)
        t1 = time.time()
        if result!=START_HEURISTICS:
            s = string.join(map(str, [seed, result, len(m.random_engine.move_history), t1-t0, simple_go.move_list_as_string(m.random_engine.move_history), m.engine.init_done]), " ")
            print s
            fp.write(s + "\n")
            fp.flush()
        else:
            sys.stderr.write("%i\r" % seed)
        if seed%1000==0:
            fp_cache = open("map_random_cache_%ix%i.dat" % (size, size), "w")
            fp_cache.write(repr(seen_chats))
            fp_cache.close()
    fp.close()

def white2tree(name = "map_random.log"):
    games = []
    for line in open(name):
        lst = line.split()
        wlst = []
        for i in range(6, len(lst), 2):
            move = lst[i]
            wlst.append(move)
        if wlst:
            games.append(wlst)
    games.sort()
    prev_game = []
    repeat_count = 0
    for j in range(len(games)):
        game = games[j]
        if j+1 < len(games) and games[j]==games[j+1]:
            repeat_count = repeat_count + 1
            continue
        print "%6i" % j, "<",
        for i in range(len(game)):
            move = game[i]
            if i >= len(prev_game) or prev_game[i]!=move:
                print "%3s" % move,
            else:
                print "   ",
        print ">",
        if repeat_count:
            print repeat_count + 1, "times"
        else:
            print
        repeat_count = 0
        prev_game = game

def almost_same_game(name = "map_random.log"):
    games = []
    seen = {}
    new_count = 0
    seen_count = 0
    ratio = 0.0
    fp1 = open("new.dat", "w")
    fp2 = open("seen.dat", "w")
    fp3 = open("seen_new_ratio.dat", "w")
    i = 0
    for line in open(name):
        lst = line.split()
        game = tuple(lst[5:-2])
        if 0 < len(game):
            if game in seen:
                if len(game) > 7:
                    print line[:-1]
                seen_count = seen_count + 1
            else:
                new_count = new_count + 1
                seen[game] = True
                #print line[:-1]
            games.append(game)
            fp1.write("%i %i\n" % (i, new_count))
            fp2.write("%i %i\n" % (i, seen_count))
            if new_count:
                ratio = seen_count / float(new_count)
            fp3.write("%i %f\n" % (i, ratio))
            #print new_count, seen_count
            i = i + 1
    fp1.close()
    fp2.close()
    fp3.close()
    print new_count, seen_count, ratio
    

def time_usage(name = "map_random.log"):
    edge_time = 0.0
    other_time = 0.0
    cache_time = 0.0
    count = 0
    last_line = ""
    for line in open(name):
        last_line = line
        lst = line.split()
        time = float(lst[4])
        if lst[-1]=="False":
            cache_time = cache_time + time
        elif lst[1]=="edge":
            edge_time = edge_time + time
        else:
            other_time = other_time + time
        count = count + 1
    total_time = edge_time + other_time + cache_time
    last_seed = int(last_line.split()[0])
    print edge_time, other_time, cache_time, "=", total_time, total_time/count, last_seed/total_time
    
if __name__=="__main__":
    print usage
    
