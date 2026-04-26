import pygame as pg
from typing import Callable

from button import Button
from floating_logo_ui import FloatingLogoUI
from helper import *

START_BTN_LOC = (40, 150)
START_BTN_IMAGE_PATH = "buttons/start.png"
START_BTN_HOVER_IMAGE_PATH = "buttons/start_highlighted.png"

SETTINGS_BTN_LOC = (20, 260)
SETTINGS_BTN_IMAGE_PATH = "buttons/settings.png"
SETTINGS_BTN_HOVER_IMAGE_PATH = "buttons/settings_highlighted.png"

EXIT_BTN_LOC = (85, 350)
EXIT_BTN_IMAGE_PATH = "buttons/exit.png"
EXIT_BTN_HOVER_IMAGE_PATH = "buttons/exit_highlighted.png"


class Menu:
    __screen: pg.Surface

    __start_btn: Button
    __settings_btn: Button
    __exit_btn: Button

    __hidden: bool = False
    __logo_ui: FloatingLogoUI

    def __init__(self, screen: pg.Surface, start_onclick: Callable):
        self.__screen = screen

        self.__logo_ui = FloatingLogoUI(self.__screen)

        self.__start_btn = Button(
            START_BTN_LOC[0],
            START_BTN_LOC[1],
            self.__screen,
            start_onclick,
            floating=True,
            floating_offset=0,
            debounce_rate=8,
            image_path=START_BTN_IMAGE_PATH,
            highlight_image_path=START_BTN_HOVER_IMAGE_PATH,
        )

        self.__settings_btn = Button(
            SETTINGS_BTN_LOC[0],
            SETTINGS_BTN_LOC[1],
            self.__screen,
            self.settings_btn_onclick,
            floating=True,
            floating_offset=2,
            debounce_rate=9,
            image_path=SETTINGS_BTN_IMAGE_PATH,
            highlight_image_path=SETTINGS_BTN_HOVER_IMAGE_PATH,
            scale=0.75,
        )

        self.__exit_btn = Button(
            EXIT_BTN_LOC[0],
            EXIT_BTN_LOC[1],
            self.__screen,
            self.exit_btn_onclick,
            floating=True,
            floating_offset=-1,
            debounce_rate=6,
            image_path=EXIT_BTN_IMAGE_PATH,
            highlight_image_path=EXIT_BTN_HOVER_IMAGE_PATH,
            scale=0.75,
        )

        self.mask = load_image("menu_mask.png").convert_alpha()

    def settings_btn_onclick(self):
        pass

    def hover_check(self, x: int, y: int):
        self.__start_btn.hover_if(x, y)
        self.__settings_btn.hover_if(x, y)
        self.__exit_btn.hover_if(x, y)

    def exit_btn_onclick(self):
        exit_game()

    def hide(self):
        self.__hidden = True
        self.__start_btn.hide()
        self.__settings_btn.hide()
        self.__exit_btn.hide()
        self.__logo_ui.hide()

    def show(self):
        self.__hidden = False
        self.__start_btn.show()
        self.__settings_btn.show()
        self.__exit_btn.show()
        self.__logo_ui.show()

    def click(self, x: int, y: int):
        if not self.__hidden:
            self.__start_btn.click_if(x, y)
            self.__settings_btn.click_if(x, y)
            self.__exit_btn.click_if(x, y)

    def update(self, dt: float):
        self.__start_btn.update(dt)
        self.__settings_btn.update(dt)
        self.__exit_btn.update(dt)
        self.__logo_ui.update(dt)

    def draw(self):
        if not self.__hidden:
            self.__screen.blit(self.mask)
        self.__start_btn.draw()
        self.__settings_btn.draw()
        self.__exit_btn.draw()
        self.__logo_ui.draw()
