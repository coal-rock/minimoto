import pygame as pg
from typing import Callable

from button import Button
from helper import *

START_BTN_LOC = (40, 150)
START_BTN_IMAGE_PATH = "../assets/buttons/start.png"

SETTINGS_BTN_LOC = (20, 260)
SETTINGS_BTN_IMAGE_PATH = "../assets/buttons/settings.png"

EXIT_BTN_LOC = (85, 345)
EXIT_BTN_IMAGE_PATH = "../assets/buttons/exit.png"

class Menu:
    __screen: pg.Surface

    __start_btn: Button
    __settings_btn: Button
    __exit_btn: Button

    __hidden: bool = False

    def __init__(self, 
                 screen: pg.Surface,
                 start_onclick: Callable):
        self.__screen = screen

        self.__start_btn = Button(
                START_BTN_LOC[0], 
                START_BTN_LOC[1], 
                self.__screen, 
                start_onclick,
                image_path=START_BTN_IMAGE_PATH)

        self.__settings_btn = Button(
                SETTINGS_BTN_LOC[0], 
                SETTINGS_BTN_LOC[1], 
                self.__screen, 
                self.settings_btn_onclick,
                image_path=SETTINGS_BTN_IMAGE_PATH,
                scale=0.75)

        self.__exit_btn = Button(
                EXIT_BTN_LOC[0], 
                EXIT_BTN_LOC[1], 
                self.__screen, 
                self.exit_btn_onclick,
                image_path=EXIT_BTN_IMAGE_PATH,
                scale=0.75)

    def settings_btn_onclick(self):
        print("settings button clicked")

    def exit_btn_onclick(self):
        exit_game()

    def hide(self):
        self.__hidden = True
        self.__start_btn.hide()
        self.__settings_btn.hide()
        self.__exit_btn.hide()

    def show(self):
        self.__hidden = False
        self.__start_btn.show()
        self.__settings_btn.show()
        self.__exit_btn.show()
        

    def click(self, x: int, y: int):
        if not self.__hidden:
            self.__start_btn.click_if(x, y)
            self.__settings_btn.click_if(x, y)
            self.__exit_btn.click_if(x, y)

    def update(self, dt: float):
        pass

    def draw(self):
        self.__start_btn.draw()
        self.__settings_btn.draw()
        self.__exit_btn.draw()
