from typing import Callable, Literal
import pygame as pg

from car import Car
from helper import load_image


class UpgradeCard:
    def __init__(
        self, state: Literal["selected", "unselected"], pos: Literal["left", "right"]
    ):

        self.selected = load_image("upgrade_menu/selected.png")
        self.unselected = load_image("upgrade_menu/unselected.png")
        self.state: Literal["selected", "unselected"] = state
        self.pos = pos
        self.car = Car(None, self.selected, None, None)

    def draw(self, surface: pg.Surface):
        center = surface.get_rect().center
        image = self.selected if self.state == "selected" else self.unselected

        if self.pos == "left":
            surface.blit(
                image,
                (center[0] - (image.width / 2) - 100, center[1] - (image.height / 2)),
            )
        else:
            surface.blit(
                image,
                (center[0] - (image.width / 2) + 100, center[1] - (image.height / 2)),
            )
