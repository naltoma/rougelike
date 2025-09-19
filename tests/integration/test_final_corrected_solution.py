#!/usr/bin/env python3
"""Test final corrected A* generated solution for generated_attack_2025"""

STAGE_ID = "generated_attack_2025"

def solve():
    """Final corrected A* generated 12-step solution"""

    print("=== 最終修正A*生成12ステップ解法テスト ===")

    turn_left()  # Step 1: Face W
    turn_left()  # Step 2: Face S
    move()       # Step 3: (0,1)S
    turn_left()  # Step 4: Face E
    move()       # Step 5: (1,1)E
    move()       # Step 6: (2,1)E
    move()       # Step 7: (3,1)E
    move()       # Step 8: (4,1)E - Enemy moves to (4,0)
    turn_left()  # Step 9: Face N - CORRECT!
    attack()     # Step 10: Attack enemy at (4,0) - SUCCESS!
    turn_left()  # Step 11: Face W
    move()       # Step 12: Move to goal (3,1)

if __name__ == "__main__":
    import sys
import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "engine"))

    from engine.api import initialize_api, initialize_stage
    from engine.api import turn_left, turn_right, move, attack, see

    print("🔍 Testing final corrected A* generated 12-step solution...")

    # Initialize API
    initialize_api("cui")

    # Initialize stage
    if not initialize_stage(STAGE_ID):
        print("❌ Stage initialization failed")
        exit(1)

    print("✅ Stage initialized successfully")
    print()

    try:
        solve()
        print("\n✅ Final corrected A* 12-step solution execution completed")
    except Exception as e:
        print(f"\n❌ Solution execution failed: {e}")
        import traceback
        traceback.print_exc()