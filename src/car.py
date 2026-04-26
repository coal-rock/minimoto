from bullet import Bullet, HitSpark
from pygame.locals import SRCALPHA
import pygame as pg
from pygame.math import Vector2
from pyscroll.group import PyscrollGroup

from typing import Literal
import math
import random
from functools import lru_cache

from helper import *
from spark import Spark
from trail import Trail
from cloud import Cloud
from explosion_puff import FirePuff

CAR_MAX_SPEED = 340
CAR_ACCEL_SPEED = 300
CAR_DECCEL_SPEED = 450
CAR_DECCEL_NO_GAS = 100
CAR_LANDING_DECCEL_SPEED = 5000

CAR_INITIAL_TURN_SPEED = 500
CAR_TURN_ACCEL = 250
CAR_TURN_DECCEL = 350
CAR_MAX_TURN_SPEED = 12 * 12
CAR_TURN_THRESHOLD = 30

CAR_SPEED_DRIFT_THRESHOLD = 100
CAR_DRIFT_BOOST = [100, 150, 200]
CAR_DRIFT_POST_TIME = [0.2, 0.5, 0.7]
CAR_DRIFT_BOOST_TIME = [0.7, 1.4, 2.3]
CAR_COLLISION_MIN_SPEED = 200
CAR_COLLISION_LANDING_MIN_SPEED = 100
CAR_COLLISION_LANDING_MAX_SPEED = 250

CAR_JUMP_FOCE = 300
CAR_GRAVITY = -1100

CAR_GAS_DRAIN = 2.8
CAR_GAS_DRIFT_DRAIN = 1.2

CAR_SHOT_TIME = 1

OFFSET = Vector2(100, 100)


class Car(pg.sprite.Sprite):
    health: int = 5
    max_health: int = 5

    gas: float = 100
    skulls: int = 0
    invuln_time: float = 0
    hit_flash_time: float = 0

    shot_delay: float = CAR_SHOT_TIME
    time_since_last_shot: float = 0

    magnet_radius = 300
    angle: float
    speed: float
    turn_speed: float
    direction: Vector2
    position: Vector2
    old_position: Vector2
    time_spent_drifting: float
    post_drift_time: float
    car_max_speed: float
    group: PyscrollGroup
    bullets_group: pg.sprite.Group

    # using strings here is prob dumb but i honestly
    # can't be fucked to use a proper enum
    turning: Literal["left", "drift_in", "drift_out", None]
    frames: list[pg.Surface]
    frame_num: int
    accelerating: bool
    sparks: list[Spark]
    world_sparks: list[Spark]
    spark_bl: Vector2
    spark_br: Vector2
    time: float
    z_pos: float
    old_z_pos: float = 0
    last_z_pos: float
    colliding: Literal["tall", "short", None]
    collision_speed: float = 0
    smoke_timer: float = 0

    image: pg.Surface
    rect: pg.Rect
    land_mask: pg.Mask
    land_aoe_mask: pg.Mask
    screen: pg.Surface

    # neither of these are offset by world pos
    # collision mask
    mask: pg.Mask
    # collision rect
    body: pg.Rect
    knockback_strength = 0.9

    def __init__(
        self,
        group: PyscrollGroup,
        screen: pg.Surface,
        bullets_group: pg.sprite.Group,
        game: Game,
    ) -> None:
        super().__init__()
        self.boost_scale = 1
        self.jump_force = CAR_JUMP_FOCE
        self.game = game
        self._layer = 3
        self.car_max_speed = CAR_MAX_SPEED
        self.bullets_group = bullets_group

        self.frames = []
        self.burnt_frames = []

        for i in range(0, 48):
            self.frames.append(load_image(f"car/car{i:03}.png").convert_alpha())

        for i in range(0, 8):
            self.burnt_frames.append(
                load_image(f"burnt_car/burnt{i}.png").convert_alpha()
            )

        self.image = pg.Surface((300, 300), pg.SRCALPHA)
        self.rect = self.image.get_rect()

        self.body = pg.Rect()
        self.group = group
        self.position = Vector2(0, 0)
        self.old_position = self.position
        self.direction = Vector2(0, -1)
        self.angle = 0
        self.display_angle = 0
        self.speed = 0
        self.turn_speed = 0
        self.accelerating = False
        self.turning = None
        self.time_spent_drifting = 0
        self.sparks = []
        self.frame_num = 0
        self.time = 0
        self.post_drift_time = 0
        self.visual_offset = 0.0
        self.screen = screen
        self.world_sparks = []
        self.z_pos = 0
        self.time_since_last_fire_puff = 0.0
        self.z_velocity = 0
        self.colliding = None
        self.num_bullets = 1
        self.collision_sound_timer = 0

        self.jump_sound = load_sound("sound/hop.mp3", 0.5)
        self.bump_sound = load_sound("sound/bump.mp3", 0.6)
        self.drift_sound = load_sound("sound/drift.mp3", 0.1)
        self.boost_sound = load_sound("sound/boost.mp3", 1)
        self.land_sound = load_sound("sound/land.mp3", 0.5)
        self.shoot_sound = load_sound("sound/shoot.wav", 0.2)
        self.explosion_sound = load_sound("sound/explosion.wav", 0.3)

        self.drift_sound_channel = None
        self.gas_drain_mult = 1

    def take_damage(self):
        if self.invuln_time > 0 or self.health <= 0:
            return
        self.health -= 1
        self.hit_flash_time = 0.15
        self.game.freeze_time = 0.05
        if self.health <= 0:
            self.health = 0
            self.explode()

        self.invuln_time = 1.5
        self.game.shake_duration = 0.5
        self.game.shake_intensity = 8
        self.bump_sound.play()

    def explode(self):
        self.explosion_sound.set_volume(0.25)
        self.explosion_sound.play()
        self.end_drift(False)

        fire_colors = [
            (255, 255, 255),
            (255, 255, 0),
            (255, 128, 0),
            (255, 0, 0),
            (50, 50, 50),
        ]
        smoke_colors = [(100, 100, 100), (50, 50, 50), (20, 20, 20)]

        for _ in range(60):
            offset = Vector2(random.uniform(-20, 20), random.uniform(-40, 40)).rotate(
                -self.display_angle
            )

            pos = self.position + offset

            vel = (
                offset.normalize() * random.uniform(50, 150)
                if offset.length() > 0
                else Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
            )

            radius = random.uniform(5, 10)
            life = random.uniform(0.4, 0.8)

            colors = fire_colors if random.random() > 0.3 else smoke_colors

            puff = FirePuff(pos, vel, radius, colors, life)
            self.game.group.add(puff)

        for _ in range(15):
            offset = Vector2(random.uniform(-15, 15), random.uniform(-30, 30)).rotate(
                -self.display_angle
            )
            pos = self.position + offset
            vel = Vector2(random.uniform(-20, 20), random.uniform(-40, -10))

            radius = random.uniform(5, 15)
            life = random.uniform(1.0, 2.0)

            puff = FirePuff(pos, vel, radius, smoke_colors, life)
            self.game.group.add(puff)

    def emit_fire(self):
        fire_colors = [
            (255, 255, 255),
            (255, 255, 0),
            (255, 128, 0),
            (255, 0, 0),
            (50, 50, 50),
        ]
        smoke_colors = [(100, 100, 100), (50, 50, 50), (20, 20, 20)]

        # Emit fire
        offset = Vector2(random.uniform(-10, 10), random.uniform(-20, 20)).rotate(
            -self.display_angle
        )
        pos = self.position + offset
        vel = Vector2(random.uniform(-20, 20), random.uniform(-40, -10)).rotate(
            -self.display_angle
        )
        radius = random.uniform(3, 8)
        life = random.uniform(0.3, 0.6)

        colors = fire_colors if random.random() > 0.2 else smoke_colors
        puff = FirePuff(pos, vel, radius, colors, life)
        self.game.group.add(puff)

    def jump(self):
        if self.health == 0 or self.gas <= 0:
            return

        if self.z_pos >= 0:
            self.z_velocity = self.jump_force
            self.jump_sound.play()
            self.game.shake_duration = 0

    def emit_sparks(self, world: bool = False):
        if self.speed < CAR_SPEED_DRIFT_THRESHOLD:
            return

        if not self.is_grounded():
            return

        if self.time_spent_drifting > CAR_DRIFT_BOOST_TIME[2]:
            COLOR = (230, 170, 255)
        elif self.time_spent_drifting > CAR_DRIFT_BOOST_TIME[1]:
            COLOR = (255, 230, 170)
        elif self.time_spent_drifting > CAR_DRIFT_BOOST_TIME[0]:
            COLOR = (255, 170, 170)
        else:
            return

        spark_bl = self.get_rotated_pos(Vector2(136, 173))
        spark_br = self.get_rotated_pos(Vector2(164, 173))

        target_arr = self.world_sparks if world else self.sparks

        offset_x = self.rect.topleft[0] if world else 0
        offset_y = self.rect.topleft[1] if world else 0

        for pos in [spark_bl, spark_br]:
            target_arr.append(
                Spark(
                    [
                        pos.x + offset_x,
                        pos.y + offset_y,
                    ],
                    math.radians(random.randint(0, 360)),
                    random.randint(1, 3),
                    COLOR,
                    0.80
                    * (
                        self.time_spent_drifting / CAR_DRIFT_BOOST_TIME[2]
                    ),  # scale drift spark with time spent drifting
                ),
            )

    def get_rotated_pos(self, pos: Vector2, display: bool = True) -> Vector2:
        body_pivot = Vector2(self.image.get_width() // 2, self.image.get_height() // 2)
        offset_pos = pos - body_pivot
        rotated_offset_pos = offset_pos.rotate(
            self.display_angle if display else self.angle
        )
        return body_pivot + rotated_offset_pos

    def get_rotated_rect(
        self,
        rect: pg.Rect,
        color: tuple[int, int, int, int] = (255, 0, 0, 255),
        border_radius: int = 0,
    ) -> tuple[pg.Rect, pg.Surface]:

        angle = self.get_angle_rot_locked()
        rect_tuple = (rect.x, rect.y, rect.w, rect.h)
        return self._get_cached_surface(rect_tuple, color, border_radius, angle)

    @lru_cache(maxsize=128)
    def _get_cached_surface(
        self,
        rect_tuple: tuple[int, int, int, int],
        color: tuple[int, int, int, int],
        border_radius: int,
        angle: float,
    ) -> tuple[pg.Rect, pg.Surface]:
        temp_rect = pg.Rect(rect_tuple)

        temp_surface = pg.Surface(self.image.get_size(), pg.SRCALPHA)
        pg.draw.rect(temp_surface, color, temp_rect, border_radius=border_radius)

        rotated_surface = pg.transform.rotate(temp_surface, -angle)

        center = (self.image.get_width() // 2, self.image.get_height() // 2)
        rotated_rect = rotated_surface.get_rect(center=center)

        return rotated_rect, rotated_surface

    def get_angle_rot_locked(self) -> float:
        if self.health != 0:
            return ((round((self.display_angle % 360) / 7.5)) % 48) * 7.5
        else:
            return ((round((self.display_angle % 360) / 45)) % 8) * 45

    def handle_collision(
        self,
        dt: float,
        wall_type: Literal["short", "tall"],
        collision_point: tuple[int, int] | None = None,
    ) -> None:
        # if we are in the air, ignore collision
        if self.z_pos > 0 and wall_type == "short":
            return

        self.position = Vector2(self.old_position)

        if collision_point:
            # Nudge away from the collision point to prevent sticking
            # collision_point is relative to the car's 300x300 surface
            center = Vector2(150, 150)
            diff = center - Vector2(collision_point)
            if diff.length() > 0:
                self.position += diff.normalize() * 4.0

        self.rect.center = (round(self.position.x), round(self.position.y))

        # if we on top of something, we should hop to get off
        if self._layer == 4 and not self.colliding == "tall":
            if wall_type == "short":
                self.jump_sound.play()
                self.z_velocity += 180

            if self.collision_sound_timer <= 0:
                self.bump_sound.play()
                self.collision_sound_timer = 0.2

            self.speed -= CAR_LANDING_DECCEL_SPEED * dt
            if self.speed > CAR_COLLISION_LANDING_MAX_SPEED:
                self.speed = CAR_COLLISION_LANDING_MAX_SPEED

            if self.speed < CAR_COLLISION_LANDING_MIN_SPEED:
                self.speed = CAR_COLLISION_LANDING_MIN_SPEED
        else:
            if self.collision_sound_timer <= 0:
                self.bump_sound.play()
                self.collision_sound_timer = 0.2

            self.collision_speed = abs(self.speed)

            is_front = True
            if collision_point:
                center = Vector2(150, 150)
                collision_vec = Vector2(collision_point) - center
                forward_vec = Vector2(0, -1).rotate(self.get_angle_rot_locked())
                is_front = collision_vec.dot(forward_vec) > 0

            if is_front:
                self.speed = min(-CAR_COLLISION_MIN_SPEED, self.speed * -0.5)
            else:
                self.speed = max(CAR_COLLISION_MIN_SPEED, self.speed * -0.5)

        # we don't call end_drift() here,
        # because we don't want the user to get the drift boost
        # maybe i should add a bail_drift() function or something (?)
        self.end_drift(False)

    def draw_motion_lines(self):
        for i in range(1, 16):
            line_len = random.randint(1, 30)
            line_pos = 140 + ((self.time * 1000) % 30)

            line_start = self.get_rotated_pos(Vector2(133 + 2 * i, line_pos))
            line_end = self.get_rotated_pos(Vector2(133 + 2 * i, line_pos + line_len))

            line_start = line_start + Vector2(0, -self.z_pos)
            line_end = line_end + Vector2(0, -self.z_pos)

            pg.draw.line(
                self.image,
                (
                    255,
                    255,
                    255,
                    max(
                        0,
                        min(255, round((max(0, self.speed) / self.car_max_speed) * 80)),
                    ),
                ),
                line_start,
                line_end,
                width=1,
            )

    def draw_sparks(self, offset: Vector2 = Vector2(0, 0)):
        for spark in self.sparks:
            spark.draw(self.image, offset=-offset)

        for spark in self.world_sparks:
            spark.draw(self.image, offset=self.rect.topleft - offset)

    def draw_headlights(self):
        beam_surf = pg.Surface(self.image.get_size(), pg.SRCALPHA)

        beam_points = [
            Vector2(142 - 5, 134),
            Vector2(158 + 5, 134),  # near
            Vector2(165, 80),
            Vector2(135, 80),  # far
        ]
        self.rotated_beams = [self.get_rotated_pos(p) for p in beam_points]
        beam_intensity = random.uniform(0.7, 1)
        for i in range(10, 0, -1):
            soft_points = [
                self.rotated_beams[0],
                self.rotated_beams[1],
                self.rotated_beams[2] + Vector2(i, 0).rotate(self.angle),
                self.rotated_beams[3] + Vector2(-i, 0).rotate(self.angle),
            ]

            alpha = 5 + (10 - i) * 2
            pg.draw.polygon(
                beam_surf, (255, 255, 200, round(alpha * beam_intensity)), soft_points
            )

        self.image.blit(beam_surf, (0, -self.z_pos), special_flags=pg.BLEND_RGBA_ADD)

    def draw_shadow(self):
        scale = (self.z_pos / 200) + 1
        shadow_rect = pg.Rect(135, 135, 33, 47).scale_by(scale)
        rect, surf = self.get_rotated_rect(shadow_rect, (0, 0, 0, 50), 8)
        self.image.blit(surf, rect.topleft)

    def draw(self, clear: bool = True, offset: Vector2 = Vector2(0, 0)) -> None:
        if clear:
            self.image.fill((0, 0, 0, 0))

        if self.invuln_time > 0:
            if round(self.time * 20) % 2 == 0:
                return

        self.draw_headlights()
        self.draw_motion_lines()
        self.draw_shadow()
        self.draw_sparks(offset)

        # offset draw pos by jump
        draw_pos = (100, 100 - self.z_pos)

        # hack
        if self.health != 0:
            frame = self.frames[self.frame_num]
            if self.hit_flash_time > 0:
                self.image.blit(get_white_surface(frame), draw_pos)
            else:
                self.image.blit(frame, draw_pos)
        else:
            self.frame_num = (round((self.display_angle % 360) / 45) + 6) % 8
            self.image.blit(self.burnt_frames[self.frame_num], draw_pos)

    def add_bullet(self, target: Vector2) -> None:
        if self.health == 0 or self.gas <= 0:
            return

        # offset the bullet start pos so it comes out of the front of the car
        bullet_start = self.get_rotated_pos(Vector2(150, 120)) + Vector2(
            self.rect.topleft
        )

        bullet = Bullet(bullet_start, target, self.group)
        self.group.add(bullet)
        self.bullets_group.add(bullet)
        self.game.shake_duration = 0.1
        self.game.shake_intensity = 1
        self.shoot_sound.set_volume(0.2)
        self.shoot_sound.play()

    def add_trail(self) -> None:
        if self.z_pos == 0:
            l_trail = self.get_rotated_pos(Vector2(140, 173)) + Vector2(
                self.rect.topleft
            )
            r_trail = self.get_rotated_pos(Vector2(160, 173)) + Vector2(
                self.rect.topleft
            )
            self.group.add(Trail(l_trail))
            self.group.add(Trail(r_trail))

    def add_cloud(self) -> None:
        for _ in range(0, random.randint(10, 60)):
            l_back = self.get_rotated_pos(Vector2(140, 173)) + Vector2(
                self.rect.topleft
            )
            r_back = self.get_rotated_pos(Vector2(160, 173)) + Vector2(
                self.rect.topleft
            )

            self.group.add(Cloud(l_back))
            self.group.add(Cloud(r_back))

    def start_drift(self):
        self.time_spent_drifting = 0
        self.turning = "drift_in"

        # UNFUCK PLEASE
        self.drift_sound_channel = self.drift_sound.play(-1)
        self.drift_sound.set_volume(0.1)

        if self.post_drift_time != 0:
            print("drift combo")

    def start_drift_out(self):
        self.turning = "drift_out"

    def start_drift_in(self):
        self.turning = "drift_in"

    def end_drift(self, give_boost: bool = True):
        self.turning = None

        if self.drift_sound_channel is not None:
            self.drift_sound_channel.stop()

        self.angle = self.display_angle
        self.visual_offset = 0
        self.velocity_dir = Vector2(0, -1).rotate(self.angle)

        if self.speed > CAR_SPEED_DRIFT_THRESHOLD and give_boost:
            self.boost_sound.play()

            if self.time_spent_drifting > CAR_DRIFT_BOOST_TIME[2]:
                self.speed += CAR_DRIFT_BOOST[2]
                self.post_drift_time = CAR_DRIFT_POST_TIME[2]
                self.game.shake_duration = 0.8
                self.game.shake_intensity = 1

            elif self.time_spent_drifting > CAR_DRIFT_BOOST_TIME[1]:
                self.speed += CAR_DRIFT_BOOST[1]
                self.post_drift_time = CAR_DRIFT_POST_TIME[1]
                self.game.shake_duration = 0.8
                self.game.shake_intensity = 1

            elif self.time_spent_drifting > CAR_DRIFT_BOOST_TIME[0]:
                self.speed += CAR_DRIFT_BOOST[0]
                self.post_drift_time = CAR_DRIFT_POST_TIME[0]
                self.game.shake_duration = 0.8
                self.game.shake_intensity = 1

    def is_drifting(self):
        return self.turning == "drift_in" or self.turning == "drift_out"

    def start_left_turn(self):
        self.turning = "left"

    def end_left_turn(self):
        self.turning = None

    def update_sparks(self, dt: float):
        for spark_list in [self.sparks, self.world_sparks]:
            for spark in spark_list[:]:
                spark.move(dt)
                if not spark.alive:
                    spark_list.remove(spark)

    def update_position(self, dt: float):
        heading_dir = Vector2(0, -1).rotate(self.angle)
        self.velocity_dir = heading_dir

        lerp_speed = 1.2 if self.is_drifting() else 6.0

        self.velocity_dir = self.velocity_dir.lerp(
            heading_dir, lerp_speed * dt
        ).normalize()

        suction_force = Vector2(0, 0)
        if self.is_drifting():
            inward_dir = self.velocity_dir.rotate(-90)
            suction_force = inward_dir * self.speed * 0.2

        current_velocity = (self.velocity_dir * self.speed) + suction_force

        self.old_position = Vector2(self.position)
        self.position += current_velocity * dt

        self.rect.center = (round(self.position.x), round(self.position.y))

        heading_dir = Vector2(0, -1).rotate(self.display_angle)
        self.velocity_dir = heading_dir

        self.old_z_pos = self.z_pos

        if self.z_pos > 0 or self.z_velocity > 0:
            self.z_velocity += CAR_GRAVITY * dt
            self.z_pos += self.z_velocity * dt

        if self.z_pos < 0:
            self.z_pos = 0
            self.z_velocity = 0

    def update_collision(self):
        car_collision_rect = pg.Rect(135, 136, 30, 40)
        body, body_surface = self.get_rotated_rect(car_collision_rect)

        # compute mask
        mask_surface = pg.Surface((300, 300), SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))
        mask_surface.blit(body_surface, body.topleft)
        self.mask = pg.mask.from_surface(mask_surface, 100)

    # am i currently touching the ground
    def is_grounded(self) -> bool:
        return self._layer == 3 and self.z_pos == 0

    # am i currently touching a raised object
    def is_landed(self) -> bool:
        return self._layer == 4 and self.z_pos == 0 and self.colliding == "short"

    # am i on or over an obstacle
    def over_obstacle(self):
        return self._layer == 4 and self.colliding == "short"

    def did_just_land(self):
        return self.z_pos == 0 and self.old_z_pos != 0

    @lru_cache(maxsize=128)
    def get_landing_mask(self) -> pg.mask.Mask:
        return self.mask.scale((600, 600))

    @lru_cache(maxsize=128)
    def get_landing_mask_aoe(self) -> pg.mask.Mask:
        return self.mask.scale((1500, 1500))

    def update_gas(self, dt: float) -> None:
        if self.game.state != "RUNNING":
            return

        if self.is_drifting():
            self.gas -= CAR_GAS_DRAIN * CAR_GAS_DRIFT_DRAIN * self.gas_drain_mult * dt
        else:
            self.gas -= CAR_GAS_DRAIN * self.gas_drain_mult * dt

    def update_shot(self, dt: float) -> None:
        self.time_since_last_shot += dt

    def update(self, dt: float) -> None:
        self.time += dt
        self.hit_flash_time -= dt
        self.hit_flash_time = max(0, self.hit_flash_time)

        deccel_speed = (
            CAR_DECCEL_SPEED * 0.8 if self.post_drift_time != 0 else CAR_DECCEL_SPEED
        )

        if self.gas <= 0 or self.health <= 0:
            self.accelerating = False
            deccel_speed = CAR_DECCEL_NO_GAS

        if self.health <= 0:
            self.time_since_last_fire_puff += dt
            if self.time_since_last_fire_puff > 0.05:
                self.time_since_last_fire_puff = 0
                self.emit_fire()

        # accel
        if self.accelerating and not self.over_obstacle():
            self.speed += CAR_ACCEL_SPEED * dt
        if (
            not self.accelerating
            or self.speed > self.car_max_speed
            and not self.over_obstacle()
        ):
            self.speed -= deccel_speed * dt
            self.speed = max(self.speed, 0)

        # turning
        if self.turning == "left":
            self.turn_speed -= CAR_TURN_ACCEL * dt

            if self.turn_speed < -CAR_MAX_TURN_SPEED:
                self.turn_speed += CAR_TURN_DECCEL * dt

        elif self.turning == "drift_in":
            self.turn_speed -= CAR_TURN_ACCEL * dt

            if self.turn_speed < -CAR_MAX_TURN_SPEED:
                self.turn_speed += CAR_TURN_DECCEL * dt

        elif self.turning == "drift_out":
            self.turn_speed -= CAR_TURN_ACCEL * dt

            if self.turn_speed < -CAR_MAX_TURN_SPEED:
                self.turn_speed += CAR_TURN_DECCEL * dt
        else:
            if self.turn_speed < 0:
                self.turn_speed += CAR_TURN_DECCEL * dt

                if self.turn_speed > 0:
                    self.turn_speed = 0

        match self.turning:
            case "drift_in":
                turn_multiplier = 2
                self.car_max_speed = CAR_MAX_SPEED * 0.65

            case "drift_out":
                turn_multiplier = 1.2
                self.car_max_speed = CAR_MAX_SPEED * 0.9

            case _:
                turn_multiplier = 1
                self.car_max_speed = CAR_MAX_SPEED * 1

        actual_turn = self.turn_speed * turn_multiplier

        # don't turn if we're not moving
        # because how on earth could we turn if we are not moving
        if self.speed > CAR_TURN_THRESHOLD:
            self.angle += actual_turn * dt

        # movement

        # drift stuff
        if self.is_drifting() and self.speed > CAR_SPEED_DRIFT_THRESHOLD:
            self.time_spent_drifting += dt * (1 if self.turning == "drift_in" else 0)

            self.time_spent_drifting = min(
                CAR_DRIFT_BOOST_TIME[2] + 0.4, self.time_spent_drifting
            )

            self.time_spent_drifting = max(0, self.time_spent_drifting)

            self.add_trail()
            target_offset = -90
            lerp_speed = 5.0
        else:
            target_offset = 0.0
            lerp_speed = 7.0

        self.visual_offset += (target_offset - self.visual_offset) * lerp_speed * dt
        self.display_angle = self.angle + self.visual_offset

        if self.post_drift_time > 0:
            self.post_drift_time -= dt
            self.post_drift_time = max(0, self.post_drift_time)
            self.emit_sparks(True)

        # holy shit make this a function ffs
        if self.health != 0:
            self.frame_num = (round((self.display_angle % 360) / 7.5) + 36) % 48
        else:
            self.frame_num = (round((self.display_angle % 360) / 45) + 6) % 8

        # evil hack so we are like above shit when we jump
        if self.z_pos > 0:
            self.group.change_layer(self, 4)
        # if we aren't colliding, we should stay on top of the obstacle
        elif not self.colliding:
            self.group.change_layer(self, 3)

        if self.is_drifting():
            self.emit_sparks()

        if self.did_just_land():
            self.land_sound.play()
            self.add_cloud()

        self.invuln_time -= dt
        self.invuln_time = max(0, self.invuln_time)

        self.collision_sound_timer -= dt
        self.collision_sound_timer = max(0, self.collision_sound_timer)

        # Low health smoke effect
        if self.health == 1:
            self.smoke_timer += dt
            # Emit smoke slightly less frequently
            smoke_delay = max(0.025, 0.15 - (self.speed / self.car_max_speed) * 0.1)
            if self.smoke_timer > smoke_delay:
                self.smoke_timer = 0

                # Alternate between dark smoke, fire, white smoke, and grey smoke
                r = random.random()
                if r < 0.3:
                    colors = [(100, 100, 100), (50, 50, 50), (20, 20, 20)]  # Dark
                elif r < 0.5:
                    colors = [
                        (255, 255, 255),
                        (220, 220, 220),
                        (200, 200, 200),
                    ]  # White
                elif r < 0.7:
                    colors = [(150, 150, 150), (120, 120, 120), (100, 100, 100)]  # Grey
                elif r < 0.9:
                    colors = [(255, 200, 0), (255, 100, 0), (255, 50, 0)]  # Fire
                else:
                    colors = [(80, 80, 80), (60, 60, 60), (40, 40, 40)]  # Soot

                offset = Vector2(
                    random.uniform(-10, 10), random.uniform(-10, 10)
                ).rotate(self.display_angle)
                # Shift slightly forward to engine bay area (Vector2(0, -15) is forward)
                forward_shift = Vector2(0, -15).rotate(self.display_angle)

                # Apply z_pos and forward shift
                pos = self.position + offset + Vector2(0, -self.z_pos) + forward_shift
                vel = Vector2(random.uniform(-12, 12), random.uniform(-25, -8)).rotate(
                    self.display_angle
                )
                # Slightly smaller size
                puff = FirePuff(
                    pos, vel, random.uniform(2, 5), colors, random.uniform(0.6, 1.2)
                )
                self.game.group.add(puff)

        self.update_shot(dt)
        self.update_gas(dt)
        self.update_sparks(dt)
        self.update_collision()
        self.update_position(dt)
