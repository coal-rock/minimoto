import pygame as pg
from math import floor
from helper import get_dir

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
    __outline_rect: pg.Rect
    __outline_rect_border_thickness: int = 1

    __main_color: tuple[int, int, int] = (200, 25, 25)
    __shadow_color: tuple[int, int, int] = (120, 20, 20)
    __outline_color: tuple[int, int, int] = (0, 0, 0)

    __flash_timer: float = 0
    __flash_speed: float = 5.0  # flashes per second
    __show_bar: bool = True
    __low_gas_threshold: float = 20.0

    def __init__(self, 
                 veiw_port: pg.Surface, 
                 surface: pg.Surface,
                 x: int,
                 y: int):
        self.__vp = veiw_port
        self.__surface = surface
        self.__x = x
        self.__y = y
        
        self.__font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"), 16)

        self.__main_rect = pg.Rect(
                self.__x + self.__bar_offset_x, 
                self.__y + self.__bar_offset_y, 
                self.__max_w_px, 
                self.__max_h_px)

        self.__outline_rect = pg.Rect(
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
        
        if self.__show_bar or amt >= self.__low_gas_threshold:
            pg.draw.rect(self.__vp, self.__main_color, self.__main_rect)
            pg.draw.rect(self.__vp, self.__shadow_color, self.__shadow_rect)
        
        pg.draw.rect(self.__vp, self.__outline_color, self.__outline_rect, self.__outline_rect_border_thickness)

        if amt < self.__low_gas_threshold and self.__show_bar:
            text = self.__font.render("LOW GAS!", True, (255, 50, 50))
            self.__vp.blit(text, (self.__x + self.__bar_offset_x, self.__y + self.__bar_offset_y + 15))

    def update(self, dt: float, gas: float):
        if self.__hidden:
            return

        self.__main_rect.width = max(floor(gas), 0)
        self.__shadow_rect.width = max(floor(gas), 0)

        if gas < self.__low_gas_threshold:
            self.__flash_timer += dt
            if self.__flash_timer >= 1.0 / self.__flash_speed:
                self.__show_bar = not self.__show_bar
                self.__flash_timer = 0
        else:
            self.__show_bar = True
            self.__flash_timer = 0

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
