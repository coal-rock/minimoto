from typing import Callable
import pygame as pg
from helper import *


class Button:
    __x: int
    __y: int
    __floating: bool
    __image_path: str
    __onclick: Callable
    __screen: pg.Surface

    __w: int
    __h: int
    __hidden: bool

    __surface: pg.Surface
    
    def __init__(
            self, 
            x: int, 
            y: int, 
            floating: bool,
            image_path: str, 
            onclick: Callable,
            screen: pg.Surface
            ):
        self.__x = x
        self.__y = y
        self.__floating = floating
        self.__image_path = image_path
        self.__onclick = onclick
        self.__screen = screen

        self.__surface = load_image(self.__image_path)
        self.__image_rect = self.__surface.get_rect()
        self.__h = self.__surface.get_height()
        self.__w = self.__surface.get_width()

        self.__hidden = False

    def get_pos(self) -> tuple[int, int]:
        """
        Get position of button
        """
        return (self.__x, self.__y)

    def get(self) -> pg.Surface:
        return self.__surface

    def update(self):
        self.__screen.blit(
                self.__surface,
                self.__image_rect)

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False

    def click(self):
        self.__onclick()
    
