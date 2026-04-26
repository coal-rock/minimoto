from helper import *
from floor_item import Item


class Heart(Item):
    image = load_image("heart/floor.png")

    item_lerp_speed = 0.05

    def __init__(self, *args):
        self.sound = load_sound("sound/heart_pickup.mp3", 1)
        super().__init__(*args)

    def collect(self):
        self.car.health = min(self.car.health + 1, self.car.max_health)
        self.sound.play()
