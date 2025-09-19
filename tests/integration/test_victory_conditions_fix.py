#!/usr/bin/env python3
"""Test victory conditions fix for pickup stages"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_pickup_2026_victory_conditions():
    """Test that pickup stage now properly requires item collection"""
    print("=== Testing Victory Conditions Fix ===")

    try:
        # Import necessary components
        from engine.api import APILayer

        # Create API layer
        api = APILayer('cui')

        # Initialize pickup stage 2026
        print("Loading generated_pickup_2026...")
        success = api.initialize_stage('generated_pickup_2026')

        if not success:
            print("❌ Failed to load stage")
            return False

        print("✅ Stage loaded successfully")

        # Check if game state has victory conditions
        game_state = api.game_manager.current_state
        print(f"Victory conditions: {game_state.victory_conditions}")

        # Test 1: Move to goal without collecting items
        print("\n=== Test 1: Move to goal without collecting items ===")

        # Simulate player at goal position without collecting items
        original_pos = game_state.player.position
        goal_pos = game_state.goal_position

        print(f"Original player position: {original_pos}")
        print(f"Goal position: {goal_pos}")
        print(f"Items in stage: {len(game_state.items)}")

        # Move player to goal
        game_state.player.position = goal_pos

        # Check victory conditions
        victory_result = game_state.check_victory_conditions()
        print(f"Victory result (without items): {victory_result}")

        if victory_result:
            print("❌ FAILED: Player won without collecting items!")
            return False
        else:
            print("✅ SUCCESS: Player cannot win without collecting items")

        # Test 2: Collect all items and then move to goal
        print("\n=== Test 2: Collect all items then move to goal ===")

        # Reset player position
        game_state.player.position = original_pos

        # Simulate collecting all items by removing them from game_state.items
        items_collected = []
        for item in game_state.items[:]:  # Copy list to avoid modification during iteration
            items_collected.append(item)
            game_state.items.remove(item)

        print(f"Items collected: {len(items_collected)}")
        print(f"Items remaining: {len(game_state.items)}")

        # Move to goal after collecting items
        game_state.player.position = goal_pos

        # Check victory conditions
        victory_result = game_state.check_victory_conditions()
        print(f"Victory result (with all items): {victory_result}")

        if victory_result:
            print("✅ SUCCESS: Player wins after collecting all items")
            return True
        else:
            print("❌ FAILED: Player cannot win even after collecting all items!")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing victory conditions fix...")
    success = test_pickup_2026_victory_conditions()
    print(f"\n{'✅ ALL TESTS PASSED' if success else '❌ TESTS FAILED'}")
    sys.exit(0 if success else 1)