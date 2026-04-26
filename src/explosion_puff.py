import pygame as pg
import random
import math


class FirePuff(pg.sprite.Sprite):
    def __init__(self, pos, vel, start_radius, color_sequence, life_time=0.5):
        super().__init__()
        self._layer = 5
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(vel)
        self.radius = start_radius
        self.initial_radius = start_radius
        self.life_time = life_time
        self.timer = 0
        self.color_sequence = color_sequence  # List of (r, g, b)

        self.image = pg.Surface(
            (int(self.radius * 2), int(self.radius * 2)), pg.SRCALPHA
        )
        self.rect = self.image.get_rect(center=self.pos)
        self.update_image()

    def update_image(self):
        progress = max(0.0, min(1.0, self.timer / self.life_time))
        color_idx = int(progress * (len(self.color_sequence) - 1))
        next_idx = min(color_idx + 1, len(self.color_sequence) - 1)
        lerp_factor = (progress * (len(self.color_sequence) - 1)) % 1

        c1 = self.color_sequence[color_idx]
        c2 = self.color_sequence[next_idx]

        current_color = (
            int(c1[0] + (c2[0] - c1[0]) * lerp_factor),
            int(c1[1] + (c2[1] - c1[1]) * lerp_factor),
            int(c1[2] + (c2[2] - c1[2]) * lerp_factor),
        )

        current_radius = self.radius * (1 - progress * 0.5)

        size = int(current_radius * 2)
        if size < 1:
            self.kill()
            return

        self.image = pg.Surface((size, size), pg.SRCALPHA)
        alpha = int(255 * (1 - progress))
        pg.draw.circle(
            self.image,
            (*current_color, alpha),
            (size // 2, size // 2),
            int(current_radius),
        )
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float):
        self.timer += dt
        if self.timer >= self.life_time:
            self.kill()
            return

        self.pos += self.vel * dt
        self.vel *= 0.95  # Friction
        self.update_image()
