class Bones:
    bones: int = 0

    def __init__(self):
        pass

    def decrement(self, amt: int = 1):
        self.bones -= amt

    def increment(self, amt: int = 1):
        self.bones += amt

    def get(self) -> int:
        return self.bones
