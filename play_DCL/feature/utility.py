# -*- coding: utf-8 -*-
"""
    utility.py
"""
import os
import os.path

from SGFGame import SGFGame

def filenames_in(path, extensions):
    for entryname in os.listdir(path):
        entrypath = os.path.abspath(os.path.join(path, entryname))
        entry_ext = os.path.splitext(entrypath)[1][1:]
        if os.path.isfile(entrypath) and (entry_ext in [ext.replace(".", "") for ext in extensions.split(";")]):
            yield entrypath
            
            
def print_features(feature_map):
    for row_index in range(feature_map.rows):
        row = "".join([(value or ".") for value in feature_map.board[row_index]])
        row += "\t"
        row += "\t".join(["".join(["{0}".format(value or ".") for value in feature[row_index]]) for feature in feature_map.features])
        print(row)

def print_board(board):
    for row_index in range(board.rows):
        print("".join([(value or ".") for value in board[row_index]]))

def print_feature(feature):
    for row_index in range(len(feature)):
        print("".join(["{0}".format(value or ".") for value in feature[row_index]]))
        
def print_int_feature(board, feature):
    for row_index in range(board.rows):
        row = "".join([(value or ".") for value in board[row_index]])
        row += "\t"
        row += " ".join(["{0:3}".format(value or "...") for value in feature[row_index]])
        print(row)
