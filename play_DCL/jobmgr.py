# -*- coding: ms949 -*-

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
import time
from time import gmtime, strftime

import socket

from graphvizresult import *

import logging

#selection, backup 
class ThreadCalc1(threading.Thread):
    """Threaded Calc1"""
    def __init__(self, logger, queue_s, queue_ev, queue_b, mode):
        threading.Thread.__init__(self)
        
        self.logger = logger
        
        self.queue_s = queue_s
        self.queue_ev = queue_ev
        self.queue_b = queue_b
        self.bStop = False
        
        if mode =="SL_SL":
            evaluation = evaluation_SL_SL
        elif mode == "RL_RL":
            evaluation = evaluation_RL_RL
        elif mode == "FR_FR":                                        
            evaluation = evaluation_FR_FR
        elif mode == "SL_RL":
            evaluation = evaluation_SL_RL
        elif mode == "SL_FR":
            evaluation = evaluation_SL_FR
        elif mode == "RL_SL":
            evaluation = evaluation_RL_SL
        elif mode == "RL_FR":
            evaluation = evaluation_RL_FR
        elif mode == "FR_SL":
            evaluation = evaluation_FR_SL
        elif mode == "FR_RL":
            evaluation = evaluation_FR_RL
        else:
            evaluation = evaluation_RL_FR
    
        self.mcts = MCTS(tree_policy=PUCT(c=g_mcts_Cpuck), 
                        default_policy=evaluation,
                        backup=minigo_backup, mode=mode)

    def run(self):
        print "start thread1"
        while True:
            #selection quque 처리.
            try:
                node = self.queue_s.get(True, 1)                
                
                self.logger.info('do for selection queue : ' + node.t)
                
                if node.t == 's' and self.bStop == False:
                    node2 = self.mcts.selection(node)
                    if node2 is not None:
                        node2.t = 'e'
                        self.queue_ev.put(node2)
                        self.logger.info('do job2-0 : ' + node.t + ' node2 is not null size : ' + str(self.queue_ev.qsize()))
                    else:
                        self.logger.info('do job2-1 : ' + node.t + ' node2 is null')
                         
                # 작업 완료를 알리기 위해 큐에 시그널을 보낸다.
                self.queue_s.task_done()
            except Queue.Empty:
                #Handle empty queue here
                #print 'Queue.Empty'
                pass
                
            #backup quque 처리.
            while not self.queue_b.empty():
                try:
                    node = self.queue_b.get(False)
                    self.logger.info('do for backup queue : ' + node.t)
                    self.mcts.backup(node)
                    self.queue_b.task_done()
                except Queue.Empty:
                    pass
                
            if self.bStop == True and self.queue_s.qsize() == 0:
                self.logger.info('stop by self.bStop == True')
                break
                    
        print "ThreadCalc1 ended"
        

#evaluation
class ThreadCalc3(threading.Thread):
    """Threaded Calc3"""
    def __init__(self, logger, queue_s, queue_ev, queue_b, host, port):
        threading.Thread.__init__(self)
        
        self.logger = logger
        
        self.queue_s = queue_s
        self.queue_ev = queue_ev
        self.queue_b = queue_b
        self.bStop = False
        self.host = host
        self.port = port
        self.count = 0
        self.curpath = os.path.dirname( os.path.abspath( __file__ ) )
        
        self.evalcount = 0

    def run(self):
        #print "start thread3"
        
        while True:                
            try:
                node = self.queue_ev.get(True, 1)     

                self.evalcount += 1
            
                #그때그때 다시 접속하게 하기. evaluator에서 accept하고 eval하는 thread가 하나이기 때문.            
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host, self.port))
                
                self.logger.info('connect pass : ' + self.host + ' : ' + str(self.port))
                
                #
                #command = 'evalrequest:' + str(len(str(node.state.state)))
                command = 'evalrequest:'+str(len(str(node.state.state)))
                s.send(command)
                self.logger.info( 'send data : ' + repr(command))
                
                #
                data = s.recv(1024)
                if data == 'ok':
                    #filename = self.savegame(node.state.state)
                    s.send(str(str(node.state.state)))
                    
                    #응답 기다림.
                    data = s.recv(1024)
                    self.logger.info( 'recv data from evaluator : ' + self.host + ':' + str(self.port) + ' : ' + repr(data))
                else:
                    print 'error : reply is not ok'
                    data = '0:0:0'
                
                
                #결과 node에 반영하고, 다시 sb queue에 넣기.
                #ex) result:1,1
                temp = data.split(":")
                temp2 = temp[1].split(",")
                                
                node.result_valuenet = int(temp2[0])
                node.result_rollout = int(temp2[1])
#                 node.result_movescore = int(temp2[2])
                node.t = 'b'
                
                self.queue_b.put(node)                
                self.queue_ev.task_done()
                
                s.close()
            except Queue.Empty:
                pass
            except Exception as e:
                #Handle empty queue here
                print 'error:' + str(self.port)
                print e
                s.close()
                pass
                
            if self.bStop == True:
                #print 'stop by self.bStop == True'
                break
                    
        print "ThreadCalc3 ended"
        
    def savegame(self, game):
        #print 'savegame : ' + str(len(game.move_history))
        #if len(game.move_history) > 0:
        #    print game.move_history
        
        sgf_name = self.curpath + '/sgfs/' + str(self.port) + '_' + str(self.count) + '.sgf'     
        fp = open(sgf_name, "w")
        fp.write(str(game))
        fp.close()
        
        self.count += 1
        
        return sgf_name 
            
        
class jobmgr2():
    """jobmgr"""
    def __init__(self, mode):
        
        self.root = None
        
        self.logger = logging.getLogger('jobmgr')
        self.logger.setLevel(logging.DEBUG)
        
        # create console handler and set level to debug
        ch = logging.FileHandler('jobmgr.log')
        ch.setLevel(logging.DEBUG)
        
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # add formatter to ch
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        self.queue_s = Queue.Queue()
        self.queue_ev = Queue.Queue()
        self.queue_b = Queue.Queue()
        
        self.listofallthread = []
        
        self.thread1 = ThreadCalc1(self.logger, self.queue_s, self.queue_ev, self.queue_b, mode)
        self.thread1.setDaemon(True)
        self.thread1.start()
        self.listofallthread.append(self.thread1)
        
        self.listofthread2 = []
        infos = EVALUATOR_INFOS.split(",")

        for info in infos:
            temp = info.split(":")
            host = temp[0]
            port = int(temp[1])
            
            print 'host : ' + host + ', port : ' + str(port)
            t = ThreadCalc3(self.logger, self.queue_s, self.queue_ev, self.queue_b, host, port)
            t.setDaemon(True)
            t.start()
            self.listofthread2.append(t)
            self.listofallthread.append(t)        
            
    def release(self):
        for a_thread in self.listofthread2:
            a_thread.bStop = True
        
        for a_thread in self.listofthread2:
            a_thread.join()
        
        print 'sb : ' + str(self.queue_s.qsize()) + ', ev : ' + str(self.queue_ev.qsize())
        self.thread1.bStop = True
        
        self.queue_s.join()        
        self.thread1.join()    
        self.queue_b.join()
    
    def genmove(self, game):
        #print 'genmove 001:'
        self.logger.info('genmove 001:')
        #print game.move_history
        self.logger.info(game.move_history)
        self.root = StateNode(None, GoState(game))
        #selection queue에 넣기 전에 한번 확장함.
        
        state_node = self.root
        #move = state_node.state.state.network.predict(state_node.state.state, type = 'SLPOLICY')
        move = state_node.state.state.generate_move(False, True)
        nextaction = GoAction([move[0], move[1]])
        t = state_node.children[nextaction].sample_state()
#         state_node.children[nextaction].Wms = 1
        state_node.children[nextaction].Pa = 0.1
        
        #print 'genmove 002'
        self.root.t = 's'
        self.logger.info('genmove 003:' + str(g_mcts_calccount))
        
        for i in range(g_mcts_calccount):
            self.queue_s.put(self.root)
        self.logger.info('genmove 004:' + str(self.queue_s.qsize()))

        #10초간 계산하도록 대기함.
        t1 = time.time()
        while True:
            time.sleep(1)
            
            t2 = time.time()
            
            if t2 - t1 > g_mcts_calctime:
                break
            
            self.logger.info('sb : ' + str(self.queue_s.qsize()) + ', ev : ' + str(self.queue_ev.qsize()) + ', b : ' + str(self.queue_b.qsize()))
        
        self.logger.info('end of waiting : ' + str(self.queue_s.qsize()) + ', ev : ' + str(self.queue_ev.qsize()) + ', b : ' + str(self.queue_b.qsize()))
        
        #time.sleep(10)
        
        #queue들 다 비우기.
        while not self.queue_s.empty():
            try:
                self.queue_s.get(False)
            except Queue.Empty:
                continue
            self.queue_s.task_done()
            
        while not self.queue_ev.empty():
            try:
                self.queue_ev.get(False)
            except Queue.Empty:
                continue
            self.queue_ev.task_done()
            
        #backup queue는 다 실행함.
        while not self.queue_b.empty():
            try:
                node = self.queue_b.get(False)
                self.thread1.mcts.backup(node)
            except Queue.Empty:
                continue
            self.queue_b.task_done()
            
        self.logger.info('end of clear : ' + str(self.queue_s.qsize()) + ', ev : ' + str(self.queue_ev.qsize()) + ', b : ' + str(self.queue_b.qsize()))
        
        evalcount = 0
        for worker in self.listofthread2:
            evalcount += worker.evalcount
            worker.evalcount = 0
        
        if g_mcts_graphviz == True:
            filename = 'result/' + strftime("%y%m%d_%H%M%S", time.localtime()) + '.gv'
            printgraph(filename, self.root)
        
        #대기후 가장 방문수가 높은 action을 move로 리턴함. 튜플로 리턴해야함.
        move = RESIGN_MOVE
        try:
            t = utils.rand_max(self.root.children.values(), key=lambda x: x.Q)
            if t is not None:
                move = tuple(t.action.move)            
        except:
            print "Unexpected error in jobmgr2.genmove :", sys.exc_info()[0]
            pass
            
             
        
        #move = tuple(utils.rand_max(self.root.children.values(), key=lambda x: x.Nv).action.move)
        return move
        