import pygame as pg
from pygame.math import Vector2
import random
import math

BULLET_COLOR = (255, 212, 110)
BULLET_SPEED = 300


class BulletTrail(pg.sprite.Sprite):
    def __init__(self, pos: Vector2, color: tuple[int, int, int]):
        super().__init__()
        self._layer = 3
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
        self._layer = 3
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

        # trail
        if random.random() < 0.8:
            trail_pos = self.pos - self.direction * 5
            self.group.add(BulletTrail(trail_pos, BULLET_COLOR))

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()


class HitSpark(pg.sprite.Sprite):
    def __init__(
        self,
        pos: Vector2,
        angle: float,
        speed: float,
        color: tuple[int, int, int],
        scale: float = 1.0,
        speed_dec: float = 0.3,
    ):
        super().__init__()
        self._layer = 3
        self.pos = Vector2(pos)
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.speed_dec = speed_dec
        self.image = pg.Surface((1, 1))
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float):
        step = dt * 60
        self.pos += (
            Vector2(math.cos(self.angle), math.sin(self.angle)) * self.speed * step
        )

        # friction/gravity logic from Spark class
        movement = [
            math.cos(self.angle) * self.speed * step,
            math.sin(self.angle) * self.speed * step,
        ]
        movement[1] = min(8, movement[1] + 0.2 * step)
        movement[0] *= 0.975
        self.angle = math.atan2(movement[1], movement[0])

        self.angle += 0.1 * step
        self.speed -= self.speed_dec * step

        if self.speed <= 0:
            self.kill()
            return

        size = max(1, int(self.speed * self.scale * 5))
        self.image = pg.Surface((size * 2, size * 2), pg.SRCALPHA)
        center = size

        points = [
            (
                center + math.cos(self.angle) * self.speed * self.scale,
                center + math.sin(self.angle) * self.speed * self.scale,
            ),
            (
                center
                + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3,
                center
                + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3,
            ),
            (
                center - math.cos(self.angle) * self.speed * self.scale * 3.5,
                center - math.sin(self.angle) * self.speed * self.scale * 3.5,
            ),
            (
                center
                + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3,
                center
                - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3,
            ),
        ]
        pg.draw.polygon(self.image, self.color, points)
        self.rect = self.image.get_rect(center=self.pos)
