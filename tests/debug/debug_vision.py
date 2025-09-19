#!/usr/bin/env python3
"""Debug vision calculation for generated_attack_2025"""

def test_vision_calculation():
    """Test if enemy at (5,0)W can see player at (4,1)E with vision_range=1"""

    # Enemy state (corrected coordinates)
    ex, ey = 5, 0
    enemy_direction = "W"
    vision_range = 1

    # Player position (corrected coordinates from step 8)
    px, py = 4, 1

    print(f"Enemy: ({ex},{ey}){enemy_direction}")
    print(f"Player: ({px},{py})")
    print(f"Vision range: {vision_range}")
    print()

    # Current A* algorithm logic
    print("=== Current A* Vision Logic ===")

    for distance in range(1, vision_range + 1):
        print(f"Distance {distance}:")
        for offset in range(-distance, distance + 1):
            if enemy_direction == "W":
                target_x = ex - distance  # Move west (decrease x)
                target_y = ey + offset    # Offset in y direction

            print(f"  offset={offset}: checking position ({target_x},{target_y})")

            if (target_x, target_y) == (px, py):
                if abs(offset) <= distance:
                    print(f"  ✓ DETECTED: Player at ({px},{py}) matches target ({target_x},{target_y})")
                    return True
                else:
                    print(f"  ✗ Outside FoV: offset {offset} > distance {distance}")

    print("  ✗ NOT DETECTED")
    return False

def test_all_adjacent_positions():
    """Test vision for all adjacent positions around enemy"""

    # Enemy state (from actual game log)
    ex, ey = 5, 0
    enemy_direction = "W"
    vision_range = 1

    print(f"\n=== Testing all adjacent positions for enemy at ({ex},{ey}){enemy_direction} ===")
    print(f"Vision range: {vision_range}")
    print()

    # Test all 8 adjacent positions
    adjacent_positions = [
        (-1, 3), (0, 3), (1, 3),  # Above
        (-1, 4),         (1, 4),  # Same row (left and right)
        (-1, 5), (0, 5), (1, 5)   # Below
    ]

    for test_px, test_py in adjacent_positions:
        print(f"Testing player at ({test_px},{test_py}):")

        detected = False
        for distance in range(1, vision_range + 1):
            for offset in range(-distance, distance + 1):
                if enemy_direction == "W":
                    target_x = ex - distance
                    target_y = ey + offset

                if (target_x, target_y) == (test_px, test_py):
                    if abs(offset) <= distance:
                        print(f"  ✓ DETECTED at distance={distance}, offset={offset}")
                        detected = True
                        break
            if detected:
                break

        if not detected:
            print(f"  ✗ NOT DETECTED")
    print()

if __name__ == "__main__":
    result = test_vision_calculation()
    test_all_adjacent_positions()

    print(f"\nResult: Enemy at (0,4)W {'CAN' if result else 'CANNOT'} see player at (1,4)E")