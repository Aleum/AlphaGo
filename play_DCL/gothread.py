class Thread:
    def __init__(self, pos1, pos2, length, color):
        self.pos1 = pos1
        self.pos2 = pos2
        self.length = length
        self.color = color
        self.strength = 1.0

    def key(self):
        return self.pos1, self.pos2

##    def strength(self):
##        return 1.0 / self.length

##    def __cmp__(self, other):
##        return cmp(self.strength(), other.strength())

    def __cmp__(self, other):
        return cmp(self.strength, other.strength)

