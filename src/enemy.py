import pygame as pg
from pygame.math import Vector2

import random

from helper import *
from car import Car

ENEMY_SPEED = 70
FRAMES = []
for i in range(1, 10):
    FRAMES.append(load_image(f"enemy/placeholder/{i}.png"))


class Enemy(pg.sprite.Sprite):
    image: pg.Surface
    rect: pg.Rect

    frames: list[pg.Surface]
    time: float
    frame_num: int
    car: Car
    pos: Vector2
    enemies: pg.sprite.Group[Enemy]
    radius: int

    def __init__(self, pos: Vector2, car: Car, enemies: pg.sprite.Group[Enemy]):
        super().__init__()
        self._layer = 2
        self.frames = [
            pg.transform.scale2x(
                frame.convert_alpha(),
            )
            for frame in FRAMES
        ]
        self.frame_num = 0
        self.image = self.frames[self.frame_num]

        self.pos = Vector2(pos)
        self.rect = self.image.get_rect(topleft=self.pos)

        self.time = random.random() * 5
        self.car = car
        self.enemies = enemies
        self.radius = 16

    def update(self, dt: float):
        self.time += dt
        self.frame_num = round((self.time * 7)) % 5
        self.image = self.frames[self.frame_num]

        target = Vector2(self.car.rect.center)
        current = Vector2(self.rect.center)

        if current != target:
            direction = (target - current).normalize()
            velocity = direction * ENEMY_SPEED

            nearby_enemies = pg.sprite.spritecollide(
                self, self.enemies, False, pg.sprite.collide_circle
            )

            separation_vec = Vector2(0, 0)
            for other in nearby_enemies:
                if other is not self:
                    diff = self.pos - other.pos
                    if diff.length() > 0:
                        separation_vec += diff.normalize() * (40 / diff.length())

            final_velocity = velocity + (separation_vec * 50)
            self.pos += final_velocity * dt
            self.rect.center = self.pos
