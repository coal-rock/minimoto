from helper import load_image
from enemy import Enemy

FRAMES = []
FRAMES.append(load_image(f"big_zombie/front1.png"))
FRAMES.append(load_image(f"big_zombie/front2.png"))

FRAMES.append(load_image(f"big_zombie/back1.png"))
FRAMES.append(load_image(f"big_zombie/back2.png"))


class BigZombie(Enemy):
    raw_frames = FRAMES
    speed = 70
    knockback_strength = 200
    animation_speed = 7
    health = 3
    skull_drop_rate = 0.4
