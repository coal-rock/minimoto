"""
This will be made with 1am tears.
    - Ruby
"""

import pygame as pg
from random import sample
from typing import Callable

from upgrade_cards import *


class UpgradeUI:
    """
    Upgrade options:
        Reload Speed
        Bullets in chamber
        Jump !!!
        Speed
        Attack Speed !!!
        Attack Damage
        Number of Shots Fired
        Boost duration !!!
        Gas/Efficiency
        Max Health !!!

    """
    __hidden: bool = True
    __options: list[UpgradeCard]

    __jump_card: JumpCard
    __attack_speed_card: AttackSpeedCard
    __boost_duration_card: BoostDurationCard
    __max_health_card: MaxHealthCard

    def __init__(self,
                 view_port: pg.Surface,
                 jump_callback: Callable,
                 attack_speed_callback: Callable,
                 boost_duration_callback: Callable,
                 max_health_callback: Callable):
        self.__options = [self.__jump_card, self.__attack_speed_card, self.__boost_duration_card, self.__max_health_card]

    def click(self, x: int, y: int):
        self.__jump_card.click_if(x, y)
        self.__attack_speed_card.click_if(x, y)
        self.__boost_duration_card.click_if(x, y)
        self.__max_health_card.click_if(x, y)


    def draw(self):
        pass

    def update(self):
        pass

    def hide(self):
        self.__hidden = True
        for c in self.__options: c.hide()

    def show(self):
        self.__hidden = False
        for c in self.__options: c.show()

    def __sample_options(self) -> list[UpgradeCard]:
        return sample(self.__options, 2)
