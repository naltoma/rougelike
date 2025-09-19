#!/usr/bin/env python3
"""Debug attack stage step by step execution"""

STAGE_ID = "generated_attack_2025"

def solve():
    """Step by step debugging with detailed position reporting"""

    # A* generated solution:
    # turn_left()  # Step 1
    # turn_left()  # Step 2
    # move()       # Step 3
    # turn_left()  # Step 4
    # move()       # Step 5
    # move()       # Step 6
    # move()       # Step 7
    # move()       # Step 8
    # attack()     # Step 9
    # turn_left()  # Step 10
    # turn_left()  # Step 11
    # move()       # Step 12

    print("=== Step-by-step execution debug ===")

    print("Step 1: turn_left() - Face W")
    turn_left()

    print("Step 2: turn_left() - Face S")
    turn_left()

    print("Step 3: move() - Should be at (0,1)S")
    move()

    print("Step 4: turn_left() - Face E")
    turn_left()

    print("Step 5: move() - Should be at (1,1)E")
    move()

    print("Step 6: move() - Should be at (2,1)E")
    move()

    print("Step 7: move() - Should be at (3,1)E")
    move()

    print("Step 8: move() - Should be at (4,1)E, Enemy should detect and move to (4,0)W")
    move()

    print("Step 9: attack() - Should attack enemy at (4,0) from (4,1)")
    attack()

    print("Step 10: turn_left() - Face N")
    turn_left()

    print("Step 11: turn_left() - Face W")
    turn_left()

    print("Step 12: move() - Should move to goal")
    move()

if __name__ == "__main__":
    import sys
import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "engine"))

    # Import the actual game engine classes
    from engine.api import initialize_api, initialize_stage
    from engine.api import turn_left, turn_right, move, attack, see

    print("🔍 Initializing attack stage debug...")

    # Initialize API
    initialize_api("cui")  # Use CUI for detailed text output

    # Initialize stage
    if not initialize_stage(STAGE_ID):
        print("❌ Stage initialization failed")
        exit(1)

    print("✅ Stage initialized successfully")
    print()

    # Run the solve function with step-by-step debugging
    try:
        solve()
        print("\n✅ Solution execution completed")
    except Exception as e:
        print(f"\n❌ Solution execution failed: {e}")
        import traceback
        traceback.print_exc()