# -*- coding: ms949 -*-

from feature.Plays import *
from feature.FeatureMap import *
from go import *
from mcts.mcts import *
from mcts.tree_policies import *
from mcts.default_policies import *
from mcts.backups import *
from mcts.graph import *

if __name__ == "__main__":    
    
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #showboard
    print str(game.current_board)
    
    #test
    game.make_move((1, 1))
    print str(game.current_board)
    game.make_move((2, 2))
    print str(game.current_board)
    
    
    #make argument to call model.predict
    i = 1
    playlist = []
    for move in game.move_history:
        if i%2 == 1:
            playlist.append(('b', (move[0]-1, move[1]-1)))
        else:
            playlist.append(('w', (move[0]-1, move[1]-1)))     
        i = i + 1
     
    plays = Plays(playlist)
    features = FeatureMap(plays, len(plays))
    print "first : "
    print features.input_planes  # <-- use this value
    
    #another way
    print "second : "
    print game.getargumenttopredict()
    
    
    #mcts test. reference only interface. inner logic will be modified.
    root = StateNode(None, GoState(game))
    mcts = MCTS(tree_policy=UCB1(c=1.41), 
                default_policy=evaluation,
                backup=monte_carlo)
    
    best_action = mcts(root)    
    
    
    print "ended"

