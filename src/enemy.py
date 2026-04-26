from heart_item import Heart
from skull import Skull
from pyscroll.group import PyscrollGroup
from typing import Literal
import pygame as pg
from pygame.math import Vector2

import random
import math

from helper import *
from car import Car
from bullet import HitSpark


class Enemy(pg.sprite.Sprite):
    heart_drop_rate = 0.02
    skull_drop_rate = 0.1
    image: pg.Surface
    rect: pg.Rect
    mask: pg.Mask
    group: PyscrollGroup

    frames: list[pg.Surface]
    time: float
    frame_num: int
    car: Car
    pos: Vector2
    velocity: Vector2
    enemies: pg.sprite.Group[Enemy]
    radius: int
    col_car_pos: tuple[int, int] | None
    frame_offset = 0
    raw_frames = []

    knockback_strength: float
    speed: float
    animation_speed: float
    health: int = 1
    hit_flash_time: float = 0

    def __init__(
        self,
        pos: Vector2,
        car: Car,
        enemies: pg.sprite.Group[Enemy],
        group: PyscrollGroup,
    ):
        super().__init__()
        # self.death_sound = load_sound("sound/zombie.mp3", 1)
        self._layer = 3
        self.frames = []
        self.group = group
        for frame in self.raw_frames:
            f = frame.convert_alpha()
            w, h = f.get_size()
            # add space for shadow twin
            surf = pg.Surface((w + 8, h + 4), pg.SRCALPHA)
            # shadow
            shadow_color = (0, 0, 0, 80)
            shadow_rect = pg.Rect(0, 0, w * 0.7, 6)
            shadow_rect.centerx = (w + 8) // 2
            shadow_rect.bottom = h + 3
            pg.draw.ellipse(surf, shadow_color, shadow_rect)
            # she bl on my i until i t
            surf.blit(f, (4, 0))
            self.frames.append(surf)

        self.frame_num = 0
        self.image = self.frames[self.frame_num]

        self.pos = Vector2(pos)
        self.velocity = Vector2(0, 0)
        self.old_pos = self.pos.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

        self.time = random.random() * 5
        self.car = car
        self.enemies = enemies
        self.radius = 16
        self.col_side: Literal["top", "left", "right", "bottom", None] = None
        self.col_car_pos = None
        self.mask = pg.mask.from_surface(self.image)

    def handle_collision(
        self, col_side: Literal["top", "left", "right", "bottom"], dt: float
    ) -> None:
        self.pos = self.old_pos.copy()
        self.rect.center = self.pos
        self.col_side = col_side

        if col_side == "left" or col_side == "right":
            self.velocity.x = 0
        if col_side == "top" or col_side == "bottom":
            self.velocity.y = 0

    def push_back(self, car_pos: tuple[int, int]):
        self.col_car_pos = car_pos

    def take_damage(self, amount: int = 1):
        self.health -= amount
        self.hit_flash_time = 0.08

        hit_sound = load_sound("sound/hit.wav", 0.5)
        hit_sound.play()

        for _ in range(10, 20):
            spark_pos = Vector2(self.rect.center) + Vector2(
                random.uniform(-5, 5), random.uniform(-5, 5)
            )
            self.group.add(
                HitSpark(
                    spark_pos,
                    math.radians(random.randint(0, 360)),
                    random.randint(1, 5),
                    (200, 20, 20),
                    scale=0.1,
                    speed_dec=0.8,
                )
            )

        if self.health <= 0:
            self.kill()

    def kill(self):
        if random.random() < self.skull_drop_rate:
            Skull(self.pos, self.car, self.group)
        elif random.random() < self.heart_drop_rate:
            Heart(self.pos, self.car, self.group)

        # self.death_sound.play()

        super().kill()

    def update(self, dt: float):
        # TODO maybe don't normalize before dealing with collision
        self.time += dt
        self.frame_num = round((self.time * 7)) % 2
        self.image = self.frames[self.frame_num + self.frame_offset]

        if self.hit_flash_time > 0:
            self.hit_flash_time -= dt
            self.image = get_white_surface(self.image)

        self.mask = pg.mask.from_surface(self.image)

        target = Vector2(self.car.rect.center)
        current = Vector2(self.rect.center)

        if current != target:
            direction = (target - current).normalize()
            target_velocity = direction * self.speed

            nearby_enemies = pg.sprite.spritecollide(
                self, self.enemies, False, pg.sprite.collide_circle
            )

            separation_vec = Vector2(0, 0)
            for other in nearby_enemies:
                if other is not self:
                    diff = self.pos - other.pos
                    if diff.length() > 0:
                        separation_vec += diff.normalize() * (40 / diff.length())

            if self.col_car_pos is not None:
                car_pos_vec = Vector2(self.col_car_pos)
                diff = self.pos - car_pos_vec

                if diff.length() > 0:
                    self.velocity = (
                        diff.normalize()
                        * self.knockback_strength
                        * self.car.knockback_strength
                    )

                self.col_car_pos = None

            desired_move = target_velocity + (separation_vec * 50)
            self.velocity = self.velocity.lerp(desired_move, 10.0 * dt)

            match self.col_side:
                case "left":
                    self.velocity.x = max(1, self.velocity.x)

                case "right":
                    self.velocity.x = min(-1, self.velocity.x)

                case "top":
                    self.velocity.y = max(1, self.velocity.y)

                case "bottom":
                    self.velocity.y = min(-1, self.velocity.y)

            if self.velocity.y > 0:
                self.frame_offset = 0
            else:
                self.frame_offset = 2

            self.old_pos = self.pos.copy()
            self.pos += self.velocity * dt
            self.rect.center = self.pos

        self.col_side = None
