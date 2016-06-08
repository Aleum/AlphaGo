from maze_ import *
#import numpy as np
from mcts.mcts import *
from mcts.tree_policies import *
from mcts.default_policies import *
from mcts.backups import *
from mcts.graph import *

from graphviz import Digraph

def printnode(dot, node, parent):
    if node.type == 'StateNode':
        a = node.state.tostr()
        #print a
        dot.node(a, a + " \: " + str(node.q))
        if parent is not None:
            b = parent.parent.state.tostr()  
            c = parent.action.tostr()
            dot.edge(b, a, label=c)
    
    for child in node.child:
        printnode(dot, child, node)

if __name__=="__main__":
    mcts =MCTS(tree_policy=UCB1(c=1.41), 
                default_policy=immediate_reward,
                backup=monte_carlo)
    
    root = StateNode(None, MazeState([0, 0]))
    best_action = mcts(root)
    a = 1
    print best_action.move[0], best_action.move[1]

    '''
    dot = Digraph(comment='The Round Table')
    dot  #doctest: +ELLIPSIS
    dot.node('A', 'King Arthur')
    dot.node('B', 'Sir Bedevere the Wise')
    dot.node('L', 'Sir Lancelot the Brave')
    
    dot.edges(['AB', 'AL'])
    dot.edge('B', 'L', constraint='false')
    print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
    dot.render('test.gv', view=True)
    '''
    
    print "started"
    
    dot = Digraph(comment='The Round Table')
    dot  #doctest: +ELLIPSIS
    printnode(dot, root, None)
    print "writing"    
    print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
    print "drawing"
    dot.render('test2.gv', view=True)
    
    print "ended"
    
    
    
            
    