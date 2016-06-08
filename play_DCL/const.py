# -*- coding: ms949 -*-

EMPTY = "."
BLACK = "X"
WHITE = "O"
EDGE = "#"

BOTH = BLACK + WHITE

colors = [BLACK, WHITE]

other_side = {BLACK: WHITE, WHITE: BLACK}

CEMPTY = 0
CWHITE = 1
CBLACK = 2
color2ccolor = {BLACK: CBLACK, WHITE: CWHITE, EMPTY: CEMPTY}

PASS_MOVE = (-1, -1)
UNDO_MOVE = (-2, -2)
NO_MOVE = (-3, -3)
RESIGN_MOVE = (-4, -4)

BEST_SCORE = 1000000000
WORST_SCORE = -BEST_SCORE

INFINITE_DISTANCE = 1000000

normal_stone_value_ratio = 0.9 #how much value is given to stones that are not unconditionally alive and have max liberties
dead_stone_value_ratio = -0.8
our_critical_stone_value = 0.6
other_critical_stone_value = -0.6

x_coords_string = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
#x_coords_string = "12345678901234567890"
max_size = len(x_coords_string)

UNCONDITIONAL_LIVE = "alive"
UNCONDITIONAL_DEAD = "dead"
UNCONDITIONAL_UNKNOWN = "unknown"
UNCONDITIONAL_TERRITORY = " territory"
WHITE_UNCONDITIONAL_TERRITORY = WHITE + UNCONDITIONAL_TERRITORY
BLACK_UNCONDITIONAL_TERRITORY = BLACK + UNCONDITIONAL_TERRITORY

TACTICALLY_UNKNOWN = "tactically unknown" #capture; life&death
TACTICALLY_LIVE = "tactically alive" #life&death
TACTICALLY_DEAD = "tactically dead" #capture; life&death
TACTICALLY_CRITICAL = "tactically critical" #capture; life&death

PN_UNKNOWN = 0.5
PN_OR = "or"
PN_AND = "and"
PN_INF = 1000000000



#custom setting
g_mcts_threshold = 15
g_mcts_legalmove_restrict = 100
g_mcts_Cpuck = 10
g_mcts_msweight = 0.5
g_mcts_lamda = 0.5  #for Q value calculation
g_mcts_calctime = 10 
g_mcts_graphviz = False

g_mcts_threadcount_eval = 1 #evaluation thread 
g_mcts_calccount = 100        #count of selection
g_mcts_vl = 5               #virtual loss

SLPOLICY_JSON = "network/slpolicy_model_0.json"
SLPOLICY_H5 = "network/slpolicy_model_0.h5"
ROLLOUT_JSON = "network/rollout_policy_net_model.json"
ROLLOUT_H5 = "network/rollout_policy_net_weights.h5"
VALUE_JSON = "network/value_net_model.json"
VALUE_H5 = "network/value_net_weights_5.h5"
RLPOLICY_JSON = "network/2nd_rlpolicy_model_21.json"
RLPOLICY_H5 = "network/2nd_rlpolicy_model_21.h5"


#EVALUATOR_PORTS = 50001,50002,50003
EVALUATOR_PORTS = 50001
#EVALUATOR_INFOS = "165.132.122.42:50001,165.132.122.41:50001"
#EVALUATOR_INFOS = "165.132.122.42:50001"
#EVALUATOR_INFOS = "127.0.0.1:50001"
EVALUATOR_INFOS = "165.132.122.42:50001,165.132.122.41:50001,165.132.122.41:50002,165.132.122.41:50003,165.132.122.41:50004,165.132.122.43:50001,165.132.122.43:50002"

