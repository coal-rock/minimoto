import pygame as pg

class BonesUI:
    __hidden: bool = True

    def __init__(self, veiw_port: pg.Surface, surface: pg.Surface):
        pass

    def draw(self, amt: int):
        pass

    def update(self, dt: float, bones_amd: int):
        pass
    
    def hide(self):
        self.__hidden = True

    def show(self):
        self.__hidden = False
