from helper import load_image
from enemy import Enemy

FRAMES = []
FRAMES.append(load_image(f"small_zombie/front1.png"))
FRAMES.append(load_image(f"small_zombie/front2.png"))

FRAMES.append(load_image(f"small_zombie/back1.png"))
FRAMES.append(load_image(f"small_zombie/back2.png"))

ENEMY_SPEED = 70
KNOCKBACK_STRENGTH = 300


class SmallZombie(Enemy):
    raw_frames = FRAMES
    speed = 40
    knockback_strength = 350
    animation_speed = 4

    pass
