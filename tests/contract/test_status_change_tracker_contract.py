"""
Contract tests for StatusChangeTracker API
These tests MUST FAIL initially to follow TDD principles.
"""

import unittest
from typing import Dict
import sys
import os

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
from engine.gui_enhancement.data_types import ChangeResult
from engine.gui_enhancement.display_types import EmphasisType


class TestStatusChangeTrackerContract(unittest.TestCase):
    """Contract tests for StatusChangeTracker API based on yaml specification."""

    def setUp(self):
        """Set up test instance."""
        self.tracker = StatusChangeTracker()

    def test_track_changes_contract_with_first_update(self):
        """Test track_changes contract: first update should show no changes."""
        # Arrange
        entity_id = "player"
        current_status = {"hp": 100, "attack": 15}

        # Act
        result = self.tracker.track_changes(entity_id, current_status)

        # Assert - Contract requirements
        self.assertIsInstance(result, ChangeResult)
        self.assertEqual(result.entity_id, entity_id)
        self.assertIsInstance(result.status_changes, dict)
        self.assertIsInstance(result.has_any_changes, bool)
        self.assertIsInstance(result.emphasis_map, dict)

        # First update should have no changes
        self.assertFalse(result.has_any_changes)
        self.assertEqual(len(result.status_changes), 0)

    def test_track_changes_contract_with_decrease(self):
        """Test track_changes contract: decrease should be negative delta."""
        # Arrange
        entity_id = "player"
        initial_status = {"hp": 100, "attack": 15}
        decreased_status = {"hp": 90, "attack": 15}

        # Act - First update to establish baseline
        self.tracker.track_changes(entity_id, initial_status)
        # Second update with decrease
        result = self.tracker.track_changes(entity_id, decreased_status)

        # Assert - Contract requirements
        self.assertTrue(result.has_any_changes)
        self.assertEqual(result.status_changes["hp"], -10)
        self.assertEqual(result.emphasis_map["hp"], EmphasisType.DECREASED)

    def test_track_changes_contract_with_increase(self):
        """Test track_changes contract: increase should be positive delta."""
        # Arrange
        entity_id = "player"
        initial_status = {"hp": 90, "attack": 15}
        increased_status = {"hp": 100, "attack": 15}

        # Act - First update to establish baseline
        self.tracker.track_changes(entity_id, initial_status)
        # Second update with increase
        result = self.tracker.track_changes(entity_id, increased_status)

        # Assert - Contract requirements
        self.assertTrue(result.has_any_changes)
        self.assertEqual(result.status_changes["hp"], 10)
        self.assertEqual(result.emphasis_map["hp"], EmphasisType.INCREASED)

    def test_has_changes_contract(self):
        """Test has_changes contract: returns boolean."""
        # Arrange
        entity_id = "player"
        status = {"hp": 100}

        # Act
        self.tracker.track_changes(entity_id, status)
        result = self.tracker.has_changes(entity_id)

        # Assert - Contract requirements
        self.assertIsInstance(result, bool)
        self.assertFalse(result)  # No changes on first update

    def test_get_change_delta_contract(self):
        """Test get_change_delta contract: returns integer delta."""
        # Arrange
        entity_id = "player"
        initial_status = {"hp": 100}
        changed_status = {"hp": 85}

        # Act
        self.tracker.track_changes(entity_id, initial_status)
        self.tracker.track_changes(entity_id, changed_status)
        result = self.tracker.get_change_delta(entity_id, "hp")

        # Assert - Contract requirements
        self.assertIsInstance(result, int)
        self.assertEqual(result, -15)

    def test_reset_entity_tracking_contract(self):
        """Test reset_entity_tracking contract: clears state."""
        # Arrange
        entity_id = "player"
        status = {"hp": 100}

        # Act
        self.tracker.track_changes(entity_id, status)
        result = self.tracker.reset_entity_tracking(entity_id)

        # Assert - Contract requirements
        self.assertIsNone(result)  # Should return None
        self.assertFalse(self.tracker.has_changes(entity_id))

    def test_track_changes_with_invalid_entity_id(self):
        """Test contract error handling: empty entity_id should raise error."""
        # Arrange
        empty_entity_id = ""
        status = {"hp": 100}

        # Act & Assert
        with self.assertRaises(ValueError):
            self.tracker.track_changes(empty_entity_id, status)

    def test_track_changes_with_non_integer_status(self):
        """Test contract error handling: non-integer status values should raise error."""
        # Arrange
        entity_id = "player"
        invalid_status = {"hp": "100"}  # String instead of int

        # Act & Assert
        with self.assertRaises(TypeError):
            self.tracker.track_changes(entity_id, invalid_status)


if __name__ == '__main__':
    unittest.main()