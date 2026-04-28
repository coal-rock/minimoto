import pygame as pg

from hearts import HeartsUI
from gas import GasUI
from bones import BonesUI

from helper import load_image, get_dir, HEIGHT

HEARTS_IMAGE_PATH: str = "heart/ui.png"
HEARTS_X: int = 5
HEARTS_Y: int = 5

GAS_IMAGE_PATH: str = "gas_can/ui.png"
GAS_X: int = 5
GAS_Y: int = 45

BONES_IMAGE_PATH: str = "skull/ui.png"
BONES_X: int = 5
BONES_Y: int = 85


class GameUI:
    __vp: pg.Surface
    __hidden: bool = True

    def __init__(self, vp: pg.Surface):
        self.__vp = vp
        self.hearts = HeartsUI(vp, load_image(HEARTS_IMAGE_PATH), HEARTS_X, HEARTS_Y)
        self.gas = GasUI(vp, load_image(GAS_IMAGE_PATH), GAS_X, GAS_Y)
        self.bones = BonesUI(vp, load_image(BONES_IMAGE_PATH), BONES_X, BONES_Y)
        self.font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"), 16)

    def draw(
        self,
        hearts_amt: float,
        max_hearts_amt: int,
        gas_amt: float,
        bones_amt: int,
        fps: int = 0,
        enemy_count: int = 0,
    ):
        self.hearts.draw(hearts_amt, max_hearts_amt)
        self.gas.draw(gas_amt)
        self.bones.draw(bones_amt)

        if not self.__hidden:
            fps_text = self.font.render(f"FPS: {fps}", True, (255, 255, 255))
            enemy_text = self.font.render(
                f"ENEMIES: {enemy_count}", True, (255, 255, 255)
            )

            self.__vp.blit(fps_text, (5, HEIGHT - 45))
            self.__vp.blit(enemy_text, (5, HEIGHT - 25))

    def update(self, dt: float, hearts_amt: int, gas_amt: float, bones_amt: int):
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
