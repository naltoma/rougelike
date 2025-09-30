"""
Contract tests for Item Management API (is_available, dispose)
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.commands import ExecutionResult


@pytest.mark.contract
@pytest.mark.item_management
@pytest.mark.bomb
class TestIsAvailableContract:
    """Contract tests for is_available() function"""

    def test_is_available_with_beneficial_item_returns_true(self):
        """Given beneficial item at position, when is_available(), then return True"""
        # TODO: This test MUST FAIL initially - function doesn't exist yet
        from engine.api import is_available

        # Setup: Mock game state with beneficial item at current position
        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items:

            mock_pos.return_value = (1, 1)
            mock_items.return_value = [{'id': 'key1', 'type': 'key'}]

            result = is_available()

            assert result is True, "is_available() should return True for beneficial items"

    def test_is_available_with_bomb_item_returns_false(self):
        """Given bomb item at position, when is_available(), then return False"""
        from engine.api import is_available

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items:

            mock_pos.return_value = (2, 2)
            mock_items.return_value = [{'id': 'bomb1', 'type': 'bomb', 'damage': 50}]

            result = is_available()

            assert result is False, "is_available() should return False for bomb items"

    def test_is_available_with_no_item_returns_false(self):
        """Given no item at position, when is_available(), then return False"""
        from engine.api import is_available

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items:

            mock_pos.return_value = (3, 3)
            mock_items.return_value = []

            result = is_available()

            assert result is False, "is_available() should return False when no item present"

    def test_is_available_does_not_consume_turn(self):
        """Given any position, when is_available(), then turn count unchanged"""
        from engine.api import is_available

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items, \
             patch('engine.api.get_turn_count') as mock_turns:

            mock_pos.return_value = (1, 1)
            mock_items.return_value = [{'id': 'key1', 'type': 'key'}]
            mock_turns.return_value = 5

            is_available()

            # Verify no turn increment was called
            assert mock_turns.call_count <= 1, "is_available() should not increment turn count"


@pytest.mark.contract
@pytest.mark.item_management
@pytest.mark.bomb
class TestDisposeContract:
    """Contract tests for dispose() function"""

    def test_dispose_bomb_item_succeeds(self):
        """Given bomb at position, when dispose(), then success result"""
        from engine.api import dispose

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items, \
             patch('engine.api.remove_item_from_map') as mock_remove, \
             patch('engine.api.add_to_disposed_items') as mock_disposed, \
             patch('engine.api.increment_turn') as mock_turn:

            mock_pos.return_value = (2, 2)
            mock_items.return_value = [{'id': 'bomb1', 'type': 'bomb', 'damage': 50}]

            result = dispose()

            assert isinstance(result, ExecutionResult), "dispose() should return ExecutionResult"
            assert result.success is True, "dispose() should succeed for bomb items"
            mock_remove.assert_called_once()
            mock_disposed.assert_called_once()
            mock_turn.assert_called_once()

    def test_dispose_beneficial_item_fails(self):
        """Given beneficial item at position, when dispose(), then failure result"""
        from engine.api import dispose

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items:

            mock_pos.return_value = (1, 1)
            mock_items.return_value = [{'id': 'key1', 'type': 'key'}]

            result = dispose()

            assert isinstance(result, ExecutionResult), "dispose() should return ExecutionResult"
            assert result.success is False, "dispose() should fail for beneficial items"

    def test_dispose_no_item_fails(self):
        """Given no item at position, when dispose(), then failure result"""
        from engine.api import dispose

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items:

            mock_pos.return_value = (3, 3)
            mock_items.return_value = []

            result = dispose()

            assert isinstance(result, ExecutionResult), "dispose() should return ExecutionResult"
            assert result.success is False, "dispose() should fail when no item present"

    def test_dispose_consumes_turn(self):
        """Given valid dispose, when dispose(), then turn count incremented"""
        from engine.api import dispose

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items, \
             patch('engine.api.remove_item_from_map') as mock_remove, \
             patch('engine.api.add_to_disposed_items') as mock_disposed, \
             patch('engine.api.increment_turn') as mock_turn:

            mock_pos.return_value = (2, 2)
            mock_items.return_value = [{'id': 'bomb1', 'type': 'bomb', 'damage': 50}]

            dispose()

            mock_turn.assert_called_once(), "dispose() should consume exactly one turn"

    def test_dispose_removes_item_from_map(self):
        """Given bomb at position, when dispose(), then item removed from map"""
        from engine.api import dispose

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items, \
             patch('engine.api.remove_item_from_map') as mock_remove, \
             patch('engine.api.add_to_disposed_items') as mock_disposed, \
             patch('engine.api.increment_turn') as mock_turn:

            mock_pos.return_value = (2, 2)
            bomb_item = {'id': 'bomb1', 'type': 'bomb', 'damage': 50}
            mock_items.return_value = [bomb_item]

            dispose()

            mock_remove.assert_called_once_with(bomb_item)

    def test_dispose_updates_disposed_items(self):
        """Given bomb at position, when dispose(), then item added to disposed_items"""
        from engine.api import dispose

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items, \
             patch('engine.api.remove_item_from_map') as mock_remove, \
             patch('engine.api.add_to_disposed_items') as mock_disposed, \
             patch('engine.api.increment_turn') as mock_turn:

            mock_pos.return_value = (2, 2)
            bomb_item = {'id': 'bomb1', 'type': 'bomb', 'damage': 50}
            mock_items.return_value = [bomb_item]

            dispose()

            mock_disposed.assert_called_once_with('bomb1')

    def test_dispose_already_handled_item_fails(self):
        """Given previously handled item, when dispose(), then failure result"""
        from engine.api import dispose

        with patch('engine.api.get_current_position') as mock_pos, \
             patch('engine.api.get_items_at_position') as mock_items, \
             patch('engine.api.is_item_already_handled') as mock_handled:

            mock_pos.return_value = (2, 2)
            mock_items.return_value = [{'id': 'bomb1', 'type': 'bomb', 'damage': 50}]
            mock_handled.return_value = True

            result = dispose()

            assert isinstance(result, ExecutionResult), "dispose() should return ExecutionResult"
            assert result.success is False, "dispose() should fail for already handled items"