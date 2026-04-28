import pygame as pg
from helper import get_dir


class BonesUI:
    __hidden: bool = True
    __vp: pg.Surface
    __surface: pg.Surface
    __text: pg.Surface
    __shadow_text: pg.Surface
    __text_color: tuple[int, int, int]

    __last_count: int = 0
    __scale: float = 1.0

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
        self.__scale = 1.0
        self.__last_count = 0
        self.__text = self.__font.render("x0", True, self.__text_color)
        self.__shadow_text = self.__font.render("x0", True, (0, 0, 0))

    def draw(self, amt: int):
        if self.__hidden:
            return

        # We draw the icon and text to a temp surface to scale them together
        # The total area is roughly 150x40
        temp_surf = pg.Surface((200, 50), pg.SRCALPHA)

        # Draw icon to temp
        temp_surf.blit(self.__surface, (0, 0))

        # Draw text to temp
        text_pos = (self.__text_offset_x, self.__text_offset_y)
        temp_surf.blit(self.__shadow_text, (text_pos[0] + 1, text_pos[1] + 1))
        temp_surf.blit(self.__text, text_pos)

        if self.__scale != 1.0:
            size = temp_surf.get_size()
            scaled_surf = pg.transform.scale(
                temp_surf,
                (int(size[0] * self.__scale), int(size[1] * self.__scale)),
            )
            pos = (
                self.__x - (scaled_surf.get_width() - size[0]) // 4,
                self.__y - (scaled_surf.get_height() - size[1]) // 2,
            )
            self.__vp.blit(scaled_surf, pos)
        else:
            self.__vp.blit(temp_surf, (self.__x, self.__y))

    def update(self, dt: float, bones_amt: int):
        if self.__hidden:
            return

        if self.__last_count != bones_amt:
            if bones_amt > self.__last_count:
                self.__scale = 1.5
            self.__last_count = bones_amt
            self.__text = self.__font.render(f"x{bones_amt}", True, self.__text_color)
            self.__shadow_text = self.__font.render(f"x{bones_amt}", True, (0, 0, 0))

        if self.__scale > 1.0:
            self.__scale -= 2.0 * dt
            if self.__scale < 1.0:
                self.__scale = 1.0

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
        self.__scale = 1.5
