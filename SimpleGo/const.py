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
