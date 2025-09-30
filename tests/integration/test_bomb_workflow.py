"""
End-to-end integration tests for bomb workflow
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
import sys
import os
import yaml
from unittest.mock import patch, mock_open

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine import Position


@pytest.mark.integration
@pytest.mark.bomb
@pytest.mark.e2e
class TestCompleteBombWorkflow:
    """End-to-end tests for complete bomb item workflow"""

    def test_complete_bomb_stage_workflow(self):
        """Given bomb stage, when played with optimal strategy, then completed successfully"""
        # TODO: This test MUST FAIL initially - complete bomb system doesn't exist yet
        from engine.game_state import GameState
        from engine.commands import DisposeCommand, PickupCommand, MoveCommand
        from engine.validator import is_stage_complete
        from engine.api import is_available

        # Setup complete bomb stage
        game_state = GameState()

        # Stage with mixed items requiring strategy
        stage_items = [
            {"id": "entrance_bomb", "type": "bomb", "position": [1, 2], "damage": 30},
            {"id": "key1", "type": "key", "position": [3, 2]},
            {"id": "path_bomb", "type": "bomb", "position": [2, 4], "damage": 40},
            {"id": "treasure1", "type": "treasure", "position": [4, 4]}
        ]
        game_state.items = stage_items
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(5, 5)
        game_state.player.position = Position(1, 1)

        initial_hp = game_state.player.hp

        # Execute optimal strategy
        move_command = MoveCommand()
        dispose_command = DisposeCommand()
        pickup_command = PickupCommand()

        # 1. Move to entrance bomb and check
        game_state.player.position = Position(1, 2)
        available = is_available()
        assert available is False, "Should detect bomb as not available for pickup"

        # 2. Dispose entrance bomb
        result = dispose_command.execute(game_state)
        assert result.success, "Should successfully dispose bomb"

        # 3. Move to key and collect
        game_state.player.position = Position(3, 2)
        available = is_available()
        assert available is True, "Should detect key as available for pickup"
        pickup_command.execute(game_state)

        # 4. Move to path bomb and dispose
        game_state.player.position = Position(2, 4)
        dispose_command.execute(game_state)

        # 5. Move to treasure and collect
        game_state.player.position = Position(4, 4)
        pickup_command.execute(game_state)

        # 6. Move to goal
        game_state.player.position = Position(5, 5)

        # Verify completion
        assert is_stage_complete(game_state), "Stage should be completed"
        assert game_state.player.hp == initial_hp, "No HP should be lost with proper strategy"

    def test_bomb_workflow_with_damage_taken(self):
        """Given bomb stage, when bombs are picked up instead of disposed, then damage taken"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand
        from engine.validator import is_stage_complete

        game_state = GameState()

        # Setup stage with bombs
        stage_items = [
            {"id": "damage_bomb1", "type": "bomb", "position": [1, 1], "damage": 25},
            {"id": "damage_bomb2", "type": "bomb", "position": [2, 2], "damage": 35}
        ]
        game_state.items = stage_items
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(3, 3)
        game_state.player.position = Position(1, 1)

        initial_hp = game_state.player.hp
        pickup_command = PickupCommand()

        # Pick up bombs instead of disposing (suboptimal strategy)
        pickup_command.execute(game_state)  # First bomb
        game_state.player.position = Position(2, 2)
        pickup_command.execute(game_state)  # Second bomb

        # Move to goal
        game_state.player.position = Position(3, 3)

        # Verify completion with damage
        assert is_stage_complete(game_state), "Stage should be completed"
        expected_hp = initial_hp - 25 - 35
        assert game_state.player.hp == expected_hp, "HP should be reduced by bomb damage"

    def test_mixed_strategy_workflow(self):
        """Given mixed items, when using both dispose and pickup, then stage completed optimally"""
        from engine.game_state import GameState
        from engine.commands import DisposeCommand, PickupCommand
        from engine.validator import is_stage_complete
        from engine.api import is_available

        game_state = GameState()

        # Setup complex mixed stage
        stage_items = [
            {"id": "bomb_a", "type": "bomb", "position": [1, 1], "damage": 20},
            {"id": "key_a", "type": "key", "position": [1, 2]},
            {"id": "bomb_b", "type": "bomb", "position": [2, 1], "damage": 30},
            {"id": "treasure_a", "type": "treasure", "position": [2, 2]},
            {"id": "bomb_c", "type": "bomb", "position": [3, 3], "damage": 40}
        ]
        game_state.items = stage_items
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(4, 4)

        initial_hp = game_state.player.hp
        dispose_command = DisposeCommand()
        pickup_command = PickupCommand()

        # Execute mixed strategy
        positions_and_actions = [
            (Position(1, 1), "dispose"),    # bomb_a
            (Position(1, 2), "pickup"),     # key_a
            (Position(2, 1), "dispose"),    # bomb_b
            (Position(2, 2), "pickup"),     # treasure_a
            (Position(3, 3), "dispose"),    # bomb_c
        ]

        for pos, action in positions_and_actions:
            game_state.player.position = pos

            # Verify is_available() gives correct guidance
            available = is_available()
            if action == "dispose":
                assert available is False, f"Bomb at {pos} should not be available for pickup"
                dispose_command.execute(game_state)
            else:
                assert available is True, f"Beneficial item at {pos} should be available for pickup"
                pickup_command.execute(game_state)

        # Move to goal
        game_state.player.position = Position(4, 4)

        # Verify optimal completion
        assert is_stage_complete(game_state), "Stage should be completed"
        assert game_state.player.hp == initial_hp, "No HP loss with optimal mixed strategy"

    def test_stage_generation_to_completion_workflow(self):
        """Given stage generation, when stage created and played, then completable"""
        from scripts.generate_stage import generate_stage
        from scripts.validate_stage import validate_stage
        from engine.stage_loader import load_stage_from_file

        # Generate bomb stage
        with patch('scripts.generate_stage.save_stage_to_file') as mock_save:
            stage_data = {
                "id": "generated_bomb_test",
                "title": "Generated Bomb Test",
                "board": [[".", ".", "."], [".", "P", "."], [".", ".", "G"]],
                "player": {"position": [1, 1]},
                "goal": {"position": [2, 2]},
                "enemies": [],
                "items": [
                    {"id": "gen_bomb", "type": "bomb", "position": [0, 0], "damage": 50},
                    {"id": "gen_key", "type": "key", "position": [2, 0]}
                ],
                "constraints": {"collect_all_items": True}
            }
            mock_save.return_value = "stages/generated_bomb_test.yml"

            generated_file = generate_stage(stage_type="mixed", seed=999, include_bombs=True)

        # Validate generated stage
        with patch('builtins.open', mock_open(read_data=yaml.dump(stage_data))):
            validation_result = validate_stage(generated_file)

        assert validation_result is True, "Generated bomb stage should validate"

        # Play generated stage
        with patch('builtins.open', mock_open(read_data=yaml.dump(stage_data))):
            game_state = load_stage_from_file(generated_file)

        # Should be playable to completion
        assert game_state is not None, "Generated stage should load successfully"
        assert len(game_state.items) == 2, "Should have both bomb and key items"

    def test_error_recovery_workflow(self):
        """Given errors during bomb workflow, when recovered, then workflow continues"""
        from engine.game_state import GameState
        from engine.commands import DisposeCommand, PickupCommand
        from engine.api import is_available

        game_state = GameState()

        stage_items = [
            {"id": "error_bomb", "type": "bomb", "position": [1, 1], "damage": 30}
        ]
        game_state.items = stage_items
        game_state.player.position = Position(2, 2)  # Not at bomb position

        dispose_command = DisposeCommand()

        # Try to dispose bomb from wrong position (should fail)
        result = dispose_command.execute(game_state)
        assert result.success is False, "Should fail when not at bomb position"

        # Move to correct position and try again
        game_state.player.position = Position(1, 1)
        available = is_available()
        assert available is False, "Should detect bomb correctly"

        result = dispose_command.execute(game_state)
        assert result.success is True, "Should succeed when at correct position"

    def test_performance_workflow_large_stage(self):
        """Given large stage with many bombs, when played, then completes in reasonable time"""
        from engine.game_state import GameState
        from engine.commands import DisposeCommand
        from engine.api import is_available
        import time

        game_state = GameState()

        # Create large stage with many bombs
        large_stage_items = []
        for i in range(50):
            bomb = {
                "id": f"perf_bomb_{i}",
                "type": "bomb",
                "position": [i % 10, i // 10],
                "damage": 10
            }
            large_stage_items.append(bomb)

        game_state.items = large_stage_items
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(9, 9)

        dispose_command = DisposeCommand()
        start_time = time.time()

        # Dispose all bombs
        for item in large_stage_items:
            pos = Position(item["position"][0], item["position"][1])
            game_state.player.position = pos

            available = is_available()
            assert available is False, "All items should be bombs"

            dispose_command.execute(game_state)

        end_time = time.time()
        processing_time = end_time - start_time

        # Should complete large stage in reasonable time
        assert processing_time < 5.0, f"Large stage processing too slow: {processing_time}s"
        assert len(game_state.items) == 0, "All bombs should be disposed"


@pytest.mark.integration
@pytest.mark.bomb
@pytest.mark.api
class TestBombWorkflowAPIIntegration:
    """Test bomb workflow integration with API layer"""

    def test_api_functions_in_workflow(self):
        """Given bomb workflow, when using API functions, then work correctly together"""
        from engine.game_state import GameState
        from engine.api import is_available, dispose, pickup, move, turn_left, turn_right

        game_state = GameState()

        # Setup stage for API testing
        stage_items = [
            {"id": "api_bomb", "type": "bomb", "position": [2, 1], "damage": 25},
            {"id": "api_key", "type": "key", "position": [2, 3]}
        ]
        game_state.items = stage_items
        game_state.player.position = Position(1, 1)

        # Test API movement to bomb
        move()  # Should move forward
        turn_right()
        move()  # Should be at bomb position (2, 1)

        # Test is_available() API
        available = is_available()
        assert available is False, "API should detect bomb as not available"

        # Test dispose() API
        result = dispose()
        assert result.success, "API dispose should succeed"

        # Move to key position
        move()
        move()  # Should be at key position (2, 3)

        # Test with beneficial item
        available = is_available()
        assert available is True, "API should detect key as available"

        # Test pickup() API
        result = pickup()
        assert result.success, "API pickup should succeed"

    def test_workflow_with_student_code_pattern(self):
        """Given typical student code pattern, when using bomb APIs, then works correctly"""
        from engine.game_state import GameState
        from engine.api import is_available, dispose, pickup, move, see

        game_state = GameState()

        # Setup stage mimicking student exercise
        stage_items = [
            {"id": "student_bomb", "type": "bomb", "position": [1, 2], "damage": 20}
        ]
        game_state.items = stage_items
        game_state.player.position = Position(1, 1)

        # Simulate typical student code pattern
        def student_solve():
            """Typical student solution using new APIs"""
            while True:
                # Check surroundings
                vision = see()

                # Check current position for items
                if vision.get("current_tile", {}).get("items"):
                    if is_available():
                        pickup()  # Safe to pickup
                    else:
                        dispose()  # Must be a bomb, dispose it
                    break
                else:
                    move()  # Continue searching

        # Execute student code
        student_solve()

        # Verify student code worked correctly
        assert len(game_state.items) == 0, "Student code should have handled the bomb"
        assert "student_bomb" in game_state.player.disposed_items, "Bomb should be in disposed items"


@pytest.mark.integration
@pytest.mark.bomb
@pytest.mark.educational
class TestBombWorkflowEducationalScenarios:
    """Test bomb workflow in educational scenarios"""

    def test_beginner_friendly_error_messages(self):
        """Given beginner mistakes, when errors occur, then helpful messages provided"""
        from engine.game_state import GameState
        from engine.commands import DisposeCommand
        from engine.api import dispose

        game_state = GameState()
        game_state.items = []  # No items
        game_state.player.position = Position(1, 1)

        # Test dispose with no item
        result = dispose()
        assert result.success is False, "Should fail with no item"
        assert "no item" in result.message.lower(), "Error message should be clear for beginners"

        # Test dispose with beneficial item
        key_item = {"id": "help_key", "type": "key", "position": [1, 1]}
        game_state.items = [key_item]

        result = dispose()
        assert result.success is False, "Should fail for beneficial item"
        error_msg = result.message.lower()
        assert any(word in error_msg for word in ["beneficial", "key", "pickup"]), "Should suggest correct action"

    def test_progressive_difficulty_workflow(self):
        """Given progressive difficulty, when stages increase complexity, then manageable"""
        from engine.game_state import GameState
        from engine.api import is_available, dispose, pickup

        # Stage 1: Single bomb (beginner)
        game_state = GameState()
        game_state.items = [{"id": "beginner_bomb", "type": "bomb", "position": [1, 1], "damage": 10}]
        game_state.player.position = Position(1, 1)

        assert not is_available(), "Beginner should learn to detect bombs"
        result = dispose()
        assert result.success, "Simple disposal should work"

        # Stage 2: Mixed items (intermediate)
        game_state = GameState()
        mixed_items = [
            {"id": "int_bomb", "type": "bomb", "position": [1, 1], "damage": 20},
            {"id": "int_key", "type": "key", "position": [2, 1]}
        ]
        game_state.items = mixed_items

        # Test decision making
        game_state.player.position = Position(1, 1)
        assert not is_available(), "Should detect bomb"
        dispose()

        game_state.player.position = Position(2, 1)
        assert is_available(), "Should detect beneficial item"
        pickup()

        # Both strategies should be learned progressively
        assert len(game_state.items) == 0, "All items should be handled correctly"