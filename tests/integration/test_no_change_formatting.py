"""
Integration test for no change default formatting functionality.
Based on quickstart scenario 4: No Change Behavior.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestNoChangeFormatting(unittest.TestCase):
    """Integration tests for no change default formatting based on quickstart scenarios."""

    @patch('pygame.font.Font')
    def test_no_change_default_formatting_integration(self, mock_font):
        """
        Integration test: No status change displays in default white text.

        Scenario from quickstart.md:
        1. Setup: Any HP value
        2. Action: Perform action that doesn't affect HP (move, turn)
        3. Verify: Status displays in default white text
        4. Verify: No change indicators (↓ or ↑) displayed
        5. Verify: Normal font weight (not bold)
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        entity_id = "player"
        status = {"hp": 75, "attack": 18}
        same_status = {"hp": 75, "attack": 18}  # Identical to previous

        # Act - Establish baseline then no change
        tracker.track_changes(entity_id, status)
        change_result = tracker.track_changes(entity_id, same_status)

        # Format for display
        hp_change = change_result.status_changes.get("hp", 0)
        attack_change = change_result.status_changes.get("attack", 0)

        hp_formatted = display_manager.format_status_text(
            entity_id, "hp", same_status["hp"], hp_change
        )
        attack_formatted = display_manager.format_status_text(
            entity_id, "attack", same_status["attack"], attack_change
        )

        # Assert - Default formatting requirements
        self.assertFalse(change_result.has_any_changes)
        self.assertEqual(hp_change, 0)
        self.assertEqual(attack_change, 0)

        # HP formatting
        self.assertFalse(hp_formatted.is_bold)
        self.assertEqual(hp_formatted.color, (255, 255, 255))  # White color
        self.assertNotIn("↓", hp_formatted.content)
        self.assertNotIn("↑", hp_formatted.content)
        self.assertEqual(hp_formatted.content, "75")

        # Attack formatting
        self.assertFalse(attack_formatted.is_bold)
        self.assertEqual(attack_formatted.color, (255, 255, 255))  # White color
        self.assertNotIn("↓", attack_formatted.content)
        self.assertNotIn("↑", attack_formatted.content)

        # Verify emphasis type
        from engine.gui_enhancement.display_types import EmphasisType
        self.assertEqual(hp_formatted.emphasis_type, EmphasisType.DEFAULT)
        self.assertEqual(attack_formatted.emphasis_type, EmphasisType.DEFAULT)

    @patch('pygame.font.Font')
    def test_first_update_no_change_integration(self, mock_font):
        """
        Integration test: First status update shows no change (baseline establishment).
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        entity_id = "player"
        initial_status = {"hp": 100, "attack": 20, "defense": 15}

        # Act - First update (establishes baseline)
        change_result = tracker.track_changes(entity_id, initial_status)

        # Format all status values
        formatted_results = {}
        for status_key, value in initial_status.items():
            change = change_result.status_changes.get(status_key, 0)
            formatted_results[status_key] = display_manager.format_status_text(
                entity_id, status_key, value, change
            )

        # Assert - All should be default formatting (no baseline to compare)
        self.assertFalse(change_result.has_any_changes)

        for status_key, formatted in formatted_results.items():
            self.assertFalse(formatted.is_bold, f"{status_key} should not be bold")
            self.assertEqual(formatted.color, (255, 255, 255), f"{status_key} should be white")
            self.assertNotIn("↓", formatted.content, f"{status_key} should not have decrease symbol")
            self.assertNotIn("↑", formatted.content, f"{status_key} should not have increase symbol")

    @patch('pygame.font.Font')
    def test_return_to_default_after_change_integration(self, mock_font):
        """
        Integration test: Status returns to default formatting after highlighted change.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        entity_id = "player"
        status1 = {"hp": 100}
        status2 = {"hp": 85}  # Damage
        status3 = {"hp": 85}  # No change

        # Act - Sequence: baseline → change → no change
        tracker.track_changes(entity_id, status1)
        change_result_damage = tracker.track_changes(entity_id, status2)
        change_result_no_change = tracker.track_changes(entity_id, status3)

        # Format damage turn
        damage_formatted = display_manager.format_status_text(
            entity_id, "hp", status2["hp"], change_result_damage.status_changes["hp"]
        )

        # Format no change turn
        no_change_formatted = display_manager.format_status_text(
            entity_id, "hp", status3["hp"], change_result_no_change.status_changes.get("hp", 0)
        )

        # Assert - Damage turn should be highlighted
        self.assertTrue(damage_formatted.is_bold)
        self.assertEqual(damage_formatted.color, (255, 0, 0))  # Red
        self.assertIn("↓", damage_formatted.content)

        # No change turn should be default
        self.assertFalse(no_change_formatted.is_bold)
        self.assertEqual(no_change_formatted.color, (255, 255, 255))  # White
        self.assertNotIn("↓", no_change_formatted.content)
        self.assertNotIn("↑", no_change_formatted.content)

    @patch('pygame.font.Font')
    def test_mixed_change_and_no_change_integration(self, mock_font):
        """
        Integration test: Some statuses change while others don't.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        entity_id = "player"
        status1 = {"hp": 100, "attack": 20, "defense": 15}
        status2 = {"hp": 90, "attack": 20, "defense": 18}  # hp down, defense up, attack same

        # Act
        tracker.track_changes(entity_id, status1)
        change_result = tracker.track_changes(entity_id, status2)

        # Format all statuses
        hp_formatted = display_manager.format_status_text(
            entity_id, "hp", status2["hp"], change_result.status_changes["hp"]
        )
        attack_formatted = display_manager.format_status_text(
            entity_id, "attack", status2["attack"], change_result.status_changes.get("attack", 0)
        )
        defense_formatted = display_manager.format_status_text(
            entity_id, "defense", status2["defense"], change_result.status_changes["defense"]
        )

        # Assert - Each should have appropriate formatting
        # HP decreased (highlighted)
        self.assertTrue(hp_formatted.is_bold)
        self.assertEqual(hp_formatted.color, (255, 0, 0))  # Red
        self.assertIn("↓", hp_formatted.content)

        # Attack unchanged (default)
        self.assertFalse(attack_formatted.is_bold)
        self.assertEqual(attack_formatted.color, (255, 255, 255))  # White
        self.assertNotIn("↓", attack_formatted.content)
        self.assertNotIn("↑", attack_formatted.content)

        # Defense increased (highlighted)
        self.assertTrue(defense_formatted.is_bold)
        self.assertEqual(defense_formatted.color, (0, 255, 0))  # Green
        self.assertIn("↑", defense_formatted.content)

    @patch('pygame.font.Font')
    def test_zero_value_no_change_integration(self, mock_font):
        """
        Integration test: Zero values with no change display correctly.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        entity_id = "player"
        status_with_zero = {"hp": 0, "attack": 0}
        same_zero_status = {"hp": 0, "attack": 0}

        # Act
        tracker.track_changes(entity_id, status_with_zero)
        change_result = tracker.track_changes(entity_id, same_zero_status)

        # Format zero values
        hp_formatted = display_manager.format_status_text(
            entity_id, "hp", same_zero_status["hp"], change_result.status_changes.get("hp", 0)
        )

        # Assert - Zero with no change should be default
        self.assertFalse(change_result.has_any_changes)
        self.assertFalse(hp_formatted.is_bold)
        self.assertEqual(hp_formatted.color, (255, 255, 255))
        self.assertEqual(hp_formatted.content, "0")


if __name__ == '__main__':
    unittest.main()