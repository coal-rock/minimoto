import pygame as pg

from hearts import HeartsUI
from gas import GasUI
from bones import BonesUI

from helper import load_image

HEARTS_IMAGE_PATH: str = "heart/ui.png"
HEARTS_X: int = 20
HEARTS_Y: int = 10

GAS_IMAGE_PATH: str = "gas_can/ui.png"
GAS_X: int = 20
GAS_Y: int = 50

BONES_IMAGE_PATH: str = "skull/ui.png"
BONES_X: int = 20
BONES_Y: int = 10


class GameUI:
    __vp: pg.Surface
    __hidden: bool = True

    def __init__(self, vp: pg.Surface):
        self.__vp = vp
        self.hearts = HeartsUI(vp, load_image(HEARTS_IMAGE_PATH), HEARTS_X, HEARTS_Y)
        self.gas = GasUI(vp, load_image(GAS_IMAGE_PATH), GAS_X, GAS_Y)
        self.bones = BonesUI(vp, load_image(BONES_IMAGE_PATH))

    def draw(self, hearts_amt: float, gas_amt: float, bones_amt: int):
        self.hearts.draw(hearts_amt)
        self.gas.draw(gas_amt)
        self.bones.draw(bones_amt)

    def update(self, 
               dt: float, 
               hearts_amt: int, 
               gas_amt: float, 
               bones_amt:int
               ):
        self.hearts.update(dt, hearts_amt)
        self.gas.update(dt, gas_amt)
        self.bones.update(dt, bones_amt)

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
