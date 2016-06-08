class Chain:
    def __init__(self):
        self.blocks = {}

    def add_block(self, block):
        self.blocks[block.get_origin()] = block
        block.chain = self

    def has_block(self, block):
        return block.get_origin() in self.blocks

    def get_color(self):
        return self.blocks[self.get_origin()].color

    def get_origin(self):
        return min(self.blocks)
