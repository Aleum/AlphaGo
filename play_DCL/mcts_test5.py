# -*- coding: ms949 -*-


from play_gtp import *
from const import *

def test1():
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs\\test.sgf")
    print str(game.current_board)
    
    turn = 0
    
    legalmove = {}
    legalmove = game.list_moves()
    legalmove.remove((-1, -1))
    
    while True:        
        if turn == 14:
            l2 = {}
            l2 = game.list_moves()
            l2.remove((-1, -1))
            a = 1
        
        #tt = random.choice(legalmove)
        legalmove = game.generate_move()
        if len(legalmove) == 0 or legalmove == PASS_MOVE:
            print 'exit2'
            break
        
        tt = legalmove
        if game.legal_move(tt) == True: 
            result = game.make_move((tt[0], tt[1])) 
            if result == None:
                print 'exit1'
                break
            else:
                print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(game.current_board)                
        else:
            print 'exit3'
            break
        
        turn += 1
        
    score = game.current_board.score_position()
    if game.current_board.side==simple_go.BLACK:
        score = -score
    score = score + komi
    if score>=0:
        result = "W+%.1f" % score
    else:
        result = "B+%.1f" % -score
    print result
    
    
def test2():
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs\\test.sgf")
    print str(game.current_board)
    
    turn = 0
    
    legalmove = {}
    legalmove = game.list_moves()
    legalmove.remove((-1, -1))
    
    while game.is_end() == False:
        legalmove = game.generate_move()
        if len(legalmove) == 0 or legalmove == PASS_MOVE:
            print 'exit2'
            break
        
        tt = legalmove
        if game.legal_move(tt) == True: 
            result = game.make_move((tt[0], tt[1])) 
            if result == None:
                print 'exit1'
                break
            else:
                print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(game.current_board)                
        else:
            print 'exit3'
            break
        
        turn += 1
        
    score = game.current_board.score_position()
    if game.current_board.side==simple_go.BLACK:
        score = -score
    score = score + komi
    if score>=0:
        result = "W+%.1f" % score
    else:
        result = "B+%.1f" % -score
    print result
    



def test3():
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs\\test.sgf")
    print str(game.current_board)
    
    turn = 0
    
    legalmove = {}
    legalmove = game.list_moves()
    legalmove.remove((-1, -1))
    
    while game.is_end() == False:
        
        if len(legalmove) == 0:
            print 'exit2'
            break
        
        tt = legalmove[0]
        
        if game.legal_move(tt) == True: 
            result = game.make_move((tt[0], tt[1])) 
            if result == None:
                print 'exit1'
                break
            else:
                print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(game.current_board)                
        else:
            del legalmove[0]
        
        turn += 1
        
    score = game.current_board.score_position()
    if game.current_board.side==simple_go.BLACK:
        score = -score
    score = score + komi
    if score>=0:
        result = "W+%.1f" % score
    else:
        result = "B+%.1f" % -score
    print result
    
    
    
def test4():
    game = simple_go.Game(9)     
    
    komi = 6.5
    game.set_komi(komi)
    
    #현재상태.
    game =  load_sgf.load_file("sgfs\\test.sgf")
    print str(game.current_board)
    
    turn = 0
    
    legalmove = {}
    legalmove = game.list_moves()
    legalmove.remove((-1, -1))
    
    while game.is_end() == False:
        legalmove = game.generate_move()
        if len(legalmove) == 0 or legalmove == PASS_MOVE:
            print 'exit2'
            break
        
        tt = legalmove
        if game.legal_move(tt) == True: 
            result = game.make_move((tt[0], tt[1])) 
            if result == None:
                print 'exit1'
                break
            else:
                print 'turn ' + str(turn) + ' move on ' + str(tt[0]) + ',' + str(tt[1]) + ' \n' + str(game.current_board)                
        else:
            print 'exit3'
            break
        
        turn += 1
        
    print 'ended game. winner is ' + str(game.getwinner()) + ' with ' + str(game.getscore()) 
    
    
    
if __name__=="__main__":    
    test4()
        