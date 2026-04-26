from pygame import Vector2
import pygame as pg
import math
import random

from helper import *
from car import Car

_SKULL_SURFACE = None


def get_skull_surface():
    global _SKULL_SURFACE
    if _SKULL_SURFACE is None:
        _SKULL_SURFACE = load_image("skull/floor.png").convert_alpha()
    return _SKULL_SURFACE


SKULL_LERP_SPEED = 0.05


class GhostParticle(pg.sprite.Sprite):
    def __init__(self, pos: Vector2, group: pg.sprite.Group):
        super().__init__(group)
        self._layer = 3
        self.pos = pos.copy()
        self.vel = Vector2(random.uniform(-5, 5), random.uniform(-10, -5))
        self.life = 0.8
        self.max_life = 0.8
        self.size = random.uniform(1, 2)
        self.color = (180, 255, 255)
        self.update_image()

    def update_image(self):
        alpha = int((self.life / self.max_life) * 80)
        s = int(self.size * 2)
        if s < 1:
            s = 1
        self.image = pg.Surface((s, s), pg.SRCALPHA)
        pg.draw.circle(self.image, (*self.color, alpha), (s // 2, s // 2), self.size)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float):
        self.life -= dt
        if self.life <= 0:
            self.kill()
            return
        self.pos += self.vel * dt
        self.vel.x *= 0.95
        self.update_image()


class SkullShadow(pg.sprite.Sprite):
    def __init__(self, owner: "Skull", group: pg.sprite.Group):
        super().__init__(group)
        self._layer = 1
        self.owner = owner
        self.image = pg.Surface((32, 16), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update_image(0)

    def update_image(self, offset_y: float):
        # scale shadow based on height
        scale = 1.0 - (offset_y / 60.0)
        width = int(20 * scale)
        height = int(8 * scale)
        alpha = int(60 * scale)

        if width < 1:
            width = 1
        if height < 1:
            height = 1

        self.image = pg.Surface((width, height), pg.SRCALPHA)
        pg.draw.ellipse(self.image, (0, 0, 0, alpha), (0, 0, width, height))

        self.rect = self.image.get_rect(
            center=(self.owner.original_pos.x, self.owner.original_pos.y + 12)
        )

    def update(self, dt: float):
        if not self.owner.alive():
            self.kill()
            return

        self.rect.center = (self.owner.pos.x, self.owner.pos.y + 12)

        offset_y = self.owner.rect.center[1] - self.owner.pos.y
        self.update_image(offset_y)


class Skull(pg.sprite.Sprite):
    image: pg.Surface
    _layer = 2
    time: float = 0
    rect: pg.Rect
    car: Car

    def __init__(self, pos: Vector2, car: Car, group: pg.sprite.Group):
        super().__init__(group)
        self.image = get_skull_surface().copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pos.copy()
        self.original_pos = pos.copy()
        self.car = car
        self.group = group
        self.shadow = SkullShadow(self, group)
        self.particle_timer = 0

    def update(self, dt: float):
        self.time += dt

        glow_val = (math.sin(self.time * 3) + 1) * 0.5
        tint_surf = get_skull_surface().copy()
        tint = (int(40 * glow_val), int(100 * glow_val), int(100 * glow_val))
        tint_surf.fill((*tint, 50), special_flags=pg.BLEND_RGB_ADD)
        self.image = tint_surf

        self.particle_timer += dt
        if self.particle_timer > 0.4:
            self.particle_timer = 0
            GhostParticle(Vector2(self.rect.center), self.group)

        car_center = Vector2(self.car.rect.center)
        distance = self.pos.distance_to(car_center)

        if distance < 20:
            self.car.skulls += 1
            self.kill()
            return

        if self.time < 0.5:
            bob_offset = math.sin(self.time * 5) * 10
            self.rect.center = Vector2(self.pos.x, self.pos.y + bob_offset)
            return

        if distance < self.car.magnet_radius:
            lerp_pos = self.pos.lerp(car_center, SKULL_LERP_SPEED)

            direction = car_center - self.pos
            if direction.length() > 0:
                direction = direction.normalize()

            min_speed = 10 * dt if distance > 60 else 500 * dt

            move_vec = lerp_pos - self.pos
            if move_vec.length() < min_speed:
                self.pos += direction * min_speed
            else:
                self.pos = lerp_pos

            bob_offset = math.sin(self.time * 5) * 10
            self.rect.center = Vector2(self.pos.x, self.pos.y + bob_offset)
        else:
            bob_offset = math.sin(self.time * 5) * 10
            self.rect.center = Vector2(self.pos.x, self.pos.y + bob_offset)
