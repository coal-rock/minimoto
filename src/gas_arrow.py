import pygame as pg
from pygame.math import Vector2
from helper import load_image, get_dir


class GasArrow(pg.sprite.Sprite):
    def __init__(self, car, group, gas_cans_group):
        self._layer = 20
        super().__init__(group)

        self.car = car
        self.gas_cans_group = gas_cans_group
        self.arrow_image = load_image("arrow.png").convert_alpha()

        group.change_layer(self, self._layer)

        self.font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"), 16)

        self.radius = 120
        self.image = pg.Surface((0, 0), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.current_angle = 0

        self.last_nearest_gas = None
        self.displayed_distance_m = 0
        self.text_side_y = -1
        self.alpha = 0

    def update(self, dt):
        if self.car.game.state != "RUNNING":
            self.image = pg.Surface((0, 0), pg.SRCALPHA)
            return

        active_gas_cans = [g for g in self.gas_cans_group if g.alive()]

        target_alpha = 0
        nearest_gas = None
        actual_dist_m = 0

        car_pos = self.car.position
        visual_center = Vector2(self.car.rect.center) + Vector2(0, -self.car.z_pos)

        if active_gas_cans:
            nearest_gas = min(active_gas_cans, key=lambda g: car_pos.distance_to(g.pos))
            actual_dist_m = car_pos.distance_to(nearest_gas.pos) / 16
            if actual_dist_m > 20:
                target_alpha = 255

        alpha_speed = 600 if target_alpha == 0 else 400
        if self.alpha < target_alpha:
            self.alpha = min(target_alpha, self.alpha + alpha_speed * dt)
        elif self.alpha > target_alpha:
            self.alpha = max(target_alpha, self.alpha - alpha_speed * dt)

        if self.alpha <= 0:
            self.image = pg.Surface((0, 0), pg.SRCALPHA)
            self.last_nearest_gas = nearest_gas  # Keep track even when hidden
            return

        direction = nearest_gas.pos - car_pos
        if direction.length() > 0:
            target_angle = -Vector2(0, -1).angle_to(direction)
        else:
            target_angle = 0

        angle_diff = (target_angle - self.current_angle + 180) % 360 - 180
        self.current_angle += angle_diff * 10 * dt
        self.current_angle %= 360

        if nearest_gas != self.last_nearest_gas:
            self.displayed_distance_m = round(actual_dist_m)
            self.last_nearest_gas = nearest_gas
        elif abs(actual_dist_m - self.displayed_distance_m) > 0.6:
            self.displayed_distance_m = round(actual_dist_m)

        orbit_vec = Vector2(0, -1).rotate(-self.current_angle)
        arrow_center = visual_center + orbit_vec * self.radius

        if self.text_side_y == -1 and orbit_vec.y > 0.4:
            self.text_side_y = 1
        elif self.text_side_y == 1 and orbit_vec.y < -0.4:
            self.text_side_y = -1

        surf_w, surf_h = 100, 100
        self.image = pg.Surface((surf_w, surf_h), pg.SRCALPHA)

        rotated_arrow = pg.transform.rotate(self.arrow_image, self.current_angle)
        arrow_rect = rotated_arrow.get_rect(center=(surf_w // 2, surf_h // 2))
        self.image.blit(rotated_arrow, arrow_rect)

        dist_str = f"{self.displayed_distance_m}m"
        dist_text = self.font.render(dist_str, True, (255, 255, 255))
        shadow_text = self.font.render(dist_str, True, (0, 0, 0))

        text_y_offset = 25 * self.text_side_y
        text_pos = (
            surf_w // 2 - dist_text.get_width() // 2,
            surf_h // 2 + text_y_offset - dist_text.get_height() // 2,
        )

        self.image.blit(shadow_text, (text_pos[0] + 1, text_pos[1] + 1))
        self.image.blit(dist_text, text_pos)

        # smooth alpha (ruby)
        self.image.set_alpha(int(self.alpha))
        self.rect = self.image.get_rect(
            center=(round(arrow_center.x), round(arrow_center.y))
        )
