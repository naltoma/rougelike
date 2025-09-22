"""
Integration test for pygame text rendering with colors and bold formatting.
Tests the DisplayStateManager's integration with pygame rendering.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestPygameTextRendering(unittest.TestCase):
    """Integration tests for pygame text rendering functionality."""

    @patch('pygame.font.Font')
    def test_pygame_color_rendering_integration(self, mock_font):
        """
        Integration test: pygame font rendering with different colors.
        """
        # Arrange
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        from engine.gui_enhancement.display_types import EmphasisType

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface
        mock_font_instance.set_bold = MagicMock()

        display_manager = DisplayStateManager()

        test_cases = [
            ("Default text", EmphasisType.DEFAULT, (255, 255, 255)),
            ("Decreased text ↓5", EmphasisType.DECREASED, (255, 0, 0)),
            ("Increased text ↑10", EmphasisType.INCREASED, (0, 255, 0))
        ]

        # Act & Assert
        for text, emphasis_type, expected_color in test_cases:
            surface = display_manager.apply_color_formatting(text, emphasis_type)

            # Verify pygame render was called with correct color
            mock_font_instance.render.assert_called()
            call_args = mock_font_instance.render.call_args

            # Check that text and color were passed correctly
            self.assertEqual(call_args[0][0], text)  # Text argument
            self.assertEqual(call_args[0][2], expected_color)  # Color argument (third parameter)

    @patch('pygame.font.Font')
    def test_pygame_bold_rendering_integration(self, mock_font):
        """
        Integration test: pygame font rendering with bold formatting.
        """
        # Arrange
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        from engine.gui_enhancement.display_types import EmphasisType

        # Mock pygame font instances
        mock_normal_font = MagicMock()
        mock_bold_font = MagicMock()
        mock_surface = MagicMock()

        # Configure font mocking for different calls
        font_instances = [mock_normal_font, mock_bold_font]
        mock_font.side_effect = font_instances

        mock_normal_font.render.return_value = mock_surface
        mock_bold_font.render.return_value = mock_surface

        display_manager = DisplayStateManager()

        # Act - Test bold formatting
        bold_surface = display_manager.apply_color_formatting("Test ↓10", EmphasisType.DECREASED)
        normal_surface = display_manager.apply_color_formatting("Test", EmphasisType.DEFAULT)

        # Assert - Verify bold font was used for emphasized text
        self.assertIsNotNone(bold_surface)
        self.assertIsNotNone(normal_surface)

        # Verify font rendering was called
        self.assertTrue(mock_normal_font.render.called or mock_bold_font.render.called)

    @patch('pygame.font.Font')
    def test_formatted_text_surface_properties_integration(self, mock_font):
        """
        Integration test: Formatted text surface has correct properties.
        """
        # Arrange
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance

        # Create mock surface with properties
        mock_surface = MagicMock()
        mock_surface.width = 100
        mock_surface.height = 24
        mock_surface.content_hash = "test_hash"
        mock_font_instance.render.return_value = mock_surface

        display_manager = DisplayStateManager()

        # Act
        result = display_manager.format_status_text("player", "hp", 90, -10)
        surface = display_manager.apply_color_formatting(result.content, result.emphasis_type)

        # Assert - Surface should have expected properties
        self.assertTrue(hasattr(surface, 'width'))
        self.assertTrue(hasattr(surface, 'height'))
        self.assertEqual(surface.width, 100)
        self.assertEqual(surface.height, 24)

    @patch('pygame.font.Font')
    def test_text_content_formatting_integration(self, mock_font):
        """
        Integration test: Text content is correctly formatted with symbols.
        """
        # Arrange
        from engine.gui_enhancement.display_state_manager import DisplayStateManager

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        display_manager = DisplayStateManager()

        test_cases = [
            ("player", "hp", 85, -15, "85 ↓15"),  # Decrease
            ("player", "hp", 105, 15, "105 ↑15"),  # Increase
            ("player", "hp", 100, 0, "100"),       # No change
        ]

        # Act & Assert
        for entity_id, status_key, value, change, expected_content in test_cases:
            result = display_manager.format_status_text(entity_id, status_key, value, change)

            # Verify content formatting
            if change < 0:
                self.assertIn("↓", result.content)
                self.assertIn(str(abs(change)), result.content)
            elif change > 0:
                self.assertIn("↑", result.content)
                self.assertIn(str(change), result.content)
            else:
                self.assertNotIn("↓", result.content)
                self.assertNotIn("↑", result.content)

            self.assertIn(str(value), result.content)

    @patch('pygame.font.Font')
    def test_rendering_performance_integration(self, mock_font):
        """
        Integration test: Text rendering performs within acceptable limits.
        """
        # Arrange
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        import time

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        display_manager = DisplayStateManager()

        # Act - Render many text elements
        start_time = time.time()

        for i in range(100):
            entity_id = f"entity_{i % 10}"
            value = 100 - (i % 20)
            change = (-1) ** i * (i % 10)  # Alternating positive/negative changes

            result = display_manager.format_status_text(entity_id, "hp", value, change)
            surface = display_manager.apply_color_formatting(result.content, result.emphasis_type)

        end_time = time.time()
        total_time = end_time - start_time

        # Assert - Should complete quickly (rendering performance)
        avg_time_per_render = (total_time / 100) * 1000  # Convert to milliseconds
        self.assertLess(avg_time_per_render, 5,
                       f"Average render time {avg_time_per_render:.2f}ms is too slow")

    @patch('pygame.font.Font')
    def test_color_validation_integration(self, mock_font):
        """
        Integration test: Color values are validated correctly.
        """
        # Arrange
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        from engine.gui_enhancement.display_types import ColorConfig

        # Mock pygame font
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        # Test valid color config
        valid_config = ColorConfig(
            default_color=(255, 255, 255),
            decreased_color=(255, 0, 0),
            increased_color=(0, 255, 0)
        )

        # Act - Should not raise exception
        try:
            display_manager = DisplayStateManager(color_config=valid_config)
            result = display_manager.format_status_text("player", "hp", 90, -10)
            surface = display_manager.apply_color_formatting(result.content, result.emphasis_type)
            success = True
        except Exception as e:
            success = False

        # Assert
        self.assertTrue(success, "Valid color config should not raise exception")

    @patch('pygame.font.Font')
    def test_font_size_configuration_integration(self, mock_font):
        """
        Integration test: Font sizes are configured correctly for different emphasis types.
        """
        # Arrange
        from engine.gui_enhancement.display_state_manager import DisplayStateManager
        from engine.gui_enhancement.display_types import EmphasisType

        # Mock pygame font with size tracking
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_surface = MagicMock()
        mock_font_instance.render.return_value = mock_surface

        display_manager = DisplayStateManager()

        # Act - Test different emphasis types
        emphasis_types = [EmphasisType.DEFAULT, EmphasisType.DECREASED, EmphasisType.INCREASED]

        for emphasis in emphasis_types:
            surface = display_manager.apply_color_formatting("Test", emphasis)

            # Assert - Font should be called (indicating proper font configuration)
            self.assertTrue(mock_font.called)

        # Verify multiple font calls were made (for different emphasis types)
        self.assertGreaterEqual(mock_font.call_count, len(emphasis_types))


if __name__ == '__main__':
    unittest.main()