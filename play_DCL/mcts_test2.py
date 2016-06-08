from play_gtp import *

'''
name
boardsize 9
clear_board
komi 6.5
play B A1
genmove w
genmove b
showboard

'''

if __name__=="__main__":    
    player = GTP_player()
    
    #name
    player.master.set_result("= " + player.name + "\n\n")
    
    #boardsize 9
    player.boardsize(9)    
    
    #clear_board
    player.clear_board()
    
    #komi 6.5
    player.komi = 6.5
    player.engine.set_komi(player.komi + player.handicap)
    
    #showboard
    player.master.set_result(player.showboard())
    
    #play B A1
    player.play('B', 'A1')
    player.master.set_result(player.showboard())
    
    player.play('W', 'A2')
    player.master.set_result(player.showboard())
    
    player.engine.make_move((2, 2))
    player.master.set_result(player.showboard())
    
    player.engine.make_move((2, 3))
    player.master.set_result(player.showboard())
    
    
    player2 = GTP_player()
    player2.engine = load_sgf.load_file("sgfs\\0323_result01-0.sgf")
    player2.master.set_result(player2.showboard())
    
    player3 = GTP_player()
    player3 = player2
    player3.master.set_result(player3.showboard())
    
    for move in player3.engine.iterate_moves():
        a = move
        print move    
    
    print "ended"
