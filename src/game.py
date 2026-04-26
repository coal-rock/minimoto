from upgrade_cards import UICard

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
from bullet import Bullet
from menu import Menu
from gas_can import GasCan
from gas_arrow import GasArrow

from user_events import MUSIC_END
from game_ui import GameUI
from floating_text import FloatingText

DOUBLE_CLICK_TIME = 300
HOLD_TIME = 0.15

WAVE_INTERVAL_SECS = 10


class Game:
    map_path = ASSETS_DIR / "tiled" / "Map.tmx"
    map_layer: BufferedRenderer
    group: PyscrollGroup

    screen: pg.Surface
    font: pg.font.Font
    running: bool = True
    fps: float = 0
    state: Literal["MENU", "RUNNING", "UPGRADE", "GAMEOVER"]

    shake_duration: float = 0
    shake_intensity: float = 0
    freeze_time: float = 0

    time_to_next_wave = 3
    death_timer: float = 0
    game_time: float = 0
    wave_count: int = 0

    menu: Menu
    game_ui: GameUI
    car: Car
    bullets_to_shoot: int = 0

    upgrade_left: UICard
    upgrade_right: UICard

    enemies: pg.sprite.Group[Enemy]
    bullets: pg.sprite.Group[Bullet]

    volume: float = 0.3
    skulls_to_upgrade = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90]

    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen
        self.surface = pg.Surface((WIDTH, HEIGHT))
        self.font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"))

        self.game_over_sound = load_sound("sound/game_over.mp3", 1)

        self.upgrade_left = UICard("selected", "left")
        self.upgrade_right = UICard("unselected", "right")

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

        self.map_width = tmx_data.width * tmx_data.tilewidth
        self.map_height = tmx_data.height * tmx_data.tileheight

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
        self.gas_cans = pg.sprite.Group()

        self.car = Car(self.group, self.screen, self.bullets, self)
        self.car.position = Vector2(101.9 * 16, 69.1 * 16)
        self.group.add(self.car)
        self.group.center(self.car.position + Vector2(-140, -40))

        self.gas_arrow = GasArrow(self.car, self.group, self.gas_cans)

        pg.mixer.music.set_endevent(MUSIC_END)
        pg.mixer.music.load("assets/music/1.wav")
        for i in range(2, 9):
            pg.mixer.music.queue(f"assets/music/{i}.wav")

        pg.mixer.music.set_volume(self.volume)
        pg.mixer.music.play()

        self.menu = Menu(screen, self.state_set_running)
        self.game_ui = GameUI(screen)
        self.state = "MENU"

        # # Create vignette
        # self.vignette = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        # for i in range(WIDTH // 2, 0, -1):
        #     alpha = int(160 * (1 - (i / (WIDTH // 2)))**2)
        #     pg.draw.circle(self.vignette, (0, 0, 0, alpha), (WIDTH // 2, HEIGHT // 2), WIDTH // 2 + (WIDTH // 2 - i))

        self.upgrade_types = [
            "jump",
            "fire_rate",
            "health",
            "knockback",
            "projectiles",
            "boost",
            "gas",
        ]

        self.spawn_gas()

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        if self.state == "RUNNING":
            # Camera lead-in
            lead_offset = self.car.velocity_dir * (self.car.speed * 0.2)
            target_pos = self.car.position + lead_offset

            if Vector2(self.group.view.center).distance_to(target_pos) > 5:
                target_center = Vector2(self.group.view.center).lerp(target_pos, 0.1)
            else:
                target_center = target_pos

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

        # if self.state == "RUNNING":
        # self.screen.blit(self.vignette, (0, 0))

        # text = self.font.render(
        #     f"{self.fps}\nHealth: {self.car.health}\nGas: {self.car.gas}\nBones: {self.car.skulls}\nZPos: {self.car.z_pos}",
        #     True,
        #     (255, 255, 255),
        # )

        # self.screen.blit(text, (0, 0))

        if self.state == "MENU":
            self.menu.draw()

        self.game_ui.draw(
            self.car.health, self.car.max_health, self.car.gas, self.car.skulls
        )

        if self.state == "UPGRADE" or self.state == "GAMEOVER":
            overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

        if self.state == "UPGRADE":
            self.upgrade_left.draw(self.screen)
            self.upgrade_right.draw(self.screen)

        if self.state == "GAMEOVER":
            text = self.font.render("GAME OVER", True, (255, 50, 50))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            self.screen.blit(text, text_rect)

            sub_text = self.font.render(
                f"SCORE: {self.car.skulls}", True, (255, 255, 255)
            )
            sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(sub_text, sub_rect)

            sub_text = self.font.render("PRESS R TO RESTART", True, (255, 255, 255))
            sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
            self.screen.blit(sub_text, sub_rect)

    def handle_input(self, dt: float) -> None:
        for event in pg.event.get():
            pos = pg.mouse.get_pos()

            if self.state == "MENU":
                self.menu.hover_check(pos[0], pos[1])

            if event.type == pg.QUIT:
                self.running = False
                break

            elif event.type == MUSIC_END:
                pg.mixer.music.load("assets/music/1.wav")
                for i in range(2, 9):
                    pg.mixer.music.queue(f"assets/music/{i}.wav")
                pg.mixer.music.play()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.state == "GAMEOVER":
                        self.state_set_menu()
                        return
                    else:
                        self.running = False
                        break

                if event.key == pg.K_r:
                    if self.state == "GAMEOVER":
                        self.restart()
                        return
                    else:
                        # TODO: remove in prod lel
                        self.map_layer.reload()
                        break

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.state == "MENU":
                    self.menu.click(pos[0], pos[1])

        if self.state == "GAMEOVER":
            return

        pressed = pg.key.get_pressed()
        just_pressed = pg.key.get_just_pressed()
        just_released = pg.key.get_just_released()
        current_time = pg.time.get_ticks()

        if self.state == "UPGRADE":
            if just_released[pg.K_LEFT] or just_pressed[pg.K_RIGHT]:
                if self.upgrade_left.state == "selected":
                    self.upgrade_left.state = "unselected"
                    self.upgrade_right.state = "selected"

                elif self.upgrade_right.state == "selected":
                    self.upgrade_left.state = "selected"
                    self.upgrade_right.state = "unselected"

            if just_released[pg.K_RETURN]:
                if self.upgrade_left.state == "selected":
                    self.upgrade_left.upgrade(self.car)
                elif self.upgrade_right.state == "selected":
                    self.upgrade_right.upgrade(self.car)

                self.skulls_to_upgrade = self.skulls_to_upgrade[1:-1]
                self.skulls_to_upgrade.append(self.skulls_to_upgrade[0] + 10)
                self.state = "RUNNING"

        # IF STATE IS MENU (MAIN MENU)
        # DO NO ALLOW USER INPUT
        if self.state != "RUNNING":
            self.car.accelerating = True
            self.car.turning = "drift_in"
            return

        if just_released[pg.K_0]:
            self.car.take_damage()

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

    def restart(self):
        pg.mixer.stop()

        self.enemies.empty()
        self.bullets.empty()
        self.gas_cans.empty()
        self.group.empty()

        self.car = Car(self.group, self.screen, self.bullets, self)
        self.car.position = Vector2(101.9 * 16, 69.1 * 16)
        self.group.add(self.car)
        self.group.center(self.car.position + Vector2(-140, -40))

        self.gas_arrow = GasArrow(self.car, self.group, self.gas_cans)

        self.skulls_to_upgrade = [1, 5, 10, 20, 30, 40, 50]
        self.death_timer = 0
        self.game_time = 0
        self.wave_count = 0
        self.time_to_next_wave = WAVE_INTERVAL_SECS
        self.bullets_to_shoot = 0

        self.volume = 0.3
        pg.mixer.music.set_volume(self.volume)

        self.state_set_menu()
        self.spawn_gas()
        print("GAME RESTARTED")

    def spawn_wave(self):
        self.wave_count += 1

        difficulty = min(1.0, self.game_time / 100.0)

        min_size = int(3 + (difficulty * 12))
        max_size = int(6 + (difficulty * 24))

        probs = [
            1.0,  # Small
            min(1.0, difficulty * 1.5),  # Mid
            min(0.5, difficulty * 1.0),  # Big
        ]

        for _ in range(min_size, max_size):
            for i in range(0, 3):
                enemy_class = [SmallZombie, MidZombie, BigZombie][i]

                if random.random() < probs[i]:
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
        # find random valid pos
        valid_pos = False
        pos = Vector2(0, 0)

        # Bounds in pixels based on 16x16 tiles
        min_x, min_y = 6 * 16, 4 * 16
        max_x, max_y = 186 * 16, 144 * 16

        # Max attempts to prevent infinite loop
        attempts = 0
        while not valid_pos and attempts < 200:
            attempts += 1
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            pos = Vector2(x, y)

            # Check if too close to player
            if pos.distance_to(self.car.position) < 500:
                continue

            # check collisions (with a buffer)
            test_rect = pg.Rect(0, 0, 32, 32)
            test_rect.center = pos

            valid_pos = True
            for wall in self.walls + self.tall_walls:
                if test_rect.colliderect(wall):
                    valid_pos = False
                    break

        GasCan(pos, self.car, self.group, self.gas_cans)

    def spawn_floating_text(self, pos: Vector2, text: str, color: tuple[int, int, int]):
        ft = FloatingText(pos, text, color, get_dir("fonts/BoldPixels.ttf"), 16)
        self.group.add(ft)

    def update(self, dt: float) -> None:
        if self.freeze_time > 0:
            self.freeze_time -= dt
            return

        self.car.accelerating = True

        if self.state == "RUNNING" or self.state == "MENU" or self.state == "GAMEOVER":
            self.group.update(dt)

        if self.shake_duration > 0:
            self.shake_duration -= dt

        if self.car.collision_speed > 0:
            self.shake_duration = 0.2
            self.shake_intensity = self.car.collision_speed / 100.0
            self.car.collision_speed = 0

        if self.state == "MENU":
            self.menu.update(dt)

        if self.state == "UPGRADE":
            self.upgrade_left.update(dt)
            self.upgrade_right.update(dt)

        if self.state == "RUNNING":
            self.game_time += dt

            # Death conditions
            is_dead = False
            if self.car.health <= 0:
                is_dead = True
            elif self.car.gas <= 0 and self.car.speed <= 0:
                is_dead = True

            if is_dead:
                self.death_timer += dt
                if self.death_timer >= 1.0:
                    self.state = "GAMEOVER"
                    self.game_over_sound.set_volume(0.45)
                    self.game_over_sound.play()
            else:
                self.death_timer = 0

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
                    if self.car.is_drifting():
                        enemy.push_back(self.car.rect.center)

                    if (
                        self.car.did_just_land()
                        or self.car.post_drift_time != 0
                        or self.car.invuln_time != 0
                    ):
                        enemy.take_damage(1)

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
                if self.bullets_to_shoot == 0:
                    self.bullets_to_shoot = self.car.num_bullets

                forward = Vector2(0, -1).rotate(self.car.display_angle)
                enemies_in_fov = []

                for enemy in self.enemies:
                    to_enemy = Vector2(enemy.rect.center) - Vector2(
                        self.car.rect.center
                    )
                    if to_enemy.length() > 0:
                        angle_to_enemy = forward.angle_to(to_enemy)
                        if abs(angle_to_enemy) < 45:  # 90 degree FOV (45 each side)
                            enemies_in_fov.append(enemy)

                if enemies_in_fov:
                    closest = min(
                        enemies_in_fov,
                        key=lambda e: Vector2(self.car.rect.center).distance_to(
                            e.rect.center
                        ),
                    )

                    dist_to_closest = Vector2(self.car.rect.center).distance_to(
                        closest.rect.center
                    )

                    if dist_to_closest < 250:
                        self.car.add_bullet(Vector2(closest.rect.center))
                        if self.bullets_to_shoot != 0:
                            self.bullets_to_shoot -= 1
                            self.car.time_since_last_shot = self.car.shot_delay - 0.1

                        if self.bullets_to_shoot == 0:
                            self.car.time_since_last_shot = 0
                else:
                    # If no enemies in FOV, we don't shoot and we don't start/continue a burst
                    # but we keep the timer running so it can shoot as soon as an enemy enters FOV
                    # if the delay has already passed.
                    pass

            # bullet/enemy collision
            collisions = pg.sprite.groupcollide(self.bullets, self.enemies, True, False)
            if collisions:
                for bullet, hit_enemies in collisions.items():
                    for enemy in hit_enemies:
                        enemy.take_damage(1)

        # self.menu.update(dt)
        # maybe remove?
        if self.car.health == 0:
            self.car.turning = "left"

        if (
            self.state != "MENU"
            and self.state != "UPGRADE"
            and self.state != "GAMEOVER"
        ):
            if self.car.skulls >= self.skulls_to_upgrade[0]:
                left_type, right_type = random.sample(self.upgrade_types, 2)
                self.upgrade_left = UICard("selected", "left", left_type)
                self.upgrade_right = UICard("unselected", "right", right_type)
                self.state = "UPGRADE"
            else:
                self.state = "RUNNING"

        self.game_ui.update(dt, self.car.health, self.car.gas, self.car.skulls)

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
