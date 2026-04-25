from pygame.locals import SRCALPHA
import pygame as pg
from pygame.math import Vector2
from pyscroll.group import PyscrollGroup

from typing import Literal

from helper import *
from spark import Spark

CAR_MAX_SPEED = 400


class Car(pg.sprite.Sprite):
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
