import pygame as pg
from helper import *
from settings import Setting

VEHICLES = {
    "car": ["default"],
    "sedan": ["black", "blue", "brown", "green", "magenta", "red", "white", "yellow"],
    "sport": ["black", "blue", "brown", "green", "magenta", "red", "white", "yellow"],
    "pickup": ["black", "blue", "brown", "green", "magenta", "red", "white", "yellow"],
    "musclecar": [
        "black",
        "blue",
        "brown",
        "green",
        "magenta",
        "red",
        "white",
        "yellow",
    ],
    "police": ["default"],
    "taxi": ["default"],
    "ambulance": ["default"],
    "supercar": [
        "black",
        "blue",
        "brown",
        "green",
        "magenta",
        "red",
        "white",
        "yellow",
    ],
    "suv": ["black", "blue", "brown", "green", "magenta", "red", "white", "yellow"],
    "jeep": ["black", "blue", "brown", "green", "magenta", "red", "white", "yellow"],
    "van": ["black", "blue", "brown", "green", "magenta", "red", "white", "yellow"],
}

VEHICLE_NAMES = list(VEHICLES.keys())


class VehicleSelector:
    def __init__(self, screen: pg.Surface, x, y, car):
        self.screen = screen
        self.x = x
        self.y = y
        self.car = car
        self.settings = Setting()

        self.current_vehicle_idx = VEHICLE_NAMES.index(self.settings.get_vehicle())
        self.current_color_idx = VEHICLES[
            VEHICLE_NAMES[self.current_vehicle_idx]
        ].index(self.settings.get_color())

        self.font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"), 16)

        self.update_selection()

        self.v_arrow_l_rect = pg.Rect(x, y, 32, 32)
        self.v_arrow_r_rect = pg.Rect(x + 200, y, 32, 32)
        self.c_arrow_l_rect = pg.Rect(x, y + 40, 32, 32)
        self.c_arrow_r_rect = pg.Rect(x + 200, y + 40, 32, 32)

        self.hidden = False

    def update_selection(self):
        v = VEHICLE_NAMES[self.current_vehicle_idx]
        c = VEHICLES[v][self.current_color_idx]
        self.settings.set_vehicle(v, c)
        if self.car:
            self.car.reload_assets()

    def next_vehicle(self):
        self.current_vehicle_idx = (self.current_vehicle_idx + 1) % len(VEHICLE_NAMES)
        self.current_color_idx = 0
        self.update_selection()

    def prev_vehicle(self):
        self.current_vehicle_idx = (self.current_vehicle_idx - 1) % len(VEHICLE_NAMES)
        self.current_color_idx = 0
        self.update_selection()

    def next_color(self):
        v = VEHICLE_NAMES[self.current_vehicle_idx]
        self.current_color_idx = (self.current_color_idx + 1) % len(VEHICLES[v])
        self.update_selection()

    def prev_color(self):
        v = VEHICLE_NAMES[self.current_vehicle_idx]
        self.current_color_idx = (self.current_color_idx - 1) % len(VEHICLES[v])
        self.update_selection()

    def click(self, x, y):
        if self.hidden:
            return

        if self.v_arrow_l_rect.collidepoint(x, y):
            self.prev_vehicle()
            return True
        if self.v_arrow_r_rect.collidepoint(x, y):
            self.next_vehicle()
            return True
        if self.c_arrow_l_rect.collidepoint(x, y):
            self.prev_color()
            return True
        if self.c_arrow_r_rect.collidepoint(x, y):
            self.next_color()
            return True
        return False

    def draw_arrow(self, rect, direction="right"):
        color = (255, 255, 255)
        if rect.collidepoint(pg.mouse.get_pos()):
            color = (255, 200, 0)

        padding = 6
        if direction == "right":
            points = [
                (rect.left + padding, rect.top + padding),
                (rect.right - padding, rect.centery),
                (rect.left + padding, rect.bottom - padding),
            ]
        else:
            points = [
                (rect.right - padding, rect.top + padding),
                (rect.left + padding, rect.centery),
                (rect.right - padding, rect.bottom - padding),
            ]
        pg.draw.polygon(self.screen, color, points)

    def draw_text_with_shadow(self, text_str, y_offset):
        text = self.font.render(text_str.upper(), False, (255, 255, 255))
        shadow = self.font.render(text_str.upper(), False, (0, 0, 0))

        text_rect = text.get_rect(center=(self.x + 116, self.y + y_offset + 16))

        self.screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
        self.screen.blit(text, text_rect)

    def draw(self):
        if self.hidden:
            return

        v = VEHICLE_NAMES[self.current_vehicle_idx]
        c = VEHICLES[v][self.current_color_idx]

        self.draw_arrow(self.v_arrow_l_rect, "left")
        self.draw_text_with_shadow(v, 0)
        self.draw_arrow(self.v_arrow_r_rect, "right")

        if len(VEHICLES[v]) > 1:
            self.draw_arrow(self.c_arrow_l_rect, "left")
            self.draw_text_with_shadow(c, 40)
            self.draw_arrow(self.c_arrow_r_rect, "right")
