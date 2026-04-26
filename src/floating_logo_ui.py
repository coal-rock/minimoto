from typing import List
import pygame as pg
from helper import *
from math import floor

class FloatingLogoUI:
    __logo: pg.Surface
    __vp: pg.Surface
    __hidden: bool = False

    __x: int
    __y: int = 10

    # Animation
    __bounds: int = 3
    __offset: int = 0
    __rate: int = 1
    __debounce: int = 0
    __debounce_rate: int = 22
    __direction: bool = True

    def __init__(self, viewport: pg.Surface):
        self.__vp = viewport
        self.__logo = load_image("logo/logo_2.png")
        self.__logo = pg.transform.scale_by(self.__logo, 0.8)
        self.__x = floor(((36 * 16) - self.__logo.width) / 2)

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False

    def draw(self):
        if self.__hidden:
            return
        self.__vp.blit(self.__logo, (self.__x, self.__y))

    def update(self, dt: float):
        if self.__hidden:
            return

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
