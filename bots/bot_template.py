"""
GitWars - Bot Template
======================
CONSOLE Tank Tournament

This is your STARTER CODE! Edit this file to control your tank.
Read the comments carefully to understand the API.

Your tank will call your update() function every frame.
You must return an action tuple: (ACTION, PARAMETER)

ACTIONS:
--------
("MOVE", (dx, dy))   - Move in direction (dx, dy). Values are normalized.
                       Example: ("MOVE", (1, 0)) = move right
                       Example: ("MOVE", (0, -1)) = move up
                       Example: ("MOVE", (-1, 1)) = move down-left

("SHOOT", angle)     - Fire a bullet at the given angle (in degrees).
                       Example: ("SHOOT", 0) = shoot right
                       Example: ("SHOOT", 90) = shoot down
                       Example: ("SHOOT", 180) = shoot left

("STOP", None)       - Stop moving, stay in place.

CONTEXT DICTIONARY:
-------------------
The engine passes you a `context` dictionary every frame with this structure:

context = {
    "me": {
        "x": float,      # Your tank's X position
        "y": float,      # Your tank's Y position  
        "angle": float,  # Your tank's facing angle (degrees)
        "health": int,   # Your current health (0-100)
        "ammo": int,     # Your remaining bullets
        "coins": int     # Coins collected (Mode 1 only)
    },
    "enemies": [
        {"x": float, "y": float, "id": int},  # List of enemy positions
        ...
    ],
    "coins": [
        {"x": float, "y": float},  # List of coin positions (Mode 1 only)
        ...
    ],
    "walls": [
        {"x": float, "y": float, "width": float, "height": float},  # Walls
        ...
    ],
    "bullets": [
        {"x": float, "y": float, "vx": float, "vy": float},  # Enemy bullets
        ...
    ],
    "game_mode": int,     # 1=Scramble, 2=Labyrinth, 3=Duel
    "time_left": float    # Time remaining in seconds
}

TIPS:
-----
1. Don't try to modify the context - it's a read-only copy!
2. Your update() function has a 100ms time limit - keep it fast!
3. If your code crashes, your tank will freeze but the game continues.
4. Use math.atan2(dy, dx) to calculate angles to targets.
5. In Mode 1 (Scramble), bullets only knock back - they don't damage!

HELPER FUNCTIONS:
-----------------
Below are some useful helper functions you can use or modify.
"""

import math
import random


def distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def angle_to(x1, y1, x2, y2):
    """Calculate angle from point (x1, y1) to point (x2, y2) in degrees."""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def find_nearest(my_x, my_y, targets):
    """
    Find the nearest target from a list of targets.
    Each target must have 'x' and 'y' keys.
    Returns (target, distance) or (None, float('inf')) if list is empty.
    """
    nearest = None
    min_dist = float('inf')
    
    for target in targets:
        dist = distance(my_x, my_y, target["x"], target["y"])
        if dist < min_dist:
            min_dist = dist
            nearest = target
    
    return nearest, min_dist


def will_bullet_hit_me(my_x, my_y, bullet, danger_radius=50):
    """
    Predict if a bullet will come close to your position.
    Returns True if bullet is dangerous.
    """
    # Future position of bullet
    future_x = bullet["x"] + bullet["vx"] * 10
    future_y = bullet["y"] + bullet["vy"] * 10
    
    # Check if bullet path intersects with our position
    dist_now = distance(my_x, my_y, bullet["x"], bullet["y"])
    dist_future = distance(my_x, my_y, future_x, future_y)
    
    # Bullet is approaching if it gets closer
    return dist_future < dist_now and dist_now < danger_radius * 2


# =============================================================================
# YOUR CODE STARTS HERE!
# =============================================================================

def update(context):
    """
    This function is called every frame.
    
    Args:
        context: Dictionary containing game state (see above for structure)
    
    Returns:
        (ACTION, PARAMETER) tuple - your tank's action for this frame
    """
    
    # Get my tank's info
    me = context["me"]
    my_x = me["x"]
    my_y = me["y"]
    
    enemies = context["enemies"]
    coins = context["coins"]
    bullets = context["bullets"]
    game_mode = context["game_mode"]
    
    # =========================================================================
    # EXAMPLE STRATEGY: This is a basic bot, modify it!
    # =========================================================================
    
    # Priority 1: Dodge incoming bullets
    for bullet in bullets:
        if will_bullet_hit_me(my_x, my_y, bullet):
            # Dodge perpendicular to bullet direction
            dodge_angle = math.degrees(math.atan2(bullet["vy"], bullet["vx"])) + 90
            dx = math.cos(math.radians(dodge_angle))
            dy = math.sin(math.radians(dodge_angle))
            return ("MOVE", (dx, dy))
    
    # Game Mode specific behavior
    if game_mode == 1:  # THE SCRAMBLE - Collect coins!
        if coins:
            nearest_coin, dist = find_nearest(my_x, my_y, coins)
            if nearest_coin:
                # Move toward nearest coin
                dx = nearest_coin["x"] - my_x
                dy = nearest_coin["y"] - my_y
                return ("MOVE", (dx, dy))
    
    elif game_mode in [2, 3]:  # LABYRINTH or DUEL - Fight!
        if enemies and me["ammo"] > 0:
            # Find and attack nearest enemy
            nearest_enemy, dist = find_nearest(my_x, my_y, enemies)
            if nearest_enemy:
                if dist < 200:
                    # Close enough - SHOOT!
                    target_angle = angle_to(my_x, my_y, nearest_enemy["x"], nearest_enemy["y"])
                    return ("SHOOT", target_angle)
                else:
                    # Too far - move closer
                    dx = nearest_enemy["x"] - my_x
                    dy = nearest_enemy["y"] - my_y
                    return ("MOVE", (dx, dy))
    
    # Default: Wander around
    angle = random.uniform(0, 360)
    dx = math.cos(math.radians(angle))
    dy = math.sin(math.radians(angle))
    return ("MOVE", (dx, dy))
