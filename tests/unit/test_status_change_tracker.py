"""
Unit tests for StatusChangeTracker implementation.
Tests internal behavior and edge cases.
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


class TestStatusChangeTrackerUnit(unittest.TestCase):
    """Unit tests for StatusChangeTracker implementation."""

    def setUp(self):
        """Set up test instance."""
        self.tracker = StatusChangeTracker()

    def test_init_creates_empty_state(self):
        """Test initialization creates empty internal state."""
        self.assertEqual(len(self.tracker.previous_states), 0)
        self.assertEqual(len(self.tracker.last_changes), 0)

    def test_first_track_call_establishes_baseline(self):
        """Test first track_changes call establishes baseline with no changes."""
        entity_id = "test_entity"
        status = {"hp": 100, "attack": 20}

        result = self.tracker.track_changes(entity_id, status)

        # Should establish baseline
        self.assertFalse(result.has_any_changes)
        self.assertEqual(len(result.status_changes), 0)
        self.assertEqual(result.entity_id, entity_id)

        # Should store previous state
        self.assertIn(entity_id, self.tracker.previous_states)
        self.assertEqual(self.tracker.previous_states[entity_id], status)

    def test_multiple_entities_tracked_independently(self):
        """Test multiple entities are tracked independently."""
        # Track entity 1
        self.tracker.track_changes("entity1", {"hp": 100})
        result1 = self.tracker.track_changes("entity1", {"hp": 90})

        # Track entity 2
        self.tracker.track_changes("entity2", {"hp": 50})
        result2 = self.tracker.track_changes("entity2", {"hp": 60})

        # Results should be independent
        self.assertEqual(result1.status_changes["hp"], -10)
        self.assertEqual(result2.status_changes["hp"], 10)
        self.assertEqual(result1.emphasis_map["hp"], EmphasisType.DECREASED)
        self.assertEqual(result2.emphasis_map["hp"], EmphasisType.INCREASED)

    def test_emphasis_mapping_for_changes(self):
        """Test emphasis mapping is correct for different change types."""
        entity_id = "test"

        # Establish baseline
        self.tracker.track_changes(entity_id, {"hp": 100, "attack": 20, "defense": 15})

        # Make various changes
        result = self.tracker.track_changes(entity_id, {"hp": 85, "attack": 25, "defense": 15})

        # Check emphasis mapping
        self.assertEqual(result.emphasis_map["hp"], EmphasisType.DECREASED)
        self.assertEqual(result.emphasis_map["attack"], EmphasisType.INCREASED)
        self.assertEqual(result.emphasis_map["defense"], EmphasisType.DEFAULT)

    def test_zero_changes_have_default_emphasis(self):
        """Test zero changes get DEFAULT emphasis type."""
        entity_id = "test"

        self.tracker.track_changes(entity_id, {"hp": 100})
        result = self.tracker.track_changes(entity_id, {"hp": 100})  # No change

        self.assertEqual(result.emphasis_map["hp"], EmphasisType.DEFAULT)
        self.assertFalse(result.has_any_changes)

    def test_has_changes_reflects_last_update(self):
        """Test has_changes method reflects last update status."""
        entity_id = "test"

        # No changes initially
        self.assertFalse(self.tracker.has_changes(entity_id))

        # First update (no changes expected)
        self.tracker.track_changes(entity_id, {"hp": 100})
        self.assertFalse(self.tracker.has_changes(entity_id))

        # Second update with changes
        self.tracker.track_changes(entity_id, {"hp": 90})
        self.assertTrue(self.tracker.has_changes(entity_id))

        # Third update with no changes
        self.tracker.track_changes(entity_id, {"hp": 90})
        self.assertFalse(self.tracker.has_changes(entity_id))

    def test_get_change_delta_returns_correct_values(self):
        """Test get_change_delta returns correct delta values."""
        entity_id = "test"

        # Before any tracking
        self.assertEqual(self.tracker.get_change_delta(entity_id, "hp"), 0)

        # After first update (no changes)
        self.tracker.track_changes(entity_id, {"hp": 100, "attack": 20})
        self.assertEqual(self.tracker.get_change_delta(entity_id, "hp"), 0)
        self.assertEqual(self.tracker.get_change_delta(entity_id, "attack"), 0)

        # After second update with changes
        self.tracker.track_changes(entity_id, {"hp": 85, "attack": 25})
        self.assertEqual(self.tracker.get_change_delta(entity_id, "hp"), -15)
        self.assertEqual(self.tracker.get_change_delta(entity_id, "attack"), 5)

        # Non-existent status key
        self.assertEqual(self.tracker.get_change_delta(entity_id, "nonexistent"), 0)

    def test_reset_entity_tracking_clears_state(self):
        """Test reset_entity_tracking clears all state for entity."""
        entity_id = "test"

        # Establish state
        self.tracker.track_changes(entity_id, {"hp": 100})
        self.tracker.track_changes(entity_id, {"hp": 90})

        # Verify state exists
        self.assertTrue(self.tracker.has_changes(entity_id))
        self.assertIn(entity_id, self.tracker.previous_states)

        # Reset
        self.tracker.reset_entity_tracking(entity_id)

        # Verify state cleared
        self.assertFalse(self.tracker.has_changes(entity_id))
        self.assertNotIn(entity_id, self.tracker.previous_states)
        self.assertNotIn(entity_id, self.tracker.last_changes)
        self.assertEqual(self.tracker.get_change_delta(entity_id, "hp"), 0)

    def test_new_status_keys_added_dynamically(self):
        """Test new status keys are handled correctly."""
        entity_id = "test"

        # Start with limited status
        self.tracker.track_changes(entity_id, {"hp": 100})

        # Add new status key in second update
        result = self.tracker.track_changes(entity_id, {"hp": 90, "attack": 20})

        # New key should be treated as no change (baseline)
        self.assertEqual(result.status_changes["hp"], -10)
        self.assertNotIn("attack", result.status_changes)  # No change for new key
        self.assertEqual(result.emphasis_map["attack"], EmphasisType.DEFAULT)

    def test_removed_status_keys_ignored(self):
        """Test removed status keys are handled gracefully."""
        entity_id = "test"

        # Start with multiple status
        self.tracker.track_changes(entity_id, {"hp": 100, "attack": 20})

        # Remove attack in second update
        result = self.tracker.track_changes(entity_id, {"hp": 90})

        # Only hp should be in result
        self.assertEqual(len(result.status_changes), 1)
        self.assertEqual(result.status_changes["hp"], -10)
        self.assertNotIn("attack", result.status_changes)
        self.assertNotIn("attack", result.emphasis_map)

    def test_large_positive_and_negative_changes(self):
        """Test handling of large positive and negative changes."""
        entity_id = "test"

        self.tracker.track_changes(entity_id, {"hp": 1000})
        result = self.tracker.track_changes(entity_id, {"hp": 1})

        self.assertEqual(result.status_changes["hp"], -999)
        self.assertEqual(result.emphasis_map["hp"], EmphasisType.DECREASED)

        result = self.tracker.track_changes(entity_id, {"hp": 9999})
        self.assertEqual(result.status_changes["hp"], 9998)
        self.assertEqual(result.emphasis_map["hp"], EmphasisType.INCREASED)

    def test_input_validation_empty_entity_id(self):
        """Test input validation for empty entity ID."""
        with self.assertRaises(ValueError) as context:
            self.tracker.track_changes("", {"hp": 100})

        self.assertIn("entity_id must be a non-empty string", str(context.exception))

    def test_input_validation_none_entity_id(self):
        """Test input validation for None entity ID."""
        with self.assertRaises(ValueError):
            self.tracker.track_changes(None, {"hp": 100})

    def test_input_validation_non_dict_status(self):
        """Test input validation for non-dict status."""
        with self.assertRaises(TypeError) as context:
            self.tracker.track_changes("test", "not_a_dict")

        self.assertIn("current_status must be a dictionary", str(context.exception))

    def test_input_validation_non_integer_status_values(self):
        """Test input validation for non-integer status values."""
        test_cases = [
            {"hp": "100"},      # String
            {"hp": 100.5},      # Float
            {"hp": None},       # None
            {"hp": []},         # List
        ]

        for invalid_status in test_cases:
            with self.assertRaises(TypeError) as context:
                self.tracker.track_changes("test", invalid_status)

            self.assertIn("Status value for 'hp' must be an integer", str(context.exception))

    def test_mixed_valid_invalid_status_values(self):
        """Test validation catches invalid values even when mixed with valid ones."""
        invalid_status = {"hp": 100, "attack": "invalid", "defense": 15}

        with self.assertRaises(TypeError) as context:
            self.tracker.track_changes("test", invalid_status)

        self.assertIn("Status value for 'attack' must be an integer", str(context.exception))

    def test_state_isolation_between_instances(self):
        """Test that different tracker instances don't share state."""
        tracker1 = StatusChangeTracker()
        tracker2 = StatusChangeTracker()

        # Track same entity in both
        tracker1.track_changes("entity", {"hp": 100})
        tracker1.track_changes("entity", {"hp": 90})

        tracker2.track_changes("entity", {"hp": 50})
        tracker2.track_changes("entity", {"hp": 60})

        # Results should be different
        self.assertEqual(tracker1.get_change_delta("entity", "hp"), -10)
        self.assertEqual(tracker2.get_change_delta("entity", "hp"), 10)
        self.assertTrue(tracker1.has_changes("entity"))
        self.assertTrue(tracker2.has_changes("entity"))


if __name__ == '__main__':
    unittest.main()