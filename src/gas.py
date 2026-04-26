import pygame as pg
from math import floor

class GasUI:
    __hidden: bool = True
    __vp: pg.Surface
    __surface: pg.Surface

    __x: int
    __y: int

    __max_w_px: int = 100
    __max_h_px: int = 10
    __shadow_h_px: int = 2

    __bar_offset_x: int = 40
    __bar_offset_y: int = 13

    __main_rect: pg.Rect
    __shadow_rect: pg.Rect

    __main_color: tuple[int, int, int] = (200, 25, 25)
    __shadow_color: tuple[int, int, int] = (120, 20, 20)

    def __init__(self, 
                 veiw_port: pg.Surface, 
                 surface: pg.Surface,
                 x: int,
                 y: int):
        self.__vp = veiw_port
        self.__surface = surface
        self.__x = x
        self.__y = y

        self.__main_rect = pg.Rect(
                self.__x + self.__bar_offset_x, 
                self.__y + self.__bar_offset_y, 
                self.__max_w_px, 
                self.__max_h_px)

        self.__shadow_rect = pg.Rect(
                self.__x + self.__bar_offset_x, 
                self.__y + self.__bar_offset_y + self.__max_h_px - self.__shadow_h_px,
                self.__max_w_px, 
                self.__shadow_h_px)

    def draw(self, amt: float):
        if self.__hidden:
            return
        
        self.__vp.blit(self.__surface, (self.__x, self.__y))
        pg.draw.rect(self.__vp, self.__main_color, self.__main_rect)
        pg.draw.rect(self.__vp, self.__shadow_color, self.__shadow_rect)

    def update(self, dt: float, gas: float):
        if self.__hidden:
            return

        self.__main_rect.width = max(floor(gas), 0)
        self.__shadow_rect.width = max(floor(gas), 0)

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
