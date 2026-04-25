from typing import Literal
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
    mask: pg.Mask

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
        self.old_pos = self.pos.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

        self.time = random.random() * 5
        self.car = car
        self.enemies = enemies
        self.radius = 16
        self.col_side: Literal["top", "left", "right", "bottom", None] = None
        self.mask = pg.mask.from_surface(self.image)

    def handle_collision(
        self, col_side: Literal["top", "left", "right", "bottom"], dt: float
    ) -> None:
        self.position = self.old_pos.copy()
        self.rect.center = self.position
        self.col_side = col_side

    def update(self, dt: float):
        # TODO maybe don't normalize before dealing with collision
        self.time += dt
        self.frame_num = round((self.time * 7)) % 5
        self.image = self.frames[self.frame_num]
        self.mask = pg.mask.from_surface(self.image)

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

            match self.col_side:
                case "left":
                    final_velocity = Vector2(
                        max(1, final_velocity.x),
                        final_velocity.y,
                    )

                case "right":
                    final_velocity = Vector2(
                        min(-1, final_velocity.x),
                        final_velocity.y,
                    )

                case "top":
                    final_velocity = Vector2(
                        final_velocity.x,
                        max(1, final_velocity.y),
                    )

                case "bottom":
                    final_velocity = Vector2(
                        final_velocity.x,
                        min(-1, final_velocity.y),
                    )

            self.old_pos = self.pos.copy()
            self.pos += final_velocity * dt
            self.rect.center = self.pos

        self.col_side = None
