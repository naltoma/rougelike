#!/usr/bin/env python3
"""
CLI command for status_tracker library.
Provides command-line interface for testing and debugging status change tracking.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from engine.gui_enhancement.status_change_tracker import StatusChangeTracker
from engine.gui_enhancement.display_types import EmphasisType


def format_change_result(result, format_type="human"):
    """Format change result for output."""
    if format_type == "json":
        # Convert EmphasisType enums to strings for JSON serialization
        emphasis_map_str = {k: v.value for k, v in result.emphasis_map.items()}

        return json.dumps({
            "entity_id": result.entity_id,
            "status_changes": result.status_changes,
            "has_any_changes": result.has_any_changes,
            "emphasis_map": emphasis_map_str
        }, indent=2)
    else:
        # Human-readable format
        output = []
        output.append(f"Entity: {result.entity_id}")
        output.append(f"Has changes: {result.has_any_changes}")

        if result.has_any_changes:
            output.append("Changes:")
            for key, delta in result.status_changes.items():
                emphasis = result.emphasis_map[key]
                if delta < 0:
                    output.append(f"  {key}: {delta} (DECREASED)")
                elif delta > 0:
                    output.append(f"  {key}: +{delta} (INCREASED)")
                else:
                    output.append(f"  {key}: {delta} (DEFAULT)")
        else:
            output.append("No changes detected")

        return "\n".join(output)


def simulate_status_changes(args):
    """Simulate status changes for testing."""
    tracker = StatusChangeTracker()

    print("=== Status Change Tracker CLI Demo ===")
    print()

    # Example 1: Player taking damage
    print("1. Player takes damage:")
    player_initial = {"hp": 100, "attack": 20}
    player_damaged = {"hp": 85, "attack": 20}

    tracker.track_changes("player", player_initial)
    result = tracker.track_changes("player", player_damaged)
    print(format_change_result(result, args.format))
    print()

    # Example 2: Enemy healing
    print("2. Enemy healing:")
    enemy_initial = {"hp": 30, "attack": 15}
    enemy_healed = {"hp": 45, "attack": 15}

    tracker.track_changes("enemy_01", enemy_initial)
    result = tracker.track_changes("enemy_01", enemy_healed)
    print(format_change_result(result, args.format))
    print()

    # Example 3: No changes
    print("3. No status changes:")
    result = tracker.track_changes("player", player_damaged)  # Same as before
    print(format_change_result(result, args.format))
    print()

    # Example 4: Multiple status changes
    print("4. Multiple status changes:")
    player_buffed = {"hp": 100, "attack": 25}
    result = tracker.track_changes("player", player_buffed)
    print(format_change_result(result, args.format))


def test_edge_cases(args):
    """Test edge cases and error handling."""
    tracker = StatusChangeTracker()

    print("=== Edge Case Testing ===")
    print()

    try:
        # Test empty entity ID
        tracker.track_changes("", {"hp": 100})
        print("ERROR: Should have failed with empty entity ID")
    except ValueError as e:
        print(f"✓ Correctly caught empty entity ID: {e}")

    try:
        # Test non-integer status value
        tracker.track_changes("test", {"hp": "100"})
        print("ERROR: Should have failed with non-integer status")
    except TypeError as e:
        print(f"✓ Correctly caught non-integer status: {e}")

    # Test reset functionality
    tracker.track_changes("test_entity", {"hp": 100})
    tracker.track_changes("test_entity", {"hp": 90})

    print(f"✓ Has changes before reset: {tracker.has_changes('test_entity')}")
    tracker.reset_entity_tracking("test_entity")
    print(f"✓ Has changes after reset: {tracker.has_changes('test_entity')}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Status Tracker CLI - Test and debug status change tracking"
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format (default: human)"
    )
    parser.add_argument(
        "--test-edge-cases",
        action="store_true",
        help="Run edge case tests"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="status_tracker 1.2.11"
    )

    args = parser.parse_args()

    if args.test_edge_cases:
        test_edge_cases(args)
    else:
        simulate_status_changes(args)


if __name__ == "__main__":
    main()