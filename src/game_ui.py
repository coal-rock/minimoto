import pygame as pg

import gas
from hearts import HeartsUI
from gas import GasUI
from bones import BonesUI

HEARTS_IMAGE_PATH: str = ""

GAS_IMAGE_PATH: str = ""

BONES_IMAGE_PATH: str = ""

class GameUI:
    hearts = HeartsUI()
    gas = GasUI()
    bones = BonesUI()

    __vp: pg.Surface
    __hidden: bool = True

    def __init__(self, vp: pg.Surface):
        self.__vp = vp

    def draw(self, hearts_amt: int, gas_amt: int, bones_amt: int):
        self.hearts.draw(hearts_amt)
        self.gas.draw(gas_amt)
        self.bones.draw(bones_amt)

    def update(self, dt: float):
        self.hearts.update(dt)
        self.gas.update(dt)
        self.bones.update(dt)

    def hide(self):
        self.__hidden = True
        self.hearts.hide()
        self.gas.hide()
        self.bones.hide()

    def show(self):
        self.__hidden = False
        self.hearts.show()
        self.gas.show()
        self.bones.show()
