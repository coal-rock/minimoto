import pygame as pg
from pygame.math import Vector2
import math
from floor_item import Item
from helper import *

def create_star_surface():
    surf = pg.Surface((32, 32), pg.SRCALPHA)
    points = []
    for i in range(10):
        angle = math.radians(i * 36)
        r = 14 if i % 2 == 0 else 6
        points.append((16 + r * math.sin(angle), 16 - r * math.cos(angle)))
    pg.draw.polygon(surf, (255, 255, 0), points)
    pg.draw.polygon(surf, (255, 200, 0), points, 2)
    return surf

class Star(Item):
    image = create_star_surface()
    glow_color = (255, 255, 100)
    item_lerp_speed = 0.08

    def __init__(self, *args):
        self.sound = load_sound("sound/boost.mp3", 1) # Using boost sound as placeholder for pickup
        super().__init__(*args)

    def collect(self):
        self.car.star_time = 8.0 # 8 seconds of star power
        self.sound.play()
        self.car.game.spawn_floating_text(
            Vector2(self.rect.center), "STAR POWER!", (255, 255, 0)
        )
