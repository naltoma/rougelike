"""
Integration tests for Stage completion with disposed items
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine import Position


@pytest.mark.integration
@pytest.mark.bomb
@pytest.mark.core
class TestStageCompletionWithDisposedItems:
    """Integration tests for stage completion logic with disposed items"""

    def test_stage_complete_with_disposed_bomb_only(self):
        """Given stage with only bomb, when bomb disposed and at goal, then stage complete"""
        # TODO: This test MUST FAIL initially - disposed items don't count for completion yet
        from engine.game_state import GameState
        from engine.validator import is_stage_complete
        from engine.commands import DisposeCommand

        game_state = GameState()

        # Setup stage with single bomb
        bomb_item = {
            "id": "only_bomb",
            "type": "bomb",
            "position": [1, 1],
            "damage": 50
        }
        game_state.items = [bomb_item]
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(3, 3)

        # Move player to bomb and dispose
        game_state.player.position = Position(1, 1)
        dispose_command = DisposeCommand()
        dispose_command.execute(game_state)

        # Move to goal
        game_state.player.position = Position(3, 3)

        # Should be complete
        assert is_stage_complete(game_state), "Stage should be complete with all items disposed"

    def test_stage_complete_with_mixed_items(self):
        """Given stage with bombs and beneficial items, when all handled and at goal, then complete"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete
        from engine.commands import DisposeCommand, PickupCommand

        game_state = GameState()

        # Setup stage with mixed items
        bomb_item = {
            "id": "mixed_bomb",
            "type": "bomb",
            "position": [1, 1],
            "damage": 40
        }
        key_item = {
            "id": "mixed_key",
            "type": "key",
            "position": [2, 2]
        }
        game_state.items = [bomb_item, key_item]
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(5, 5)

        # Handle bomb - dispose
        game_state.player.position = Position(1, 1)
        dispose_command = DisposeCommand()
        dispose_command.execute(game_state)

        # Handle key - pickup
        game_state.player.position = Position(2, 2)
        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        # Move to goal
        game_state.player.position = Position(5, 5)

        # Should be complete
        assert is_stage_complete(game_state), "Stage should be complete with mixed item handling"

    def test_stage_incomplete_with_unhandled_bomb(self):
        """Given stage with unhandled bomb, when at goal, then stage incomplete"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete

        game_state = GameState()

        # Setup stage with unhandled bomb
        bomb_item = {
            "id": "unhandled_bomb",
            "type": "bomb",
            "position": [1, 1],
            "damage": 30
        }
        game_state.items = [bomb_item]
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(3, 3)

        # Move to goal without handling bomb
        game_state.player.position = Position(3, 3)

        # Should not be complete
        assert not is_stage_complete(game_state), "Stage should not be complete with unhandled items"

    def test_stage_incomplete_with_unhandled_key(self):
        """Given stage with unhandled key, when at goal, then stage incomplete"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete

        game_state = GameState()

        # Setup stage with unhandled key
        key_item = {
            "id": "unhandled_key",
            "type": "key",
            "position": [2, 2]
        }
        game_state.items = [key_item]
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(4, 4)

        # Move to goal without collecting key
        game_state.player.position = Position(4, 4)

        # Should not be complete
        assert not is_stage_complete(game_state), "Stage should not be complete with uncollected items"

    def test_stage_completion_no_collect_all_constraint(self):
        """Given stage without collect_all_items constraint, when at goal, then complete regardless of items"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete

        game_state = GameState()

        # Setup stage without collection constraint
        bomb_item = {
            "id": "ignored_bomb",
            "type": "bomb",
            "position": [1, 1],
            "damage": 25
        }
        game_state.items = [bomb_item]
        game_state.constraints = {}  # No collect_all_items constraint
        game_state.goal_position = Position(3, 3)

        # Move to goal without handling bomb
        game_state.player.position = Position(3, 3)

        # Should be complete
        assert is_stage_complete(game_state), "Stage should be complete without collection constraint"

    def test_stage_completion_count_calculation(self):
        """Given mixed items, when some handled, then completion count calculated correctly"""
        from engine.game_state import GameState
        from engine.validator import get_completion_status

        game_state = GameState()

        # Setup stage with multiple items
        items = [
            {"id": "bomb1", "type": "bomb", "position": [1, 1], "damage": 30},
            {"id": "bomb2", "type": "bomb", "position": [2, 2], "damage": 40},
            {"id": "key1", "type": "key", "position": [3, 3]},
            {"id": "treasure1", "type": "treasure", "position": [4, 4]}
        ]
        game_state.items = items
        game_state.constraints = {"collect_all_items": True}

        # Initially no items handled
        status = get_completion_status(game_state)
        assert status["total_items"] == 4, "Should count all items"
        assert status["handled_items"] == 0, "No items handled initially"
        assert status["completion_percentage"] == 0.0, "0% completion initially"

        # Handle some items
        game_state.player.collected_items = ["key1", "treasure1"]
        game_state.player.disposed_items = ["bomb1"]

        status = get_completion_status(game_state)
        assert status["handled_items"] == 3, "Should count collected and disposed items"
        assert status["completion_percentage"] == 75.0, "75% completion with 3/4 items handled"

    def test_disposed_items_validation(self):
        """Given disposed items, when validation checked, then no conflicts with collected items"""
        from engine.game_state import GameState
        from engine.validator import validate_item_handling

        game_state = GameState()
        player = game_state.player

        # Setup conflicting item handling (should be prevented)
        player.collected_items = ["item1", "item2"]
        player.disposed_items = ["item1", "item3"]  # item1 in both lists

        validation_result = validate_item_handling(game_state)
        assert not validation_result["valid"], "Items cannot be both collected and disposed"
        assert "conflict" in validation_result["error"].lower(), "Error should mention conflict"

    def test_multiple_bomb_disposal_completion(self):
        """Given stage with multiple bombs, when all disposed, then stage complete"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete
        from engine.commands import DisposeCommand

        game_state = GameState()

        # Setup stage with multiple bombs
        bombs = [
            {"id": "bomb_a", "type": "bomb", "position": [1, 1], "damage": 20},
            {"id": "bomb_b", "type": "bomb", "position": [2, 2], "damage": 30},
            {"id": "bomb_c", "type": "bomb", "position": [3, 3], "damage": 40}
        ]
        game_state.items = bombs
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(5, 5)

        dispose_command = DisposeCommand()

        # Dispose all bombs
        for bomb in bombs:
            pos = Position(bomb["position"][0], bomb["position"][1])
            game_state.player.position = pos
            dispose_command.execute(game_state)

        # Move to goal
        game_state.player.position = Position(5, 5)

        # Should be complete
        assert is_stage_complete(game_state), "Stage should be complete with all bombs disposed"

    def test_stage_completion_with_empty_items(self):
        """Given stage with no items, when at goal, then complete"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete

        game_state = GameState()

        # Setup stage with no items
        game_state.items = []
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(2, 2)

        # Move to goal
        game_state.player.position = Position(2, 2)

        # Should be complete
        assert is_stage_complete(game_state), "Stage with no items should be complete at goal"


@pytest.mark.integration
@pytest.mark.bomb
class TestStageCompletionEdgeCases:
    """Edge case tests for stage completion with bomb system"""

    def test_bomb_disposal_after_goal_reached(self):
        """Given player at goal, when bomb disposed after, then completion status updated"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete
        from engine.commands import DisposeCommand

        game_state = GameState()

        bomb_item = {
            "id": "late_bomb",
            "type": "bomb",
            "position": [1, 1],
            "damage": 35
        }
        game_state.items = [bomb_item]
        game_state.constraints = {"collect_all_items": True}
        game_state.goal_position = Position(3, 3)

        # Move to goal first (should not be complete)
        game_state.player.position = Position(3, 3)
        assert not is_stage_complete(game_state), "Should not be complete with unhandled bomb"

        # Dispose bomb while at goal
        game_state.player.position = Position(1, 1)
        dispose_command = DisposeCommand()
        dispose_command.execute(game_state)

        # Return to goal
        game_state.player.position = Position(3, 3)
        assert is_stage_complete(game_state), "Should be complete after disposing bomb"

    def test_completion_with_duplicate_item_ids(self):
        """Given stage with duplicate item IDs, when handled, then completion calculated correctly"""
        from engine.game_state import GameState
        from engine.validator import is_stage_complete

        game_state = GameState()

        # This should be prevented by validation, but test robustness
        items = [
            {"id": "duplicate", "type": "bomb", "position": [1, 1], "damage": 25},
            {"id": "duplicate", "type": "key", "position": [2, 2]}  # Same ID
        ]
        game_state.items = items
        game_state.constraints = {"collect_all_items": True}

        # The system should handle this gracefully
        game_state.player.disposed_items = ["duplicate"]
        game_state.goal_position = Position(3, 3)
        game_state.player.position = Position(3, 3)

        # Behavior with duplicate IDs should be defined
        completion_result = is_stage_complete(game_state)
        assert isinstance(completion_result, bool), "Should return boolean result even with duplicates"