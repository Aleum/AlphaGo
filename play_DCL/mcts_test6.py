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

from network import *


def test1():
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs/test.sgf")
    print str(game.current_board)
    
    #network test
    m_network = network()
    m_network.init2()
    t1 = time.time()
    col, row = m_network.predict(game, type = 'SLPOLICY')
    t2 = time.time()    
    print 'col : ' + str(col) + ', row : ' + str(row) + "  takes : " + str(t2 - t1)
    
    game.network = m_network
    
    m_jobmgr = jobmgr()
    m_jobmgr.genmove(game)
    
    time.sleep(10)
    
    m_jobmgr.release()
    
    printgraph('result/test.gv', m_jobmgr.root)
    print 'main ended'


def test2():
    #onethread로 테스트.
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs/test.sgf")
    print str(game.current_board)
    
    #network test
    m_network = network()
    m_network.init2()
    t1 = time.time()
    col, row = m_network.predict(game, type = 'SLPOLICY')
    t2 = time.time()
    print 'col : ' + str(col) + ', row : ' + str(row) + "  takes : " + str(t2 - t1)
    
    game.network = m_network
    
    root = StateNode(None, GoState(game))
    evaluation(root)
    
    print 'main ended'


def test3():
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs/test.sgf")
    print str(game.current_board)
    
    #network test
    m_network = network()
    m_network.init2()
    t1 = time.time()
    col, row = m_network.predict(game, type = 'SLPOLICY')
    t2 = time.time()    
    print 'col : ' + str(col) + ', row : ' + str(row) + "  takes : " + str(t2 - t1)
    
    game.network = m_network
    
    m_jobmgr = jobmgr3()
    m_jobmgr.genmove(game)
    
    time.sleep(10)
    
    m_jobmgr.release()
    
    printgraph('result/test.gv', m_jobmgr.root)
    print 'main ended'
    
    
def test4():
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs/test.sgf")
    print str(game.current_board)
    
    #network test
    m_network = network()
    m_network.init2()
    t1 = time.time()
    col, row = m_network.predict(game, type = 'SLPOLICY')
    t2 = time.time()    
    print 'col : ' + str(col) + ', row : ' + str(row) + "  takes : " + str(t2 - t1)
    
    game.network = m_network
    
    valunetresult = m_network.predict_valuenet(game)
    print 'valunetresult : ' + str(valunetresult)
    
    print 'main ended'
    
    
if __name__=="__main__":    
    test4()
    
