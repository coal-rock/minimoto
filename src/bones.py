import pygame as pg
from helper import get_dir


class BonesUI:
    __hidden: bool = True
    __vp: pg.Surface
    __surface: pg.Surface
    __text: pg.Surface
    __text_color: tuple[int, int, int]

    __last_count: int = -1

    __x: int
    __y: int
    __text_offset_x: int = 40
    __text_offset_y: int = 5

    def __init__(
        self,
        veiw_port: pg.Surface,
        surface: pg.Surface,
        x: int,
        y: int,
        color: tuple[int, int, int] = (255, 255, 255),
    ):
        self.__vp = veiw_port
        self.__surface = surface
        self.__x = x
        self.__y = y
        self.__text_color = color
        self.__font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"), 24)

    def draw(self, amt: int):
        if self.__hidden:
            return

        self.__vp.blit(self.__surface, (self.__x, self.__y))

        text_pos = (self.__x + self.__text_offset_x, self.__y + self.__text_offset_y)
        # shadow bc based
        self.__vp.blit(self.__shadow_text, (text_pos[0] + 1, text_pos[1] + 1))
        # Draw main text
        self.__vp.blit(self.__text, text_pos)

    def update(self, dt: float, bones_amt: int):
        if self.__hidden:
            return

        if self.__last_count == bones_amt:
            return

        self.__text = self.__font.render(f"x{bones_amt}", True, self.__text_color)
        self.__shadow_text = self.__font.render(f"x{bones_amt}", True, (0, 0, 0))

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
