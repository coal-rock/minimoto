from typing import Callable
import pygame as pg
from helper import *


class Button:
    __x: int
    __y: int
    __floating: bool
    __image_path: str | None
    __rect: pg.Rect
    __onclick: Callable
    __screen: pg.Surface

    __rect_mode: bool
    __rect: pg.Rect

    __w: int
    __h: int
    __scale: float
    __hidden: bool

    __surface: pg.Surface
    
    def __init__(
            self, 
            x: int, 
            y: int, 
            screen: pg.Surface,
            onclick: Callable,
            floating: bool = False,
            image_path: str = "",
            rect_mode: bool = False,
            rect_w: int = 10,
            rect_h: int = 10,
            scale: float = 1.0
            ):
        self.__x = x
        self.__y = y
        self.__floating = floating
        self.__image_path = image_path
        self.__rect_mode = rect_mode
        self.__onclick = onclick
        self.__screen = screen
        self.__scale = scale

        if self.__rect_mode:
            self.__rect = pg.Rect(x, y, rect_w, rect_h)
            self.__w = rect_w
            self.__h = rect_h
        else:
            self.__surface = load_image(self.__image_path)
            self.__image_rect = self.__surface.get_rect()
            self.__h = self.__surface.get_height()
            self.__w = self.__surface.get_width()
            self.__surface = pg.transform.scale_by(self.__surface, self.__scale)


        self.__hidden = False

    def get_pos(self) -> tuple[int, int]:
        """
        Get position of button
        """
        return (self.__x, self.__y)

    def get(self) -> pg.Surface:
        return self.__surface

    def draw(self):
        if self.__hidden:
            return
        if self.__rect_mode:
            pg.draw.rect(self.__screen, (255, 255, 255), self.__rect)
        else:
            self.__screen.blit(self.__surface, (self.__x, self.__y))
            

    def update(self, dt: float):
        pass
        # self.__screen.blit(
        #         self.__surface,
        #         self.__image_rect)

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False

    def click(self):
        self.__onclick()

    def click_if(self, x: int, y: int):
        """
        Runs __onclick if in bounds
        """
        if self.in_bounds(x, y):
            self.__onclick()

    def in_bounds(self, x: int, y: int) -> bool:
        return (x >= self.__x and 
                x <= self.__x + self.__w and 
                y >= self.__y and 
                y <= self.__y +self.__h)
    
