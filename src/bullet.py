import pygame as pg
from pygame.math import Vector2

BULLET_COLOR = (255, 212, 110)
BULLET_SPEED = 100


class Bullet(pg.sprite.Sprite):
    image: pg.surface.Surface
    rect: pg.rect.Rect

    def __init__(self, pos: Vector2, target: Vector2):
        super().__init__()
        self._layer = 2
        self.pos = pos.copy()

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

        angle = -self.direction.angle_to(Vector2(1, 0))
        self.image = pg.transform.rotate(base_image, angle)

        self.rect = self.image.get_rect(center=self.pos)
        self.lifetime = 1.5  # seconds

    def update(self, dt: float):
        self.pos += self.direction * BULLET_SPEED * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
