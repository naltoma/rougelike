"""
Integration test for status decrease highlighting functionality.
Based on quickstart scenario 2: Status Decrease Highlighting.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestStatusDecreaseHighlighting(unittest.TestCase):
    """Integration tests for status decrease highlighting based on quickstart scenarios."""

    @patch('pygame.font.Font')
    def test_hp_decrease_highlighting_integration(self, mock_font):
        """
        Integration test: HP decrease shows red bold text with ↓ symbol.

        Scenario from quickstart.md:
        1. Setup: Start game with full HP (100/100)
        2. Action: Perform action that causes damage
        3. Verify: Status shows red bold text with decrease indicator
        4. Example: `90/100 ↓10` in red bold font
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
        initial_status = {"hp": 100, "max_hp": 100}
        damaged_status = {"hp": 90, "max_hp": 100}

        # Act - First update to establish baseline
        tracker.track_changes(entity_id, initial_status)

        # Simulate damage
        change_result = tracker.track_changes(entity_id, damaged_status)

        # Format for display
        hp_change = change_result.status_changes.get("hp", 0)
        formatted_text = display_manager.format_status_text(
            entity_id, "hp", damaged_status["hp"], hp_change
        )

        # Assert - Check highlighting behavior
        self.assertTrue(change_result.has_any_changes)
        self.assertEqual(hp_change, -10)  # Decrease of 10

        # Check formatted text properties
        self.assertTrue(formatted_text.is_bold)
        self.assertEqual(formatted_text.color, (255, 0, 0))  # Red color
        self.assertIn("↓", formatted_text.content)
        self.assertIn("10", formatted_text.content)  # Change amount

        # Verify emphasis type
        from engine.gui_enhancement.display_types import EmphasisType
        self.assertEqual(formatted_text.emphasis_type, EmphasisType.DECREASED)

    @patch('pygame.font.Font')
    def test_multiple_status_decrease_integration(self, mock_font):
        """
        Integration test: Multiple status decreases all highlighted properly.
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
        damaged_status = {"hp": 85, "attack": 18, "defense": 12}

        # Act
        tracker.track_changes(entity_id, initial_status)
        change_result = tracker.track_changes(entity_id, damaged_status)

        # Format each changed status
        hp_formatted = display_manager.format_status_text(
            entity_id, "hp", damaged_status["hp"], change_result.status_changes["hp"]
        )
        attack_formatted = display_manager.format_status_text(
            entity_id, "attack", damaged_status["attack"], change_result.status_changes["attack"]
        )
        defense_formatted = display_manager.format_status_text(
            entity_id, "defense", damaged_status["defense"], change_result.status_changes["defense"]
        )

        # Assert - All should be highlighted as decreased
        self.assertTrue(hp_formatted.is_bold)
        self.assertTrue(attack_formatted.is_bold)
        self.assertTrue(defense_formatted.is_bold)

        # All should be red color
        self.assertEqual(hp_formatted.color, (255, 0, 0))
        self.assertEqual(attack_formatted.color, (255, 0, 0))
        self.assertEqual(defense_formatted.color, (255, 0, 0))

        # All should have decrease symbols
        self.assertIn("↓", hp_formatted.content)
        self.assertIn("↓", attack_formatted.content)
        self.assertIn("↓", defense_formatted.content)

    @patch('pygame.font.Font')
    def test_next_turn_default_formatting_integration(self, mock_font):
        """
        Integration test: Next turn with no change returns to default formatting.

        Scenario from quickstart.md:
        5. Next Turn: No damage taken
        6. Verify: Status returns to default `90/100` formatting
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
        initial_status = {"hp": 100}
        damaged_status = {"hp": 90}
        no_change_status = {"hp": 90}  # Same as previous turn

        # Act - Simulate sequence of turns
        tracker.track_changes(entity_id, initial_status)
        tracker.track_changes(entity_id, damaged_status)  # Damage turn
        change_result_no_change = tracker.track_changes(entity_id, no_change_status)  # No change turn

        # Format for display
        hp_change = change_result_no_change.status_changes.get("hp", 0)
        formatted_text = display_manager.format_status_text(
            entity_id, "hp", no_change_status["hp"], hp_change
        )

        # Assert - Should be default formatting
        self.assertFalse(change_result_no_change.has_any_changes)
        self.assertEqual(hp_change, 0)  # No change

        # Check default formatting
        self.assertFalse(formatted_text.is_bold)
        self.assertEqual(formatted_text.color, (255, 255, 255))  # White/default color
        self.assertNotIn("↓", formatted_text.content)
        self.assertNotIn("↑", formatted_text.content)

        # Verify emphasis type
        from engine.gui_enhancement.display_types import EmphasisType
        self.assertEqual(formatted_text.emphasis_type, EmphasisType.DEFAULT)

    @patch('pygame.font.Font')
    def test_enemy_status_decrease_integration(self, mock_font):
        """
        Integration test: Enemy status decreases also highlighted properly.
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

        enemy_id = "enemy_01"
        initial_status = {"hp": 50}
        damaged_status = {"hp": 35}

        # Act
        tracker.track_changes(enemy_id, initial_status)
        change_result = tracker.track_changes(enemy_id, damaged_status)

        # Format for display
        hp_change = change_result.status_changes["hp"]
        formatted_text = display_manager.format_status_text(
            enemy_id, "hp", damaged_status["hp"], hp_change
        )

        # Assert - Enemy damage should also be highlighted
        self.assertEqual(hp_change, -15)
        self.assertTrue(formatted_text.is_bold)
        self.assertEqual(formatted_text.color, (255, 0, 0))  # Red color
        self.assertIn("↓", formatted_text.content)
        self.assertIn("15", formatted_text.content)


if __name__ == '__main__':
    unittest.main()