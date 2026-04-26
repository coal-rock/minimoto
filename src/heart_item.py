from helper import *
from floor_item import Item


class Heart(Item):
    image = load_image("heart/floor.png")

    item_lerp_speed = 0.05
    # item_lerp_speed = 0
    # min_speed = 0

    def collect(self):
        self.car.health = min(self.car.health + 30, 100)
