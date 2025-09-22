"""
Unit tests for DisplayStateManager implementation.
Tests visual formatting and pygame integration logic.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.gui_enhancement.display_state_manager import DisplayStateManager
from engine.gui_enhancement.data_types import FormattedText, DisplayConfig, ColorConfig, TextConfig
from engine.gui_enhancement.display_types import EmphasisType


class TestDisplayStateManagerUnit(unittest.TestCase):
    """Unit tests for DisplayStateManager implementation."""

    def setUp(self):
        """Set up test instance with mock pygame."""
        # Mock pygame to avoid initialization requirements
        self.pygame_patcher = patch('engine.gui_enhancement.display_state_manager.pygame')
        self.mock_pygame = self.pygame_patcher.start()

        # Mock pygame.font.Font
        self.mock_font = Mock()
        self.mock_pygame.font.Font.return_value = self.mock_font

        self.manager = DisplayStateManager()

    def tearDown(self):
        """Clean up patches."""
        self.pygame_patcher.stop()

    def test_init_creates_default_configuration(self):
        """Test initialization creates default configuration."""
        self.assertIsInstance(self.manager.display_config, DisplayConfig)
        self.assertIsInstance(self.manager.color_config, ColorConfig)
        self.assertIsInstance(self.manager.text_config, TextConfig)

        # Check default values
        self.assertEqual(self.manager.color_config.default_color, (255, 255, 255))
        self.assertEqual(self.manager.color_config.increased_color, (0, 255, 0))
        self.assertEqual(self.manager.color_config.decreased_color, (255, 0, 0))
        self.assertEqual(self.manager.text_config.increase_symbol, "↑")
        self.assertEqual(self.manager.text_config.decrease_symbol, "↓")

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        custom_display_config = DisplayConfig(
            font_size=24,
            font_path="custom_font.ttf"
        )
        custom_color_config = ColorConfig(
            default_color=(200, 200, 200),
            increased_color=(100, 255, 100),
            decreased_color=(255, 100, 100)
        )
        custom_text_config = TextConfig(
            increase_symbol="▲",
            decrease_symbol="▼"
        )

        manager = DisplayStateManager(
            display_config=custom_display_config,
            color_config=custom_color_config,
            text_config=custom_text_config
        )

        self.assertEqual(manager.display_config.font_size, 24)
        self.assertEqual(manager.color_config.default_color, (200, 200, 200))
        self.assertEqual(manager.text_config.increase_symbol, "▲")

    def test_load_fonts_creates_normal_and_bold_fonts(self):
        """Test font loading creates both normal and bold fonts."""
        self.manager._load_fonts()

        # Should call pygame.font.Font twice (normal and bold)
        self.assertEqual(self.mock_pygame.font.Font.call_count, 2)

        # Check that fonts are stored
        self.assertIsNotNone(self.manager.normal_font)
        self.assertIsNotNone(self.manager.bold_font)

    def test_format_status_text_with_increase(self):
        """Test formatting status text with positive change."""
        result = self.manager.format_status_text("player", "hp", 100, 15)

        self.assertIsInstance(result, FormattedText)
        self.assertEqual(result.content, "100 ↑15")
        self.assertEqual(result.color, (0, 255, 0))  # Green for increase
        self.assertEqual(result.font, self.manager.bold_font)
        self.assertTrue(result.is_bold)

    def test_format_status_text_with_decrease(self):
        """Test formatting status text with negative change."""
        result = self.manager.format_status_text("player", "hp", 85, -15)

        self.assertIsInstance(result, FormattedText)
        self.assertEqual(result.content, "85 ↓15")  # Absolute value shown
        self.assertEqual(result.color, (255, 0, 0))  # Red for decrease
        self.assertEqual(result.font, self.manager.bold_font)
        self.assertTrue(result.is_bold)

    def test_format_status_text_with_no_change(self):
        """Test formatting status text with no change."""
        result = self.manager.format_status_text("player", "hp", 100, 0)

        self.assertIsInstance(result, FormattedText)
        self.assertEqual(result.content, "100")
        self.assertEqual(result.color, (255, 255, 255))  # Default white
        self.assertEqual(result.font, self.manager.normal_font)
        self.assertFalse(result.is_bold)

    def test_format_stage_name_display(self):
        """Test formatting stage name for display."""
        result = self.manager.format_stage_name("Stage 05")

        self.assertIsInstance(result, FormattedText)
        self.assertEqual(result.content, "Stage: Stage 05")
        self.assertEqual(result.color, (255, 255, 255))  # Default color
        self.assertEqual(result.font, self.manager.normal_font)
        self.assertFalse(result.is_bold)

    def test_get_emphasis_display_with_different_types(self):
        """Test emphasis display for different emphasis types."""
        test_cases = [
            (EmphasisType.INCREASED, (0, 255, 0), True),
            (EmphasisType.DECREASED, (255, 0, 0), True),
            (EmphasisType.DEFAULT, (255, 255, 255), False),
        ]

        for emphasis_type, expected_color, expected_bold in test_cases:
            color, is_bold = self.manager.get_emphasis_display(emphasis_type)
            self.assertEqual(color, expected_color)
            self.assertEqual(is_bold, expected_bold)

    def test_render_text_surface_calls_font_render(self):
        """Test render_text_surface calls pygame font render."""
        formatted_text = FormattedText(
            content="Test Text",
            color=(255, 255, 255),
            font=self.mock_font,
            is_bold=False
        )

        # Mock the font render method
        mock_surface = Mock()
        self.mock_font.render.return_value = mock_surface

        result = self.manager.render_text_surface(formatted_text)

        # Check font.render was called with correct parameters
        self.mock_font.render.assert_called_once_with(
            "Test Text",
            True,  # Anti-aliasing
            (255, 255, 255)  # Color
        )
        self.assertEqual(result, mock_surface)

    def test_large_positive_and_negative_changes(self):
        """Test handling of large positive and negative changes."""
        # Large positive change
        result_pos = self.manager.format_status_text("enemy", "hp", 9999, 5000)
        self.assertEqual(result_pos.content, "9999 ↑5000")
        self.assertEqual(result_pos.color, (0, 255, 0))

        # Large negative change
        result_neg = self.manager.format_status_text("enemy", "hp", 1, -9998)
        self.assertEqual(result_neg.content, "1 ↓9998")
        self.assertEqual(result_neg.color, (255, 0, 0))

    def test_zero_values_and_changes(self):
        """Test handling of zero values and changes."""
        # Zero value, no change
        result = self.manager.format_status_text("player", "hp", 0, 0)
        self.assertEqual(result.content, "0")
        self.assertEqual(result.color, (255, 255, 255))
        self.assertFalse(result.is_bold)

        # Zero value, positive change
        result_pos = self.manager.format_status_text("player", "hp", 0, 10)
        self.assertEqual(result_pos.content, "0 ↑10")
        self.assertEqual(result_pos.color, (0, 255, 0))

        # Zero value, negative change (shouldn't happen in practice but test anyway)
        result_neg = self.manager.format_status_text("player", "hp", 0, -5)
        self.assertEqual(result_neg.content, "0 ↓5")
        self.assertEqual(result_neg.color, (255, 0, 0))

    def test_custom_symbols_usage(self):
        """Test usage of custom increase/decrease symbols."""
        custom_text_config = TextConfig(
            increase_symbol="++",
            decrease_symbol="--"
        )

        manager = DisplayStateManager(text_config=custom_text_config)

        result_inc = manager.format_status_text("player", "attack", 25, 5)
        result_dec = manager.format_status_text("player", "attack", 15, -10)

        self.assertEqual(result_inc.content, "25 ++5")
        self.assertEqual(result_dec.content, "15 --10")

    def test_custom_colors_usage(self):
        """Test usage of custom colors."""
        custom_color_config = ColorConfig(
            default_color=(128, 128, 128),
            increased_color=(0, 128, 255),
            decreased_color=(255, 128, 0)
        )

        manager = DisplayStateManager(color_config=custom_color_config)

        result_default = manager.format_status_text("player", "hp", 100, 0)
        result_inc = manager.format_status_text("player", "hp", 110, 10)
        result_dec = manager.format_status_text("player", "hp", 90, -10)

        self.assertEqual(result_default.color, (128, 128, 128))
        self.assertEqual(result_inc.color, (0, 128, 255))
        self.assertEqual(result_dec.color, (255, 128, 0))

    def test_font_size_configuration(self):
        """Test font size configuration affects font loading."""
        custom_display_config = DisplayConfig(font_size=32)
        manager = DisplayStateManager(display_config=custom_display_config)

        manager._load_fonts()

        # Check that fonts were loaded with correct size
        calls = self.mock_pygame.font.Font.call_args_list
        for call in calls:
            args, kwargs = call
            # Second argument should be font size
            self.assertEqual(args[1], 32)

    def test_state_isolation_between_instances(self):
        """Test that different manager instances have independent state."""
        config1 = ColorConfig(increased_color=(255, 255, 0))
        config2 = ColorConfig(increased_color=(0, 255, 255))

        manager1 = DisplayStateManager(color_config=config1)
        manager2 = DisplayStateManager(color_config=config2)

        result1 = manager1.format_status_text("test", "hp", 100, 10)
        result2 = manager2.format_status_text("test", "hp", 100, 10)

        self.assertEqual(result1.color, (255, 255, 0))
        self.assertEqual(result2.color, (0, 255, 255))

    def test_none_font_handling(self):
        """Test handling when font is None (fallback behavior)."""
        # Set fonts to None to test fallback
        self.manager.normal_font = None
        self.manager.bold_font = None

        # Should still create FormattedText but with None font
        result = self.manager.format_status_text("player", "hp", 100, 10)

        self.assertIsInstance(result, FormattedText)
        self.assertEqual(result.content, "100 ↑10")
        # Font might be None but should not crash
        self.assertIsNotNone(result.color)

    def test_edge_case_empty_stage_name(self):
        """Test formatting empty stage name."""
        result = self.manager.format_stage_name("")

        self.assertEqual(result.content, "Stage: ")
        self.assertEqual(result.color, (255, 255, 255))

    def test_edge_case_very_long_content(self):
        """Test handling very long content strings."""
        long_stage_name = "A" * 1000
        result = self.manager.format_stage_name(long_stage_name)

        expected_content = f"Stage: {long_stage_name}"
        self.assertEqual(result.content, expected_content)

    @patch('engine.gui_enhancement.display_state_manager.pygame.font.Font')
    def test_font_loading_error_handling(self, mock_font_class):
        """Test handling of font loading errors."""
        # Make font loading raise an exception
        mock_font_class.side_effect = Exception("Font loading failed")

        # Should not crash but handle gracefully
        try:
            manager = DisplayStateManager()
            manager._load_fonts()
            # If no exception, fonts should be None or handle gracefully
        except Exception as e:
            self.fail(f"Font loading error should be handled gracefully: {e}")


if __name__ == '__main__':
    unittest.main()