import pygame as pg
from pygame.math import Vector2
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup
from pyscroll.orthographic import BufferedRenderer
from pytmx import load_pygame

from typing import Literal
import random

from helper import *

from car import Car
from enemy import Enemy
from menu import Menu

from game_ui import GameUI

DOUBLE_CLICK_TIME = 300
HOLD_TIME = 0.15

WAVE_INTERVAL_SECS = 10
WAVE_MIN_SIZE = 10
WAVE_MAX_SIZE = 20


class Game:
    map_path = ASSETS_DIR / "tiled" / "Map.tmx"
    map_layer: BufferedRenderer
    group: PyscrollGroup

    screen: pg.Surface
    font: pg.font.Font
    running: bool = True
    fps: float = 0
    state: Literal["MENU", "RUNNING"] = "MENU"

    time_to_next_wave = WAVE_INTERVAL_SECS
    

    menu: Menu
    game_ui: GameUI
    car: Car
    enemies: pg.sprite.Group[Enemy]

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
        self.fps = 0

        self.car = Car(self.group, self.screen)
        self.enemies = pg.sprite.Group()
        self.car.position = Vector2(415, 265)
        self.group.add(self.car)

        pg.mixer.music.load("assets/music/1.wav")
        for i in range(2, 9):
            pg.mixer.music.queue(f"assets/music/{i}.wav")

        pg.mixer.music.play()

        self.menu = Menu(screen, self.state_set_running)
        self.game_ui = GameUI(screen)

    def draw(self) -> None:
        if self.state == "RUNNING":
            self.group.center(self.car.position)

        # redrawing here is a gross hack but like don't question it
        self.car.draw()
        self.group.draw(self.screen)

        text = self.font.render(
            f"Hello, world!",
            True,
            (255, 255, 255),
        )

        self.screen.blit(text, (0, 0))
        self.menu.draw()

    def handle_input(self, dt: float) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                break

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                    break

                if event.key == pg.K_r:
                    # TODO: remove in prod lel
                    self.map_layer.reload()
                    break

            elif event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()

                if self.state == "MENU":
                    self.menu.click(pos[0], pos[1])

        # IF STATE IS MENU (MAIN MENU)
        # DO NO ALLOW USER INPUT
        if self.state == "MENU":
            self.car.accelerating = True
            self.car.turning = "drift_in"
            return

        pressed = pg.key.get_pressed()
        just_pressed = pg.key.get_just_pressed()
        just_released = pg.key.get_just_released()
        current_time = pg.time.get_ticks()

        if just_released[pg.K_SPACE]:
            if self.car.turning == "drift_in":
                # click
                if self.space_held_time < HOLD_TIME:
                    self.car.end_drift()
                # hold
                else:
                    self.car.start_drift_out()

            elif self.car.turning is None:
                if self.space_held_time < HOLD_TIME:
                    if self.car.z_pos == 0:
                        self.car.jump()

        if just_pressed[pg.K_SPACE]:
            if self.car.turning == "drift_out":
                self.car.start_drift_in()

        # has space been pressed
        if pressed[pg.K_SPACE]:
            if self.car.turning is None:
                if self.car.z_pos == 0:
                    if self.space_held_time > HOLD_TIME:
                        self.car.start_left_turn()
                else:
                    self.car.start_drift()

        if just_released[pg.K_SPACE] and self.car.turning == "left":
            self.car.end_left_turn()

        self.car.accelerating = True

        if pressed[pg.K_SPACE]:
            self.space_held_time += dt
        else:
            self.space_held_time = 0

    def state_set_running(self):
        self.state = "RUNNING"
        print("GAME STATE: RUNNING")
        self.menu.hide()
        self.game_ui.show()

    def state_set_menu(self):
        self.state = "MENU"
        print("GAME STATE: MENU")

    def spawn_wave(self):
        for _ in range(WAVE_MIN_SIZE, WAVE_MAX_SIZE):
            enemy = Enemy(
                Vector2(
                    self.car.rect.topleft[0] + random.randint(-200, 200),
                    self.car.rect.topleft[1] + random.randint(-200, 200),
                ),
                self.car,
                self.enemies,
            )
            self.group.add(enemy)
            self.enemies.add(enemy)
        pass

    def update(self, dt: float) -> None:
        self.car.accelerating = True
        self.group.update(dt)

        if self.state == "RUNNING":
            self.time_to_next_wave -= dt

            if self.time_to_next_wave < 0:
                self.spawn_wave()
                self.time_to_next_wave = WAVE_INTERVAL_SECS

            car_collision_detected = False

            for wall in self.walls:
                for enemy in self.enemies:
                    if enemy.rect.colliderect(wall):
                        enemy_dr = enemy.rect.right - wall.left
                        enemy_dl = wall.right - enemy.rect.left
                        enemy_db = enemy.rect.bottom - wall.top
                        enemy_dt = wall.bottom - enemy.rect.top

                        min_overlap = min(enemy_dr, enemy_dl, enemy_db, enemy_dt)

                        if min_overlap == enemy_dr:
                            enemy.handle_collision("right", dt)
                        elif min_overlap == enemy_dl:
                            enemy.handle_collision("left", dt)
                        elif min_overlap == enemy_db:
                            enemy.handle_collision("bottom", dt)
                        elif min_overlap == enemy_dt:
                            enemy.handle_collision("top", dt)

                if self.car.rect.colliderect(wall):
                    wall_mask = pg.mask.Mask(wall.size)
                    wall_mask.fill()

                    offset = (wall.x - self.car.rect.x, wall.y - self.car.rect.y)
                    if self.car.mask.overlap(wall_mask, offset):
                        car_collision_detected = True
                        break

            self.car.colliding = car_collision_detected
            if car_collision_detected:
                self.car.handle_collision(dt)

        # self.menu.update(dt)

    def run(self):
        clock = pg.time.Clock()
        self.running = True

        try:
            while self.running:
                dt = clock.tick(60) / 1000.0
                self.fps = clock.get_fps()
                self.handle_input(dt)
                self.update(dt)
                self.draw()
                pg.display.flip()
        except KeyboardInterrupt:
            self.running = False
