import pygame as pg

from button import Button
from helper import *

START_BTN_LOC = (50, 150)

SETTINGS_BTN_LOC = (75, 250)

EXIT_BTN_LOC = (75, 350)

class Menu:
    __screen: pg.Surface

    __start_btn: Button
    __settings_btn: Button
    __exit_btn: Button

    def __init__(self, screen: pg.Surface):
        self.__screen = screen

        self.__start_btn = Button(
                START_BTN_LOC[0], 
                START_BTN_LOC[1], 
                self.__screen, 
                self.test,
                rect_mode=True,
                rect_h=50,
                rect_w=150)

        self.__settings_btn = Button(
                SETTINGS_BTN_LOC[0], 
                SETTINGS_BTN_LOC[1], 
                self.__screen, 
                self.test,
                rect_mode=True,
                rect_h=50,
                rect_w=100)

        self.__exit_btn = Button(
                EXIT_BTN_LOC[0], 
                EXIT_BTN_LOC[1], 
                self.__screen, 
                self.exit_btn_onclick,
                rect_mode=True,
                rect_h=50,
                rect_w=100)

    def test(self):
        print("TEST")

    def exit_btn_onclick(self):
        exit_game()

    def click(self, x: int, y: int):
        self.__start_btn.click_if(x, y)
        self.__settings_btn.click_if(x, y)
        self.__exit_btn.click_if(x, y)

    def update(self, dt: float):
        pass

    def draw(self):
        self.__start_btn.draw()
        self.__settings_btn.draw()
        self.__exit_btn.draw()
