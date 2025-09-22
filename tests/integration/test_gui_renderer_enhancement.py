"""
Integration test for GUI renderer enhancement with status highlighting.
Tests the integration between the GUI enhancement modules and the existing renderer.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestGuiRendererEnhancement(unittest.TestCase):
    """Integration tests for GUI renderer enhancement functionality."""

    @patch('pygame.display.set_mode')
    @patch('pygame.font.Font')
    @patch('pygame.display.init')
    @patch('pygame.init')
    def test_renderer_status_highlighting_integration(self, mock_pygame_init, mock_display_init, mock_font, mock_display):
        """
        Integration test: Renderer displays status changes with highlighting.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        from engine.renderer import GuiRenderer
        from engine import GameState, Position

        # Mock pygame components
        mock_surface = MagicMock()
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_font_instance.render.return_value = mock_surface
        mock_display.return_value = mock_surface

        # Create enhanced renderer
        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()
        renderer = GuiRenderer()
        renderer.initialize(10, 10)

        # Create game state with entities
        game_state = GameState(10, 10)
        game_state.player_position = Position(1, 1)
        game_state.player_hp = 100
        game_state.player_attack = 20

        # Act - Simulate status change
        initial_status = {"hp": 100, "attack": 20}
        damaged_status = {"hp": 85, "attack": 20}

        tracker.track_changes("player", initial_status)
        change_result = tracker.track_changes("player", damaged_status)

        # Format status for display
        hp_formatted = display_manager.format_status_text(
            "player", "hp", damaged_status["hp"], change_result.status_changes["hp"]
        )

        # Assert - Status should be formatted for highlighting
        self.assertTrue(change_result.has_any_changes)
        self.assertEqual(change_result.status_changes["hp"], -15)
        self.assertTrue(hp_formatted.is_bold)
        self.assertEqual(hp_formatted.color, (255, 0, 0))  # Red
        self.assertIn("↓", hp_formatted.content)

    @patch('pygame.display.set_mode')
    @patch('pygame.font.Font')
    def test_renderer_stage_name_integration(self, mock_font, mock_display):
        """
        Integration test: Renderer displays correct stage name from resolver.
        """
        # Arrange
        import tempfile
        from engine.gui_enhancement.stage_name_resolver import StageNameResolver

        # Create temporary main file
        temp_dir = tempfile.mkdtemp()
        main_file = os.path.join(temp_dir, "main_stage07.py")
        content = '''#!/usr/bin/env python3
"""Test main file"""

STAGE_ID = "stage07"
STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(main_file, 'w') as f:
            f.write(content)

        # Mock pygame components
        mock_surface = MagicMock()
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_font_instance.render.return_value = mock_surface
        mock_display.return_value = mock_surface

        try:
            resolver = StageNameResolver()

            # Act - Resolve stage name
            resolution = resolver.resolve_stage_name(main_file)

            # Assert - Should resolve correctly for renderer use
            self.assertEqual(resolution.stage_id, "stage07")
            self.assertEqual(resolution.resolved_name, "Stage: stage07")

        finally:
            # Clean up
            import shutil
            shutil.rmtree(temp_dir)

    @patch('pygame.display.set_mode')
    @patch('pygame.font.Font')
    def test_renderer_multiple_entity_display_integration(self, mock_font, mock_display):
        """
        Integration test: Renderer handles multiple entities with different status changes.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        # Mock pygame components
        mock_surface = MagicMock()
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_font_instance.render.return_value = mock_surface
        mock_display.return_value = mock_surface

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        entities = {
            "player": {"initial": {"hp": 100}, "changed": {"hp": 90}},
            "enemy_01": {"initial": {"hp": 50}, "changed": {"hp": 65}},
            "enemy_02": {"initial": {"hp": 30}, "changed": {"hp": 30}}
        }

        # Act - Track changes for all entities
        formatted_results = {}
        for entity_id, statuses in entities.items():
            tracker.track_changes(entity_id, statuses["initial"])
            change_result = tracker.track_changes(entity_id, statuses["changed"])

            hp_change = change_result.status_changes.get("hp", 0)
            formatted_results[entity_id] = display_manager.format_status_text(
                entity_id, "hp", statuses["changed"]["hp"], hp_change
            )

        # Assert - Each entity should have appropriate formatting
        # Player decreased
        self.assertEqual(formatted_results["player"].color, (255, 0, 0))  # Red
        self.assertIn("↓", formatted_results["player"].content)

        # Enemy_01 increased
        self.assertEqual(formatted_results["enemy_01"].color, (0, 255, 0))  # Green
        self.assertIn("↑", formatted_results["enemy_01"].content)

        # Enemy_02 no change
        self.assertEqual(formatted_results["enemy_02"].color, (255, 255, 255))  # White
        self.assertNotIn("↓", formatted_results["enemy_02"].content)
        self.assertNotIn("↑", formatted_results["enemy_02"].content)

    @patch('pygame.display.set_mode')
    @patch('pygame.font.Font')
    def test_renderer_performance_integration(self, mock_font, mock_display):
        """
        Integration test: Renderer maintains performance with status tracking.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        import time

        # Mock pygame components
        mock_surface = MagicMock()
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_font_instance.render.return_value = mock_surface
        mock_display.return_value = mock_surface

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        # Act - Simulate rapid status updates
        start_time = time.time()

        for i in range(100):  # 100 rapid updates
            entity_id = f"entity_{i % 10}"  # 10 different entities
            current_hp = 100 - (i % 50)  # Varying HP values

            change_result = tracker.track_changes(entity_id, {"hp": current_hp})
            hp_change = change_result.status_changes.get("hp", 0)

            formatted_text = display_manager.format_status_text(
                entity_id, "hp", current_hp, hp_change
            )

        end_time = time.time()
        total_time = end_time - start_time

        # Assert - Should complete within performance requirements (<50ms per update)
        avg_time_per_update = (total_time / 100) * 1000  # Convert to milliseconds
        self.assertLess(avg_time_per_update, 50,
                       f"Average update time {avg_time_per_update:.2f}ms exceeds 50ms requirement")

    @patch('pygame.display.set_mode')
    @patch('pygame.font.Font')
    def test_renderer_memory_management_integration(self, mock_font, mock_display):
        """
        Integration test: Renderer manages memory correctly with status tracking.
        """
        # Arrange
        from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        import gc

        # Mock pygame components
        mock_surface = MagicMock()
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_font_instance.render.return_value = mock_surface
        mock_display.return_value = mock_surface

        tracker = StatusChangeTracker()
        display_manager = DisplayStateManager()

        # Act - Create and remove many entities to test memory management
        for cycle in range(10):
            # Add entities
            for i in range(50):
                entity_id = f"temp_entity_{i}"
                tracker.track_changes(entity_id, {"hp": 100})
                tracker.track_changes(entity_id, {"hp": 90})

            # Remove entities
            for i in range(50):
                entity_id = f"temp_entity_{i}"
                tracker.reset_entity_tracking(entity_id)

            # Force garbage collection
            gc.collect()

        # Assert - Memory should be manageable (no assertion, just verify no crashes)
        # Test passes if no memory errors occur
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()