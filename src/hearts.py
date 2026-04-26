from math import floor
import pygame as pg


class HeartsUI:
    __hidden: bool = True

    __vp: pg.Surface
    __surface: pg.Surface
    __x: int
    __y: int
    __spacing_px: int = 30

    def __init__(self, veiw_port: pg.Surface, surface: pg.Surface, x: int, y: int):
        self.__vp = veiw_port
        self.__surface = surface
        self.__x = x
        self.__y = y

        # grey version for empty hearts
        self.__grey_surface = surface.copy()
        for x_pos in range(self.__grey_surface.get_width()):
            for y_pos in range(self.__grey_surface.get_height()):
                r, g, b, a = self.__grey_surface.get_at((x_pos, y_pos))
                grey = int(0.299 * r + 0.587 * g + 0.114 * b)
                self.__grey_surface.set_at((x_pos, y_pos), (grey, grey, grey, a))

    def draw(self, amt: float, max_amt: int = 3):
        if self.__hidden:
            return

        _amt: int = floor(amt)

        for i in range(0, max_amt):
            surf = self.__surface if i < _amt else self.__grey_surface
            self.__vp.blit(surf, (self.__x + (self.__spacing_px * i), self.__y))

    def update(self, dt: float, hearts_amt: int):
        if self.__hidden:
            return

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
