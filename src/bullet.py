import pygame as pg
from pygame.math import Vector2
import random

BULLET_COLOR = (255, 212, 110)
BULLET_SPEED = 500


class BulletTrail(pg.sprite.Sprite):
    def __init__(self, pos: Vector2, color: tuple[int, int, int]):
        super().__init__()
        self._layer = 1
        self.pos = pos.copy()
        self.color = color
        self.radius = random.uniform(1.5, 3.0)
        self.lifetime = 0.4
        self.initial_lifetime = self.lifetime
        self.update_image()

    def update_image(self):
        size = int(self.radius * 2) + 2
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        alpha = int((self.lifetime / self.initial_lifetime) * 200)
        pg.draw.circle(
            self.image, (*self.color, alpha), (size // 2, size // 2), self.radius
        )
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        else:
            self.radius *= 0.95
            self.update_image()


class Bullet(pg.sprite.Sprite):
    image: pg.surface.Surface
    rect: pg.rect.Rect

    def __init__(self, pos: Vector2, target: Vector2, group: pg.sprite.Group):
        super().__init__()
        self._layer = 2
        self.pos = pos.copy()
        self.group = group

        diff = target - pos
        if diff.length() == 0:
            self.direction = Vector2(0, -1)
        else:
            self.direction = diff.normalize()

        self.radius = 2

        width = self.radius * 8
        height = self.radius * 2
        base_image = pg.Surface((width, height), pg.SRCALPHA)

        pg.draw.ellipse(
            base_image,
            BULLET_COLOR,
            (0, 0, width, height),
        )

        pg.draw.circle(
            base_image,
            (255, 255, 255),
            (width - self.radius, height // 2),
            self.radius,
        )

        angle = self.direction.angle_to(Vector2(1, 0))
        self.image = pg.transform.rotate(base_image, angle)

        self.rect = self.image.get_rect(center=self.pos)
        self.lifetime = 1.5  # seconds

    def update(self, dt: float):
        self.pos += self.direction * BULLET_SPEED * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Spawn trail particles
        if random.random() < 0.8:
            trail_pos = self.pos - self.direction * 5
            self.group.add(BulletTrail(trail_pos, BULLET_COLOR))

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
