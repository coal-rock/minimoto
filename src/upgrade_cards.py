from typing import Literal
import pygame as pg
from pygame.math import Vector2
from car import Car
from helper import *
import random
import math


class UICard:
    def __init__(
        self,
        state: Literal["selected", "unselected"],
        pos: Literal["left", "right"],
        upgrade_type: Literal[
            "jump", "fire_rate", "health", "knockback", "projectiles", "boost", "gas"
        ] = "jump",
    ):

        self.state: Literal["selected", "unselected"] = state
        self.pos = pos
        self.upgrade_type = upgrade_type
        
        self.image = load_image(f"upgrade_menu/unselected_{self.pos}.png")
        
        self.text = ""
        self.scale = 1.0

        class DummyGame:
            def __init__(self):
                self.shake_duration = 0
                self.shake_intensity = 0

                class DummyGroup(pg.sprite.Group):
                    def change_layer(self, sprite, layer):
                        pass

                self.group = DummyGroup()
                self.state = "UPGRADE"

        self.game = DummyGame()
        self.car = Car(
            self.game.group, pg.Surface((300, 300)), pg.sprite.Group(), self.game
        )
        self.car.position = Vector2(150, 150)
        self.car.gas = 100
        self.car.health = 3

        self.font = pg.font.Font(get_dir("fonts/BoldPixels.ttf"), 20)

        self.timer = 0.0
        self.progress = 0.0
        self.heart_ui = load_image("heart/ui.png")
        self.gas_ui = load_image("gas_can/ui.png")

        self.demo_objects = []

        self.car.angle = 90
        if self.upgrade_type == "jump":
            self.jump_card_update(0)
        elif self.upgrade_type == "fire_rate":
            self.fire_rate_update(0)
        elif self.upgrade_type == "health":
            self.health_update(0)
        elif self.upgrade_type == "knockback":
            self.knockback_update(0)
        elif self.upgrade_type == "projectiles":
            self.projectiles_update(0)
        elif self.upgrade_type == "boost":
            self.boost_update(0)
        elif self.upgrade_type == "gas":
            self.gas_update(0)

    def set_progress(self, progress: float):
        self.progress = progress

    def reset_progress(self):
        self.progress = 0.0

    def jump_card_update(self, dt: float):
        self.text = "JUMP +1"

        self.car.angle = 90
        self.timer += dt
        if self.timer > 1:
            self.car.jump()
            self.timer = 0

        self.car.speed = 0
        self.car.update(dt)
        self.car.position = Vector2(150, 150)
        self.car.rect.center = (150, 150)

    def fire_rate_update(self, dt: float):
        self.text = "FIRE RATE +1"

        self.car.angle = 90
        self.timer += dt
        if self.timer > 1.5:
            self.car.add_bullet(Vector2(1000, 150))
            self.timer = 0

        self.car.speed = 0
        self.car.update(dt)
        self.car.position = Vector2(150, 150)
        self.car.rect.center = (150, 150)

    def health_update(self, dt: float):
        self.text = "MAX HEALTH +1"
        self.car.angle = 90
        self.timer += dt

        if self.timer > 2.0:
            self.timer = 0

        self.car.speed = 0
        self.car.update(dt)
        self.car.position = Vector2(150, 150)
        self.car.rect.center = (150, 150)

    def knockback_update(self, dt: float):
        self.text = "KNOCKBACK +1"
        self.car.angle = 90
        self.timer += dt

        if self.timer > 1:
            self.car.jump()
            self.timer = 0

        if self.car.did_just_land():
            self.demo_objects.append({"type": "shockwave", "radius": 10, "alpha": 255})

        for obj in self.demo_objects[:]:
            if obj["type"] == "shockwave":
                obj["radius"] += 200 * dt
                obj["alpha"] -= 400 * dt
                if obj["alpha"] <= 0:
                    self.demo_objects.remove(obj)

        self.car.speed = 0
        self.car.update(dt)
        self.car.position = Vector2(150, 150)
        self.car.rect.center = (150, 150)

    def projectiles_update(self, dt: float):
        self.text = "BULLETS +1"
        self.car.angle = 90
        self.timer += dt

        if self.timer > 1.0:
            center_target = Vector2(1000, 150)
            self.car.add_bullet(center_target)
            self.car.add_bullet(center_target + Vector2(0, -100))
            self.car.add_bullet(center_target + Vector2(0, 100))
            self.timer = 0

        self.car.speed = 0
        self.car.update(dt)
        self.car.position = Vector2(150, 150)
        self.car.rect.center = (150, 150)

    def boost_update(self, dt: float):
        self.text = "BOOST +1"
        self.car.angle = 90
        self.timer += dt

        if self.timer < 1.0:
            self.car.speed = 200
            self.car.post_drift_time = 0
            self.car.time_spent_drifting = 0
        elif self.timer < 2.5:
            self.car.speed = 600
            self.car.post_drift_time = 1.0
            self.car.time_spent_drifting = 2.5  # purple sparks
        else:
            self.timer = 0

        self.car.update(dt)
        self.car.position = Vector2(150, 150)
        self.car.rect.center = (150, 150)
        self.car.turning = None

    def gas_update(self, dt: float):
        self.text = "EFFICIENCY +1"
        self.car.angle = 90
        self.timer += dt

        if self.timer > 4.0:
            self.timer = 0

        self.car.speed = 200
        self.car.accelerating = True
        self.car.update(dt)
        self.car.position = Vector2(150, 150)
        self.car.rect.center = (150, 150)

    def upgrade(self, car: Car):
        if self.upgrade_type == "jump":
            car.jump_force += 25
        elif self.upgrade_type == "fire_rate":
            car.shot_delay *= 0.9
        elif self.upgrade_type == "health":
            car.max_health += 1
        elif self.upgrade_type == "knockback":
            car.knockback_strength *= 1.1
        elif self.upgrade_type == "projectiles":
            car.num_bullets += 1
        elif self.upgrade_type == "boost":
            car.boost_scale *= 1.1
        elif self.upgrade_type == "gas":
            car.gas_drain_mult *= 0.9

    def update(self, dt: float):
        if self.state != "selected":
            self.timer = 0.5
            self.demo_objects = []
            self.car.speed = 0
            self.car.z_pos = 0
            self.car.z_velocity = 0
            self.car.angle = 90
            self.car.position = Vector2(150, 150)
            self.car.rect.center = (150, 150)
            self.car.turning = None
            self.car.post_drift_time = 0
            for sprite in self.car.group:
                if sprite != self.car:
                    sprite.kill()
            return

        if self.upgrade_type == "jump":
            self.jump_card_update(dt)
        elif self.upgrade_type == "fire_rate":
            self.fire_rate_update(dt)
        elif self.upgrade_type == "health":
            self.health_update(dt)
        elif self.upgrade_type == "knockback":
            self.knockback_update(dt)
        elif self.upgrade_type == "projectiles":
            self.projectiles_update(dt)
        elif self.upgrade_type == "boost":
            self.boost_update(dt)
        elif self.upgrade_type == "gas":
            self.gas_update(dt)

        self.car.group.update(dt)

    def draw_demo_extras(self, surface, effect_offset, behind=True):
        if not behind:
            if self.upgrade_type == "health":
                alpha = abs(math.sin(self.timer * math.pi)) * 255
                temp_heart = self.heart_ui.copy()
                temp_heart.set_alpha(alpha)
                draw_pos = (150 - temp_heart.get_width() // 2, 90)
                
                mask = pg.mask.from_surface(temp_heart)
                shadow = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                shadow.set_alpha(alpha)
                surface.blit(shadow, (draw_pos[0] + 6, draw_pos[1] + 6))
                surface.blit(temp_heart, draw_pos)

        if behind:
            if self.upgrade_type == "knockback":
                for obj in self.demo_objects:
                    if obj["type"] == "shockwave":
                        pg.draw.circle(
                            surface,
                            (255, 255, 255, obj["alpha"]),
                            (150 + effect_offset.x, 170 + effect_offset.y),
                            int(obj["radius"]),
                            2,
                        )

            # Draw car shadow
            car_draw_pos = (self.car.rect.x + effect_offset.x, self.car.rect.y + effect_offset.y)
            mask = pg.mask.from_surface(self.car.frames[self.car.frame_num])
            shadow = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            # The car frame is drawn at (100, 100 - self.z_pos), we need to match this offset for the shadow mask
            draw_pos = (100 + effect_offset.x, 100 - self.car.z_pos + effect_offset.y)
            surface.blit(shadow, (draw_pos[0] + 6, draw_pos[1] + 6))

        if not behind:
            if self.upgrade_type == "gas":
                bar_width = 60
                bar_height = 8
                fill_width = bar_width * (1.0 - (self.timer / 4.0))
                pg.draw.rect(surface, (50, 50, 50), (120, 100, bar_width, bar_height))
                pg.draw.rect(surface, (255, 200, 0), (120, 100, fill_width, bar_height))
                
                draw_pos = (120 - 25, 100 - 8)
                mask = pg.mask.from_surface(self.gas_ui)
                shadow = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                surface.blit(shadow, (draw_pos[0] + 6, draw_pos[1] + 6))
                surface.blit(self.gas_ui, draw_pos)

        for sprite in self.car.group:
            if sprite != self.car:
                layer = getattr(sprite, "_layer", 0)
                draw_pos = sprite.rect.topleft + effect_offset
                
                if behind and layer < 3:
                    mask = pg.mask.from_surface(sprite.image)
                    shadow = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                    surface.blit(shadow, (draw_pos[0] + 6, draw_pos[1] + 6))
                    surface.blit(sprite.image, draw_pos)
                elif not behind and layer >= 3:
                    mask = pg.mask.from_surface(sprite.image)
                    shadow = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                    surface.blit(shadow, (draw_pos[0] + 6, draw_pos[1] + 6))
                    surface.blit(sprite.image, draw_pos)

    def draw(self, surface: pg.Surface):
        center = surface.get_rect().center
        image = self.image

        if self.pos == "left":
            card_pos = (
                center[0] - (image.get_width() / 2) - 100,
                center[1] - (image.get_height() / 2) + 20,
            )
        else:
            card_pos = (
                center[0] - (image.get_width() / 2) + 100,
                center[1] - (image.get_height() / 2) + 20,
            )

        if self.state == "selected":
            mask = pg.mask.from_surface(image)
            shadow = mask.to_surface(setcolor=(0, 0, 0, 150), unsetcolor=(0, 0, 0, 0))
            surface.blit(shadow, (card_pos[0] + 10, card_pos[1] + 10))

        surface.blit(image, card_pos)

        effect_offset = Vector2(-7, 3)

        self.car.image.fill((0, 0, 0, 0))
        self.draw_demo_extras(self.car.image, effect_offset, behind=True)
        self.car.draw(clear=False, offset=effect_offset)
        self.draw_demo_extras(self.car.image, effect_offset, behind=False)

        car_draw_pos = (
            card_pos[0] + (image.get_width() / 2) - 150,
            card_pos[1] + (image.get_height() / 2) - 150 - 20,
        )

        old_clip = surface.get_clip()
        surface.set_clip(pg.Rect(card_pos, image.get_size()))
        surface.blit(self.car.image, car_draw_pos)
        surface.set_clip(old_clip)

        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.shadow_surface = self.font.render(self.text, True, (0, 0, 0))

        text_pos = (
            card_pos[0] + (image.get_width() / 2) - (self.text_surface.get_width() / 2),
            card_pos[1] + image.get_height() - 44,
        )
        surface.blit(self.shadow_surface, (text_pos[0] + 2, text_pos[1] + 2))
        surface.blit(self.text_surface, text_pos)

        if self.state == "selected" and self.progress > 0:
            delay = 0.15
            if self.progress > delay:
                adjusted_progress = (self.progress - delay) / (1.0 - delay)
                rect = pg.Rect(card_pos[0], card_pos[1], image.get_width(), image.get_height())
                points = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft, rect.topleft]
                perimeter = 2 * rect.width + 2 * rect.height
                target_len = perimeter * adjusted_progress

                curr_len = 0
                for i in range(4):
                    p1 = Vector2(points[i])
                    p2 = Vector2(points[i+1])
                    seg_len = p1.distance_to(p2)

                    if curr_len + seg_len <= target_len:
                        pg.draw.line(surface, (255, 255, 255), points[i], points[i+1], 4)
                        curr_len += seg_len
                    else:
                        rem = target_len - curr_len
                        ratio = rem / seg_len
                        p_end = p1.lerp(p2, ratio)
                        pg.draw.line(surface, (255, 255, 255), points[i], (int(p_end.x), int(p_end.y)), 4)
                        break
