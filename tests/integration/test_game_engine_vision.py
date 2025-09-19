#!/usr/bin/env python3
"""Test game engine vision calculation vs A* vision calculation"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from engine import Enemy, Position, Direction

def test_game_engine_vision():
    """Test game engine vision calculation"""

    # Create enemy at (5,0) facing W with vision_range=1 (from actual game log)
    enemy = Enemy(
        position=Position(5, 0),
        direction=Direction.WEST,
        vision_range=1
    )

    # Test player position (1,4) (from step 8)
    player_pos = Position(1, 4)

    print("=== Game Engine Vision Test ===")
    print(f"Enemy: ({enemy.position.x},{enemy.position.y}){enemy.direction.value}")
    print(f"Player: ({player_pos.x},{player_pos.y})")
    print(f"Vision range: {enemy.vision_range}")
    print()

    # Get vision cells from game engine
    vision_cells = enemy.get_vision_cells(board=None)
    print(f"Game engine vision cells: {[(cell.x, cell.y) for cell in vision_cells]}")

    # Test if player can be seen
    can_see = enemy.can_see_player(player_pos, board=None)
    print(f"Game engine can see player: {can_see}")
    print()

    # Test A* logic manually for comparison
    print("=== A* Logic Test (Manual) ===")
    ex, ey = enemy.position.x, enemy.position.y
    px, py = player_pos.x, player_pos.y

    print(f"Enemy: ({ex},{ey}){enemy.direction.value}")
    print(f"Player: ({px},{py})")
    print(f"Vision range: {enemy.vision_range}")

    for distance in range(1, enemy.vision_range + 1):
        print(f"Distance {distance}:")
        for offset in range(-distance, distance + 1):
            if enemy.direction == Direction.WEST:
                target_x = ex - distance
                target_y = ey + offset

            print(f"  offset={offset}: checking position ({target_x},{target_y})")

            if (target_x, target_y) == (px, py):
                if abs(offset) <= distance:
                    print(f"  ✓ DETECTED: Player at ({px},{py}) matches target ({target_x},{target_y})")
                    print("  A* can see player: True")
                    return
                else:
                    print(f"  ✗ Outside FoV: offset {offset} > distance {distance}")

    print("  A* can see player: False")

if __name__ == "__main__":
    test_game_engine_vision()