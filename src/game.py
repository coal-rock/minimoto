import pygame as pg
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup
from pyscroll.orthographic import BufferedRenderer
from pytmx import load_pygame

import random

from helper import *


class Game:
    map_path = ASSETS_DIR / "tiled" / "Map.tmx"
    map_layer: BufferedRenderer
    group: PyscrollGroup

    screen: pg.Surface
    font: pg.font.Font
    running: bool = True
    fps: float = 0

    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen
        self.surface = pg.Surface((WIDTH, HEIGHT))
        self.font = pg.font.Font()

        tmx_data = load_pygame(str(self.map_path))

        self.walls = []
        for obj in tmx_data.objects:
            self.walls.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))

        self.map_layer = pyscroll.BufferedRenderer(
            data=pyscroll.data.TiledMapData(tmx_data),
            size=self.screen.get_size(),
            clamp_camera=True,
        )

        self.map_layer.zoom = 1
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)

    def draw(self) -> None:
        self.group.draw(self.screen)

        text = self.font.render(
            f"Hello, world!",
            True,
            (255, 255, 255),
        )

        self.screen.blit(text, (0, 0))

    def handle_input(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                break

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                    break

    def update(self, dt: float) -> None:
        self.group.update(dt)

    def run(self):
        clock = pg.time.Clock()
        self.running = True

        try:
            while self.running:
                dt = clock.tick(60) / 1000.0
                self.fps = clock.get_fps()
                self.handle_input()
                self.update(dt)
                self.draw()
                pg.display.flip()
        except KeyboardInterrupt:
            self.running = False
