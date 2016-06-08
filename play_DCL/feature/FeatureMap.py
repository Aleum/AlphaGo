# -*- coding: utf-8 -*-
"""
    FeatureMap.py
"""
from Plays import Plays

"""
Handling of pass (play is None)
turns_since_played_plane -> skip
label_plane -> all-zeroes map is returned
"""
class FeatureMap(object):
    FEATURES = (
        {'name': "player_stones", 'method_name': "_player_stones_plane", 'planes': 1},
        {'name': "opponent_stones", 'method_name': "_opponent_stones_plane", 'planes': 1},
        {'name': "empty_positions", 'method_name': "_empty_positions_plane", 'planes': 1},
        {'name': "ones", 'method_name': "_ones_plane", 'planes': 1},
        {'name': "turns_since_played", 'method_name': "_turns_since_played_binary_planes", 'planes': 8},
        {'name': "liberties", 'method_name': "_liberties_binary_planes", 'planes': 8},
        {'name': "capture_size", 'method_name': "_capture_size_binary_planes", 'planes': 8},
        {'name': "self_atari_size", 'method_name': "_self_atari_size_binary_planes", 'planes': 8},
        {'name': "sensibleness", 'method_name': "_sensibleness_plane", 'planes': 1},
        {'name': "zeroes", 'method_name': "_zeroes_plane", 'planes': 1},
    )
    VALUE_NET_ADDITIONAL_FEATURES = (
        {'name': "player_color", 'method_name': "_player_color_plane", 'planes': 1},
    )
    LABEL = {'name': "label", 'method_name': "label_plane", 'planes': 1}

    def __init__(self, plays, turn_number):
        if turn_number > len(plays):
            turn_number = len(plays)

        self._plays = plays
        self._turn_number = turn_number

    @property
    def play(self):
        return self._plays.play(self._turn_number)

    @property
    def next_play(self):
        if self._turn_number < self.total_plays:
            return self._plays.play(self._turn_number + 1)
        else:
            return None
        
    @property
    def player_color(self):
        return self._plays.next_player_color(self._turn_number)

    @property
    def opponent_color(self):
        return self.play.opponent_of(self.player_color)

    @property
    def turn_number(self):
        return self._turn_number

    @property
    def total_plays(self):
        return self._plays.total_plays

    @property
    def rows(self):
        return self._plays.rows

    @property
    def cols(self):
        return self._plays.cols

    def _player_stones_plane(self):
        mapper = {self._plays.play(self._turn_number).color: 1}
        return [[mapper.get(stone_color, 0) for stone_color in row] for row in self._plays.board(self._turn_number)]
        
    def _opponent_stones_plane(self):
        mapper = {self._plays.play(self._turn_number).opponent_color: 1}
        return [[mapper.get(stone_color, 0) for stone_color in row] for row in self._plays.board(self._turn_number)]
        
    def _empty_positions_plane(self):
        mapper = {None: 1}
        return [[mapper.get(stone_color, 0) for stone_color in row] for row in self._plays.board(self._turn_number)]
        
    def _ones_plane(self):
        return [[1 for i in range(self._plays.rows)] for j in range(self._plays.cols)]
        
    def _zeroes_plane(self):
        return [[0 for i in range(self._plays.rows)] for j in range(self._plays.cols)]

    def _bitwise_planes_of(self, feature_plane, plane_count=8):
        row_planes = []
        for row in feature_plane:
            col_planes = []
            for turns in row:
                value_planes = []
                for i in range(plane_count):
                    value_planes.append((turns & (1 << i)) >> i)
                col_planes.append(value_planes)

            row_planes.append(list(zip(*col_planes)))

        feature_planes = list(zip(*row_planes))

        return feature_planes

    def _binary_planes_of(self, feature_plane, plane_count=8):
        planes = []
        for plane_index in range(plane_count):
            plane = [[1 if value == plane_index + 1 else 0 for value in row] for row in feature_plane]
            planes.append(plane)

        return planes
        
    def _turns_since_played_plane(self):
        feature_plane = self._zeroes_plane()
        for turns_since, play in enumerate(reversed(self._plays[:self._turn_number])):
            if (not play.is_pass()) and feature_plane[play.row][play.col] == 0:
                feature_plane[play.row][play.col] = turns_since + 1
                
        return feature_plane
        
    def _turns_since_played_binary_planes(self, plane_count=8):
        return self._bitwise_planes_of(self._turns_since_played_plane(), plane_count)

    def _liberties_plane(self):
        feature_plane = self._zeroes_plane()
        board = self._plays.board(self._turn_number)

        stone_groups = board.groups()
        for group in stone_groups:
            liberty = board.liberty_of(group)
            for position in group[1]:
                if feature_plane[position[0]][position[1]] != 0:
                    raise ValueError("Something went wrong! One position belonged to more than one group.")

                feature_plane[position[0]][position[1]] = liberty

        return feature_plane

    def _liberties_binary_planes(self, plane_count=8):
        return self._binary_planes_of(self._liberties_plane(), plane_count)

    def _capture_size_plane(self):
        feature_plane = self._zeroes_plane()
        board = self._plays.board(self._turn_number)

        stone_groups = board.groups()
        for group in stone_groups:
            if group[0] == self.player_color:
                continue
            liberty_positions = board.liberty_positions_of(group)
            if len(liberty_positions) == 0:
                raise ValueError("Something went wrong! There is a block with zero liberty.")
            elif len(liberty_positions) == 1:
                feature_plane[tuple(liberty_positions)[0][0]][tuple(liberty_positions)[0][1]] = len(group[1])

        return feature_plane

    def _capture_size_binary_planes(self, plane_count=8):
        return self._binary_planes_of(self._capture_size_plane(), plane_count)

    def _self_atari_size_plane(self):
        feature_plane = self._zeroes_plane()
        board = self._plays.board(self._turn_number)

        stone_groups = board.groups()
        for group in stone_groups:
            if group[0] == self.opponent_color:
                continue
            liberty_positions = board.liberty_positions_of(group)
            if len(liberty_positions) == 0:
                raise ValueError("Something went wrong! There is a block with zero liberty.")
            elif len(liberty_positions) == 1:
                feature_plane[tuple(liberty_positions)[0][0]][tuple(liberty_positions)[0][1]] = len(group[1])

        return feature_plane

    def _self_atari_size_binary_planes(self, plane_count=8):
        return self._binary_planes_of(self._self_atari_size_plane(), plane_count)

    def _sensibleness_plane(self):
        feature_plane = self._zeroes_plane()
        board = self._plays.board(self._turn_number)

        for position in board.sensible_positions(self.player_color):
            feature_plane[position[0]][position[1]] = 1

        return feature_plane
        
    def _next_play_plane(self):
        """
        Note the implication of "pass" play.
        If the next play is "pass," the next play map is all zeroes.

        Returns:

        """
        feature_plane = self._zeroes_plane()
        next_play = self.next_play
        if (next_play is not None) and (not next_play.is_pass()):
            feature_plane[next_play.row][next_play.col] = 1
            
        return feature_plane

    def _player_color_plane(self):
        if self.player_color == 'b':
            return self._zeroes_plane()
        else:
            return self._ones_plane()

    def _board_plane(self):
        return self._plays.board(self._turn_number)

    def _label_plane(self):
        return self._next_play_plane()

    def _input_planes(self, features):
        input_planes = []
        for feature in features:
            if feature['planes'] > 1:
                input_planes.extend(getattr(self, feature['method_name'])(feature['planes']))
            else:
                input_planes.append(getattr(self, feature['method_name'])())

        return input_planes

    @property
    def input_planes_policynet(self):
        return self._input_planes(FeatureMap.FEATURES)

    @property
    def input_planes_valuenet(self):
        features = list(FeatureMap.FEATURES)
        features.extend(list(FeatureMap.VALUE_NET_ADDITIONAL_FEATURES))
        return self._input_planes(tuple(features))

    @property
    def board(self):
        return self._plays.board(self._turn_number)

    @property
    def label(self):
        return self._label_plane()

    # def __getattr__(self, attrname):
    #     from functools import partial
    #
    #     for feature in FeatureMap.FEATURES:
    #         if feature['name'] == attrname:
    #             return partial(type(self).__dict__[feature['method_name']], self)
    #     try:
    #         return super(FeatureMap, self).__getattr__(self, attrname)
    #     except AttributeError as e:
    #         raise AttributeError("{0!r} object has no attribute {1!r}".format(type(self).__name__, attrname))


if __name__ == "__main__":

    import os.path
    from utility import print_features, print_int_feature, print_board, print_feature

    SGF_STORAGE_PATH = "."
    SGF_FILENAME = "0323_result01-0.sgf"
    TURN_NUMBER = 69

    plays = Plays()
    plays.load_from_sgf(os.path.join(SGF_STORAGE_PATH, SGF_FILENAME))
    features = FeatureMap(plays, TURN_NUMBER)

    print("After move {0}{1}".format(features.turn_number,
                                     " (Game ended.)" if features.turn_number == features.total_plays else " / {0}".format(
                                         features.total_plays)))
    print("Next player: {0!r}{1}".format(features.player_color,
                                         "" if features.turn_number != features.total_plays else "(Game ended.)"))
    print("")
    print("{0}\t{1}")
    print_features(features)
    print_int_feature(features.board, features._turns_since_played_plane())
    print("")
    print_int_feature(features.board, features._liberties_plane())
    print("")
    print_int_feature(features.board, features._capture_size_plane())
    print("")
    print_int_feature(features.board, features._self_atari_size_plane())
    print("")
    print_feature(features._label_plane())
    print("")
    print_board(features.board)
    print("")

    print("Done.")
