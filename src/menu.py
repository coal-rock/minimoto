import pygame as pg

from button import Button
from helper import *

class Menu:
    __screen: pg.Surface

    __start_btn: Button
    __settings_btn: Button
    __exit_btn: Button

    def __init__(self, screen: pg.Surface):
        self.__screen = screen

    def init_start_btn(self) -> Button:
        pass

    def init_settings_btn(self) -> Button:
        pass

    def init_exit_btn(self) -> Button:
        pass

    def exit_btn_onclick(self):
        exit_game()
