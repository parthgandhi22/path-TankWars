"""
GitWars - My Bot (Beginner-Friendly Strategy)
==============================================
CONSOLE Tank Tournament - Example Bot

This is a 'Smart Bot' that demonstrates how to use the GitWars API.
A beginner should read these comments to understand how to read the 
game state and make decisions for their tank.

RULES FOR YOUR BOT:
1. Don't modify the 'context' - it's a read-only copy!
2. You have a 100ms time limit per frame.
3. If your code crashes, your tank will freeze.
"""

import math
import random

# --- HELPER FUNCTIONS ---
# These functions handle common math tasks so the main logic stays clean.

def distance(x1, y1, x2, y2):
    """
    Calculates the straight-line distance between two points (x1, y1) and (x2, y2).
    Uses the Pythagorean theorem (A^2 + B^2 = C^2).
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def angle_to(x1, y1, x2, y2):
    """
    Calculates the angle (in degrees) from point 1 to point 2.
    Essential for aiming your barrel at a target.
    """
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def find_nearest(my_x, my_y, targets):
    """
    Searches through a list of 'targets' (like coins or enemies) and finds 
    the one closest to your current position.
    Returns: (nearest_object, distance_to_it)
    """
    nearest = None
    min_dist = float('inf') # Start with 'infinity'
    for target in targets:
        # Calculate distance to this specific target
        dist = distance(my_x, my_y, target["x"], target["y"])
        # If it's closer than the best we've seen so far, save it!
        if dist < min_dist:
            min_dist = dist
            nearest = target
    return nearest, min_dist


def is_bullet_dangerous(my_x, my_y, bullet, threshold=100):
    """
    Checks if a bullet is likely to hit you.
    A bullet is 'dangerous' if it is:
    1. Nearby (closer than 'threshold' pixels)
    2. Moving TOWARD you (not away from you)
    """
    # Check current distance
    dist = distance(my_x, my_y, bullet["x"], bullet["y"])
    if dist > threshold:
        return False # Too far away to care
    
    # Check direction: Does the bullet's velocity point toward our position?
    # We use 'dot product' math to check alignment of vectors.
    to_us_x = my_x - bullet["x"]
    to_us_y = my_y - bullet["y"]
    
    # If dot > 0, the bullet is moving toward us.
    dot = to_us_x * bullet["vx"] + to_us_y * bullet["vy"]
    return dot > 0


def update(context):
    """
    MAIN Logic: Runs every frame (60 times per second).
    You must return an action like ("MOVE", (dx, dy)) or ("SHOOT", angle).
    """
    
    # 1. EXTRACT DATA: Get info about ourselves and the world
    me = context["me"]           # Your tank's info (x, y, health, ammo)
    my_x, my_y = me["x"], me["y"] # Simplified variables for position
    enemies = context["enemies"] # List of other tanks
    coins = context["coins"]     # List of coins (Round 1 only)
    bullets = context["bullets"] # List of all flying bullets
    game_mode = context["game_mode"] # 1: Scramble, 2: Labyrinth, 3: Duel
    
    # 2. PRIORITY 1 - DEFENSE: Dodge incoming bullets
    for bullet in bullets:
        # We look 120 pixels around us for threats
        if is_bullet_dangerous(my_x, my_y, bullet, 120):
            # Calculate an angle perpendicular (90 degrees) to the bullet's path
            # to sidestep the incoming shot.
            perp_angle = math.degrees(math.atan2(bullet["vy"], bullet["vx"])) + 90
            
            # Convert that angle into movement directions (X and Y)
            dx = math.cos(math.radians(perp_angle))
            dy = math.sin(math.radians(perp_angle))
            
            return ("MOVE", (dx, dy))
    
    # 3. PRIORITY 2 - OBJECTIVES: Round-specific goals
    
    # MODE 1: THE SCRAMBLE (Goal: Collect Coins)
    if game_mode == 1:
        if coins:
            # Find the closest coin
            nearest, dist = find_nearest(my_x, my_y, coins)
            if nearest:
                # OPTIONAL STRATEGY: Harass enemies near the coin
                # If an enemy is closer than us or within 200px, shoot to push them back
                for enemy in enemies:
                    enemy_dist = distance(enemy["x"], enemy["y"], nearest["x"], nearest["y"])
                    if enemy_dist < dist and distance(my_x, my_y, enemy["x"], enemy["y"]) < 200:
                        if me["ammo"] > 10:  # Only shoot if we have spare ammo
                            angle = angle_to(my_x, my_y, enemy["x"], enemy["y"])
                            return ("SHOOT", angle)
                
                # If no enemies to harass, move directly to the coin!
                dx = nearest["x"] - my_x
                dy = nearest["y"] - my_y
                return ("MOVE", (dx, dy))
    
    # MODE 2 & 3: COMBAT (Goal: Eliminate Enemies)
    else:
        # If no enemies are left, move to the center to stay safe from the zone
        if not enemies:
            center_x, center_y = 640, 360 # Middle of 1280x720 screen
            dx = center_x - my_x
            dy = center_y - my_y
            return ("MOVE", (dx, dy))
        
        # Find the nearest threat
        nearest_enemy, dist = find_nearest(my_x, my_y, enemies)
        
        if nearest_enemy:
            enemy_x = nearest_enemy["x"]
            enemy_y = nearest_enemy["y"]
            # Target the enemy's current position
            target_angle = angle_to(my_x, my_y, enemy_x, enemy_y)
            
            # A reference value for combat range (150 pixels)
            ideal_range = 150
            
            # SITUATION: Defensive (They are too close!)
            if dist < 80:
                if me["ammo"] > 0:
                    # Retreat angle is the opposite of the target angle (+180 degrees)
                    retreat_angle = target_angle + 180
                    dx = math.cos(math.radians(retreat_angle))
                    dy = math.sin(math.radians(retreat_angle))
                    
                    # Retreat while shooting back (70% chance to shoot)
                    if random.random() < 0.7:
                        return ("SHOOT", target_angle)
                    return ("MOVE", (dx, dy))
            
            # SITUATION: Offensive (In attack range!)
            elif dist < 250:
                if me["ammo"] > 0:
                    # Add a tiny bit of random 'spray' (+/- 5 degrees) to be unpredictable
                    aim_angle = target_angle + random.uniform(-5, 5)
                    return ("SHOOT", aim_angle)
            
            # SITUATION: Pursuit (Too far away!)
            else:
                # Move directly toward the enemy to close the distance
                dx = enemy_x - my_x
                dy = enemy_y - my_y
                return ("MOVE", (dx, dy))
    
    # 4. DEFAULT: Wander randomly
    # If none of the above logic triggers, move in a random direction so 
    # you aren't a sitting duck.
    angle = random.uniform(0, 360)
    return ("MOVE", (math.cos(math.radians(angle)), math.sin(math.radians(angle))))
