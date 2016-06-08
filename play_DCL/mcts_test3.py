# -*- coding: ms949 -*-

from feature.Plays import *
from feature.FeatureMap import *

#import feature


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
from graphvizresult import *
from jobmgr import *
      
class ThreadCalc(threading.Thread):
    """Threaded Calc"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.bStop = False
        self.mcts = MCTS(tree_policy=PUCT(c=g_mcts_Cpuck), 
                        default_policy=evaluation,
                        backup=minigo_backup)

    def run(self):
        print "start thread"
        while True:
            try:
                node = self.queue.get(True, 1)                
                print 'do job'                
                self.mcts.doaction(node)                
                # 작업 완료를 알리기 위해 큐에 시그널을 보낸다.
                self.queue.task_done()
            except Queue.Empty:
                #Handle empty queue here
                print 'Queue.Empty'
                pass
                
            if self.bStop == True:
                print 'stop by self.bStop == True'
                break
                    
        print "ThreadCalc ended"
        
        
#selection, backup 



#evaluation




if __name__=="__main__":    
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs\\test.sgf")
    print str(game.current_board)
    
    t = game.getargumenttopredict()
            
    root = StateNode(None, GoState(game))
    a = root.is_terminal()
    mcts = MCTS(tree_policy=PUCT(c=g_mcts_Cpuck), 
                default_policy=evaluation,
                backup=minigo_backup)
    
    '''
    thread 전
    best_action = mcts(root)
    b = root.is_terminal()
    '''
    
    queue = Queue.Queue()    
    listofthread = []
    for i in range(10):
        t = ThreadCalc(queue)
        t.setDaemon(True)
        t.start()
        listofthread.append(t)
        
    for i in range(1000):
        queue.put(root)
        
    time.sleep(5)
    queue.join()
    
    for a_thread in listofthread:
        a_thread.bStop = True
    
    for a_thread in listofthread:
        a_thread.join()
     
    #g_mcts_threshold
    
    printgraph('result\\test.gv', root)
    print 'main ended'
    



