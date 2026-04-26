from helper import *
from pygame.math import Vector2
from floor_item import Item


class Heart(Item):
    image = load_image("heart/floor.png")
    glow_color = (255, 50, 50)
    item_lerp_speed = 0.05

    def __init__(self, *args):
        self.sound = load_sound("sound/heart_pickup.mp3", 1)
        super().__init__(*args)

    def collect(self):
        self.car.health = min(self.car.health + 1, self.car.max_health)
        self.sound.play()
        self.car.game.spawn_floating_text(
            Vector2(self.rect.center), "+1 HEALTH", (255, 50, 50)
        )
