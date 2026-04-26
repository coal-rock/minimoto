import sys
import pygame as pg

from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent.parent

ASSETS_DIR = BASE_DIR / "assets"

WIDTH = 36 * 16
HEIGHT = 27 * 16


def get_dir(filename: str) -> str:
    return str(ASSETS_DIR / filename)


def load_image(filename: str) -> pg.Surface:
    return pg.image.load(str(ASSETS_DIR / filename))


def load_sound(filename: str, vol: float) -> pg.mixer.Sound:
    sound = pg.mixer.Sound(get_dir(filename))
    sound.set_volume(vol)
    return sound


def play_sound(sound: pg.mixer.Sound, volume: float = -1.0, vary_pitch: bool = True):
    """Plays a sound with optional volume override and pitch variation (pseudo-variation via multiple channels if needed, or just play)."""
    if volume >= 0:
        sound.set_volume(volume)
    sound.play()


def get_white_surface(surface: pg.Surface) -> pg.Surface:
    """Returns a white silhouette of the given surface."""
    w, h = surface.get_size()
    white_surf = pg.Surface((w, h), pg.SRCALPHA)
    mask = pg.mask.from_surface(surface)
    white_surf.blit(mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)), (0, 0))
    return white_surf


def exit_game():
    pg.event.post(pg.event.Event(pg.QUIT))
