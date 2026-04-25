INITIAL_HEARTS: int = 10

class Hearts:
    hearts: int = INITIAL_HEARTS

    def __init__(self):
        pass

    def decrement(self, amt: int = 1):
        self.hearts -= amt

    def increment(self, amt: int = 1):
        self.hearts += amt

    def get(self) -> int:
        return self.hearts
