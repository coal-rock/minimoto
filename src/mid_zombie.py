from helper import load_image
from enemy import Enemy

FRAMES = []
FRAMES.append(load_image(f"mid_zombie/front1.png"))
FRAMES.append(load_image(f"mid_zombie/front2.png"))

FRAMES.append(load_image(f"mid_zombie/back1.png"))
FRAMES.append(load_image(f"mid_zombie/back2.png"))


class MidZombie(Enemy):
    raw_frames = FRAMES
    speed = 70
    knockback_strength = 300
    animation_speed = 7
    health = 2
    skull_drop_rate = 0.3
