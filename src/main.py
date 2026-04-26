import pygame as pg

from helper import *
from game import Game


def main() -> None:
    pg.init()
    pg.font.init()
    pg.display.set_caption("MiniMoto")
    
    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED)
    
    icon = load_image("car/car000.png").convert_alpha()
    icon = icon.subsurface(icon.get_bounding_rect())
    pg.display.set_icon(icon)

    try:
        game = Game(screen)
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
