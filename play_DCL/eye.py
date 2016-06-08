from const import *
from utils import *


class Eye:
    """Eye: collection of empty blocks and either black or white blocks

       Attributes:
       parts: list of blocks forming this eye
    """
    def __init__(self):
        self.parts = []

    def iterate_stones(self):
        """Go through all stones in all blocks in eye
        """
        for block in self.parts:
            for stone in block.stones:
                yield stone

    def mark_status(self, live_color):
        """Go through all stones in all blocks in eye
           All opposite colored blocks are marked dead.
           Empty blocks are marked as territory for live_color.
        """
        for block in self.parts:
            if block.color == live_color:
                block.status = UNCONDITIONAL_LIVE
            elif block.color == other_side[live_color]:
                block.status = UNCONDITIONAL_DEAD
            else:
                block.status = live_color + UNCONDITIONAL_TERRITORY

