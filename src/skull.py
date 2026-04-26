from helper import *
from floor_item import Item


class Skull(Item):
    image = load_image("skull/floor.png")

    item_lerp_speed = 0.05

    def collect(self):
        self.car.skulls += 1
