#!/usr/bin/env python3
"""Debug A* attack positioning issue"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "engine"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

from src.stage_validator.pathfinding import StagePathfinder
from engine.models.stage import Stage
import yaml

def debug_astar_attack():
    """Debug why A* thinks attack is possible when it's not"""

    # Load stage
    with open("stages/generated_attack_2025.yml", "r") as f:
        stage_data = yaml.safe_load(f)

    stage = Stage(stage_data)
    pathfinder = StagePathfinder(stage, ["turn_left", "turn_right", "move", "attack", "see"])

    # Manually simulate the state just before Step 9 (attack)
    # After: turn_left, turn_left, move, turn_left, move, move, move, move
    initial_state = pathfinder._create_initial_state()

    # Apply actions step by step
    actions = ["turn_left", "turn_left", "move", "turn_left", "move", "move", "move", "move"]

    current_state = initial_state
    for i, action in enumerate(actions):
        print(f"Step {i+1}: {action}")
        print(f"  Before: Player({current_state.player_pos[0]},{current_state.player_pos[1]}){current_state.player_dir}")

        # Check enemy positions before action
        for enemy_id, enemy_state in current_state.enemies.items():
            print(f"  Enemy {enemy_id}: ({enemy_state.position[0]},{enemy_state.position[1]}){enemy_state.direction}, Alert={enemy_state.is_alert}")

        # Apply action
        current_state = pathfinder._apply_action(current_state, getattr(pathfinder.ActionType, action.upper()))

        print(f"  After: Player({current_state.player_pos[0]},{current_state.player_pos[1]}){current_state.player_dir}")

        # Check enemy positions after action
        for enemy_id, enemy_state in current_state.enemies.items():
            print(f"  Enemy {enemy_id}: ({enemy_state.position[0]},{enemy_state.position[1]}){enemy_state.direction}, Alert={enemy_state.is_alert}")

        print()

    # Now check if attack is possible
    print("=== ATTACK POSSIBILITY CHECK ===")
    print(f"Current player position: ({current_state.player_pos[0]},{current_state.player_pos[1]}){current_state.player_dir}")

    for enemy_id, enemy_state in current_state.enemies.items():
        print(f"Enemy {enemy_id}: ({enemy_state.position[0]},{enemy_state.position[1]}){enemy_state.direction}")

    # Check what _can_attack returns
    can_attack = pathfinder._can_attack(current_state)
    print(f"_can_attack result: {can_attack}")

    # Check attack target position
    dx, dy = pathfinder.directions[current_state.player_dir]
    target_x = current_state.player_pos[0] + dx
    target_y = current_state.player_pos[1] + dy
    print(f"Attack target position: ({target_x}, {target_y})")

    # Check if there's an enemy at target position
    for enemy_id, enemy_state in current_state.enemies.items():
        if enemy_state.position == (target_x, target_y):
            print(f"Enemy {enemy_id} found at target position!")
        else:
            print(f"Enemy {enemy_id} NOT at target position. Distance: {abs(enemy_state.position[0] - target_x) + abs(enemy_state.position[1] - target_y)}")

if __name__ == "__main__":
    debug_astar_attack()