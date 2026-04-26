from helper import *
from floor_item import Item


class GasCan(Item):
    image = load_image("gas_can/floor.png")

    item_lerp_speed = 0
    min_speed = 0

    def __init__(self, *args):
        self.sound = load_sound("sound/gas.mp3", 1)
        super().__init__(*args)

    def collect(self):
        self.car.gas = 100
        self.sound.play()
