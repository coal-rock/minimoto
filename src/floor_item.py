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


class ItemParticle(pg.sprite.Sprite):
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


class ItemShadow(pg.sprite.Sprite):
    def __init__(self, owner, group: pg.sprite.Group):
        super().__init__(group)
        self._layer = 1
        self.owner = owner
        self.image = pg.Surface((64, 32), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update_image(0)

    def update_image(self, offset_y: float):
        # scale shadow based on height
        scale = 1.0 - (offset_y / 60.0)
        width = int(24 * scale)
        height = int(10 * scale)
        alpha = int(80 * scale)

        if width < 1:
            width = 1
        if height < 1:
            height = 1

        self.image = pg.Surface((width * 2, height * 2), pg.SRCALPHA)

        # Draw soft colored aura
        aura_color = (*self.owner.glow_color, int(40 * scale))
        pg.draw.ellipse(self.image, aura_color, (0, 0, width * 2, height * 2))

        # Draw dark shadow core
        pg.draw.ellipse(
            self.image, (0, 0, 0, alpha), (width // 2, height // 2, width, height)
        )

        self.rect = self.image.get_rect(
            center=(self.owner.pos.x, self.owner.pos.y + 12)
        )

    def update(self, dt: float):
        if not self.owner.alive():
            self.kill()
            return

        offset_y = self.owner.rect.center[1] - self.owner.pos.y
        self.update_image(offset_y)


class Item(pg.sprite.Sprite):
    image: pg.Surface
    _layer = 3
    time: float = 0
    rect: pg.Rect
    car: Car
    item_lerp_speed = 0.05
    min_speed = None
    glow_color = (0, 0, 0)

    def __init__(self, pos: Vector2, car: Car, *groups: pg.sprite.Group):
        super().__init__(*groups)
        self.image = self.image.convert_alpha()
        self.original_image = self.image.convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pos.copy()
        self.original_pos = pos.copy()
        self.car = car
        self.group = groups[0]
        self.shadow = ItemShadow(self, self.group)
        self.particle_timer = 0

    def collect(self):
        pass

    def update(self, dt: float):
        self.time += dt

        bob_offset = math.sin(self.time * 5) * 8
        self.image = self.original_image.copy()

        glow_val = (math.sin(self.time * 4) + 1) * 0.5
        tint = (
            int(self.glow_color[0] * glow_val * 0.2),
            int(self.glow_color[1] * glow_val * 0.2),
            int(self.glow_color[2] * glow_val * 0.2),
        )
        self.image.fill((*tint, 0), special_flags=pg.BLEND_RGB_ADD)

        glint_pos = (self.time * 40) % 200
        if glint_pos < 40:
            glint_surf = pg.Surface(self.image.get_size(), pg.SRCALPHA)
            pg.draw.line(
                glint_surf,
                (255, 255, 255, 100),
                (int(glint_pos - 20), 20),
                (int(glint_pos), 0),
                2,
            )
            self.image.blit(glint_surf, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        self.rect = self.image.get_rect(
            center=Vector2(self.pos.x, self.pos.y + bob_offset)
        )

        self.particle_timer += dt
        if self.particle_timer > 0.6:
            self.particle_timer = 0
            ItemParticle(Vector2(self.pos.x, self.pos.y + bob_offset), self.group)

        car_center = Vector2(self.car.rect.center)
        distance = self.pos.distance_to(car_center)

        if distance < 20:
            self.collect()
            self.kill()
            return

        if self.time < 0.5:
            return

        if distance < self.car.magnet_radius:
            lerp_pos = self.pos.lerp(car_center, self.item_lerp_speed)

            direction = car_center - self.pos
            if direction.length() > 0:
                direction = direction.normalize()

            min_speed = 10 * dt if distance > 60 else 500 * dt
            if self.min_speed is not None:
                min_speed = self.min_speed

            move_vec = lerp_pos - self.pos
            if move_vec.length() < min_speed:
                self.pos += direction * min_speed
            else:
                self.pos = lerp_pos
