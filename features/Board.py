# -*- coding: utf-8 -*-
"""
    Board.py
"""

class Board(object):
    def __init__(self, rows, cols, stones=None):
        """

        Args:
            rows:
            cols:
            stones: A tuple of (row, col, color)'s
        """
        self._board = [[None for j in range(cols)] for j in range(rows)]
        if stones is not None:
            for stone in stones:
                self._board[stone[0]][stone[1]] = stone[2]

    def group_of(self, row, col):
        """
        Args:
            row:
            col:

        Returns:
            (stone color, group)
            A stone group which includes the stone at (row, col).
            (), if board[row][col] is empty.
        """
        stone_color = self._board[row][col]
        if stone_color is None:
            return tuple()

        unvisited_positions = [(row, col),]
        group = []
        while len(unvisited_positions) > 0:
            # current_position = unvisited_positions.pop(len(unvisited_positions) - 1)
            current_position = unvisited_positions.pop(0)
            group.append(current_position)
            for position in self.neighbor_positions(current_position[0], current_position[1]):
                if (self._board[position[0]][position[1]] == stone_color) and ((position[0], position[1]) not in (group + unvisited_positions)):
                    unvisited_positions.append((position[0], position[1]))

        return (stone_color, tuple(group))

    def groups(self):
        occupied_positions = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self._board[row][col] is not None:
                    occupied_positions.append((row, col))

        stone_groups = []
        skip_positions = []
        for position in occupied_positions:
            if position in skip_positions: continue
            group = self.group_of(position[0], position[1])
            for group_position in group[1]:
                index = occupied_positions.index(group_position)
                skip_positions.append(occupied_positions[index])

            stone_groups.append(group)

        return tuple(stone_groups)

    def eye_color(self, row, col):
        """

        Args:
            row:
            col:

        Returns:
            color of surrounding color, if (row, col) is an eye.
            None, otherwise
        """
        if self._board[row][col] is not None:
            return None

        neighbor_color = None
        for position in self.neighbor_positions(row, col):
            if (neighbor_color is not None) and (neighbor_color != self._board[row][col]):
               return None

            neighbor_color = self._board[row][col]

        return neighbor_color

    def liberty_positions_of(self, group):
        if (len(group) == 0) or (len(group[1]) == 0):
            return 0

        # stone_color = group[0]
        positions = group[1]
        liberty_positions = []
        for current_position in positions:
            for position in self.neighbor_positions(current_position[0], current_position[1]):
                if self._board[position[0]][position[1]] is None:
                    liberty_positions.append(position)

        return set(liberty_positions)

    def liberty_of(self, group):
        return len(self.liberty_positions_of(group))

    def is_legal(self, row, col, color):
        """

        Args:
            row:
            col:
            color:

        Returns:

        Also, the play should not gill own eyes, although technically it is a legal play.
        """
        if self._board[row][col] is not None:
            return False

        liberties = []
        for position in self.neighbor_positions(row, col):
            if (self._board[position[0]][position[1]] is None) or (self._board[position[0]][position[1]] == color):
                return True
            liberties.append(self.liberty_of(self.group_of(position[0], position[1])))

        return min(liberties) <= 1

    def legal_positions(self, color):
        legals = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.is_legal(row, col, color):
                    legals.append((row, col))

        return legals

    def is_sensible(self, row, col, color):
        if not self.is_legal(row, col, color):
            return False

        # Check if the play fills own eye.
        for position in self.neighbor_positions(row, col):
            if (self._board[position[0]][position[1]] is None) or (self._board[position[0]][position[1]] != color):
                return True

        return False

    def sensible_positions(self, color):
        sensibles = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.is_sensible(row, col, color):
                    sensibles.append((row, col))

        return sensibles


    @property
    def rows(self):
        return len(self._board)

    @property
    def cols(self):
        return len(self._board[0])

    def neighbor_positions(self, row, col):
        if row > 0:
            yield (row - 1, col)
        if row < self.rows - 1:
            yield (row + 1, col)
        if col > 0:
            yield (row, col - 1)
        if col < self.cols - 1:
            yield (row, col + 1)

    def __getitem__(self, item):
        return self._board[item]

    def __setitem__(self, item, value):
        self._board[item] = value

    def __repr__(self):
        return "[{0}]".format("; ".join(["".join([(stone_color or ".") for stone_color in row]) for row in self._board]))

    def __str__(self):
        return "\n".join(["".join([(stone_color or ".") for stone_color in row]) for row in self._board])

if __name__ == "__main__":
    from Plays import Plays

    PLAYS = (
        ('b', (0, 0)),
        ('w', (0, 1)),
        ('b', (0, 2)),
        ('w', (1, 0))
    )

    plays = Plays(PLAYS)
    board = plays.board(3)
    legal_plays = board.legal_plays('b')
    print(len(legal_plays))
    print(legal_plays)