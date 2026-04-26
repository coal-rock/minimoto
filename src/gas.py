import pygame as pg

class GasUI:
    __hidden: bool = True

    def __init__(self, veiw_port: pg.Surface, surface: pg.Surface):
        pass

    def draw(self, amt: float):
        if self.__hidden:
            return

    def update(self, dt: float, gas: float):
        if self.__hidden:
            return

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
