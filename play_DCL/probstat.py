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

import sys
import math

class Probstat:
    """A class for storing and retrieving statistical information,
    or for calculating probabilities.
    """
    
    def __init__(self, maximum_size=5000):
        """The class is constructed with one optional integer argument that
        specifies the number of data points to store. While add functionality 
        remains active the entire time, if the size of the cache exceeds the 
        number specified in the constructor call the earliest data points will 
        be deleted without notice.
        """
        
        self.data_list = []
        self.index = 0
        self._max_size = 0
        self.int_type = type(5)
        self.float_type = type(5.0)
        self.list_type = type([])
        if type(maximum_size) == self.int_type:
            self._max_size = maximum_size
        else:
            error_response = "expected int got " + str(type(maximum_size))
            raise ValueError, error_response
    
    def clear_data(self):
        """Removes all stored data in the cache.
        """
        
        self.data_list = []
        self.index = 0
        
    def has_data(self):
        """Returns boolean 
        True if there is any data in the cache
        """
        
        return len(self.data_list) > 0
    
    def size(self):
        """Returns int
        The size of the data stored locally
        """
        
        return len(self.data_list)
    
    def capacity(self):
        """Returns int
        This is the allowable number of elements for data storage
        """
        
        return self._max_size
    
    def add_data(self, data):
        """Appends data to the cache.        
        If the size of the cache exceeds the set amount,
        the earliest value added is overwritten. If argument
        provided is not a single number or list of numbers an
        exception is raised.
        """
        
        if self.capacity() == 0:
            return
        if type(data) == self.list_type:
            for i in data:
                self.add_data(i)
        elif type(data) == self.int_type or type(data) == self.float_type:
            if self.size() == self._max_size:
                self.data_list[self.index] = data
                self.index = self.index + 1
                if self.index == self._max_size:
                    self.index = 0
            else:
                self.data_list.append(data)
        else:
            error_response = "expected number or list of numbers got " + str(type(data))
            raise ValueError, error_response
            
    def median(self):
        """Returns a float
        If there is no data, returns zero
        """
        
        result = float(0)
        if self.has_data():  
            if len(self.data_list) == 1:
                return self.data_list[0]
            local = []
            for i in self.data_list:
                local.append(i) 
            local.sort()
            size = len(local)
            if size%2 == 0:
                result = (local[size/2] + local[((size/2) - 1)]) / 2
            else:
                result = local[(size-1)/2]
        return result
    
    def mode(self):
        """Returns a float
        If the mode is not unique, or if there is no data, this returns zero.
        """
        
        result = float(0)
        largest_value = float(0)
        occurance_of_largest_value = 0
        if self.has_data():
            if len(self.data_list) == 1:
                return self.data_list[0]
            local = []
            for i in self.data_list:
                local.append(i)
            local.sort()
            cache = {} # use data point : instance count
            for i in local:
                if cache.has_key(i):
                    cache[i] = cache[i] + 1
                else:
                    cache[i] = 1
            for k in cache.keys():
                if cache[k] > largest_value:
                    largest_value = cache[k]
                    result = k
                    occurance_of_largest_value = 0
                if cache[k] == largest_value:
                    occurance_of_largest_value = occurance_of_largest_value + 1
        if occurance_of_largest_value > 1:
            result = float(0)
        return result
        
    def mean(self):
        """Returns a float.
        This is the mean of data entered by other methods. This returns zero 
        if there is no data.
        """
        
        result = float(0)
        if self.has_data():
            for i in self.data_list:
                result = result + i
            result = result / len(self.data_list)
        return result 
    
    def variance(self, sample=True):
        """Returns the variance of the data entered by other methods. 
        When called without arguments, or with "True", it returns the sample variance.
        Otherwise it returns the population variance.
        """
        
        N = len(self.data_list)
        if sample:
            N = N - 1
        if N == 0:
            return 0
        mean = self.mean()
        result = float(0)
        for i in self.data_list:
            result = result + (mean - i)**2
        return (result / N)
    
    def stdev(self, sample=True):
        """Returns a float.
        This is the standard deviation of the data entered by other methods. 
        When called without arguments, or with "True", it returns the sample
        standard deviation. Otherwise it returns the population standard deviation.
        """
        
        return math.sqrt(self.variance(sample))
    
    def confidence_interval(self, interval, sample=True):
        """Returns a two-item list of floats for a confidence interval
        [xbar - interval * sigma, xbar + interval * sigma]
        Set last argument to False for the population standard deviation.
        1 sigma is a 68% confidence interval
        2 sigma is a 95% confidence interval
        3 sigma is a 99% confidence interval
        See stdev
        """
        
        return [(self.mean() - interval*self.stdev(sample)), (self.mean() + interval*self.stdev(sample))]
    
    def factorial(self, n, stop=0):
        """Returns int
        factorial(n) returns n!
        factorial(n,stop) calculates n!/stop!
        """
        
        if n == stop:
            return 1
        else:
            return n * self.factorial(n-1, stop)
    
    def choose(self, n, r):
        """Returns int
        This is the number of unordered ways to choose r objects from n objects
        """
        
        # if-else clause minimizes the recursion depth of factorial(n)
        if r > n-r:
            numerator = self.factorial(n, r)
            denominator = self.factorial(n-r)
        else:
            numerator = self.factorial(n, n-r)
            denominator = self.factorial(r)
        return numerator/denominator
    
    def permute(self, n, r):
        """Returns int
        This is the number of ordered ways to choose r objects from n objects
        """
        
        return self.factorial(n, n-r)
    
    def binomial_trial(self, successes, trials, p_win):
        """Returns float
        This is the probability of given successes in given independent trials 
        with given a probability of a 'win' for the trial.
        """
        
        combination = self.choose(trials, successes)
        win = p_win**successes
        lose = (1-p_win)**(trials-successes)
        return combination * win * lose
    
    def make_binomial_trial(self, fixed_p_win):
        """Returns function
        This function is an 'exactly X wins' binomial trial function with a fixed 
        value in place of winning probability
        see binomial_trial
        """
        
        def _b_t(successes, trials):        
            combination = self.choose(trials, successes)
            win = fixed_p_win**successes
            lose = (1-fixed_p_win)**(trials-successes)
            return combination * win * lose
        return _b_t
    
    def binomial_trials(self, at_least_successes, trials, p_win, at_most_successes = 0):
        """Returns float
        This the probability sum of separate binomial trials. 
        Example:
            to calculate the odds of getting at least 20 heads from 40 tosses of a 
            fair coin, one would call:
                binomial_trials(20, 40, 0.5)
            to calculate the odds of getting between 20 and 30 heads from 40 tosses
            of a fair coin, one would call:
                binomial_trials(20, 40, 0.5, 30)
            to calculate the odds of getting up to 19 heads from 40 tosses
            of a fair coin, one would call:
                binomial_trials(0, 40, 0.5, 19)
        """
        
        result = 0
        if at_most_successes <= at_least_successes:
            at_most_successes = trials
        while at_least_successes <= at_most_successes:
            result = result + self.binomial_trial(at_least_successes, trials, p_win)
            at_least_successes = at_least_successes +1
        return result
    
    def make_binomial_trials(self, fixed_p_win):
        """Returns a function
        This is an 'at least X wins' binomial trial function with a fixed 
        value in place of winning probability
        see binomial_trials
        """
        
        def _b_ts(at_least_successes, trials, at_most_successes = 0):
            result = 0
            if at_most_successes <= at_least_successes:
                at_most_successes = trials
            while at_least_successes <= at_most_successes:
                result = result + self.binomial_trial(at_least_successes, trials, fixed_p_win)
                at_least_successes = at_least_successes + 1
            return result
        return _b_ts

if __name__ == "__main__": #test-bed
    help(Probstat)
    #fail_ = Probstat("fails")
    p_size = 7
    print "\nSTATISTICS TEST"
    print "Creating Probstat object with size " + str(p_size)
    s = Probstat(p_size)
    print "Size of Probstat object is " + str(s.capacity())
    data = [10.0,11,11,12,13,13,13,13,13,13,13,13,14]
    print "Adding data"
    print str(data)
    s.add_data(data)
    print "Data: \n" + str(s.data_list)
    print "Adding data"
    print "15.5"
    s.add_data(15.5)
    print "Data: \n" + str(s.data_list)
    #s.add_data("word")
    print "The mean is " + str(s.mean())
    print "The population variance is " + str(s.variance(False))
    print "The population standard deviation is " + str(s.stdev(False))
    interval = s.confidence_interval(3)
    print "99 percent of data is between " + str(interval[0]) + " and " + str(interval[1])
    print "The sample variance is " + str(s.variance())
    print "The sample standard deviation is " + str(s.stdev())
    print "95 percent confidence interval is " + str(s.confidence_interval(2))
    print "99 percent of data is between " + str(s.mean()-3*s.stdev()) + " and " + str(s.mean()+3*s.stdev())
    print "The median is " + str(s.median())
    print "The mode is " + str(s.mode())
    print "\nPROBABILITY TEST"
    print "Odds of winning a 6 choice, 59 number lottery: 1 in " + str(s.choose(59,6))
    print "Fair coin toss: 20 wins in 40 tosses: " + str(s.binomial_trial(20,40,0.5))
    print "Fair coin toss: at least 20 in 40: " + str(s.binomial_trials(20,40,0.5))
    print "Fair coin toss: 20-30 in 40: " + str(s.binomial_trials(20,40,0.5,30))
    print "Fair coin toss: 0-19 in 40: " + str(s.binomial_trials(0,40,0.5,19))
    print "Sanity check of binomial trials\n odds of 0-19 in 40 plus odds of 20-40 in 40: " + str(s.binomial_trials(0,40,0.5,19) + s.binomial_trials(20,40,0.5))
