from helper import *
from pygame import Vector2
from floor_item import Item


class Skull(Item):
    image = load_image("skull/floor.png")
    glow_color = (255, 255, 255)
    item_lerp_speed = 0.05

    def __init__(self, *args):
        self.sound = load_sound("sound/skull.mp3", 1)
        super().__init__(*args)

    def collect(self):
        self.car.skulls += 1
        self.sound.play()
        self.car.game.spawn_floating_text(
            Vector2(self.rect.center), "+1 SKULL", (255, 255, 255)
        )
