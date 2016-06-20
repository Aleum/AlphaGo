# -*- coding: ms949 -*-

import socket

from play_gtp import *
from const import *

from mcts.mcts import *
from mcts.tree_policies import *
from mcts.default_policies import *
from mcts.backups import *
from mcts.graph import *

import Queue
import threading

import numpy as np
import sys

from network import *

import logging

#evaluation
class ThreadEval():
    """ThreadEval"""
    def __init__(self, conn, addr, logger, port, mode):
        self.bStop = False
        
        self.mode = mode
        self.conn = conn
        self.addr = addr
        
        self.m_network = None
        
        self.logger = logger
        self.port = port
        
        self.curpath = os.path.dirname( os.path.abspath( __file__ ) )
        
        self.count = 0

    def run(self):
        print "start ThreadEval"
        
        try:
            conn, addr = self.conn, self.addr
            
            data = conn.recv(1024)
            self.logger.info( 'Received raw data : ' + repr(data))                 
            
            
            temp = data.split(":")
            action = temp[0]
            filesize = int(temp[1])
            
            if action == 'evalrequest':
                reply = 'ok'
                conn.sendall(reply)        
                
                #get file data                        
#                 data = conn.recv(filesize)                        
#                 
#                 filename = self.curpath + '/sgfs/' + str(self.port) + '_' + str(self.count) + '_recv' + '.sgf'
#                 fp = open(filename, "w")
#                 fp.write(data)
#                 fp.close()
                data = conn.recv(filesize)
                
                self.count += 1
                
                value, rollout = self.eval(data)
                
                reply = 'result:'
                reply += str(value) + ',' + str(rollout)
                conn.sendall(reply)
                self.logger.info( 'send data : ' + repr(reply))
                
            conn.close()                
            
        except Exception as e:
            print "Unexpected error in ThreadEval.run : ", sys.exc_info()[0]
            print e
            pass
                    
        print "ThreadEval ended"
        
#     def eval(self, filename):        
#         try:
#             #여기서 valuenet과 rollout을 계산하여 넘긴다.
#             game = simple_go.Game(9)
#             komi = 6.5
#             game.set_komi(komi)
#             
#             #현재상태.
#             game =  load_sgf.load_file(filename)
#             
#             game.network = self.m_network
#             
#             root = StateNode(None, GoState(game))
#             evaluation(root)
#             
#             return root.result_valuenet, root.result_rollout, root.result_movescore
#         except Exception as e:
#             print "Unexpected error in ThreadEval.eval : ", sys.exc_info()[0]
#             print e
#             return 0, 0, 0
        
    def eval(self, game_state):        
        try:
            #여기서 valuenet과 rollout을 계산하여 넘긴다.
            game = simple_go.Game(9)
            komi = 6.5
            game.set_komi(komi)
            #현재상태.
            game = load_sgf.load_file(game_state)
            
            game.network = self.m_network
            
            root = StateNode(None, GoState(game))
            
            
            if self.mode =="SL_SL":
                evaluation_SL_SL(root)
            elif self.mode == "RL_RL":
                evaluation_RL_RL(root)
            elif self.mode == "FR_FR":                                        
                evaluation_FR_FR(root)
            elif self.mode == "SL_RL":
                evaluation_SL_RL(root)
            elif self.mode == "SL_FR":
                evaluation_SL_FR(root)
            elif self.mode == "RL_SL":
                evaluation_RL_SL(root)
            elif self.mode == "RL_FR":
                evaluation_RL_FR(root)
            elif self.mode == "FR_SL":
                evaluation_FR_SL(root)
            elif self.mode == "FR_RL":
                evaluation_FR_RL(root)
            else:
                evaluation_RL_FR(root)
                
            return root.result_valuenet, root.result_rollout
        except Exception as e:
            print "Unexpected error in ThreadEval.eval : ", sys.exc_info()[0]
            print e
            return 0, 0

class Evaluator():
    def __init__(self, host, port, name, mode):
        self.host = host
        self.port = port
        self.mode = mode
        
        self.name = name
        self.queue = Queue.Queue()
        
        self.logger = logging.getLogger('evaluator_' + name)
        self.logger.setLevel(logging.DEBUG)
        
        # create console handler and set level to debug
        ch = logging.FileHandler('evaluator.log')
        ch.setLevel(logging.DEBUG)
        
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # add formatter to ch
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        '''
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')
        '''
        
        self.m_network = network()
        self.m_network.init2()
        
        self.init_conn()
        
        
    def init_conn(self):
        try:
            print "start socket"
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('', self.port))
            self.s.listen(1)
            print "listen socket"
            self.logger.info("start Evaluator" + '  pid : ' + str(os.getpid()))    
        except Exception as e:
            print e
            self.s.close()
        
        while True:
            try:
                conn, addr = self.s.accept()
                self.logger.info('Connected by ' + str(addr))
                
                thread1 = ThreadEval(conn, addr, self.logger, self.port, self.mode)
                thread1.m_network = self.m_network
                thread1.run()
                
            except Exception as e: 
                self.logger.info('except : ' + str(e))
                pass
        
        self.logger.info('exit')
        
    
if __name__=="__main__":
    HOST = '127.0.0.1'
    PORT = int(sys.argv[1])
    MODE = sys.argv[2]
    evaluator = Evaluator(HOST, PORT, HOST + ':' + str(PORT), MODE)
    
