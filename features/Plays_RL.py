# -*- coding: utf-8 -*-
"""
    Plays.py
"""
from Board import Board

from gomill import sgf
from gomill import sgf_moves
import gomill


class Play_RL(object):
    """
    A utility wrapper class for a single turn play.
    """
    PLAYER_COLORS = {
        'b': 1,
        'B': 1,
        'w': 2,
        'W': 2
    }
        
    def __init__(self, turn_number, color, position):
        if color not in Play_RL.PLAYER_COLORS:
            raise ValueError("Invalid player color: {0!r}".format(color))
            
        self._turn_number = turn_number
        self._color = color
        self._row = position[0] if position is not None else None
        self._col = position[1] if position is not None else None
    
    @property
    def row(self):
        return self._row
        
    @property
    def col(self):
        return self._col
        
    @property
    def color(self):
        """
        Returns:
            Letter of player color: 'b' or 'w'
        """
        return self._color

    @property
    def turn_number(self):
        return self._turn_number

    @property
    def opponent_color(self):
        for color in Play_RL.PLAYER_COLORS.keys():
            if color.lower() != self.color:
                return color.lower()

        # Execution should never reach here!
        raise KeyError("Something is wrong. This should never have executed.")

    def opponent_of(self, player_color):
        if player_color not in Play_RL.PLAYER_COLORS.keys():
            raise ValueError("Invalid player color.")

        for color in Play_RL.PLAYER_COLORS.keys():
            if color.lower() != player_color:
                return color.lower()

        # Execution should never reach here!
        raise ValueError("Something is wrong. This should never have executed.")
        
    @property
    def color_upper(self):
        """
        Returns:
            Upper case letter of player color: 'B' or 'W'
        """
        return self._color.upper()
        
    @property
    def color_digit(self):
        """
        Returns:
            Digit of player color: 1 or 2, as indicated in COLOR_TABLE.
        """
        try:
            return Play_RL.PLAYER_COLORS[self._color]
        except KeyError:
            raise ValueError("Invalid player color: {0!r}".format(self._color))
        
    @property
    def position(self):
        if (self._row is None) and (self._col is None):
            return None
        return (self._row, self._col)
        
    def to_tuple(self):
        """
        Returns:
            A (row, col, color) tuple.
        """
        return (self._row, self._col, self._color)
        
    def to_digited_tuple(self):
        """
        Returns:
            A (row, col, color digit) tuple.
            
        Raises:
            ValueError, if color value is invalid (either 'b' or 'w').
            (propagated from self.color_digit())
        """
        return (self._row, self._col, self.color_digit)
        
    def is_pass(self):
        """
        Returns:
            True, if this play is pass, that is, if play[1] is None.
        """
        return ((self._row is None) and (self._col is None))

    def __repr__(self):
        return "{0.__class__.__name__}({0.turn_number}, ({0.row}, {0.col}), {0.color})".format(self)

class Plays_RL(object):
    """
    When accessing individual play, it is recommended to use Plays.play() method.
    It will reduce possible confusions from different base-indexing.
    turn_number is 1-based.
    """
    def __init__(self, plays=(), initial_board=None, rows=9, cols=9):
        """
        Args:
            plays: a list of tuple (color, (row, col))
        """
        self.plays = plays
        self._rows = rows
        self._cols = cols
        self.initial_board = initial_board
        self._winner = None

        invalid_play = self.first_invalid_play
        if invalid_play is not None:
            print("Invalid play: [{0.turn_number:3}]: {0.color_upper}({0.row}, {0.col})".format(invalid_play))
            raise ValueError("There are invalid play in the plays.")

    @property
    def plays(self):
        return self._plays

    @plays.setter
    def plays(self, plays):
        """
            Args:
                plays: a list of tuple (color, (row, col))
        """
        self._plays = [Play_RL(turn + 1, play[0], play[1]) for turn, play in enumerate(plays)]

    @property
    def initial_board(self):
        return self._initial_board

    @initial_board.setter
    def initial_board(self, initial_board):
        self._initial_board = [[col for col in row] for row in initial_board] if initial_board is not None else [[None] * self._cols] * self._rows

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols
        
    @property
    def total_plays(self):
        """
        Returns:
            Number of play turns of the game. (Initial handicaps are not accounted for.)
        """
        return len(self._plays) if self._plays is not None else 0

    @property
    def total_nonpass_plays(self):
        if self._plays is None:
            return 0

        nonpass_turns = 0
        for play in self._plays:
            if not play.is_pass():
                nonpass_turns += 1

        return nonpass_turns
        
    def play(self, turn_number):
        """
        Args:
            turn_number: A 1-based turn number for which play is to be retrieved.
            
        Returns:
            A Play instance of the play corresponding to turn_number.
                
        Raises:
            ValueError, if turn_number is not a valid, i.e., total number of plays
                is smaller than turn_number.
                
        Note: turn_number is 1-based!
        """
        if (turn_number <= 0) or (turn_number > self.total_plays):
#            raise ValueError("Invalid turn number: {0}. Valid range is 0 < turn number <= {1}".format(turn_number, self.total_plays))
            return None
            
        return self._plays[turn_number - 1]

    @property
    def _initial_board_gomill(self):
        gomill_board = gomill.boards.Board(self._rows)
        ab = [(row, col) for row in range(self._rows) for col in range(self._cols) if self._initial_board[row][col] in ('b', 'B')]
        aw = [(row, col) for row in range(self._rows) for col in range(self._cols) if self._initial_board[row][col] in ('w', 'W')]
        is_legal = gomill_board.apply_setup(ab, aw, ())
        if not is_legal:
            raise ValueError("Illegal moves in the initial board!")

        return gomill_board
        
    def board(self, turn_number):
        """
        Args:
            turn_number: 1-based index

        Returns:
            A list of list board instance after turn_number plays.
        """
        gomill_board = self._initial_board_gomill

        for turn in range(turn_number):
            try:
                play = self.play(turn + 1)
                if not play.is_pass():
                    gomill_board.play(play.row, play.col, play.color)

            except ValueError as e:
                raise StandardError("illegal move in plays: ({row}, {col}, {color})".format(self.play(turn)))
            except AttributeError:
                # if self.turn_number + 1 > max play
                continue

        return Board(self._rows, self._cols, ((row, col, gomill_board.board[row][col]) for col in range(gomill_board.side) for row in range(gomill_board.side) if gomill_board.board[row][col] is not None))

    @property
    def first_invalid_play(self):
        """
        Checks if SGF file has an invalid (mostly illegal) play.
        
        Returns:
            A Play instance of the first invalid play.
        """
        gomill_board = self._initial_board_gomill

        for play in self._plays:
            try:
                if not play.is_pass():
                    gomill_board.play(play.row, play.col, play.color)
            except ValueError:
                # ValueError indicates that the latest play is invalid.
                return play
            
        return None
        
    @property
    def pass_count(self):
        """
        Counts the number of None move entries in the plays.
        (that is, the number of passes)
        
        Returns:
            Number of passes in the SGF game.
            Counted until the first invalid (if there is any), or the game end.
            
        Assumes nothings has been played yet.
        It is not possible to "resume" from certain point in the course of the
        game, since gomil.Board class does not track the number of moves.
        """
        return len(self.pass_plays)
        
    @property
    def pass_plays(self):
        """
        Counts the number of None move entries in the plays.
        (that is, the number of passes)
        
        Returns:
            Number of passes in the SGF game.
            Counted until the first invalid (if there is any), or the game end.
            
        Assumes nothings has been played yet.
        It is not possible to "resume" from certain point in the course of the
        game, since gomil.Board class does not track the number of moves.
        """
        return [play for play in self._plays if play.is_pass()]
                
    def format_play_sequence(self, turn_number, turns_before=2, turns_after=2, format_str="[{0.turn_number:3}]: {0.color_upper}({0.row}, {0.col})", format_str_pass="[{0.turn_number:3}]: {0.color_upper}(., .)"):
        """
        Formats a sequene of play.
        
        Args:
            turn_number: Turn number of the play to format.
            turns_before: Number of turns before the play to format.
            turns_after: Number of turns after the play to format.
            format_str
            format_str_pass
        """
        formatted_plays = []
        for play_offset in range(-min(turns_before, turn_number - turns_before + 1), min(turns_after + 1, self.total_plays - turn_number + 1)):
            play = self._plays[turn_number + play_offset - 1]
            if not play.is_pass():
                formatted_plays.append(format_str.format(play))
            else:
                formatted_plays.append(format_str_pass.format(play))
            
        return ", ".join(formatted_plays)
        
    def next_play(self, turn_number):
        """
        Returns:
            None, if there is no play after the latest play, i.e. if the game ended.
        """
        try:
            return self.play(turn_number + 1)
        except ValueError as e:
            return None

    def next_player_color(self, turn_number):
        """
        Args:
            turn_number: Turn number after which the next player is to be looked for.

        Returns:
            Color of the next player. (Even if the game ended.)
            'b', if this is the first turn.
        """
        # If turn_number is a valid turn number, return the opponent color of the corresponding play.
        play = self.play(turn_number)
        if play is not None:
            return play.opponent_color

        # Otherwise, look for the latest valid play.
        if self.total_plays > 0:
            return self.play(self.total_plays)
        else:
            # If there is no play at all, assume the beginning of play and return 'b'
            return 'b'

    def load_from_sgf(self, sgf_filepath):
        """
        Adaptation of show_sgf_file function on examples/show_sgf in gomill package.

        Args:
            sgf_filepath

        Raises:
            IOError, if file open and/or read fails.
        """
        try:
            with open(sgf_filepath) as f:
                sgf_game = sgf.Sgf_game.from_string(f.read())
        except ValueError:
            raise StandardError("bad sgf file")

        try:
            (gomill_board, plays) = sgf_moves.get_setup_and_moves(sgf_game)
        except ValueError as e:
            raise StandardError(str(e))

        self.initial_board = gomill_board.board
        self.plays = plays
        self._winner = sgf_game.get_winner()
        
        if sgf_filepath[-5:] == "1.sgf":
            self.win = True
        else:
            self.win = False

    def __len__(self):
        return len(self._plays)

    def __getitem__(self, item):
        return self._plays[item]


if __name__ == "__main__":
    import os.path
    import pprint
    
    PLAYS = (
        ( # capture at corner
            ('b', (0, 0)),
            ('w', (0, 1)),
            ('b', (0, 2)),
            ('w', (1, 0))
        ),

        ( # ko (repetitive capture) - 패(劫)
            ('b', (3, 3)),
            ('w', (3, 4)),
            ('b', (2, 4)),
            ('w', (2, 3)),
            ('b', (3, 5)),
            ('w', (3, 2)),
            ('b', (4, 4)), # black captures ('w', (3, 4))
            ('w', (4, 3)),
            ('b', (7, 7)),
            ('w', (3, 4)), # white captures ('b', (3, 3))
            ('b', (3, 3)), # black captures ('w', (3, 4)) again!
            ('w', (3, 4)), # white captures ('b', (3, 3)) again!
        ),

        ( # black stones with two holes
            ('b', (1, 1)), ('b', (1, 2)), ('b', (1, 3)), ('b', (1, 4)), ('b', (1, 5)),
            ('b', (2, 1)), ('b', (2, 2)), ('b', (2, 3)), ('b', (2, 4)), ('b', (2, 5)),
            ('b', (3, 1)),                ('b', (3, 3)), ('b', (3, 4)), ('b', (3, 5)),
            ('b', (4, 1)), ('b', (4, 2)), ('b', (4, 3)),                ('b', (4, 5)),
            ('b', (5, 1)), ('b', (5, 2)), ('b', (5, 3)), ('b', (5, 4)), ('b', (5, 5)),
        ),

        (  # black stones with two holes
            ('b', (0, 0)), ('b', (0, 1)), ('b', (0, 2)), ('b', (0, 3)), ('b', (0, 4)),
            ('b', (1, 0)), ('b', (1, 1)), ('b', (1, 2)), ('b', (1, 3)), ('b', (1, 4)),
            ('b', (2, 0)),                ('b', (2, 2)), ('b', (2, 3)), ('b', (2, 4)),
            ('b', (3, 0)), ('b', (3, 1)), ('b', (3, 2)),                ('b', (3, 4)),
            ('b', (4, 0)), ('b', (4, 1)), ('b', (4, 2)), ('b', (4, 3)), ('b', (4, 4)),
        )
    )

    SGF_STORAGE_PATH = "../kifu/result_T"
    SGF_FILENAME = "0323_result01-0.sgf"
    #    SGF_FILENAME = "0323_result01-104.sgf"
    TURN_NUMBER = 69

    # plays = Plays()
    # plays.load_from_sgf(os.path.join(SGF_STORAGE_PATH, SGF_FILENAME))
    plays = Plays_RL(PLAYS[2])
    # pprint.pprint(board.board)
    # pprint.pprint(plays._initial_board)
    pprint.pprint(plays.board(TURN_NUMBER))

    # print(plays.board(TURN_NUMBER).group_of(1, 2))
    # print(plays.board(TURN_NUMBER).group_of(1, 8))
    # print(plays.board(TURN_NUMBER).group_of(2, 1))
    # group = plays.board(TURN_NUMBER).group_of(2, 4)
    # print(group)
    # print(plays.board(TURN_NUMBER).liberty_of(group))

    # group = plays.board(TURN_NUMBER).group_of(2, 4)
    # print(group)
    # print(plays.board(TURN_NUMBER).liberty_of(group))

    groups = plays.board(TURN_NUMBER).groups()
    print(groups)
    print(len(groups))
    for group in groups:
        print(plays.board(TURN_NUMBER).liberty_of(group))

    # print(plays.board(TURN_NUMBER).is_legal(0, 0, 'w')) # False
    # print(plays.board(TURN_NUMBER).is_legal(1, 1, 'w')) # False
    # print(plays.board(TURN_NUMBER).is_legal(5, 0, 'w')) # True
    # print(plays.board(TURN_NUMBER).is_legal(6, 8, 'w'))  # True
    #
    # print(plays.board(TURN_NUMBER).is_legal(1, 1, 'b')) # True
    # print(plays.board(TURN_NUMBER).is_legal(6, 8, 'w'))  # True

    legal_positions = plays.board(TURN_NUMBER).legal_positions('b')
    print(len(legal_positions))
    print(legal_positions)

    legal_positions = plays.board(TURN_NUMBER).legal_positions('w')
    print(len(legal_positions))
    print(legal_positions)

    print(plays.board(TURN_NUMBER).is_legal(3, 2, 'b'))
    print(plays.board(TURN_NUMBER).is_sensible(3, 2, 'b'))
    print(plays.board(TURN_NUMBER).is_sensible(4, 4, 'b'))