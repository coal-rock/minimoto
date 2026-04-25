import pygame as pg
from pygame.math import Vector2

from helper import *

TRAIL_SURFACE = load_image("car/trail.png")


class Trail(pg.sprite.Sprite):
    image: pg.Surface

    def __init__(self, pos: Vector2):
        super().__init__()
        self.image = TRAIL_SURFACE.copy().convert_alpha()
        self.rect = self.image.get_rect(center=(pos.x, pos.y))
        # TODO: maybe tweak these? this was stolen LMAO
        self.lifetime = 1.5
        self.alpha = 200
        self._layer = 1

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        else:
            self.alpha = max(0, self.alpha - (200 / 1.5) * dt)
            self.image.set_alpha(int(self.alpha))
