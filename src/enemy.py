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

    _asset_cache = {}

    frames: list[pg.Surface]
    white_frames: list[pg.Surface]
    masks: list[pg.Mask]

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

    # Spatial partitioning grid
    grid = {}
    grid_cell_size = 64

    @classmethod
    def update_grid(cls, enemies):
        cls.grid.clear()
        for enemy in enemies:
            cell = (
                int(enemy.pos.x // cls.grid_cell_size),
                int(enemy.pos.y // cls.grid_cell_size),
            )
            if cell not in cls.grid:
                cls.grid[cell] = []
            cls.grid[cell].append(enemy)

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
        self.group = group

        cache_key = id(self.raw_frames)
        if cache_key not in self._asset_cache:
            processed_frames = []
            white_frames = []
            masks = []
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
                processed_frames.append(surf)
                white_frames.append(get_white_surface(surf))
                masks.append(pg.mask.from_surface(surf))
            self._asset_cache[cache_key] = (processed_frames, white_frames, masks)

        self.frames, self.white_frames, self.masks = self._asset_cache[cache_key]

        self.frame_num = 0
        self.image = self.frames[self.frame_num]
        self.mask = self.masks[self.frame_num]

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

        if Vector2(self.rect.center).distance_to(self.car.position) < 400:
            for _ in range(5, 10):
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
        self.time += dt
        self.frame_num = round((self.time * 7)) % 2
        idx = self.frame_num + self.frame_offset

        if self.hit_flash_time > 0:
            self.hit_flash_time -= dt
            self.image = self.white_frames[idx]
        else:
            self.image = self.frames[idx]

        self.mask = self.masks[idx]

        target_pos = self.car.position

        diff_to_target = target_pos - self.pos
        dist_sq = diff_to_target.length_squared()

        if dist_sq > 1:
            direction = diff_to_target / math.sqrt(dist_sq)
            target_velocity = direction * self.speed

            separation_vec = Vector2(0, 0)
            if dist_sq < 250000:  # 500^2
                cell_x = int(self.pos.x // self.grid_cell_size)
                cell_y = int(self.pos.y // self.grid_cell_size)

                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        cell = (cell_x + dx, cell_y + dy)
                        if cell in self.grid:
                            for other in self.grid[cell]:
                                if other is not self:
                                    diff = self.pos - other.pos
                                    d_sq = diff.length_squared()
                                    if 0 < d_sq < 1024:  # 32^2
                                        d = math.sqrt(d_sq)
                                        separation_vec += diff / d * (40 / d)

            if self.col_car_pos is not None:
                car_pos_vec = Vector2(self.col_car_pos)
                diff = self.pos - car_pos_vec
                d_sq = diff.length_squared()

                if d_sq > 0:
                    self.velocity = (
                        diff
                        / math.sqrt(d_sq)
                        * self.knockback_strength
                        * self.car.knockback_strength
                    )

                self.col_car_pos = None

            desired_move = target_velocity + (separation_vec * 50)
            self.velocity = self.velocity.lerp(desired_move, max(0, min(10.0 * dt, 1)))

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

            self.old_pos.x = self.pos.x
            self.old_pos.y = self.pos.y
            self.pos += self.velocity * dt
            self.rect.center = self.pos

        self.col_side = None
