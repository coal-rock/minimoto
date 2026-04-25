from pygame.locals import SRCALPHA
import pygame as pg
from pygame.math import Vector2
from pyscroll.group import PyscrollGroup

from typing import Literal
from functools import lru_cache

from helper import *
from spark import Spark
from trail import Trail

CAR_MAX_SPEED = 400
CAR_DECCEL_SPEED = 450
CAR_ACCEL_SPEED = 300
CAR_DECCEL_SPEED = 450

CAR_INITIAL_TURN_SPEED = 600
CAR_TURN_ACCEL = 300
CAR_TURN_DECCEL = 350
CAR_MAX_TURN_SPEED = 12 * 12
CAR_TURN_THRESHOLD = 30

CAR_SPEED_DRIFT_THRESHOLD = 200
CAR_DRIFT_BOOST = [100, 150, 200]
CAR_DRIFT_POST_TIME = [0.2, 0.5, 0.7]
CAR_DRIFT_BOOST_TIME = [0.7, 1.4, 2.3]


class Car(pg.sprite.Sprite):
    angle: float
    display_angle: float
    speed: float
    turn_speed: float
    direction: Vector2
    position: Vector2
    old_position: Vector2
    time_spent_drifting: float
    post_drift_time: float
    car_max_speed: float
    group: PyscrollGroup

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
    last_z_pos: float
    colliding: bool

    image: pg.Surface
    rect: pg.Rect
    screen: pg.Surface

    # neither of these are offset by world pos
    # collision mask
    mask: pg.Mask
    # collision rect
    body: pg.Rect

    def __init__(self, group: PyscrollGroup, screen: pg.Surface) -> None:
        super().__init__()
        self._layer = 2
        self.car_max_speed = CAR_MAX_SPEED

        self.frames = []
        for i in range(0, 48):
            self.frames.append(load_image(f"car/car{i:03}.png").convert_alpha())

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
        self.old_z_pos = 0
        self.z_velocity = 0
        self.colliding = False

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
        return ((round((self.display_angle % 360) / 7.5)) % 48) * 7.5

    def get_rotated_pos(self, pos: Vector2) -> Vector2:
        body_pivot = Vector2(self.image.get_width() // 2, self.image.get_height() // 2)
        offset_pos = pos - body_pivot
        rotated_offset_pos = offset_pos.rotate(self.display_angle)
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

    def draw(self) -> None:
        self.image.fill((0, 0, 0, 0))

        # offset draw pos by jump
        draw_pos = (100, 100 - self.z_pos)

        # hack
        self.image.blit(self.frames[self.frame_num], draw_pos)

    def update_collision(self):
        car_collision_rect = pg.Rect(135, 136, 30, 40)
        body, body_surface = self.get_rotated_rect(car_collision_rect)

        # compute mask
        mask_surface = pg.Surface((300, 300), SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))
        mask_surface.blit(body_surface, body.topleft)
        self.mask = pg.mask.from_surface(mask_surface, 100)

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

    def is_drifting(self):
        return self.turning == "drift_in" or self.turning == "drift_out"

    def start_drift_out(self):
        self.turning = "drift_out"

    def start_drift_in(self):
        self.turning = "drift_in"

    def end_drift(self):
        self.turning = None

    # am i currently touching the ground
    def is_grounded(self) -> bool:
        return self._layer == 2 and self.z_pos == 0

    # am i currently touching a raised object
    def is_landed(self) -> bool:
        return self._layer == 4 and self.z_pos == 0

    # am i on or over an obstacle
    def over_obstacle(self):
        return self._layer == 4 and self.colliding

    def update(self, dt: float) -> None:
        self.time += dt

        deccel_speed = (
            CAR_DECCEL_SPEED * 0.8 if self.post_drift_time != 0 else CAR_DECCEL_SPEED
        )

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

        # holy shit make this a function ffs
        self.frame_num = (round((self.display_angle % 360) / 7.5) + 36) % 48

        # evil hack so we are like above shit when we jump
        if self.z_pos > 0:
            self.group.change_layer(self, 4)
        # if we aren't colliding, we should stay on top of the obstacle
        elif not self.colliding:
            self.group.change_layer(self, 2)

        self.update_collision()
