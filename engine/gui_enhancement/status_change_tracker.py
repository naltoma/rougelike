"""
StatusChangeTracker implementation for tracking entity status changes.
Detects status value changes between game turns and calculates deltas for visual emphasis.
"""

from typing import Dict
from .data_types import ChangeResult
from .display_types import EmphasisType


class StatusChangeTracker:
    """Tracks status value changes between game turns and calculates deltas for visual emphasis."""

    def __init__(self):
        """Initialize the status change tracker."""
        self.previous_states: Dict[str, Dict[str, int]] = {}
        self.last_changes: Dict[str, Dict[str, int]] = {}
        self.persistent_changes: Dict[str, Dict[str, int]] = {}  # Changes to display until next turn
        self.turn_counter: int = 0
        self.entity_turn_stamps: Dict[str, int] = {}  # Track when each entity last changed

    def track_changes(self, entity_id: str, current_status: Dict[str, int]) -> ChangeResult:
        """
        Track changes between previous and current status values.

        Args:
            entity_id: Unique identifier for the entity
            current_status: Current status values (e.g., {"hp": 90, "attack": 15})

        Returns:
            ChangeResult containing status changes and emphasis mapping

        Raises:
            ValueError: If entity_id is empty
            TypeError: If status values are not integers
        """
        # Validate inputs
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError("entity_id must be a non-empty string")

        if not isinstance(current_status, dict):
            raise TypeError("current_status must be a dictionary")

        for key, value in current_status.items():
            if not isinstance(value, int):
                raise TypeError(f"Status value for '{key}' must be an integer, got {type(value)}")

        # Get previous state or empty dict for first update
        previous_status = self.previous_states.get(entity_id, {})

        # Calculate actual changes from previous state
        actual_changes = {}
        for key, current_value in current_status.items():
            if entity_id in self.previous_states and key in previous_status:
                # We have previous data - calculate real delta
                previous_value = previous_status[key]
                delta = current_value - previous_value
                if delta != 0:
                    actual_changes[key] = delta
            # For first-time tracking, don't consider it a "change"
            # Changes should only be detected after we have a baseline

        # Update persistent changes if there are actual changes
        if actual_changes:
            # New changes detected - replace old highlighting with new
            self.persistent_changes[entity_id] = actual_changes.copy()
            self.entity_turn_stamps[entity_id] = self.turn_counter
        # If no actual changes, preserve existing highlighting until turn advance
        # Do NOT clear highlighting just because there are no new changes

        # Get display changes (persistent changes for this entity)
        display_changes = self.persistent_changes.get(entity_id, {})

        # Build emphasis map based on display changes
        emphasis_map = {}
        for key, current_value in current_status.items():
            if key in display_changes:
                delta = display_changes[key]
                if delta < 0:
                    emphasis_map[key] = EmphasisType.DECREASED
                else:
                    emphasis_map[key] = EmphasisType.INCREASED
            else:
                emphasis_map[key] = EmphasisType.DEFAULT

        # Store current state as previous for next update
        self.previous_states[entity_id] = current_status.copy()

        # Store last changes for get_change_delta method (use display_changes for consistency)
        self.last_changes[entity_id] = display_changes.copy()

        # Create result with display changes (persistent until next turn)
        # has_any_changes should indicate if there were actual changes in THIS call
        return ChangeResult(
            entity_id=entity_id,
            status_changes=display_changes,
            has_any_changes=len(actual_changes) > 0,  # Use actual_changes, not display_changes
            emphasis_map=emphasis_map
        )

    def has_changes(self, entity_id: str) -> bool:
        """
        Check if entity has any status changes.

        Args:
            entity_id: Entity identifier

        Returns:
            True if entity has any persistent changes to display
        """
        return entity_id in self.persistent_changes and len(self.persistent_changes[entity_id]) > 0

    def get_change_delta(self, entity_id: str, status_key: str) -> int:
        """
        Get the change delta for specific entity status.

        Args:
            entity_id: Entity identifier
            status_key: Status key (e.g., "hp", "attack")

        Returns:
            Change delta (0 if no change or no previous state)
        """
        if entity_id not in self.persistent_changes:
            return 0

        return self.persistent_changes[entity_id].get(status_key, 0)

    def advance_turn(self) -> None:
        """
        Advance to the next turn and clear persistent changes.
        This should be called at the end of each game turn.
        """
        self.turn_counter += 1
        self.persistent_changes.clear()
        self.entity_turn_stamps.clear()

    def start_new_turn(self) -> None:
        """
        Start a new turn, clearing all persistent highlighting.
        Alias for advance_turn() for clearer semantic meaning.
        """
        self.advance_turn()

    def get_current_turn(self) -> int:
        """
        Get the current turn number.

        Returns:
            Current turn number
        """
        return self.turn_counter

    def reset_entity_tracking(self, entity_id: str) -> None:
        """
        Clear tracking state for specific entity.

        Args:
            entity_id: Entity identifier
        """
        if entity_id in self.previous_states:
            del self.previous_states[entity_id]
        if entity_id in self.last_changes:
            del self.last_changes[entity_id]
        if entity_id in self.persistent_changes:
            del self.persistent_changes[entity_id]
        if entity_id in self.entity_turn_stamps:
            del self.entity_turn_stamps[entity_id]