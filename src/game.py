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
import time

from helper import *

import grass

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
    state: Literal["MENU", "RUNNING", "UPGRADE", "GAMEOVER", "PAUSED"]
    started: bool = False

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

    space_held_time: float = 0.0
    left_held_time: float = 0.0
    right_held_time: float = 0.0
    space_bar_press_tmr: float = 0.0
    space_bar_press_tmr_target: float = 1.5

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
        self.game_start_sound = load_sound("sound/game_start.wav", 1)
        self.upgrade_charge_sound = load_sound("sound/upgrade.mp3", 1.0)
        self.upgrade_swap_sound = load_sound("sound/menu_select.wav", 0.5)
        self.pause_sound = load_sound("sound/menu_select.wav", 0.6)
        self.upgrade_charge_channel = None

        self.space_held_time = 0.0
        self.space_bar_press_tmr_target = self.upgrade_charge_sound.get_length()

        self.upgrade_left = UICard("selected", "left")
        self.upgrade_right = UICard("unselected", "right")

        self.walls = []
        self.tall_walls = []

        self.map_width = 1000000  # Effectively infinite
        self.frame_count = 0
        self.map_height = 1000000

        # We keep map_layer for camera handling but point it to dummy data
        # or just use its size. Pyscroll needs it.
        tmx_data = load_pygame(str(self.map_path))
        self.map_layer = pyscroll.BufferedRenderer(
            data=pyscroll.data.TiledMapData(tmx_data),
            size=self.screen.get_size(),
            clamp_camera=False,  # Allow moving anywhere
        )

        self.map_layer.zoom = 1
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)
        self.fps = 0

        # Initialize grass
        self.grass_manager = grass.GrassManager(
            get_dir("grass"),
            tile_size=16,
            stiffness=20,  # Increased from 5 for better performance (returns to cache faster)
            max_unique=15,
            place_range=[0, 1],
        )
        self.grass_manager.enable_ground_shadows(
            shadow_radius=4, shadow_color=(0, 0, 1), shadow_strength=40
        )
        self.generated_grass_tiles = set()

        # Load the dirt floor pattern from dirt.tmx
        dirt_tmx = load_pygame(str(ASSETS_DIR / "tiled" / "dirt.tmx"))
        self.floor_tile = pg.Surface(
            (dirt_tmx.width * dirt_tmx.tilewidth, dirt_tmx.height * dirt_tmx.tileheight)
        )
        for layer in dirt_tmx.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = dirt_tmx.get_tile_image_by_gid(gid)
                    if tile:
                        self.floor_tile.blit(
                            tile, (x * dirt_tmx.tilewidth, y * dirt_tmx.tileheight)
                        )
        self.floor_tile = self.floor_tile.convert()

        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.gas_cans = pg.sprite.Group()

        self.car = Car(self.group, self.screen, self.bullets, self)
        self.car.position = Vector2(101.9 * 16, 69.1 * 16)
        self.group.add(self.car)

        self.group.center(self.car.position + Vector2(-160, -110))

        self.gas_arrow = GasArrow(self.car, self.group, self.gas_cans)

        pg.mixer.music.set_endevent(MUSIC_END)
        pg.mixer.music.load(get_dir("music/1.ogg"))
        for i in range(2, 9):
            pg.mixer.music.queue(get_dir(f"music/{i}.ogg"))

        pg.mixer.music.set_volume(self.volume)
        pg.mixer.music.play()

        self.menu = Menu(screen, self.car, self.state_set_running)
        self.game_ui = GameUI(screen)
        self.state = "MENU"
        self.started = False
        self.last_dt = 0.016

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
                target_center = Vector2(self.group.view.center).lerp(
                    target_pos, max(0.0, min(1.0, 0.1))
                )
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

        view_rect = self.group.view
        view_offset_x = view_rect.x
        view_offset_y = view_rect.y

        tile_w = self.floor_tile.get_width()
        tile_h = self.floor_tile.get_height()

        start_x = int((view_offset_x // tile_w) * tile_w)
        start_y = int((view_offset_y // tile_h) * tile_h)

        for y in range(start_y, start_y + HEIGHT + tile_h, tile_h):
            for x in range(start_x, start_x + WIDTH + tile_w, tile_w):
                self.screen.blit(
                    self.floor_tile, (x - view_offset_x, y - view_offset_y)
                )

        visible_sprites = sorted(
            [s for s in self.group if s.rect.colliderect(view_rect)],
            key=lambda s: getattr(s, "_layer", 0),
        )

        i = 0
        while i < len(visible_sprites) and getattr(visible_sprites[i], "_layer", 0) < 0:
            sprite = visible_sprites[i]
            self.screen.blit(
                sprite.image,
                (sprite.rect.x - view_offset_x, sprite.rect.y - view_offset_y),
            )
            i += 1

        t = pg.time.get_ticks() / 1000.0
        self.grass_manager.update_render(
            self.screen,
            self.last_dt,
            offset=(view_offset_x, view_offset_y),
            rot_function=lambda x, y: int(math.sin(t + x / 100) * 15),
        )

        while i < len(visible_sprites):
            sprite = visible_sprites[i]
            self.screen.blit(
                sprite.image,
                (sprite.rect.x - view_offset_x, sprite.rect.y - view_offset_y),
            )
            i += 1

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

        if self.state == "RUNNING" and not self.started:
            prompts = [
                "PRESS LEFT OR RIGHT TO START",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "TAP LEFT OR RIGHT TO HOP",
                "HOLD BEFORE LANDING TO INITIATE A DRIFT",
                "RELEASE TO DRIFT OUT",
                "TAP TO BOOST OUT OF DRIFT",
            ]
            blink = (pg.time.get_ticks() // 600) % 2 == 0
            for i, line in enumerate(prompts):
                if not line:
                    continue
                if i == 0 and not blink:
                    continue
                text = self.font.render(line, True, (255, 255, 255))
                shadow = self.font.render(line, True, (0, 0, 0))
                text_rect = text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 - 200 + (i * 20))
                )
                self.screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
                self.screen.blit(text, text_rect)

        if (
            self.state == "UPGRADE"
            or self.state == "GAMEOVER"
            or self.state == "PAUSED"
        ):
            overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

        if self.state == "PAUSED":
            blink = (pg.time.get_ticks() // 600) % 2 == 0
            lines = ["PAUSED", "PRESS P TO RESUME"]
            for i, line in enumerate(lines):
                if i == 1 and not blink:
                    continue
                text = self.font.render(line, True, (255, 255, 255))
                shadow = self.font.render(line, True, (0, 0, 0))
                text_rect = text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 - 20 + (i * 30))
                )
                self.screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
                self.screen.blit(text, text_rect)

        if self.state == "UPGRADE":
            self.upgrade_left.draw(self.screen)
            self.upgrade_right.draw(self.screen)

            text = self.font.render("HOLD SPACE TO SELECT", True, (255, 255, 255))
            shadow = self.font.render("HOLD SPACE TO SELECT", True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, 65))
            self.screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            self.screen.blit(text, text_rect)

        if self.state == "GAMEOVER":
            text = self.font.render("GAME OVER", True, (255, 50, 50))
            shadow = self.font.render("GAME OVER", True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            self.screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            self.screen.blit(text, text_rect)

            sub_text = self.font.render(
                f"SCORE: {self.car.skulls}", True, (255, 255, 255)
            )
            sub_shadow = self.font.render(f"SCORE: {self.car.skulls}", True, (0, 0, 0))
            sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(sub_shadow, (sub_rect.x + 2, sub_rect.y + 2))
            self.screen.blit(sub_text, sub_rect)

            if (pg.time.get_ticks() // 600) % 2 == 0:
                sub_text = self.font.render("PRESS R TO RESTART", True, (255, 255, 255))
                sub_shadow = self.font.render("PRESS R TO RESTART", True, (0, 0, 0))
                sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
                self.screen.blit(sub_shadow, (sub_rect.x + 2, sub_rect.y + 2))
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
                pg.mixer.music.load(get_dir("music/1.ogg"))
                for i in range(2, 9):
                    pg.mixer.music.queue(get_dir(f"music/{i}.ogg"))
                pg.mixer.music.play()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    timestamp = int(time.time())
                    pg.image.save(self.screen, f"screenshot_{timestamp}.png")
                    print(f"Screenshot saved as screenshot_{timestamp}.png")

                if event.key == pg.K_f:
                    pg.display.toggle_fullscreen()

                if event.key == pg.K_p:
                    if self.state == "RUNNING" and self.started:
                        self.state = "PAUSED"
                        self.pause_sound.play()
                        pg.mixer.music.set_volume(self.volume * 0.1)
                    elif self.state == "PAUSED":
                        self.state = "RUNNING"
                        self.pause_sound.play()
                        pg.mixer.music.set_volume(self.volume)

                if self.state == "RUNNING" and not self.started:
                    if event.key in [pg.K_SPACE, pg.K_LEFT, pg.K_RIGHT]:
                        self.started = True
                        self.game_start_sound.play()
                        self.game_ui.show()

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

        if self.state == "GAMEOVER" or self.state == "PAUSED":
            return

        pressed = pg.key.get_pressed()
        just_pressed = pg.key.get_just_pressed()
        just_released = pg.key.get_just_released()
        current_time = pg.time.get_ticks()

        if self.state == "UPGRADE":
            if (
                just_pressed[pg.K_SPACE]
                or just_pressed[pg.K_LEFT]
                or just_pressed[pg.K_RIGHT]
            ):
                self.upgrade_charge_sound.set_volume(1.0)
                self.upgrade_charge_channel = self.upgrade_charge_sound.play()

            if pressed[pg.K_SPACE] or pressed[pg.K_LEFT] or pressed[pg.K_RIGHT]:
                self.space_bar_press_tmr += dt
                progress = max(
                    0.0,
                    min(
                        1.0, self.space_bar_press_tmr / self.space_bar_press_tmr_target
                    ),
                )

                if self.upgrade_left.state == "selected":
                    self.upgrade_left.set_progress(progress)
                elif self.upgrade_right.state == "selected":
                    self.upgrade_right.set_progress(progress)

            if self.space_bar_press_tmr >= self.space_bar_press_tmr_target:
                if getattr(self, "upgrade_charge_channel", None):
                    self.upgrade_charge_channel.stop()
                    self.upgrade_charge_channel = None

                if self.upgrade_left.state == "selected":
                    self.upgrade_left.upgrade(self.car)
                elif self.upgrade_right.state == "selected":
                    self.upgrade_right.upgrade(self.car)

                self.space_bar_press_tmr = 0.0

                self.skulls_to_upgrade = self.skulls_to_upgrade[1:-1]
                self.skulls_to_upgrade.append(self.skulls_to_upgrade[0] + 10)
                self.state = "RUNNING"
                self.game_ui.show()
                pg.mixer.unpause()
                pg.mixer.music.set_volume(self.volume)
                return

            if (
                just_released[pg.K_SPACE]
                or just_released[pg.K_LEFT]
                or just_released[pg.K_RIGHT]
            ):
                if getattr(self, "upgrade_charge_channel", None):
                    self.upgrade_charge_channel.stop()
                    self.upgrade_charge_channel = None

                held_time = self.space_bar_press_tmr
                self.space_bar_press_tmr = 0.0

                if self.upgrade_left.state == "selected":
                    self.upgrade_left.reset_progress()
                elif self.upgrade_right.state == "selected":
                    self.upgrade_right.reset_progress()

                if held_time < 0.2:
                    if self.upgrade_left.state == "selected":
                        self.upgrade_left.state = "unselected"
                        self.upgrade_right.state = "selected"
                        self.upgrade_swap_sound.play()
                    elif self.upgrade_right.state == "selected":
                        self.upgrade_left.state = "selected"
                        self.upgrade_right.state = "unselected"
                        self.upgrade_swap_sound.play()

            return

        # IF STATE IS MENU (MAIN MENU)
        # DO NO ALLOW USER INPUT
        if self.state == "MENU":
            self.car.accelerating = True
            self.car.turning = "drift_in"
            return

        if not self.started:
            self.car.accelerating = True
            self.car.turning = "drift_in"
            return

        if just_released[pg.K_0]:
            self.car.take_damage()

        # Handle both directions
        for key, direction in [(pg.K_LEFT, -1), (pg.K_RIGHT, 1)]:
            opposite_key = pg.K_RIGHT if key == pg.K_LEFT else pg.K_LEFT
            key_held_time = (
                self.left_held_time if key == pg.K_LEFT else self.right_held_time
            )

            if just_released[key]:
                if self.car.is_drifting():
                    if self.car.turn_dir == direction:
                        # check if we are still holding the other key to drift out
                        if pressed[opposite_key]:
                            self.car.start_drift_out()
                        else:
                            # click to hop or release drift
                            if key_held_time < HOLD_TIME:
                                self.car.end_drift()
                            else:
                                self.car.start_drift_neutral()
                    else:
                        # Released opposite key while drifting
                        if key_held_time < HOLD_TIME:
                            self.car.end_drift()
                        else:
                            # If we held the opposite key, we were in drift_out.
                            # On release, if original key still held, go back to drift_in
                            if pressed[opposite_key]:
                                self.car.start_drift_in()
                            else:
                                self.car.start_drift_neutral()

                elif self.car.turning is None:
                    if key_held_time < HOLD_TIME:
                        if self.car.z_pos == 0:
                            self.car.jump()

                if (key == pg.K_LEFT and self.car.turning == "left") or (
                    key == pg.K_RIGHT and self.car.turning == "right"
                ):
                    self.car.turning = None

            if just_pressed[key]:
                if self.car.is_drifting():
                    if self.car.turn_dir == direction:
                        self.car.start_drift_in()
                    else:
                        self.car.start_drift_out()

            # has key been pressed
            if pressed[key]:
                if self.car.turning is None:
                    if self.car.z_pos == 0:
                        if key_held_time > HOLD_TIME:
                            if key == pg.K_LEFT:
                                self.car.start_left_turn()
                            else:
                                self.car.start_right_turn()
                    else:
                        self.car.start_drift(direction)

            # Neutral handling: if we are drifting and neither key is pressed for that drift's direction
            if self.car.is_drifting():
                drift_key = pg.K_LEFT if self.car.turn_dir == -1 else pg.K_RIGHT
                drift_opposite = pg.K_RIGHT if self.car.turn_dir == -1 else pg.K_LEFT

                if not pressed[drift_key] and not pressed[drift_opposite]:
                    self.car.start_drift_neutral()

        self.car.accelerating = True

        if pressed[pg.K_LEFT]:
            self.left_held_time += dt
        else:
            self.left_held_time = 0

        if pressed[pg.K_RIGHT]:
            self.right_held_time += dt
        else:
            self.right_held_time = 0

        if pressed[pg.K_LEFT] or pressed[pg.K_RIGHT]:
            self.space_held_time += dt
        else:
            self.space_held_time = 0

    def state_set_running(self):
        self.state = "RUNNING"
        self.started = False
        print("GAME STATE: RUNNING")
        self.menu.hide()
        self.game_ui.hide()

    def state_set_menu(self):
        self.state = "MENU"
        self.started = False
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

        self.group.center(self.car.position + Vector2(-160, -110))

        self.menu.set_car(self.car)

        self.gas_arrow = GasArrow(self.car, self.group, self.gas_cans)

        self.skulls_to_upgrade = [1, 5, 10, 20, 30, 40, 50]
        self.death_timer = 0
        self.game_time = 0
        self.wave_count = 0
        self.time_to_next_wave = WAVE_INTERVAL_SECS
        self.bullets_to_shoot = 0

        self.volume = 0.5
        pg.mixer.music.set_volume(self.volume)

        self.state_set_menu()
        self.spawn_gas()
        self.started = False
        print("GAME RESTARTED")

    def spawn_wave(self):
        self.wave_count += 1

        difficulty = min(1.0, self.game_time / 100.0)

        min_size = int(6 + (difficulty * 12))
        max_size = int(12 + (difficulty * 24))

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
        self.last_dt = dt
        if self.freeze_time > 0:
            self.freeze_time -= dt
            return

        # Pre-calculate viewport for optimization
        view_rect = pg.Rect(self.group.view)
        # Expanded view for updates (zombies just outside screen should still move)
        update_rect = view_rect.inflate(WIDTH, HEIGHT)

        if self.state == "MENU":
            pass

        if self.state == "RUNNING" or self.state == "MENU" or self.state == "GAMEOVER":
            # Update spatial grid for enemies once per frame
            Enemy.update_grid(self.enemies)

            self.group.update(dt)

            # Infinite Grass Generation around the car (optimized to run every 10 frames)
            if self.frame_count % 10 == 0:
                car_tile_x = int(self.car.position.x // 16)
                car_tile_y = int(self.car.position.y // 16)

                # radius around player to ensure grass is generated ahead
                # reduced from 35 to 25 to reduce frame spikes
                radius = 25
                for ty in range(car_tile_y - radius, car_tile_y + radius):
                    for tx in range(car_tile_x - radius, car_tile_x + radius):
                        if (tx, ty) not in self.generated_grass_tiles:
                            density = random.randint(8, 16)
                            self.grass_manager.place_tile(
                                (tx, ty), density, [0, 1, 2, 3, 4, 5]
                            )
                            self.generated_grass_tiles.add((tx, ty))

            self.frame_count += 1

            if self.car.z_pos == 0:
                mask_offset = (self.car.rect.x, self.car.rect.y)
                self.grass_manager.apply_mask_force(self.car.mask, mask_offset)

                dist = self.car.position.distance_to(self.car.old_position)
                # Increased threshold and step for intermediate force application
                if dist > 20:
                    num_steps = int(dist / 20)
                    for i in range(1, num_steps):
                        lerp_pos = self.car.old_position.lerp(
                            self.car.position, i / num_steps
                        )
                        # Center of mask
                        mask_tl = (lerp_pos.x - 150, lerp_pos.y - 150)
                        self.grass_manager.apply_mask_force(self.car.mask, mask_tl)

            cell_x = int(self.car.position.x // Enemy.grid_cell_size)
            cell_y = int(self.car.position.y // Enemy.grid_cell_size)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    cell = (cell_x + dx, cell_y + dy)
                    if cell in Enemy.grid:
                        for enemy in Enemy.grid[cell]:
                            self.grass_manager.apply_force(enemy.pos, 10, 20)

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
            if self.started:
                self.game_time += dt

            # death conditions
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

            new_vol = pg.math.lerp(self.volume, 0.1, max(0.0, min(1.0, 0.01)))
            if new_vol != self.volume:
                self.volume = new_vol
                pg.mixer.music.set_volume(self.volume)

            if self.started:
                self.time_to_next_wave -= dt

                if self.time_to_next_wave < 0:
                    self.spawn_wave()
                    self.time_to_next_wave = WAVE_INTERVAL_SECS

            landing_mask = self.car.get_landing_mask()
            landing_aoe_mask = self.car.get_landing_mask_aoe()

            landing_shift = 150  # (600 - 300) / 2
            landing_aoe_shift = 600  # (1500 - 300) / 2

            check_cells = 4  # landing aoe
            for dx in range(-check_cells, check_cells + 1):
                for dy in range(-check_cells, check_cells + 1):
                    cell = (cell_x + dx, cell_y + dy)
                    if cell in Enemy.grid:
                        for enemy in Enemy.grid[cell]:
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

                            # damage collision
                            if self.car.z_pos == 0 and self.car.invuln_time <= 0:
                                offset = (
                                    enemy.rect.x - self.car.rect.x,
                                    enemy.rect.y - self.car.rect.y,
                                )
                                if self.car.mask.overlap(enemy.mask, offset):
                                    if not (
                                        self.car.did_just_land()
                                        or self.car.post_drift_time != 0
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

                for dx in range(-4, 5):
                    for dy in range(-4, 5):
                        cell = (cell_x + dx, cell_y + dy)
                        if cell in Enemy.grid:
                            for enemy in Enemy.grid[cell]:
                                to_enemy = Vector2(enemy.rect.center) - Vector2(
                                    self.car.rect.center
                                )
                                dist_sq = to_enemy.length_squared()
                                if 0 < dist_sq < 62500:  # 250^2
                                    angle_to_enemy = forward.angle_to(to_enemy)
                                    if abs(angle_to_enemy) < 45:
                                        enemies_in_fov.append((enemy, dist_sq))

                if enemies_in_fov:
                    closest_enemy, _ = min(enemies_in_fov, key=lambda x: x[1])

                    self.car.add_bullet(Vector2(closest_enemy.rect.center))
                    if self.bullets_to_shoot != 0:
                        self.bullets_to_shoot -= 1
                        self.car.time_since_last_shot = self.car.shot_delay - 0.1

                    if self.bullets_to_shoot == 0:
                        self.car.time_since_last_shot = 0

            # bullet/enemy collision
            for bullet in self.bullets:
                b_cell_x = int(bullet.rect.centerx // Enemy.grid_cell_size)
                b_cell_y = int(bullet.rect.centery // Enemy.grid_cell_size)
                hit = False
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        cell = (b_cell_x + dx, b_cell_y + dy)
                        if cell in Enemy.grid:
                            for enemy in Enemy.grid[cell]:
                                if bullet.rect.colliderect(enemy.rect):
                                    enemy.take_damage(1)
                                    bullet.kill()
                                    hit = True
                                    break
                        if hit:
                            break
                    if hit:
                        break

        # self.menu.update(dt)
        # maybe remove?
        if self.car.health == 0:
            self.car.turning = "left"

        if (
            self.state != "MENU"
            and self.state != "UPGRADE"
            and self.state != "GAMEOVER"
            and self.state != "PAUSED"
        ):
            if self.car.skulls >= self.skulls_to_upgrade[0]:
                left_type, right_type = random.sample(self.upgrade_types, 2)
                self.upgrade_left = UICard("selected", "left", left_type)
                self.upgrade_right = UICard("unselected", "right", right_type)
                self.state = "UPGRADE"
                self.game_ui.hide()
                pg.mixer.pause()
                self.game_start_sound.play()
                pg.mixer.music.set_volume(self.volume * 0.3)
            else:
                self.state = "RUNNING"

        self.game_ui.update(dt, self.car.health, self.car.gas, self.car.skulls)

    def run(self):
        clock = pg.time.Clock()
        self.running = True
        pg.display.set_caption("MiniMoto")

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
