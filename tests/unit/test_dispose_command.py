"""
Unit tests for DisposeCommand class
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.commands import ExecutionResult
from engine import Position


@pytest.mark.unit
@pytest.mark.bomb
@pytest.mark.core
class TestDisposeCommand:
    """Unit tests for DisposeCommand class"""

    def test_dispose_command_exists(self):
        """Given DisposeCommand import, when imported, then class exists"""
        # TODO: This test MUST FAIL initially - DisposeCommand doesn't exist yet
        from engine.commands import DisposeCommand

        assert DisposeCommand is not None, "DisposeCommand class should exist"
        assert hasattr(DisposeCommand, 'execute'), "DisposeCommand should have execute method"

    def test_dispose_command_inheritance(self):
        """Given DisposeCommand, when checked, then inherits from Command base class"""
        from engine.commands import DisposeCommand, Command

        assert issubclass(DisposeCommand, Command), "DisposeCommand should inherit from Command"

    def test_dispose_bomb_item_success(self):
        """Given bomb item at player position, when dispose executed, then succeeds"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        # Setup game state with bomb at player position
        game_state = GameState()
        player_pos = game_state.player.position

        bomb_item = {
            "id": "test_bomb",
            "type": "bomb",
            "position": [player_pos.x, player_pos.y],
            "damage": 50
        }
        game_state.items = [bomb_item]

        # Execute dispose command
        dispose_command = DisposeCommand()
        result = dispose_command.execute(game_state)

        assert isinstance(result, ExecutionResult), "Should return ExecutionResult"
        assert result.success is True, "Dispose should succeed for bomb items"
        assert "bomb1" in result.message or "disposed" in result.message.lower(), "Message should mention disposal"

    def test_dispose_removes_item_from_game_state(self):
        """Given bomb item, when disposed, then item removed from game state"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        game_state = GameState()
        player_pos = game_state.player.position

        bomb_item = {
            "id": "bomb_to_remove",
            "type": "bomb",
            "position": [player_pos.x, player_pos.y],
            "damage": 30
        }
        game_state.items = [bomb_item]

        dispose_command = DisposeCommand()
        dispose_command.execute(game_state)

        # Verify item is removed
        assert len(game_state.items) == 0, "Bomb item should be removed from game state"

        # Verify no item with that ID exists
        remaining_items = [item for item in game_state.items if item["id"] == "bomb_to_remove"]
        assert len(remaining_items) == 0, "Disposed bomb should not exist in items"

    def test_dispose_adds_to_disposed_items(self):
        """Given bomb disposal, when executed, then item added to player disposed_items"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        game_state = GameState()
        player_pos = game_state.player.position
        player = game_state.player

        bomb_item = {
            "id": "bomb_for_disposal_list",
            "type": "bomb",
            "position": [player_pos.x, player_pos.y],
            "damage": 25
        }
        game_state.items = [bomb_item]

        dispose_command = DisposeCommand()
        dispose_command.execute(game_state)

        assert hasattr(player, 'disposed_items'), "Player should have disposed_items attribute"
        assert "bomb_for_disposal_list" in player.disposed_items, "Disposed bomb ID should be in disposed_items"

    def test_dispose_consumes_turn(self):
        """Given dispose command, when executed, then turn count incremented"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        game_state = GameState()
        player_pos = game_state.player.position
        initial_turn = game_state.turn_count

        bomb_item = {
            "id": "turn_consuming_bomb",
            "type": "bomb",
            "position": [player_pos.x, player_pos.y],
            "damage": 45
        }
        game_state.items = [bomb_item]

        dispose_command = DisposeCommand()
        dispose_command.execute(game_state)

        assert game_state.turn_count == initial_turn + 1, "Turn count should be incremented"

    def test_dispose_no_item_fails(self):
        """Given no item at position, when dispose executed, then fails"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        game_state = GameState()
        game_state.items = []  # No items

        dispose_command = DisposeCommand()
        result = dispose_command.execute(game_state)

        assert isinstance(result, ExecutionResult), "Should return ExecutionResult"
        assert result.success is False, "Dispose should fail when no item present"
        assert "no item" in result.message.lower(), "Error message should mention no item"

    def test_dispose_beneficial_item_fails(self):
        """Given beneficial item at position, when dispose executed, then fails"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        game_state = GameState()
        player_pos = game_state.player.position

        key_item = {
            "id": "beneficial_key",
            "type": "key",
            "position": [player_pos.x, player_pos.y]
        }
        game_state.items = [key_item]

        dispose_command = DisposeCommand()
        result = dispose_command.execute(game_state)

        assert isinstance(result, ExecutionResult), "Should return ExecutionResult"
        assert result.success is False, "Dispose should fail for beneficial items"
        assert "beneficial" in result.message.lower() or "key" in result.message.lower(), "Error should mention item type"

    def test_dispose_already_handled_item_fails(self):
        """Given already handled item, when dispose attempted, then fails"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        game_state = GameState()
        player_pos = game_state.player.position
        player = game_state.player

        # Pre-dispose the item
        player.disposed_items = ["already_disposed_bomb"]

        bomb_item = {
            "id": "already_disposed_bomb",
            "type": "bomb",
            "position": [player_pos.x, player_pos.y],
            "damage": 35
        }
        game_state.items = [bomb_item]

        dispose_command = DisposeCommand()
        result = dispose_command.execute(game_state)

        assert isinstance(result, ExecutionResult), "Should return ExecutionResult"
        assert result.success is False, "Dispose should fail for already handled items"
        assert "already" in result.message.lower(), "Error should mention item already handled"

    def test_dispose_multiple_items_at_position(self):
        """Given multiple items at position, when dispose executed, then only bomb disposed"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState

        game_state = GameState()
        player_pos = game_state.player.position

        bomb_item = {
            "id": "bomb_with_key",
            "type": "bomb",
            "position": [player_pos.x, player_pos.y],
            "damage": 40
        }
        key_item = {
            "id": "key_with_bomb",
            "type": "key",
            "position": [player_pos.x, player_pos.y]
        }
        game_state.items = [bomb_item, key_item]

        dispose_command = DisposeCommand()
        result = dispose_command.execute(game_state)

        assert result.success is True, "Should succeed by disposing bomb"

        # Verify only bomb was removed, key remains
        remaining_items = [item for item in game_state.items if item["id"] == "key_with_bomb"]
        assert len(remaining_items) == 1, "Key item should remain"

        removed_items = [item for item in game_state.items if item["id"] == "bomb_with_key"]
        assert len(removed_items) == 0, "Bomb item should be removed"

    def test_dispose_command_string_representation(self):
        """Given DisposeCommand, when string representation requested, then descriptive"""
        from engine.commands import DisposeCommand

        dispose_command = DisposeCommand()
        command_str = str(dispose_command)

        assert "dispose" in command_str.lower(), "String representation should mention dispose"

    def test_dispose_command_validation(self):
        """Given invalid game state, when dispose executed, then handles gracefully"""
        from engine.commands import DisposeCommand

        dispose_command = DisposeCommand()

        # Test with None game state
        with pytest.raises((TypeError, AttributeError)):
            dispose_command.execute(None)

        # Test with invalid game state structure
        class InvalidGameState:
            pass

        invalid_state = InvalidGameState()

        with pytest.raises((AttributeError, TypeError)):
            dispose_command.execute(invalid_state)


@pytest.mark.unit
@pytest.mark.bomb
@pytest.mark.integration
class TestDisposeCommandIntegration:
    """Integration tests for DisposeCommand with other systems"""

    def test_dispose_updates_stage_completion(self):
        """Given stage with collect_all_items constraint, when bomb disposed, then completion updated"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState
        from engine.validator import is_stage_complete

        game_state = GameState()
        player_pos = game_state.player.position

        # Setup stage with bomb and completion constraint
        bomb_item = {
            "id": "completion_bomb",
            "type": "bomb",
            "position": [player_pos.x, player_pos.y],
            "damage": 60
        }
        game_state.items = [bomb_item]
        game_state.constraints = {"collect_all_items": True}

        # Move player to goal position
        game_state.goal_position = Position(5, 5)
        game_state.player.position = Position(5, 5)

        # Initially should not be complete
        assert not is_stage_complete(game_state), "Stage should not be complete with unhandled bomb"

        # Dispose bomb
        dispose_command = DisposeCommand()
        dispose_command.execute(game_state)

        # Now should be complete
        assert is_stage_complete(game_state), "Stage should be complete after disposing all items"

    def test_dispose_with_logging(self):
        """Given dispose command execution, when logging enabled, then events logged"""
        from engine.commands import DisposeCommand
        from engine.game_state import GameState
        import logging

        # Setup logging capture
        with pytest.raises(Exception):  # Will fail until logging is implemented
            game_state = GameState()
            player_pos = game_state.player.position

            bomb_item = {
                "id": "logged_bomb",
                "type": "bomb",
                "position": [player_pos.x, player_pos.y],
                "damage": 55
            }
            game_state.items = [bomb_item]

            dispose_command = DisposeCommand()

            with pytest.LoggingHandler() as log_capture:
                dispose_command.execute(game_state)

                # Verify disposal was logged
                log_messages = log_capture.get_logs()
                assert any("dispose" in msg.lower() for msg in log_messages), "Disposal should be logged"