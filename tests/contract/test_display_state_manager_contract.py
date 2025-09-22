"""
Contract tests for DisplayStateManager API
These tests MUST FAIL initially to follow TDD principles.
"""

import unittest
import sys
import os

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.gui_enhancement.display_state_manager import DisplayStateManager
from engine.gui_enhancement.display_types import EmphasisType, ColorConfig
from engine.gui_enhancement.data_types import FormattedText


class TestDisplayStateManagerContract(unittest.TestCase):
    """Contract tests for DisplayStateManager API based on yaml specification."""

    def setUp(self):
        """Set up test instance."""
        self.manager = DisplayStateManager()

    def test_format_status_text_contract_no_change(self):
        """Test format_status_text contract: no change returns default formatting."""
        # Arrange
        entity_id = "player"
        status_key = "hp"
        value = 100
        change = 0

        # Act
        result = self.manager.format_status_text(entity_id, status_key, value, change)

        # Assert - Contract requirements
        self.assertIsInstance(result, FormattedText)
        self.assertIsInstance(result.content, str)
        self.assertIsInstance(result.color, tuple)
        self.assertEqual(len(result.color), 3)  # RGB tuple
        self.assertIsInstance(result.is_bold, bool)
        self.assertIsInstance(result.emphasis_type, EmphasisType)

        # No change should be default
        self.assertEqual(result.emphasis_type, EmphasisType.DEFAULT)
        self.assertFalse(result.is_bold)
        self.assertEqual(result.content, "100")

    def test_format_status_text_contract_decrease(self):
        """Test format_status_text contract: negative change returns decreased formatting."""
        # Arrange
        entity_id = "player"
        status_key = "hp"
        value = 90
        change = -10

        # Act
        result = self.manager.format_status_text(entity_id, status_key, value, change)

        # Assert - Contract requirements
        self.assertEqual(result.emphasis_type, EmphasisType.DECREASED)
        self.assertTrue(result.is_bold)
        self.assertEqual(result.color, (255, 0, 0))  # Red color
        self.assertIn("↓", result.content)
        self.assertIn("10", result.content)  # Change amount

    def test_format_status_text_contract_increase(self):
        """Test format_status_text contract: positive change returns increased formatting."""
        # Arrange
        entity_id = "player"
        status_key = "hp"
        value = 110
        change = 10

        # Act
        result = self.manager.format_status_text(entity_id, status_key, value, change)

        # Assert - Contract requirements
        self.assertEqual(result.emphasis_type, EmphasisType.INCREASED)
        self.assertTrue(result.is_bold)
        self.assertEqual(result.color, (0, 255, 0))  # Green color
        self.assertIn("↑", result.content)
        self.assertIn("10", result.content)  # Change amount

    def test_get_emphasis_type_contract_logic(self):
        """Test get_emphasis_type contract: correct logic for change deltas."""
        # Test negative change
        result_negative = self.manager.get_emphasis_type(-5)
        self.assertEqual(result_negative, EmphasisType.DECREASED)

        # Test positive change
        result_positive = self.manager.get_emphasis_type(5)
        self.assertEqual(result_positive, EmphasisType.INCREASED)

        # Test zero change
        result_zero = self.manager.get_emphasis_type(0)
        self.assertEqual(result_zero, EmphasisType.DEFAULT)

    def test_apply_color_formatting_contract_default(self):
        """Test apply_color_formatting contract: default emphasis."""
        # Arrange
        text = "100"
        emphasis = EmphasisType.DEFAULT

        # Act
        result = self.manager.apply_color_formatting(text, emphasis)

        # Assert - Contract requirements
        # Should return pygame Surface object (mock for testing)
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'width'))
        self.assertTrue(hasattr(result, 'height'))

    def test_apply_color_formatting_contract_decreased(self):
        """Test apply_color_formatting contract: decreased emphasis."""
        # Arrange
        text = "90 ↓10"
        emphasis = EmphasisType.DECREASED

        # Act
        result = self.manager.apply_color_formatting(text, emphasis)

        # Assert - Contract requirements
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'width'))
        self.assertTrue(hasattr(result, 'height'))

    def test_apply_color_formatting_contract_increased(self):
        """Test apply_color_formatting contract: increased emphasis."""
        # Arrange
        text = "110 ↑10"
        emphasis = EmphasisType.INCREASED

        # Act
        result = self.manager.apply_color_formatting(text, emphasis)

        # Assert - Contract requirements
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'width'))
        self.assertTrue(hasattr(result, 'height'))

    def test_reset_emphasis_contract(self):
        """Test reset_emphasis contract: returns None and resets state."""
        # Arrange
        entity_id = "player"

        # Set some emphasis state first
        self.manager.format_status_text(entity_id, "hp", 90, -10)

        # Act
        result = self.manager.reset_emphasis(entity_id)

        # Assert - Contract requirements
        self.assertIsNone(result)

        # Verify reset by checking next format is default
        next_result = self.manager.format_status_text(entity_id, "hp", 90, 0)
        self.assertEqual(next_result.emphasis_type, EmphasisType.DEFAULT)

    def test_color_config_validation_contract(self):
        """Test ColorConfig validation: RGB values 0-255."""
        # Test valid colors
        valid_config = ColorConfig(
            default_color=(255, 255, 255),
            decreased_color=(255, 0, 0),
            increased_color=(0, 255, 0)
        )

        # Should not raise exception
        manager_with_config = DisplayStateManager(color_config=valid_config)
        self.assertIsNotNone(manager_with_config)

        # Test invalid colors (should raise ValueError)
        with self.assertRaises(ValueError):
            invalid_config = ColorConfig(
                default_color=(256, 255, 255),  # Invalid: > 255
                decreased_color=(255, 0, 0),
                increased_color=(0, 255, 0)
            )


if __name__ == '__main__':
    unittest.main()