import copy

class PositionCache:
    def __init__(self, key, score, move, depth, exact):
        self.key = key
        self.score = score
        self.move = move
        self.depth = depth
        self.exact = exact

    def __str__(self):
        return "%s %s %s %s %s" % (self.key, self.score, self.move, self.depth, self.exact)

    def __cmp__(self, other):
        return cmp((self.exact, self.depth), (other.exact, other.depth))


LOWERBOUND = "lowerbound"
UPPERBOUND = "upperbound"
EXACTSCORE = "exactscore"

class AlphaBetaPositionCache:
    def __init__(self, key, score, move, depth, alpha, beta, shadow):
        self.key = key
        self.score = score
        self.move = move
        self.depth = depth
        self.alpha = alpha
        self.beta = beta
        if score >= beta:
            self.flag = LOWERBOUND
        elif score <= alpha:
            self.flag = UPPERBOUND
        else:
            self.flag = EXACTSCORE
        self.shadow = copy.copy(shadow)
            

    def __str__(self):
        return "%s %s %s %s %s %s %s" % (self.key, self.score, self.move, self.depth, self.alpha, self.beta, self.flag)

    #def __cmp__(self, other):
    #    return cmp((self.exact, self.depth), (other.exact, other.depth))


class LambdaPositionCache:
    def __init__(self, key, score, move, shadow, n):
        self.key = key
        self.score = score
        self.move = move
        self.shadow = copy.copy(shadow)
        self.n = n
            
    def __str__(self):
        return "%s %s %s %s" % (self.key, self.score, self.move, self.n)

