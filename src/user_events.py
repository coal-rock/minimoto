from typing import Generator
import pygame

def __new_event_gen() -> Generator[int]:
    """
    Creates unique USEREVENT in pygame
    """
    cnt: int = 0
    while True:
        cnt += 1
        event = pygame.USEREVENT + cnt
        # Ensures event is allowed in event queue
        pygame.event.set_allowed(event)
        yield event

ne = __new_event_gen()

"""
To add new custom event, create new variable (all caps)
and set it equal to `next(ne)`.

To import, do `from user_events import *`
To post, add to event queue: pygame.event.post(`YOUR EVENT`)
To poll, check against pg.event.get().type (most likley in for loop)
"""

# MENU BUTTONS
START_GAME_BTN_UP = next(ne) 
SETTINGS_BTN_UP = next(ne)

