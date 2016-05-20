from const import *
import simple_go, string, time, utils, re

##    size = 19
##    g = Game(size)

##    g = Game(5)
##    g.make_move((2,2))
##    g.make_move((2,3))
##    g.make_move((1,3))
##    g.make_move((1,4))
##    g.make_move((3,3))
##    g.make_move((3,4))
##    g.make_move((2,4))
##    g.make_move((0,3))
##    g.make_move((2,3))
##    import pdb; pdb.set_trace()
##    g.make_move((1,2))
##    print g.current_board

def diagram2game(str):
    g = None
    for line in string.split(str, "\n"):
        line = string.strip(line)
        if not line: continue
        if line[0]=="A" and not g:
            g = simple_go.Game(len(line))
        elif line[0] in string.digits:
            y, line, rest = string.split(line, "|")
            y = int(y)
            for x in range(len(line)):
                stone = line[x]
                x = x + 1
                if stone in WHITE+BLACK:
                    if g.current_board.side!=stone:
                        g.make_move(PASS_MOVE)
                    g.make_move((x, y))
    return g

def test_unconditional(str):
    g = diagram2game(str)
    print g.current_board.as_string_with_unconditional_status()


def speed(n):
    g = simple_go.Game(19)
    t0 = time.time()
    for i in xrange(n):
        b = g.current_board.copy()
    t1 = time.time()
    t_elapsed = t1-t0
    print t_elapsed, n/t_elapsed
    

def test_position(diagram, ok_result):
    g = diagram2game(diagram)
    test_result = g.current_board.as_string_with_unconditional_status()
    board_pat = re.compile(r".*?(\+.*\+)", re.DOTALL)
    m = board_pat.match(ok_result)
    if m:
        ok_result_board = m.group(1)
    else:
        ok_result_board = "1"
    m = board_pat.match(test_result)
    if m:
        test_result_board = m.group(1)
    else:
        test_result_board = "2"
    if ok_result_board==test_result_board: return
    print ok_result
    print test_result
    raise ValueError, "unconditional test failed"

def test_all():
    test_position("""
   ABCDEFGHI
  +---------+
 9|.........| 9
 8|.XX......| 8
 7|.X.XXX...| 7
 6|.XXX.XOO.| 6
 5|..XOOOX..| 5
 4|.OOXXXX..| 4
 3|..X.X.X..| 3
 2|..XXXXX..| 2
 1|.........| 1
  +---------+
   ABCDEFGHI""",
"""
   ABCDEFGHJ
  +---------+
 9|.........| 9
 8|.&&......| 8
 7|.&:&&&...| 7
 6|.&&&:&OO.| 6
 5|..&ooo&..| 5
 4|.OO&&&&..| 4
 3|..&:&:&..| 3
 2|..&&&&&..| 2
 1|.........| 1
  +---------+
   ABCDEFGHJ
""")
    

    test_position("""
   ABCDE
  +-----+
 5|.....|
 4|.XXX.|
 3|.X.X.|
 2|X.X..|
 1|XXX..|
  +-----+
   ABCDE
""", """
   ABCDE
  +-----+
 5|:::::| 5
 4|:&&&:| 4
 3|:&:&:| 3
 2|&:&::| 2
 1|&&&::| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDEFGH
  +--------+
 8|........| 8
 7|..XXXXXX| 7
 6|..X..X.X| 6
 5|.XOOOXXX| 5
 4|.X..X...| 4
 3|.XXXX...| 3
 2|..X.X...| 2
 1|..XXX...| 1
  +--------+
""", """
   ABCDEFGH
  +--------+
 8|........| 8
 7|..XXXXXX| 7
 6|..X..X.X| 6
 5|.XOOOXXX| 5
 4|.X..X...| 4
 3|.XXXX...| 3
 2|..X.X...| 2
 1|..XXX...| 1
  +--------+
   ABCDEFGH
""")

    test_position("""
   ABC
  +---+
 3|OO.| 3
 2|OXX| 2
 1|.OX| 1
  +---+
   ABC
""", """
   ABC
  +---+
 3|OO.| 3
 2|OXX| 2
 1|.OX| 1
  +---+
   ABC
""")

    test_position("""
   ABC
  +---+
 3|.OO| 3
 2|O.O| 2
 1|.O.| 1
  +---+
   ABC
""", """
   ABC
  +---+
 3|=@@| 3
 2|@=@| 2
 1|=@=| 1
  +---+
   ABC
""")

    test_position("""
   ABCDE
  +-----+
 5|X.XO.| 5
 4|.XXOO| 4
 3|X.XO.| 3
 2|OXXO.| 2
 1|.OXO.| 1
  +-----+
   ABCDE
""", """
   ABCDE
  +-----+
 5|&:&@=| 5
 4|:&&@@| 4
 3|&:&@=| 3
 2|o&&@=| 2
 1|:o&@=| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDE
  +-----+
 5|X.X.O| 5
 4|.XX.O| 4
 3|X.X.O| 3
 2|OXXO.| 2
 1|.OX..| 1
  +-----+
   ABCDE
""", """
   ABCDE
  +-----+
 5|&:&:o| 5
 4|:&&:o| 4
 3|&:&:o| 3
 2|o&&o:| 2
 1|:o&::| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDE
  +-----+
 5|X.X.O| 5
 4|.XX.O| 4
 3|X.X..| 3
 2|OXXOO| 2
 1|.OX..| 1
  +-----+
   ABCDE
""", """
   ABCDE
  +-----+
 5|&:&.O| 5
 4|:&&.O| 4
 3|&:&..| 3
 2|o&&OO| 2
 1|:o&..| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDEFGHJK
  +----------+
10|XX.XOO.XX.|10
 9|.OXXXOXX.X| 9
 8|OXX.OXOOXX| 8
 7|OOOXXX.XX.| 7
 6|OXXOOXX.OX| 6
 5|X.X.X..XX.| 5
 4|XXOXXXXOOX| 4
 3|.XOXXXXOOX| 3
 2|XOOOXOOO.X| 2
 1|.OOXXOOOOX| 1
  +----------+
   ABCDEFGHJK
""", """
   ABCDEFGHJK
  +----------+
10|&&:&oo:&&:|10
 9|:o&&&o&&:&| 9
 8|o&&:o&oo&&| 8
 7|ooo&&&:&&:| 7
 6|o&&oo&&:o&| 6
 5|&:&:&::&&:| 5
 4|&&o&&&&oo&| 4
 3|:&o&&&&oo&| 3
 2|&ooo&ooo:&| 2
 1|:oo&&oooo&| 1
  +----------+
   ABCDEFGHJK
""")

    test_position("""
   ABCDEFGHJ
  +---------+
 9|O.O.O..X.| 9
 8|.O.O..XX.| 8
 7|O.OO.XX.O| 7
 6|OX.O.X.O.| 6
 5|.O.O.X.O.| 5
 4|O.O..XO.O| 4
 3|.OO..OXO.| 3
 2|OO.O.OXXX| 2
 1|..O.XX.X.| 1
  +---------+
   ABCDEFGHJ
""", """
   ABCDEFGHJ
  +---------+
 9|@=@.O..X.| 9
 8|=@=@..XX.| 8
 7|@=@@.XX.O| 7
 6|@x=@.X.O.| 6
 5|=@=@.X.O.| 5
 4|@=@..XO.O| 4
 3|=@@..OXO.| 3
 2|@@.O.OXXX| 2
 1|..O.XX.X.| 1
  +---------+
   ABCDEFGHJ
""")

    test_position("""
   ABCDEFGHJ
  +---------+
 9|O.O.O..X.| 9
 8|.O.O..XX.| 8
 7|O.OO.XX.O| 7
 6|OX.O.X.O.| 6
 5|.O.O.X.O.| 5
 4|O.O..XO.O| 4
 3|.OOO.OXO.| 3
 2|OO.OOOXXX| 2
 1|..O..O.X.| 1
  +---------+
   ABCDEFGHJ
""", """
   ABCDEFGHJ
  +---------+
 9|@=@.O..X.| 9
 8|=@=@..XX.| 8
 7|@=@@.XX.O| 7
 6|@x=@.X.O.| 6
 5|=@=@.X.O.| 5
 4|@=@..XO.O| 4
 3|=@@@.@XO.| 3
 2|@@=@@@XXX| 2
 1|==@==@.X.| 1
  +---------+
   ABCDEFGHJ
""")

    test_position("""
   ABCDE
  +-----+
 5|.OOO.| 5
 4|OXXXO| 4
 3|OX.XO| 3
 2|OXXXO| 2
 1|.OOO.| 1
  +-----+
   ABCDE
""", """
  +-----+
 5|=@@@=| 5
 4|@xxx@| 4
 3|@x=x@| 3
 2|@xxx@| 2
 1|=@@@=| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDE
  +-----+
 5|!!?.?| 5
 4|XXXOX| 4
 3|XXXOO| 3
 2|.OOO.| 2
 1|?XO.O| 1
  +-----+
   ABCDE
""", """
   ABCDE
  +-----+
 5|=====| 5
 4|xxx@x| 4
 3|xxx@@| 3
 2|=@@@=| 2
 1|=x@=@| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDE
  +-----+
 5|XXXO.| 5
 4|X.XO.| 4
 3|XXOOO| 3
 2|X.XOO| 2
 1|XXXO.| 1
  +-----+
   ABCDE
""", """
   ABCDE
  +-----+
 5|&&&@=| 5
 4|&:&@=| 4
 3|&&@@@| 3
 2|&:&@@| 2
 1|&&&@=| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDEFG
  +-------+
 7|.OOOOX.| 7
 6|OXXXOX.| 6
 5|OX.XOX.| 5
 4|OOXOOXX| 4
 3|OX.XOX.| 3
 2|OXXXOX.| 2
 1|.OOOOX.| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|=@@@@&:| 7
 6|@xxx@&:| 6
 5|@x=x@&:| 5
 4|@@x@@&&| 4
 3|@x=x@&:| 3
 2|@xxx@&:| 2
 1|=@@@@&:| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|OOOOOOO| 7
 6|OOXXXXO| 6
 5|OXXX.XO| 5
 4|OOOXXXO| 4
 3|O.XX.XO| 3
 2|OOOXXXO| 2
 1|O..OOOO| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|ooooooo| 7
 6|oo&&&&o| 6
 5|o&&&:&o| 5
 4|ooo&&&o| 4
 3|o:&&:&o| 3
 2|ooo&&&o| 2
 1|o::oooo| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|.O.OOX.| 7
 6|OXXXOX.| 6
 5|OX.XOX.| 5
 4|OXXOOXX| 4
 3|OX.XOX.| 3
 2|OXXXOX.| 2
 1|.OOOOX.| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|.O.OO&:| 7
 6|O&&&O&:| 6
 5|O&:&O&:| 5
 4|O&&OO&&| 4
 3|O&:&O&:| 3
 2|O&&&O&:| 2
 1|.OOOO&:| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|OO.OOO.| 7
 6|OXXXOOO| 6
 5|OX.XOXX| 5
 4|OXXOOX.| 4
 3|OX.XOXX| 3
 2|OXXXOX.| 2
 1|.OOOOX.| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|OO.OOO.| 7
 6|O&&&OOO| 6
 5|O&:&O&&| 5
 4|O&&OO&:| 4
 3|O&:&O&&| 3
 2|O&&&O&:| 2
 1|.OOOO&:| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|.OOOOX.| 7
 6|OXXXOX.| 6
 5|OX.XOX.| 5
 4|O.X.OXX| 4
 3|OX.XOX.| 3
 2|OXXXOX.| 2
 1|.OOOOX.| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|=@@@@&:| 7
 6|@XXX@&:| 6
 5|@X.X@&:| 5
 4|@.X.@&&| 4
 3|@X.X@&:| 3
 2|@XXX@&:| 2
 1|=@@@@&:| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|OOOOOOO| 7
 6|OXXXXXO| 6
 5|OX.X.XO| 5
 4|OXX.XXO| 4
 3|OXXXXXO| 3
 2|OXOOOXO| 2
 1|OO?!?OO| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|OOOOOOO| 7
 6|O&&&&&O| 6
 5|O&:&:&O| 5
 4|O&&:&&O| 4
 3|O&&&&&O| 3
 2|O&OOO&O| 2
 1|OO...OO| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFGHJ
  +---------+
 9|.XXXXXXO.| 9
 8|OXOOO.XOO| 8
 7|OXO.O.XO.| 7
 6|OXXO.OXOO| 6
 5|O.XOOOXXO| 5
 4|O.XXXX?!X| 4
 3|OOOOOOX?X| 3
 2|.O.O.OOXO| 2
 1|.O.O..OOO| 1
  +---------+
   ABCDEFGHJ
""", """
   ABCDEFGHJ
  +---------+
 9|=xxxxxx@=| 9
 8|@x@@@=x@@| 8
 7|@x@=@=x@=| 7
 6|@xx@=@x@@| 6
 5|@=x@@@xx@| 5
 4|@=xxxx==x| 4
 3|@@@@@@x=x| 3
 2|=@=@=@@x@| 2
 1|=@=@==@@@| 1
  +---------+
   ABCDEFGHJ
""")

    test_position("""
   ABCDEFGHJ
  +---------+
 9|XXXXXXO..| 9
 8|XOOOXXOOO| 8
 7|XO.OX.O..| 7
 6|XOOXXOOO.| 6
 5|X.OXOXXOO| 5
 4|XOOXX?!XO| 4
 3|XO.OOX?XO| 3
 2|XOOOOOXOO| 2
 1|XXXXXXXO.| 1
  +---------+
   ABCDEFGHJ
""", """
   ABCDEFGHJ
  +---------+
 9|XXXXXX@==| 9
 8|X@@@XX@@@| 8
 7|X@=@X.@==| 7
 6|X@@XX@@@=| 6
 5|X.@X.XX@@| 5
 4|X@@XX..X@| 4
 3|X@=@@X.X@| 3
 2|X@@@@@X@@| 2
 1|XXXXXXX@=| 1
  +---------+
   ABCDEFGHJ
""")

    test_position("""
   ABCDEF
  +------+
 6|?....?| 6
 5|.XXXX.| 5
 4|.X.X.?| 4
 3|?.X.X.| 3
 2|!.XXX.| 2
 1|!?...?| 1
  +------+
   ABCDEF
""", """
   ABCDEF
  +------+
 6|......| 6
 5|.&&&&.| 5
 4|.&:&..| 4
 3|..&:&.| 3
 2|..&&&.| 2
 1|......| 1
  +------+
   ABCDEF
""")

    test_position("""
   ABCDEF
  +------+
 6|O!O!!!| 6
 5|!OOOOO| 5
 4|OO.OXX| 4
 3|X.O?X.| 3
 2|OOXXOO| 2
 1|!OOOO!| 1
  +------+
   ABCDEF
""", """
   ABCDEF
  +------+
 6|@=@===| 6
 5|=@@@@@| 5
 4|@@=@xx| 4
 3|x=@=x=| 3
 2|@@xx@@| 2
 1|=@@@@=| 1
  +------+
   ABCDEF
""")

    test_position("""
   ABCDEFG
  +-------+
 7|O.O....| 7
 6|.OOOOOO| 6
 5|OO.OXXX| 5
 4|X.O.X..| 4
 3|OOXOXXX| 3
 2|.OOOOOO| 2
 1|O.O....| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|@=@====| 7
 6|=@@@@@@| 6
 5|@@=@xxx| 5
 4|x=@=x==| 4
 3|@@=@xxx| 3
 2|=@@@@@@| 2
 1|@=@====| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|O.O....| 7
 6|OOOOOOO| 6
 5|.O.OXXX| 5
 4|X.O.X..| 4
 3|O.XOXXX| 3
 2|OOOOOOO| 2
 1|O.O....| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|@=@====| 7
 6|@@@@@@@| 6
 5|=@=@xxx| 5
 4|x=@=x==| 4
 3|@=x@xxx| 3
 2|@@@@@@@| 2
 1|@=@====| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|O.O....| 7
 6|OOOOOOO| 6
 5|...OXXX| 5
 4|XXO.X..| 4
 3|O.XOXXX| 3
 2|OOOOOOO| 2
 1|O.O....| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|@=@====| 7
 6|@@@@@@@| 6
 5|===@xxx| 5
 4|xx@=x==| 4
 3|@=x@xxx| 3
 2|@@@@@@@| 2
 1|@=@====| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|O.O....| 7
 6|OOOOOOO| 6
 5|...OXXX| 5
 4|XXO.X..| 4
 3|O.X.XXX| 3
 2|OOOOOOO| 2
 1|O.O....| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|@=@====| 7
 6|@@@@@@@| 6
 5|...@XXX| 5
 4|XXO.X..| 4
 3|@.X.XXX| 3
 2|@@@@@@@| 2
 1|@=@====| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFGHJ
  +---------+
 9|.........| 9
 8|.OOOOOOO.| 8
 7|.OXXXXXO.| 7
 6|.OX.O.XO.| 6
 5|.OOXXXOO.| 5
 4|.OO.X.OO.| 4
 3|.OXXXXXO.| 3
 2|OOX.O.XOO| 2
 1|.OXXXXXO.| 1
  +---------+
   ABCDEFGHJ
""", """
   ABCDEFGHJ
  +---------+
 9|=========| 9
 8|=@@@@@@@=| 8
 7|=@XXXXX@=| 7
 6|=@X.O.X@=| 6
 5|=@@XXX@@=| 5
 4|=@@.X.@@=| 4
 3|=@XXXXX@=| 3
 2|@@X.O.X@@| 2
 1|=@XXXXX@=| 1
  +---------+
   ABCDEFGHJ
""")

    test_position("""
   ABCDEFG
  +-------+
 7|OOOOOOO| 7
 6|OXXXXXO| 6
 5|OX.X.XO| 5
 4|OXX.XXO| 4
 3|OXXXXXO| 3
 2|OXOOOXO| 2
 1|OO?X?OO| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|ooooooo| 7
 6|o&&&&&o| 6
 5|o&:&:&o| 5
 4|o&&:&&o| 4
 3|o&&&&&o| 3
 2|o&ooo&o| 2
 1|oo:&:oo| 1
  +-------+
   ABCDEFG
""")

    test_position("""
   ABCDEFG
  +-------+
 7|.......| 7
 6|.......| 6
 5|.......| 5
 4|OOOOOO.| 4
 3|XXXXXO.| 3
 2|X.X.XO.| 2
 1|.O.XXO.| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|.......| 7
 6|.......| 6
 5|.......| 5
 4|OOOOOO.| 4
 3|&&&&&O.| 3
 2|&:&:&O.| 2
 1|:o:&&O.| 1
  +-------+
   ABCDEFG
""")


    test_position("""
   ABCDE
  +-----+
 5|OOOO.| 5
 4|OOOOO| 4
 3|XXXXX| 3
 2|XXXXX| 2
 1|.XXXX| 1
  +-----+
   ABCDE
""", """
   ABCDE
  +-----+
 5|OOOO.| 5
 4|OOOOO| 4
 3|XXXXX| 3
 2|XXXXX| 2
 1|.XXXX| 1
  +-----+
   ABCDE
""")

    test_position("""
   ABCDEFG
  +-------+
 7|....O..| 7
 6|...OOOO| 6
 5|O.O.O..| 5
 4|XOOOO..| 4
 3|.XO....| 3
 2|XXO....| 2
 1|OOO....| 1
  +-------+
   ABCDEFG
""", """
   ABCDEFG
  +-------+
 7|....@==| 7
 6|...@@@@| 6
 5|O.@=@..| 5
 4|X@@@@..| 4
 3|.X@....| 3
 2|XX@....| 2
 1|@@@....| 1
  +-------+
   ABCDEFG
""")

    
if __name__=="__main__":
    test_all()
