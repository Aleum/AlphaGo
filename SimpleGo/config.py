import sys
debug_flag = True
debug_output = sys.stderr

komi = 7.5
repeat_check = True
use_threads_scoring_system = False
use_nth_order_liberties = 3 #10
use_nth_order_liberties = 0
use_oxygen = False

use_lambda = True
debug_tactics = False
sgf_trace_tactics = False
use_shadow_cache = True
#slower settings
#lambda_node_limit = 100
#lambda_slow_node_limit = 3
#lambda_connection_node_limit = 30
#faster setting

# capture nodes:
#    max (min_capture_lambda1_nodes, lambda_node_limit * capture_lambda1_factor_limit * 8(danger sense))
# life&death: 
#    lambda_slow_node_limit*other_lambda1_factor_limit*8 (danger sense) *5 (big_block_life_death_increase)
# connection:
#    lambda_connection_node_limit*other_lambda1_factor_limit*8 (danger sense)

lambda_node_limit = 400 #capture tactics
capture_lambda1_factor_limit = 10 #multiplied with above gives 1000
min_capture_lambda1_nodes = 2000 #needed, sometimes 1000 nodes is not enough and this is fatal in ladders (==ladder limit == 2-1 liberty tactics)
lambda_slow_node_limit = 20 #life/death tactics
lambda_connection_node_limit = 100 #connection tactics
other_lambda1_factor_limit = 2 #used for life, death and connection tactics
use_danger_increase = True #if danger is detected, will increase node limits up to 8x
use_big_block_life_death_increase = True #will do up to 5x more life&death nodes for bigger blocks

# When this is on and there are no tactical moves it tries to find
# biggest unconditional move. This shortens yose significantly. Without
# this it will play in its territory until it accidentally makes it all
# unconditionally alive. Maybe first flag to turn off. First though
# reduce node limits significantly.
use_unconditional_search = True

# Expensive, allows for better shape defences: This tries other nearby
# moves in hope of finding move that defends same blocks but has better
# shape score. Sometimes expensive when it finds better move and again
# tries better neighbors, etc... 
# More important flag than use_danger_increase -flag
try_to_find_better_defense = True

# Turns on life&death and heuristical death reading. This is expensive even with low node limits.
# Turn this off before try_to_find_alive_move is turned off.
# Should turn this off before ladder limit is turned too low
use_life_and_death = True

# Crucial and when losing a lot also quite expensive. If this is false it
# will not do tactical reading for selected move. This flag is more
# important than try_to_find_better_defense. Capture node limits should
# probably be < 100 before this is used. However maybe using this before
# reducing ladder limits is reduced dangerously low.
# This disables try_to_find_better_defense also, but it should have been disabled before this anyway.
try_to_find_alive_move = True

# Crucial! All flags are off and all node limits are at 1 and still not
# enough time? Using this will make engine weaker than WeakBot50k. Maybe
# less than 1s/move.
use_tactical_reading = True

# *Fast* last resort: needs initialization when turned on (maybe make it
# detect this automatically): This is a bit like IdiotBot, but a bit:
# weaker: It will play into unconditional territories but not into eyes
# and gives priority for atari related moves. See big games project
# images. 1s of available time + time used on netlag should be enough to
# finish game. Initialization + move generation using this faster than
# use_tactical_reading and subsequent moves are  generated in less than 1/100s.
play_randomly = False


#Plays out using local scoring each block from attack and defense viewpoint
#Use that as status if tactical reading didn't give any result
#replaces most capture tactics and life and death reading
use_playout_reading = True
if use_playout_reading:
##    lambda_node_limit = 30
##    #lambda_slow_node_limit = 1
##    #use_big_block_life_death_increase = False
##    use_life_and_death = False
    eye_heuristic_move_limit = 10
##    use_danger_increase = False

fast_playout = True
if fast_playout:
    liberty_range = 2
    eye_range = 2
    connection_range = 4
else:
    liberty_range = 4
    eye_range = 3
    connection_range = 6

playout_alpha_beta = False
playout_alpha_beta_games = 13
playout_alpha_beta_depth = 4

time_usage_ratio = 1.0 #1.0: use all time

try:
    import c_board
    use_c = True
    monte_carlo_games = 1000
##    pattern_file = "patterns.dat"
##    ok = c_board.load_pattern_result_table(pattern_file)
##    if not ok:
##        sys.stderr.write("Warning: patterns file not loaded!\n")
except:
    use_c = False
    monte_carlo_games = 0
monte_carlo_games = 0

use_uct = use_c
uct_count = 100
uct_result_sure = 0.95
uct_enable_nice_endgame = False

use_uct_tactics = use_uct and False

use_opening_library = False

# time management settings
time_per_move_limit = 25
games_per_move_limit = 2**63 #let time to limit usually...
games_per_second_estimate = 2000
manage_time = False
statistics_limit = 20
lambda_node_limit_baseline = 0
node_divisor = 2
factor_divisor = 2

lambda_limit = 10
use_pn_search = True #Proof number search
lambda_depth_limit = 10001
danger_move_limit = 5

use_chains = False

purely_random_no_eye_fill = True
always_remove_opponent_dead = False
