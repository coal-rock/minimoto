INITIAL_GAS: int = 100

class Gas:
    gas: int = INITIAL_GAS

    def __init__(self):
        pass

    def decrement(self, amt: int = 1):
        self.gas -= amt

    def increment(self, amt: int = 1):
        self.gas += amt

    def get(self) -> int:
        return self.gas
