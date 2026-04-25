import pygame as pg

from pathlib import Path

CURRENT_DIR = Path(__file__).parent.parent
ASSETS_DIR = CURRENT_DIR / "assets"

WIDTH = 36 * 16
HEIGHT = 27 * 16


def load_image(filename: str) -> pg.Surface:
    return pg.image.load(str(ASSETS_DIR / filename))
