from turtle import pos

import pygame as pg
from pygame.math import Vector2
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup
from pyscroll.orthographic import BufferedRenderer
from pytmx import load_pygame

from typing import Literal
import random
import math

from helper import *

from car import Car
from enemy import Enemy
from small_zombie import SmallZombie
from mid_zombie import MidZombie
from big_zombie import BigZombie
from bullet import Bullet, HitSpark
from menu import Menu
from gas_can import GasCan

from game_ui import GameUI
from upgrade_ui import UpgradeUI

DOUBLE_CLICK_TIME = 300
HOLD_TIME = 0.15

WAVE_INTERVAL_SECS = 10
WAVE_MIN_SIZE = 10
WAVE_MAX_SIZE = 20

WAVE_PROBS = [1, 1, 1]


def throwaway():
    print("TEST")


class Game:
    map_path = ASSETS_DIR / "tiled" / "Map.tmx"
    map_layer: BufferedRenderer
    group: PyscrollGroup

    screen: pg.Surface
    font: pg.font.Font
    running: bool = True
    fps: float = 0
    state: Literal["MENU", "RUNNING"] = "MENU"

    shake_duration: float = 0
    shake_intensity: float = 0

    time_to_next_wave = WAVE_INTERVAL_SECS

    menu: Menu
    game_ui: GameUI
    car: Car
    enemies: pg.sprite.Group[Enemy]
    bullets: pg.sprite.Group[Bullet]

    volume: float = 0.3

    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen
        self.surface = pg.Surface((WIDTH, HEIGHT))
        self.font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"))

        tmx_data = load_pygame(str(self.map_path))

        self.walls = []
        self.tall_walls = []

        for objgroup in tmx_data.objectgroups:
            if objgroup.name == "Short Hitboxes":
                for obj in objgroup:
                    self.walls.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))

            if objgroup.name == "Tall Hitboxes":
                for obj in objgroup:
                    self.tall_walls.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))

        self.map_layer = pyscroll.BufferedRenderer(
            data=pyscroll.data.TiledMapData(tmx_data),
            size=self.screen.get_size(),
            clamp_camera=True,
        )

        self.map_layer.zoom = 1
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)
        self.fps = 0

        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.car = Car(self.group, self.screen, self.bullets, self)
        self.car.position = Vector2(101 * 16, 68.7 * 16)
        self.group.add(self.car)
        self.group.center(self.car.position + Vector2(-140, -40))

        pg.mixer.music.load("assets/music/1.wav")
        for i in range(2, 9):
            pg.mixer.music.queue(f"assets/music/{i}.wav")

        pg.mixer.music.set_volume(self.volume)
        pg.mixer.music.play()

        self.menu = Menu(screen, self.state_set_running)
        self.game_ui = GameUI(screen)
        self.upgrade_ui = UpgradeUI(screen, throwaway, throwaway, throwaway, throwaway)

        self.spawn_gas()

    def draw(self) -> None:
        if self.state == "RUNNING":
            if Vector2(self.group.view.center).distance_to(self.car.position) > 10:
                target_center = Vector2(self.group.view.center).lerp(
                    self.car.position, 0.1
                )
            else:
                target_center = self.car.position

            if self.shake_duration > 0:
                shake_offset = Vector2(
                    random.uniform(-self.shake_intensity, self.shake_intensity),
                    random.uniform(-self.shake_intensity, self.shake_intensity),
                )
                target_center += shake_offset

            self.group.center(target_center)

        # redrawing here is a gross hack but like don't question it
        self.car.draw()
        self.group.draw(self.screen)

        # text = self.font.render(
        #     f"{self.fps}\nHealth: {self.car.health}\nGas: {self.car.gas}\nBones: {self.car.skulls}\nZPos: {self.car.z_pos}",
        #     True,
        #     (255, 255, 255),
        # )

        # self.screen.blit(text, (0, 0))

        self.menu.draw()
<<<<<<< Updated upstream
        self.game_ui.draw(
                self.car.health, 
                self.car.max_health,
                self.car.gas, 
                self.car.skulls)
=======
        self.game_ui.draw(self.car.health, self.car.max_health, self.car.gas, self.car.skulls)
>>>>>>> Stashed changes
        self.upgrade_ui.draw()

    def handle_input(self, dt: float) -> None:
        for event in pg.event.get():
            pos = pg.mouse.get_pos()

            if self.state == "MENU":
                self.menu.hover_check(pos[0], pos[1])

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
        self.game_ui.hide()
        self.menu.show()

    def spawn_wave(self):
        for _ in range(WAVE_MIN_SIZE, WAVE_MAX_SIZE):
            for i in range(0, 3):
                enemy_class = [SmallZombie, MidZombie, BigZombie][i]

                if random.random() < WAVE_PROBS[i]:
                    match random.randint(1, 4):
                        # up
                        case 1:
                            y = self.car.rect.center[1] + (
                                (self.screen.height / 2) + 50
                            )
                            x = self.car.rect.center[0] + random.randint(-250, 250)
                        # down
                        case 2:
                            y = self.car.rect.center[1] - (
                                (self.screen.height / 2) + 50
                            )
                            x = self.car.rect.center[0] + random.randint(-250, 250)

                        # left
                        case 3:
                            x = self.car.rect.center[0] - ((self.screen.width / 2) + 50)
                            y = self.car.rect.center[1] + random.randint(
                                -self.screen.height, self.screen.height
                            )

                        # right
                        case 4:
                            x = self.car.rect.center[0] + ((self.screen.width / 2) + 50)
                            y = self.car.rect.center[1] + random.randint(
                                -self.screen.height, self.screen.height
                            )

                    enemy = enemy_class(
                        Vector2(x, y),
                        self.car,
                        self.enemies,
                        self.group,
                    )

                self.group.add(enemy)
                self.enemies.add(enemy)
        pass

    def spawn_gas(self):
        pos = self.car.position + Vector2(250, 0)
        GasCan(pos, self.car, self.group)

    def update(self, dt: float) -> None:

        self.car.accelerating = True
        self.group.update(dt)

        if self.shake_duration > 0:
            self.shake_duration -= dt

        if self.car.collision_speed > 0:
            self.shake_duration = 0.2
            self.shake_intensity = self.car.collision_speed / 100.0
            self.car.collision_speed = 0

        if self.state == "MENU":
            self.menu.update(dt)

        if self.state == "RUNNING":
            new_vol = pg.math.lerp(self.volume, 0.1, 0.01)
            if new_vol != self.volume:
                self.volume = new_vol
                pg.mixer.music.set_volume(self.volume)

            self.time_to_next_wave -= dt

            if self.time_to_next_wave < 0:
                self.spawn_wave()
                self.time_to_next_wave = WAVE_INTERVAL_SECS

            # if self.car

            car_collision_detected = None
            car_collision_point = None

            for wall_list, wall_list_type in [
                (self.walls, "short"),
                (self.tall_walls, "tall"),
            ]:
                for wall in wall_list:
                    for bullet in self.bullets.sprites():
                        if bullet.rect.colliderect(wall):
                            bullet.kill()

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
                        overlap = self.car.mask.overlap(wall_mask, offset)
                        if overlap:
                            car_collision_detected = wall_list_type
                            car_collision_point = overlap
                            break
                if car_collision_detected:
                    break

            self.car.colliding = car_collision_detected
            if car_collision_detected:
                self.car.handle_collision(
                    dt, car_collision_detected, car_collision_point
                )

            # if (
            #     self.car.did_just_land()
            #     or self.car.post_drift_time != 0
            #     or self.car.invuln_time != 0
            # ):
            # self.shake_duration = 0
            # self.shake_intensity = 1

            landing_mask = self.car.get_landing_mask()
            landing_aoe_mask = self.car.get_landing_mask_aoe()

            landing_shift = 150  # (600 - 300) / 2
            landing_aoe_shift = 600  # (1500 - 300) / 2

            for enemy in self.enemies:
                landing_offset = (
                    enemy.rect.x - (self.car.rect.x - landing_shift),
                    enemy.rect.y - (self.car.rect.y - landing_shift),
                )

                landing_aoe_offset = (
                    enemy.rect.x - (self.car.rect.x - landing_aoe_shift),
                    enemy.rect.y - (self.car.rect.y - landing_aoe_shift),
                )

                if landing_mask.overlap(enemy.mask, landing_offset):
                    if (
                        self.car.did_just_land()
                        or self.car.post_drift_time != 0
                        or self.car.invuln_time != 0
                    ):
                        enemy.kill()
                if landing_aoe_mask.overlap(enemy.mask, landing_aoe_offset):
                    if (
                        self.car.did_just_land()
                        or self.car.post_drift_time != 0
                        or self.car.invuln_time != 0
                    ):
                        enemy.push_back(self.car.rect.center)

                # Damage collision
                if self.car.z_pos == 0 and self.car.invuln_time <= 0:
                    offset = (
                        enemy.rect.x - self.car.rect.x,
                        enemy.rect.y - self.car.rect.y,
                    )
                    if self.car.mask.overlap(enemy.mask, offset):
                        if not (
                            self.car.did_just_land() or self.car.post_drift_time != 0
                        ):
                            self.car.take_damage()

            # shooting bullet
            if (
                self.car.time_since_last_shot > self.car.shot_delay
                and len(self.enemies.sprites()) != 0
            ):
                self.car.time_since_last_shot = 0

                closest = min(
                    self.enemies,
                    key=lambda e: Vector2(self.car.rect.center).distance_to(
                        e.rect.center
                    ),
                )
                self.car.add_bullet(Vector2(closest.rect.center))

            # bullet/enemy collision
            collisions = pg.sprite.groupcollide(self.bullets, self.enemies, True, True)
            if collisions:
                for hit_enemies in collisions.values():
                    for enemy in hit_enemies:
                        for _ in range(20, 30):
                            spark_pos = Vector2(enemy.rect.center) + Vector2(
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
                        enemy.kill()

        # self.menu.update(dt)
        # maybe remove?
        if self.car.health == 0:
            self.car.turning = "left"
        self.game_ui.update(dt, self.car.health, self.car.gas, self.car.skulls)
        self.upgrade_ui.update(dt)

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
