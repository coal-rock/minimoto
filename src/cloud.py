import pygame as pg

import random


PUFF_COLOR = (255, 255, 255)


class Cloud(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pg.Vector2(pos) + pg.Vector2(
            random.uniform(-5, 5), random.uniform(-5, 5)
        )
        self.vel = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.radius = random.uniform(1, 5)
        self.shrink_rate = random.uniform(10, 20)
        self.alpha = 255
        self.fade_rate = random.uniform(2, 10)
        self._layer = 2
        self.image = pg.Surface((0, 0), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update_image()

    def update_image(self):
        size = int(self.radius * 2)
        if size > 0:
            self.image = pg.Surface((size, size), pg.SRCALPHA)
            pg.draw.circle(
                self.image,
                (*PUFF_COLOR, max(0, int(self.alpha))),
                (size // 2, size // 2),
                int(self.radius),
            )
            self.rect = self.image.get_rect(center=self.pos)
        else:
            self.kill()

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.radius -= self.shrink_rate * dt
        self.alpha -= self.fade_rate * dt

        if self.radius <= 0 or self.alpha <= 0:
            self.kill()
        else:
            self.update_image()
