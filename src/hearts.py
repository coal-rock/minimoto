from math import floor
import pygame as pg

class HeartsUI:
    __hidden: bool = True

    __vp: pg.Surface
    __surface: pg.Surface
    __x: int
    __y: int
    __spacing_px: int = 30

    def __init__(self, 
                 veiw_port: pg.Surface, 
                 surface: pg.Surface,
                 x: int,
                 y:int):
        self.__vp = veiw_port
        self.__surface = surface
        self.__x = x
        self.__y = y

    def draw(self, amt: float):
        if self.__hidden:
            return

        _amt: int = floor(amt)

        for i in range(0, _amt):
            self.__vp.blit(
                    self.__surface, 
                    (self.__x + (self.__spacing_px * i), self.__y))

    def update(self, dt: float, hearts_amt: int):
        if self.__hidden:
            return

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False


