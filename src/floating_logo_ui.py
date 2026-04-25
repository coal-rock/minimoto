from typing import List
import pygame as pg
from helper import *

# USING AS PLACEHOLDER
CAR_IMG_PATH = "car/car012.png"

# M I N I M O T O ; image paths
M_IMG_PATH = ""
I_IMG_PATH = ""
N_IMG_PATH = ""
O_IMG_PATH = ""
T_IMG_PATH = ""



class FloatingLogoUI:
    __logo: List[__Letter]
    __vp: pg.Surface
    __hidden: bool = False

    class __Letter:
        __vp: pg.Surface
        __hidden: bool = False
        __x: int
        __y: int
        
        # For floating animation
        __bounds: int = 6
        __offset: int = 0
        __rate: int = 1
        __frames_per: int = 5
        __frames_per_count: int = 0
        __direction: bool = True

        def __init__(self, 
                     x: int, 
                     y: int,
                     viewport: pg.Surface, 
                     img_path: str, 
                     offset_start: int,
                     ):
            self.__vp = viewport
            self.__surface = load_image(img_path)
            self.__x = x
            self.__y = y
            self.__offset = offset_start

        def update(self):
            if self.__hidden:
                return

            self.__frames_per_count += 1

            if self.__frames_per_count >= self.__frames_per:
                self.__frames_per_count = 0
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

        def draw(self):
            if self.__hidden:
                return
            self.__vp.blit(self.__surface, (self.__x, self.__y))

        def hide(self):
            self.__hidden = True

        def show(self):
            self.__hidden = False

    def __init__(self, viewport: pg.Surface):
        self.__vp = viewport

        # TODO: Update image paths for: M I N I M O T O
        self.__logo = [
                self.__Letter(120, 30, self.__vp, CAR_IMG_PATH, -5),
                self.__Letter(160, 30, self.__vp, CAR_IMG_PATH, -3),
                self.__Letter(200, 30, self.__vp, CAR_IMG_PATH, -1),
                self.__Letter(240, 30, self.__vp, CAR_IMG_PATH, 1),
                self.__Letter(280, 30, self.__vp, CAR_IMG_PATH, 3),
                self.__Letter(320, 30, self.__vp, CAR_IMG_PATH, 5),
                self.__Letter(360, 30, self.__vp, CAR_IMG_PATH, 3),
                self.__Letter(400, 30, self.__vp, CAR_IMG_PATH, 1),
                ]

    def hide(self):
        self.__hidden = True
        for l in self.__logo: l.hide()

    def show(self):
        self.__hidden = False
        for l in self.__logo: l.show()

    def draw(self):
        for l in self.__logo: l.draw()

    def update(self, dt: float):
        for l in self.__logo: l.update()
