class GasUI:
    __hidden: bool = True

    def __init__(self):
        pass

    def draw(self, amt: int):
        pass

    def update(self, dt: float):
        pass

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
