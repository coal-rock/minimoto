import pygame as pg
from pygame.math import Vector2
import random

class FloatingText(pg.sprite.Sprite):
    def __init__(self, pos: Vector2, text: str, color: tuple[int, int, int], font_path: str, font_size: int = 16):
        super().__init__()
        self._layer = 10
        self.font = pg.font.Font(font_path, font_size)
        
        # Render text and shadow
        text_surf = self.font.render(text, True, color)
        shadow_surf = self.font.render(text, True, (0, 0, 0))
        
        w, h = text_surf.get_size()
        self.image = pg.Surface((w + 1, h + 1), pg.SRCALPHA)
        self.image.blit(shadow_surf, (1, 1))
        self.image.blit(text_surf, (0, 0))
        
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.vel = Vector2(random.uniform(-20, 20), -50)
        self.life = 1.0
        self.alpha = 255

    def update(self, dt: float):
        self.life -= dt
        if self.life <= 0:
            self.kill()
            return

        self.pos += self.vel * dt
        self.vel.y += 100 * dt  # gravity
        self.rect.center = self.pos
        
        self.alpha = int(255 * (self.life / 1.0))
        self.image.set_alpha(self.alpha)
