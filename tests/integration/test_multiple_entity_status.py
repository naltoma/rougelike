"""
Integration test for multiple entity status tracking functionality.
Based on quickstart scenario 3: Multiple Entity Status Test.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestMultipleEntityStatus(unittest.TestCase):
    """Integration tests for multiple entity status tracking based on quickstart scenarios."""

    @patch('pygame.font.Font')
    def test_player_and_enemy_status_tracking_integration(self, mock_font):
        """
        Integration test: Both player and enemy status changes are tracked independently.

        Scenario from quickstart.md:
        - Player takes damage → red highlighting
        - Enemy takes damage → red highlighting
        - Both entities when no change → default formatting
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

        player_id = "player"
        enemy_id = "enemy_01"

        # Initial status
        player_initial = {"hp": 100, "attack": 20}
        enemy_initial = {"hp": 50, "attack": 15}

        # After combat - both take damage
        player_damaged = {"hp": 85, "attack": 20}
        enemy_damaged = {"hp": 35, "attack": 15}

        # Act - Track changes for both entities
        tracker.track_changes(player_id, player_initial)
        tracker.track_changes(enemy_id, enemy_initial)

        player_changes = tracker.track_changes(player_id, player_damaged)
        enemy_changes = tracker.track_changes(enemy_id, enemy_damaged)

        # Format for display
        player_hp_formatted = display_manager.format_status_text(
            player_id, "hp", player_damaged["hp"], player_changes.status_changes["hp"]
        )
        enemy_hp_formatted = display_manager.format_status_text(
            enemy_id, "hp", enemy_damaged["hp"], enemy_changes.status_changes["hp"]
        )

        # Assert - Both should show damage highlighting
        # Player damage highlighting
        self.assertEqual(player_changes.status_changes["hp"], -15)
        self.assertTrue(player_hp_formatted.is_bold)
        self.assertEqual(player_hp_formatted.color, (255, 0, 0))  # Red
        self.assertIn("↓", player_hp_formatted.content)

        # Enemy damage highlighting
        self.assertEqual(enemy_changes.status_changes["hp"], -15)
        self.assertTrue(enemy_hp_formatted.is_bold)
        self.assertEqual(enemy_hp_formatted.color, (255, 0, 0))  # Red
        self.assertIn("↓", enemy_hp_formatted.content)

    @patch('pygame.font.Font')
    def test_independent_entity_tracking_integration(self, mock_font):
        """
        Integration test: Entity status changes are tracked independently.
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

        player_id = "player"
        enemy1_id = "enemy_01"
        enemy2_id = "enemy_02"

        # Set up different scenarios for each entity
        player_status1 = {"hp": 100}
        player_status2 = {"hp": 90}  # Player takes damage

        enemy1_status1 = {"hp": 50}
        enemy1_status2 = {"hp": 60}  # Enemy1 heals

        enemy2_status1 = {"hp": 30}
        enemy2_status2 = {"hp": 30}  # Enemy2 no change

        # Act - Track all entities
        tracker.track_changes(player_id, player_status1)
        tracker.track_changes(enemy1_id, enemy1_status1)
        tracker.track_changes(enemy2_id, enemy2_status1)

        player_changes = tracker.track_changes(player_id, player_status2)
        enemy1_changes = tracker.track_changes(enemy1_id, enemy1_status2)
        enemy2_changes = tracker.track_changes(enemy2_id, enemy2_status2)

        # Format displays
        player_formatted = display_manager.format_status_text(
            player_id, "hp", player_status2["hp"], player_changes.status_changes["hp"]
        )
        enemy1_formatted = display_manager.format_status_text(
            enemy1_id, "hp", enemy1_status2["hp"], enemy1_changes.status_changes["hp"]
        )
        enemy2_formatted = display_manager.format_status_text(
            enemy2_id, "hp", enemy2_status2["hp"], enemy2_changes.status_changes.get("hp", 0)
        )

        # Assert - Each entity should have different formatting
        # Player decreased (red)
        self.assertEqual(player_formatted.color, (255, 0, 0))
        self.assertIn("↓", player_formatted.content)

        # Enemy1 increased (green)
        self.assertEqual(enemy1_formatted.color, (0, 255, 0))
        self.assertIn("↑", enemy1_formatted.content)

        # Enemy2 no change (default)
        self.assertEqual(enemy2_formatted.color, (255, 255, 255))
        self.assertNotIn("↑", enemy2_formatted.content)
        self.assertNotIn("↓", enemy2_formatted.content)

    @patch('pygame.font.Font')
    def test_multiple_entity_reset_integration(self, mock_font):
        """
        Integration test: Resetting one entity doesn't affect others.
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

        player_id = "player"
        enemy_id = "enemy_01"

        # Set up both entities with changes
        tracker.track_changes(player_id, {"hp": 100})
        tracker.track_changes(enemy_id, {"hp": 50})

        player_changes = tracker.track_changes(player_id, {"hp": 90})
        enemy_changes = tracker.track_changes(enemy_id, {"hp": 40})

        # Verify both have changes
        self.assertTrue(player_changes.has_any_changes)
        self.assertTrue(enemy_changes.has_any_changes)

        # Act - Reset only player
        tracker.reset_entity_tracking(player_id)

        # Assert - Player should have no history, enemy should keep history
        self.assertFalse(tracker.has_changes(player_id))
        self.assertTrue(tracker.has_changes(enemy_id))

        # New changes should work correctly
        new_player_changes = tracker.track_changes(player_id, {"hp": 95})
        self.assertFalse(new_player_changes.has_any_changes)  # First update after reset

    @patch('pygame.font.Font')
    def test_simultaneous_multiple_entity_changes_integration(self, mock_font):
        """
        Integration test: Multiple entities changing simultaneously are handled correctly.
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

        entities = ["player", "enemy_01", "enemy_02", "enemy_03"]
        initial_statuses = {
            "player": {"hp": 100, "attack": 20},
            "enemy_01": {"hp": 50, "attack": 15},
            "enemy_02": {"hp": 40, "attack": 12},
            "enemy_03": {"hp": 60, "attack": 18}
        }
        changed_statuses = {
            "player": {"hp": 85, "attack": 25},  # hp down, attack up
            "enemy_01": {"hp": 35, "attack": 15},  # hp down
            "enemy_02": {"hp": 55, "attack": 12},  # hp up
            "enemy_03": {"hp": 60, "attack": 18}   # no change
        }

        # Act - Set up initial states
        for entity_id, status in initial_statuses.items():
            tracker.track_changes(entity_id, status)

        # Track changes for all entities
        change_results = {}
        for entity_id, status in changed_statuses.items():
            change_results[entity_id] = tracker.track_changes(entity_id, status)

        # Assert - Verify each entity has correct change tracking
        # Player: hp decreased, attack increased
        self.assertEqual(change_results["player"].status_changes["hp"], -15)
        self.assertEqual(change_results["player"].status_changes["attack"], 5)

        # Enemy_01: hp decreased
        self.assertEqual(change_results["enemy_01"].status_changes["hp"], -15)
        self.assertNotIn("attack", change_results["enemy_01"].status_changes)

        # Enemy_02: hp increased
        self.assertEqual(change_results["enemy_02"].status_changes["hp"], 15)

        # Enemy_03: no changes
        self.assertFalse(change_results["enemy_03"].has_any_changes)

    @patch('pygame.font.Font')
    def test_entity_lifecycle_integration(self, mock_font):
        """
        Integration test: Entity removal and re-addition works correctly.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker

        tracker = StatusChangeTracker()

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        entity_id = "enemy_01"

        # Act - Add entity, track changes, remove, re-add
        tracker.track_changes(entity_id, {"hp": 50})
        changes1 = tracker.track_changes(entity_id, {"hp": 40})

        # Verify change was tracked
        self.assertTrue(changes1.has_any_changes)

        # Remove entity
        tracker.reset_entity_tracking(entity_id)

        # Re-add with different HP
        changes2 = tracker.track_changes(entity_id, {"hp": 60})

        # Assert - Should be treated as new entity (no changes)
        self.assertFalse(changes2.has_any_changes)


if __name__ == '__main__':
    unittest.main()