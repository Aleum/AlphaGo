# -*- coding: cp1252 -*-
#! /usr/bin/env python

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 1999, 2000, 2001, 2002, 2003 and 2004               #
# by the Free Software Foundation.                              #
#                                                               #
# This program is free software; you can redistribute it and/or #
# modify it under the terms of the GNU General Public License   #
# as published by the Free Software Foundation - version 2.     #
#                                                               #
# This program is distributed in the hope that it will be       #
# useful, but WITHOUT ANY WARRANTY; without even the implied    #
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR       #
# PURPOSE.  See the GNU General Public License in file COPYING  #
# for more details.                                             #
#                                                               #
# You should have received a copy of the GNU General Public     #
# License along with this program; if not, write to the Free    #
# Software Foundation, Inc., 59 Temple Place - Suite 330,       #
# Boston, MA 02111, USA.                                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import probstat
import config
import utils
import math
import os

class Timekeeper:
    def __init__( self ):
        self.boardsize = 0
        self.num_moves = 0
        self.statistics = probstat.Probstat( config.statistics_limit )
        self.stat_limit_min = 1
        self.confidence = 1
        self.none = "none"
        self.absolute = "absolute"
        self.by = "byoyomi"
        self.cby = "canadian"
        self.main_time = "main_time"
        self.by_time = "by_time"
        self.stones = "stones"
        self.periods = "periods"
        self.manage_absolute = False
        
        self.node_divisor = config.node_divisor
        self.factor_divisor = config.factor_divisor
        self.adjustments_made = 0
        
        self.original_lambda_node_limit = config.lambda_node_limit
        self.original_min_capture_lambda1_nodes = config.min_capture_lambda1_nodes
        self.original_lambda_slow_node_limit = config.lambda_slow_node_limit
        self.original_lambda_connection_node_limit = config.lambda_connection_node_limit
        
        self.original_capture_lambda1_factor_limit = config.capture_lambda1_factor_limit
        self.original_other_lambda1_factor_limit = config.other_lambda1_factor_limit
        
        self.original_use_danger_increase = config.use_danger_increase
        self.original_use_big_block_life_death_increase = config.use_big_block_life_death_increase
        
        self.original_use_unconditional_search = config.use_unconditional_search
        self.original_try_to_find_alive_move = config.try_to_find_alive_move
        self.original_use_tactical_reading = config.use_tactical_reading
        self.original_play_randomly = config.play_randomly
        self.original_use_playout_reading = config.use_playout_reading
        
        self.time_settings = {self.none:False, 
                              self.absolute:False, 
                              self.by:False, 
                              self.cby:False, 
                              self.main_time:0, 
                              self.by_time:0, 
                              self.stones:0, 
                              self.periods:0}

        self.different_adjust_levels = 9
        self.timing_data = {}
        for size in (9, 13, 19):
            file_name = "%i_timing.txt" % size
            if os.path.exists(file_name):
                lst = []
                self.timing_data[size] = lst
                for line in open(file_name):
                    lst.append(float(line))
                if len(lst) != self.different_adjust_levels:
                    raise ValueError, "number of timing data levels doesn't match with code"
            else:
                utils.dprintnl("No timing data for size %i, use 'python -i run_test.py' and then 'play_all_sizes()' to generate it" % size)

    def reset( self ):
        """Resets all time settings to zero
        Resets boardsize to 19
        """
        
        self.manage_absolute = False
        self.adjustments_made = 0
        for k in self.time_settings.keys():
            self.time_settings[k] = 0
        config.capture_lambda1_factor_limit = self.original_capture_lambda1_factor_limit
        config.min_capture_lambda1_nodes = self.original_min_capture_lambda1_nodes
        config.lambda_slow_node_limit = self.original_lambda_slow_node_limit
        config.lambda_connection_node_limit = self.original_lambda_connection_node_limit
        config.other_lambda1_factor_limit = self.original_other_lambda1_factor_limit
        config.use_danger_increase = self.original_use_danger_increase
        config.use_big_block_life_death_increase = self.original_use_big_block_life_death_increase
        if self.original_lambda_node_limit < config.lambda_node_limit:
            self.original_lambda_node_limit = config.lambda_node_limit
        else:
            config.lambda_node_limit = self.original_lambda_node_limit
        config.use_unconditional_search = self.original_use_unconditional_search
        config.try_to_find_alive_move = self.original_try_to_find_alive_move
        config.use_tactical_reading = self.original_use_tactical_reading
        config.play_randomly = self.original_play_randomly
        config.use_playout_reading = self.original_use_playout_reading
        #General timing data is more reliable at start of game than last game yose timing data
        self.statistics.clear_data()
        self.statistics.add_data( 1.0 )
    
    def _max_moves( self ):
        """Makes an estimate of the number of moves it will have 
        to play given the size of the board
        """
        
        return int( 0.5 * self.boardsize * self.boardsize )-2
        
    def _can_get_statistics( self ):
        """True if enough data has been stored
        """
        if self.statistics.size() <= self.stat_limit_min:
            return False
        else:
            return True
        
    def set_boardsize( self, size ):
        """Sets the board size for determining the rate to adjust
        config.lambda_node_limit and to determine the approximate
        number of moves for games
        """
        
        self.boardsize = size
        #self.original_lambda_node_limit = config.lambda_node_limit
           
    def _node_aggregate( self ):
        """config.min_capture_lambda1_nodes is used to full extent only in complex ladder.
           Often it might be only few nodes, for example if block already has 3 liberties no search is done.
           Thus using for now factor of 1 for capture_lambda1 and
           factor 10 for normal capture nodes and connection nodes.
           Unconditional analysis is more expensive than normal make_move/undo_move and
           thus using factor of 100 for lambda_slow_node_limit.
        """
        timing_data = [40*60*1000.0,
                       20*60*1000.0,
                       10*60*1000.0,
                       4.2*60*1000.0,
                       46*1000.0,
                       30*1000.0,
                       13*1000.0,
                       2.4*1000.0,
                       0.07*1000.0]
        for size in range(self.boardsize, 9-1, -1):
            if size in self.timing_data:
                timing_data = self.timing_data[size]
                break
        if config.lambda_node_limit == self.original_lambda_node_limit:
            aggregate = timing_data[0]
        elif config.lambda_node_limit == self.original_lambda_node_limit / 2:
            aggregate = timing_data[1]
        elif config.use_life_and_death:
            aggregate = timing_data[2]
        elif config.use_playout_reading:
            aggregate = timing_data[3]
        elif config.lambda_node_limit > 1:
            aggregate = timing_data[4]
        elif config.min_capture_lambda1_nodes == 500:
            aggregate = timing_data[5]
        elif config.use_tactical_reading:
            aggregate = timing_data[6]
        elif not config.play_randomly:
            aggregate = timing_data[7]
        else:
            aggregate = timing_data[8]

        return aggregate
            
        
##        aggregate = 0

##        danger_sense = 1
##        if config.use_danger_increase:
##            danger_sense = 4
            
##        life_and_death = 1
##        if config.use_big_block_life_death_increase:
##            life_and_death = 5
            
##        alive_move = 1
##        if config.try_to_find_alive_move:
##            alive_move = 3
            
##        better_defense = 1
##        if config.try_to_find_better_defense:
##            better_defense = 4
        
##        unconditional_search = 0
##        if config.use_unconditional_search:
##            unconditional_search = 100
            
##        if config.use_tactical_reading:
##            #adding these isn't strictly correct, but otherwise reducing lambda_node_limit won't have any effect on aggregate which is most of time false even with low limits
##            aggregate = aggregate + max(config.min_capture_lambda1_nodes,  config.lambda_node_limit * config.capture_lambda1_factor_limit * danger_sense) + 10 * config.lambda_node_limit * danger_sense
##            if config.use_life_and_death:
##                aggregate = aggregate + 200 * config.lambda_slow_node_limit * config.other_lambda1_factor_limit * danger_sense * life_and_death
##                aggregate = aggregate + 20 * config.lambda_connection_node_limit * config.other_lambda1_factor_limit * danger_sense
##            aggregate = 2000 * aggregate * alive_move * better_defense
##            aggregate = aggregate + unconditional_search
##        elif not config.play_randomly:
##            aggregate = 200 #guess: like 10 tactical searches with 1 node limit
##        else:
##            aggregate = 2 #maybe 100x faster than quick scoring
##        return math.log10( aggregate )*9/self.boardsize
    
    def set_time( self, settings ):
        self.kgs_set_time([self.absolute] + settings)
        
    def kgs_set_time( self, settings ):
        """Handles the arguments passed from KGS's "kgs-time_settings"
        command.
        """
        
        #settings = ["type", main_time, by_time, stones/periods]
        self.reset()
        self.time_settings[settings[0]] = True
        self.num_moves = self._max_moves()
        if self.time_settings[self.none]:
            config.time_per_move_limit = 3600
            return self.none
        self.time_settings[self.main_time] = int( settings[1] )
        if self.time_settings[self.absolute]:
            self.time_left(settings + [0])
            return self.absolute + " " + str( self.time_settings[self.main_time] ) + " estimated max moves: " + str( self.num_moves )
        self.time_settings[self.by_time] = int( settings[2] )
        if self.time_settings[self.by]:
            self.time_settings[self.periods] = int( settings[3] )
            return self.by + " " + str( self.time_settings[self.main_time] ) + " " + str( self.time_settings[self.by_time] ) + " " + str( self.time_settings[self.periods] )
        else:
            self.time_settings[self.stones] = int( settings[3] )
            return self.cby + " " + str( self.time_settings[self.main_time] ) + " " + str( self.time_settings[self.by_time] ) + " " + str( self.time_settings[self.stones] )
        
    def time_left( self, parameters ):
        """Handles the arguments passed by "time_left" command.
        Determines the time per move available. Stores data
        on the time it has taken per move.
        """
        
        # parameters is [color, maintime, stones]
        # but in kgs, periods is always zero, and when 
        # byo-yomi is reached, the "main time" will be the sum
        # of all periods
        if not config.manage_time:
            return "time not managed"
        
        utils.dprintnl( "TIME MANAGEMENT", parameters[1], parameters[2] )
        
        time = float( parameters[1] )
        stones = int( parameters[2] )
        default_message = "ok"

        config.time_per_move_limit = time * 0.05 #tournament setting for absolute time
        return default_message

        if self.num_moves < 5:
            self.num_moves = 5

        if self.time_settings[self.absolute]:
            config.time_per_move_limit = int( time / self.num_moves )
            difference = max(0, self.time_settings[self.main_time] - time)
            self.num_moves = self.num_moves - 1
            data = float( difference ) / self._node_aggregate()
            self.statistics.add_data( data )
            self.time_settings[self.main_time] = time
            if not self._can_get_statistics():
                return default_message
                
        if self.time_settings[self.by]:
            total_by_time = self.time_settings[self.by_time] * self.time_settings[self.periods]
            self.num_moves = self.num_moves - 1
            if time > total_by_time:
                self.confidence = 1
                difference = max(0, self.time_settings[self.main_time] - time)
                data = float( difference ) / self._node_aggregate()
                self.statistics.add_data( data )
                by_tpm = int( 1.25 * self.time_settings[self.by_time] )
                main_time_tpm = int( self.time_settings[self.main_time] / self.num_moves )
                config.time_per_move_limit = max( by_tpm, main_time_tpm )
                self.time_settings[self.main_time] = time
            else:
                self.confidence = 2
                starting_periods = self.time_settings[self.periods]
                periods_remaining = time / self.time_settings[self.by_time]
                difference = max(0, starting_periods - periods_remaining)
                if difference == 0:
                    #assume we used most of one period
                    self.statistics.add_data( 0.75 * self.time_settings[self.by_time] / self._node_aggregate() )
                else:
                    #assume we used just over one period
                    self.statistics.add_data( 1.05 * difference * self.time_settings[self.by_time] / self._node_aggregate() )
                self.time_settings[self.periods] = periods_remaining
                # while there are three periods left, not much urgency
                config.time_per_move_limit = int( self.time_settings[self.by_time] * self.time_settings[self.periods] / float( 3 ) )
        
        if self.time_settings[self.cby]:
            difference = 0
            self.num_moves = self.num_moves - 1
            if stones == 0: # still in main time
                self.confidence = 1
                difference = max(0, self.time_settings[self.main_time] - time)
                self.time_settings[self.main_time] = time
            else:
                self.confidence = 2
                if self.time_settings[self.main_time] != 0:
                    difference = max(0, self.time_settings[self.main_time])
                    self.time_settings[self.main_time] = 0
                difference = max(0, difference + self.time_settings[self.by_time] - time)
                self.time_settings[self.by_time] = time
                self.time_settings[self.stones] = stones
            time_per_stone = int( self.time_settings[self.by_time] / self.time_settings[self.stones] )
            main_time_tpm = int( self.time_settings[self.main_time] / self.num_moves )
            config.time_per_move_limit = max( time_per_stone, main_time_tpm )
            data = float( difference ) / self._node_aggregate()
            self.statistics.add_data( data )
        
        interval = self.statistics.confidence_interval( self.confidence )
        old_config = self._config_as_string()
        #old_aggregate = str( self._node_aggregate() )
        message = ""
        config.time_per_move_limit = config.time_per_move_limit * config.time_usage_ratio
        utils.dprintnl( "time per move limit ", str( config.time_per_move_limit ) )
        utils.dprintnl( "num_moves ", str( self.num_moves ) )
        utils.dprintnl( "main time left ", str( self.time_settings[self.main_time] ) )
        if self._can_get_statistics():
            utils.dprintnl( "#", self.adjustments_made, "config now ", self._config_as_string() )
            #adjust up
            while ( interval[1] * self._node_aggregate() ) < config.time_per_move_limit:
                utils.dprintnl( "adjusting upwards..." )
                old_agg = self._node_aggregate()
                message = self._adjust_all()
                if old_agg == self._node_aggregate():
                    break
                utils.dprintnl( "#", self.adjustments_made, "config now ", self._config_as_string() )
            #adjust down
            while ( interval[1] * self._node_aggregate() ) > config.time_per_move_limit:
                utils.dprintnl( "adjusting downwards..." )
                old_agg = self._node_aggregate()
                message = self._adjust_all()
                if old_agg == self._node_aggregate():
                    break
                utils.dprintnl( "#", self.adjustments_made, "config now ", self._config_as_string() )
        else:
            message = "not enough data"
        new_config = self._config_as_string()
        utils.dprintnl( "expected maximum time of next move ", str( interval[1] * self._node_aggregate() ) )
        utils.dprintnl( "old config ", old_config )
        utils.dprintnl( "new config ", new_config )
        #utils.dprintnl( "old node aggregate ", old_aggregate )
        #utils.dprintnl( "new node aggregate ", str( self._node_aggregate() ) )
        utils.dprintnl( "data:", self.statistics.data_list)
        utils.dprintnl( "------------------------------------------------------------" )
        return message            

    def _config_as_string( self ):
        config_str = str( config.lambda_node_limit ) + " "  
        config_str = config_str + str( config.capture_lambda1_factor_limit ) + " " 
        config_str = config_str + str( config.min_capture_lambda1_nodes ) + " " 
        config_str = config_str + str( config.lambda_slow_node_limit ) + " " 
        config_str = config_str + str( config.lambda_connection_node_limit ) + " " 
        config_str = config_str + str( config.other_lambda1_factor_limit ) + " " 
        config_str = config_str + str( config.use_danger_increase ) + " " 
        config_str = config_str + str( config.try_to_find_better_defense ) + " "
        config_str = config_str + str( config.use_big_block_life_death_increase ) + " "
        config_str = config_str + str( config.use_life_and_death ) + " "
        config_str = config_str + str( config.use_unconditional_search ) + " "
        config_str = config_str + str( config.try_to_find_alive_move ) + " "
        config_str = config_str + str( config.use_tactical_reading ) + " "
        config_str = config_str + str( config.play_randomly ) + " "
        config_str = config_str + str( config.use_playout_reading ) + " "
        config_str = config_str + str( self._node_aggregate() )
        return config_str
    
    def _adjust_all( self ):
        """Adjusts nodes based on statistics of
        move history.
        """

        if self._can_get_statistics():                
            tpm_interval = self.statistics.confidence_interval( self.confidence )
##            if self.time_settings[self.absolute] and not self.manage_absolute:
##                if self.time_settings[self.main_time] > 420:
##                    utils.dprintnl("No need to adjust yet")
##                    return ""
##                else:
##                    self.statistics.clear_data()
##                    self.manage_absolute = True
            if self.time_settings[self.absolute] and not self.manage_absolute:
                self.manage_absolute = True
            undo_adjustments = not ( ( tpm_interval[1] * self._node_aggregate() ) > config.time_per_move_limit )
            #if undo_adjustments == True:
            #        self._adjust_ladder_node_limits( undo_adjustments )
            #        self._adjust_ladder_node_limits( undo_adjustments )
            self._do_adjust(undo_adjustments)
        else:
            utils.dprintnl( "not enough data" )
        return ""

    def _do_adjust( self, undo_adjustments ):
        if self.adjustments_made == 0:
            self._adjust_node_limits( undo_adjustments )
        elif self.adjustments_made == 1:
            self._adjust_node_limits( undo_adjustments )
        elif self.adjustments_made == 2:
            self._adjust_life_death( undo_adjustments )
            self._adjust_danger_sense( undo_adjustments )
        elif self.adjustments_made == 3:
            self._adjust_playout( undo_adjustments )
        elif self.adjustments_made == 4:
            self._adjust_tactical_nodes_and_flags( undo_adjustments )
        elif self.adjustments_made == 5:
            self._adjust_tactical_nodes_and_flags2( undo_adjustments )
        elif self.adjustments_made == 6:
            self._adjust_alive_move(undo_adjustments)
            self._adjust_tactical_reading(undo_adjustments)
        elif self.adjustments_made == 7:
            self._adjust_random(undo_adjustments)
        adjustment_incrementor = 1
        if undo_adjustments:
            adjustment_incrementor = -1
        self.adjustments_made = max( 0, min( self.different_adjust_levels - 2, self.adjustments_made + adjustment_incrementor ) )
        utils.dprintnl( "adjustments made", str( self.adjustments_made ) )

    def _adjust_node_factors( self, undo ):
        adjustment = float( self.factor_divisor )
        if undo:
            adjustment = 1/adjustment
        config.capture_lambda1_factor_limit = int( min( max( 1, config.capture_lambda1_factor_limit // adjustment ), self.original_capture_lambda1_factor_limit ) )
        config.other_lambda1_factor_limit = int( min( max( 1, config.other_lambda1_factor_limit // adjustment ), self.original_other_lambda1_factor_limit ) )
        utils.dprintnl( "node factors divided by ", str( adjustment ) )

    def _adjust_tactical_nodes_and_flags( self, undo ):
        if undo:
            config.lambda_node_limit = self.original_lambda_node_limit / 4
            config.capture_lambda1_factor_limit = self.original_capture_lambda1_factor_limit / 4
            config.min_capture_lambda1_nodes = self.original_min_capture_lambda1_nodes
        else:
            config.lambda_node_limit = 1
            config.capture_lambda1_factor_limit = 1
            config.min_capture_lambda1_nodes = 500

    def _adjust_tactical_nodes_and_flags2( self, undo ):
        if undo:
            config.use_unconditional_search = True
            config.try_to_find_better_defense = True
            config.min_capture_lambda1_nodes = 500
        else:
            config.use_unconditional_search = False
            config.try_to_find_better_defense = False
            config.min_capture_lambda1_nodes = 10

    def _adjust_node_limits( self, undo ):
        adjustment = float( self.node_divisor )
        if undo:
            adjustment = 1 / adjustment
        config.lambda_node_limit = int( min( max( 1, config.lambda_node_limit / adjustment ), self.original_lambda_node_limit ) )
        config.lambda_slow_node_limit = int( min( max( 1, config.lambda_slow_node_limit / adjustment ), self.original_lambda_slow_node_limit ) )
        config.lambda_connection_node_limit = int( min( max( 1, config.lambda_connection_node_limit / adjustment ), self.original_lambda_connection_node_limit ) )
        utils.dprintnl( "node limits divided by ", str( adjustment ) )
        
    def _adjust_ladder_node_limits( self, undo ):
        adjustment = float( self.node_divisor )
        if undo:
            adjustment = 1 / adjustment
        config.min_capture_lambda1_nodes = int( min( max( 1, config.min_capture_lambda1_nodes / adjustment ), self.original_min_capture_lambda1_nodes ) )
        utils.dprintnl( "ladder node limits divided by ", str( adjustment ) )

    def _adjust_playout( self, undo ):
        config.use_playout_reading = undo
        utils.dprintnl( "changed playout" )
        
    def _adjust_danger_sense( self, undo ):
        config.use_danger_increase = undo
        utils.dprintnl( "changed danger increase" )
        
    def _adjust_life_death_size_bonus( self, undo ):
        config.use_big_block_life_death_increase = undo
        utils.dprintnl( "changed big block life and death increase" )
    
    def _adjust_life_death( self, undo ):
        config.use_life_and_death = undo
        utils.dprintnl( "changed life and death reading" )
    
    def _adjust_better_defense( self, undo ):
        config.try_to_find_better_defense = undo
        utils.dprintnl( "changed trying to find better defense" )
        
    def _adjust_alive_move( self, undo ):
        config.try_to_find_alive_move = undo
        utils.dprintnl( "changed trying to find alive move" )
        
    def _adjust_unconditional_search( self, undo ):
        config.use_unconditional_search = undo
        utils.dprintnl( "changed unconditional search" )
    
    def _minimize_all_nodes( self, undo ):
        if undo:
            self._adjust_node_limits( undo )
            self._adjust_ladder_node_limits(undo)
        else:
            config.lambda_node_limit = 1
            config.min_capture_lambda1_nodes = 1
            config.lambda_slow_node_limit = 1
            config.lambda_connection_node_limit = 1
            utils.dprintnl( "all nodes dropped to 1" )
        
            
    def _minimize_all_factors( self, undo ):
        if undo:
            self._adjust_node_factors( undo )
        else:
            config.capture_lambda1_factor_limit = 1
            config.other_lambda1_factor_limit = 1
            utils.dprintnl( "all factors dropped to 1" )
            
    def _adjust_tactical_reading(self, undo):
        config.use_tactical_reading = undo
        utils.dprintnl( "changed tactical reading" )

    def _adjust_random(self, undo):
        config.play_randomly = not undo
        utils.dprintnl( "changed random" )
        
if __name__ == "__main__":
    print " "
    
