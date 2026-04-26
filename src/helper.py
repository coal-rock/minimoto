import pygame as pg

from pathlib import Path

CURRENT_DIR = Path(__file__).parent.parent
ASSETS_DIR = CURRENT_DIR / "assets"

WIDTH = 36 * 16
HEIGHT = 27 * 16

def get_dir(filename: str) -> str:
    return str(ASSETS_DIR / filename)

def load_image(filename: str) -> pg.Surface:
    return pg.image.load(str(ASSETS_DIR / filename))


def load_sound(filename: str, vol: float) -> pg.mixer.Sound:
    sound = pg.mixer.Sound(str(ASSETS_DIR / filename))
    return sound


def exit_game():
    pg.event.post(pg.event.Event(pg.QUIT))
