import pygame as pg

from helper import *
from game import Game


def main() -> None:
    pg.init()
    pg.font.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED)

    try:
        game = Game(screen)
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
