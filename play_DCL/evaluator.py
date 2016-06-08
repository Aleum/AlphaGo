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
class ThreadEval(threading.Thread):
    """ThreadEval"""
    def __init__(self, queue, logger, port):
        threading.Thread.__init__(self)
        self.queue = queue
        self.bStop = False
        
        self.m_network = network()
        self.m_network.init2()
        
        self.logger = logger
        self.port = port
        
        self.curpath = os.path.dirname( os.path.abspath( __file__ ) )
        
        self.count = 0

    def run(self):
        print "start ThreadEval"
        while True:
            try:
                conn, addr = self.queue.get(True, 1)                
                
                '''
                while 1:
                    data = conn.recv(1024)
                    self.logger.info( 'Received raw data : ' + repr(data))                 
                    if not data: break
                    
                    temp = data.split(":")
                    action = temp[0]
                    filename = temp[1]
                    
                    if action == 'eval':
                        value, rollout = self.eval(filename)
                        
                        reply = 'result:'
                        reply += str(value) + ',' + str(rollout)
                        conn.sendall(reply)                    
                '''
                
                while 1:
                    data = conn.recv(1024)
                    self.logger.info( 'Received raw data : ' + repr(data))                 
                    if not data: break
                    
                    temp = data.split(":")
                    action = temp[0]
                    filesize = int(temp[1])
                    
                    if action == 'evalrequest':
                        reply = 'ok'
                        conn.sendall(reply)        
                        
                        #get file data                        
                        data = conn.recv(filesize)                        
                        
                        filename = self.curpath + '/sgfs/' + str(self.port) + '_' + str(self.count) + '_recv' + '.sgf'
                        fp = open(filename, "w")
                        fp.write(data)
                        fp.close()
                        
                        self.count += 1
                    
                        value, rollout = self.eval(filename)
                        
                        reply = 'result:'
                        reply += str(value) + ',' + str(rollout)
                        conn.sendall(reply)

                        self.logger.info( 'send data : ' + repr(reply))
                    
                conn.close()                
                
                self.queue.task_done()
            except Queue.Empty:
                #Handle empty queue here
                #print 'Queue.Empty'
                pass
            except Exception as e:
                print "Unexpected error in ThreadEval.run : ", sys.exc_info()[0]
                print e
                pass
                
            if self.bStop == True:
                #print 'stop by self.bStop == True'
                break
                    
        print "ThreadEval ended"
        
    def eval(self, filename):        
        try:
            #여기서 valuenet과 rollout을 계산하여 넘긴다.
            game = simple_go.Game(9)
            komi = 6.5
            game.set_komi(komi)
            
            #현재상태.
            game =  load_sgf.load_file(filename)
            
            game.network = self.m_network
        
            root = StateNode(None, GoState(game))
            evaluation(root)
            
            return root.result_valuenet, root.result_rollout, root.result_movescore
        except Exception as e:
            print "Unexpected error in ThreadEval.eval : ", sys.exc_info()[0]
            print e
            return 0, 0
        

class Evaluator():
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
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
        
        
        
        self.thread1 = ThreadEval(self.queue, self.logger, self.port)
        self.thread1.setDaemon(True)
        self.thread1.start()        
        
    def init(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.port))
        self.s.listen(1)
        
    def run(self):
        self.logger.info("start Evaluator" + '  pid : ' + str(os.getpid()))    
        
        self.init()
        
        while True:
            try:
                conn, addr = self.s.accept()
                self.logger.info('Connected by ' + str(addr))
                
                self.queue.put((conn, addr))                
                
            except Exception as e: 
                self.logger.info('except : ' + str(e))
                pass
        
        self.logger.info('exit')
              
    
if __name__=="__main__":
    HOST = '127.0.0.1'
    PORT = int(sys.argv[1])
    evaluator = Evaluator(HOST, PORT, HOST + ':' + str(PORT))
    evaluator.run()
    
