from typing import Callable
import pygame as pg
from helper import *
from random import randint


class Button:
    __x: int
    __y: int
    __image_path: str | None
    __rect: pg.Rect
    __onclick: Callable
    __screen: pg.Surface

    __floating: bool
    __bounds: int = 3
    __offset: int = 0
    __rate: int = 1
    __debounce: int = 0
    __debounce_rate: int = 10
    __direction: bool = True

    __rect_mode: bool
    __rect: pg.Rect

    __w: int
    __h: int
    __scale: float
    __hidden: bool

    __surface: pg.Surface
    __highlighted_surface: pg.Surface

    __hover: bool = False
    
    def __init__(
            self, 
            x: int, 
            y: int, 
            screen: pg.Surface,
            onclick: Callable,
            floating: bool = False,
            floating_offset: int = 0,
            debounce_rate: int = 10,
            image_path: str = "",
            highlight_image_path: str = "",
            rect_mode: bool = False,
            rect_w: int = 10,
            rect_h: int = 10,
            scale: float = 1.0,
            ):
        self.__x = x
        self.__y = y
        self.__floating = floating
        self.__offset = floating_offset
        self.__debounce_rate = debounce_rate
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
            self.__highlighted_surface = load_image(highlight_image_path)
            self.__image_rect = self.__surface.get_rect()
            self.__h = self.__surface.get_height()
            self.__w = self.__surface.get_width()

            self.__surface = pg.transform.scale_by(self.__surface, self.__scale)
            self.__highlighted_surface = pg.transform.scale_by(self.__highlighted_surface, self.__scale)


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
            return
        
        if self.__hover:
            self.__screen.blit(self.__highlighted_surface, (self.__x, self.__y))
            return

        self.__screen.blit(self.__surface, (self.__x, self.__y))

    def set_hover(self, value: bool):
        self.__hover = value

    def hover_if(self, x: int, y: int):
        if self.in_bounds(x, y):
            self.set_hover(True)
        else:
            self.set_hover(False)
        

    def update(self, dt: float):
        if self.__floating:
            self.__debounce += 1

            if self.__debounce >= self.__debounce_rate:
                self.__debounce = 0
            else:
                return

            if abs(self.__offset) == self.__bounds:
                self.__direction = not self.__direction 

            if self.__direction:
                self.__y += self.__rate
                self.__offset += self.__rate
            else:
                self.__y -= self.__rate
                self.__offset -= self.__rate

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
    
