from typing import Callable
import pygame as pg

from car import Car
from helper import load_image

CARD_W = 60
CARD_H = 100

class UpgradeCard:
    __hidden: bool = True

    __vp: pg.Surface
    __callback: Callable

    __x: int
    __y: int
    __w: int = CARD_W
    __h: int = CARD_H

    # Animation
    # External, card animation
    __ex_bounds: int = 3
    __ex_offset: int = -1
    __ex_rate: int = 1
    __ex_debounce: int = 0
    __ex_debounce_rate: int = 10
    __ex_direction: bool = True
    
    # internal card animiation
    __in_bounds: int = 3
    __in_offset: int = 1
    __in_rate: int = 1
    __in_debounce: int = 0
    __in_debounce_rate: int = 10
    __in_direction: bool = True
    
    def __init__(self, view_port: pg.Surface, callback: Callable):
        self.__vp = view_port
        self.__callback = callback

    def hide(self):
        self.__hidden = True

    def show(self, x: int, y: int):
        self.__hidden = False
        self.__x = x or self.__x
        self.__y = y or self.__y

    def click_if(self, x: int, y:int):
        if self.__hidden:
            return
        if self.in_bounds(x, y):
            self.__callback()

    def in_bounds(self, x: int, y: int) -> bool:
        return (x >= self.__x and 
                x <= self.__x + self.__w and 
                y >= self.__y and 
                y <= self.__y +self.__h)
    

class JumpCard(UpgradeCard):
    __angled_car: pg.Surface = load_image("car/car008.png")
    __car: Car = Car()

    def draw(self):
        pass

    def update(self, dt: float):
        pass

class AttackSpeedCard(UpgradeCard):
    def draw(self):
        pass

    def update(self, dt: float):
        pass

class BoostDurationCard(UpgradeCard):
    def draw(self):
        pass

    def update(self, dt: float):
        pass

class MaxHealthCard(UpgradeCard):
    def draw(self):
        pass

    def update(self, dt: float):
        pass


