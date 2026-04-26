from math import floor
import pygame as pg


class HeartsUI:
    __hidden: bool = True

    __vp: pg.Surface
    __surface: pg.Surface
    __x: int
    __y: int
    __spacing_px: int = 30
    __scales: list[float]
    __last_amt: int = 0

    def __init__(self, veiw_port: pg.Surface, surface: pg.Surface, x: int, y: int):
        self.__vp = veiw_port
        self.__surface = surface
        self.__x = x
        self.__y = y
        self.__scales = [1.0] * 10  # support up to 10 hearts
        self.__last_amt = 0

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

            # Apply scale
            if self.__scales[i] != 1.0:
                size = surf.get_size()
                scaled_surf = pg.transform.scale(
                    surf,
                    (int(size[0] * self.__scales[i]), int(size[1] * self.__scales[i])),
                )
                pos = (
                    self.__x
                    + (self.__spacing_px * i)
                    - (scaled_surf.get_width() - size[0]) // 2,
                    self.__y - (scaled_surf.get_height() - size[1]) // 2,
                )
                self.__vp.blit(scaled_surf, pos)
            else:
                self.__vp.blit(surf, (self.__x + (self.__spacing_px * i), self.__y))

    def update(self, dt: float, hearts_amt: int):
        if self.__hidden:
            return

        if hearts_amt != self.__last_amt:
            for i in range(
                min(len(self.__scales), max(hearts_amt, self.__last_amt - 1))
            ):
                self.__scales[i] = 1.5
            self.__last_amt = hearts_amt

        for i in range(len(self.__scales)):
            if self.__scales[i] > 1.0:
                self.__scales[i] -= 2.0 * dt
                if self.__scales[i] < 1.0:
                    self.__scales[i] = 1.0

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
