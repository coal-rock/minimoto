from typing import Callable
import pygame as pg

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

    
    def __init__(self, view_port: pg.Surface, callback: Callable):
        self.__vp = view_port
        self.__callback = callback

    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False

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
    pass

class AttackSpeedCard(UpgradeCard):
    pass

class BoostDurationCard(UpgradeCard):
    pass

class MaxHealthCard(UpgradeCard):
    pass


