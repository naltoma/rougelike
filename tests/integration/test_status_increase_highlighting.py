"""
Integration test for status increase highlighting functionality.
Based on quickstart scenario 3: Status Increase Highlighting.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestStatusIncreaseHighlighting(unittest.TestCase):
    """Integration tests for status increase highlighting based on quickstart scenarios."""

    @patch('pygame.font.Font')
    def test_hp_increase_highlighting_integration(self, mock_font):
        """
        Integration test: HP increase shows green bold text with ↑ symbol.

        Scenario from quickstart.md:
        1. Setup: Start with reduced HP (90/100)
        2. Action: Use healing item or ability
        3. Verify: Status shows green bold text with increase indicator
        4. Example: `100/100 ↑10` in green bold font
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
        damaged_status = {"hp": 90, "max_hp": 100}
        healed_status = {"hp": 100, "max_hp": 100}

        # Act - Establish baseline with damaged status
        tracker.track_changes(entity_id, damaged_status)

        # Simulate healing
        change_result = tracker.track_changes(entity_id, healed_status)

        # Format for display
        hp_change = change_result.status_changes.get("hp", 0)
        formatted_text = display_manager.format_status_text(
            entity_id, "hp", healed_status["hp"], hp_change
        )

        # Assert - Check healing highlighting behavior
        self.assertTrue(change_result.has_any_changes)
        self.assertEqual(hp_change, 10)  # Increase of 10

        # Check formatted text properties
        self.assertTrue(formatted_text.is_bold)
        self.assertEqual(formatted_text.color, (0, 255, 0))  # Green color
        self.assertIn("↑", formatted_text.content)
        self.assertIn("10", formatted_text.content)  # Change amount

        # Verify emphasis type
        from engine.gui_enhancement.display_types import EmphasisType
        self.assertEqual(formatted_text.emphasis_type, EmphasisType.INCREASED)

    @patch('pygame.font.Font')
    def test_multiple_status_increase_integration(self, mock_font):
        """
        Integration test: Multiple status increases all highlighted properly.
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
        initial_status = {"hp": 80, "attack": 15, "defense": 10}
        buffed_status = {"hp": 95, "attack": 20, "defense": 15}

        # Act
        tracker.track_changes(entity_id, initial_status)
        change_result = tracker.track_changes(entity_id, buffed_status)

        # Format each changed status
        hp_formatted = display_manager.format_status_text(
            entity_id, "hp", buffed_status["hp"], change_result.status_changes["hp"]
        )
        attack_formatted = display_manager.format_status_text(
            entity_id, "attack", buffed_status["attack"], change_result.status_changes["attack"]
        )
        defense_formatted = display_manager.format_status_text(
            entity_id, "defense", buffed_status["defense"], change_result.status_changes["defense"]
        )

        # Assert - All should be highlighted as increased
        self.assertTrue(hp_formatted.is_bold)
        self.assertTrue(attack_formatted.is_bold)
        self.assertTrue(defense_formatted.is_bold)

        # All should be green color
        self.assertEqual(hp_formatted.color, (0, 255, 0))
        self.assertEqual(attack_formatted.color, (0, 255, 0))
        self.assertEqual(defense_formatted.color, (0, 255, 0))

        # All should have increase symbols
        self.assertIn("↑", hp_formatted.content)
        self.assertIn("↑", attack_formatted.content)
        self.assertIn("↑", defense_formatted.content)

    @patch('pygame.font.Font')
    def test_partial_healing_integration(self, mock_font):
        """
        Integration test: Partial healing shows correct increase amount.
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
        low_hp_status = {"hp": 25}
        partial_heal_status = {"hp": 40}

        # Act
        tracker.track_changes(entity_id, low_hp_status)
        change_result = tracker.track_changes(entity_id, partial_heal_status)

        # Format for display
        hp_change = change_result.status_changes["hp"]
        formatted_text = display_manager.format_status_text(
            entity_id, "hp", partial_heal_status["hp"], hp_change
        )

        # Assert - Partial healing highlighting
        self.assertEqual(hp_change, 15)  # Increase of 15
        self.assertTrue(formatted_text.is_bold)
        self.assertEqual(formatted_text.color, (0, 255, 0))
        self.assertIn("↑", formatted_text.content)
        self.assertIn("15", formatted_text.content)

    @patch('pygame.font.Font')
    def test_next_turn_after_healing_default_formatting(self, mock_font):
        """
        Integration test: Next turn after healing returns to default formatting.

        Scenario from quickstart.md:
        5. Next Turn: No healing action
        6. Verify: Status returns to default `100/100` formatting
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
        damaged_status = {"hp": 90}
        healed_status = {"hp": 100}
        no_change_status = {"hp": 100}  # Same as previous turn

        # Act - Simulate sequence of turns
        tracker.track_changes(entity_id, damaged_status)
        tracker.track_changes(entity_id, healed_status)  # Healing turn
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
    def test_mixed_status_changes_integration(self, mock_font):
        """
        Integration test: Mixed status changes (some increase, some decrease, some no change).
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
        initial_status = {"hp": 80, "attack": 15, "defense": 12}
        mixed_status = {"hp": 95, "attack": 10, "defense": 12}  # hp up, attack down, defense same

        # Act
        tracker.track_changes(entity_id, initial_status)
        change_result = tracker.track_changes(entity_id, mixed_status)

        # Format each status
        hp_formatted = display_manager.format_status_text(
            entity_id, "hp", mixed_status["hp"], change_result.status_changes["hp"]
        )
        attack_formatted = display_manager.format_status_text(
            entity_id, "attack", mixed_status["attack"], change_result.status_changes["attack"]
        )
        defense_formatted = display_manager.format_status_text(
            entity_id, "defense", mixed_status["defense"], change_result.status_changes.get("defense", 0)
        )

        # Assert - Each should have appropriate formatting
        # HP increased
        self.assertEqual(hp_formatted.color, (0, 255, 0))  # Green
        self.assertIn("↑", hp_formatted.content)

        # Attack decreased
        self.assertEqual(attack_formatted.color, (255, 0, 0))  # Red
        self.assertIn("↓", attack_formatted.content)

        # Defense unchanged (should be default)
        self.assertEqual(defense_formatted.color, (255, 255, 255))  # White
        self.assertNotIn("↑", defense_formatted.content)
        self.assertNotIn("↓", defense_formatted.content)


if __name__ == '__main__':
    unittest.main()