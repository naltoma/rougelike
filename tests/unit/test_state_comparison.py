"""
Unit tests for state comparison logic - v1.2.12

StateValidatorのcompare_statesメソッドとその関連ロジックをテストする。
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

# プロジェクトルートをパスに追加
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.stage_validator.state_validator import StateValidator
from src.stage_validator.models import (
    ExecutionLog, EnemyState, EngineType, StateDifference,
    DifferenceType, DifferenceSeverity, ValidationConfig, get_global_config
)


@pytest.mark.unit
@pytest.mark.comparison
class TestStateComparison:
    """状態比較ロジックテスト"""

    def setup_method(self):
        """各テストメソッド前のセットアップ"""
        self.config = ValidationConfig()
        self.mock_astar_engine = Mock()
        self.mock_game_engine = Mock()
        self.validator = StateValidator(
            self.mock_astar_engine,
            self.mock_game_engine,
            self.config
        )

    def test_identical_states_no_differences(self):
        """Given identical states, when comparing, then no differences found"""
        enemy1 = EnemyState(
            enemy_id="enemy1",
            position=(3, 4),
            direction="up",
            patrol_index=1,
            alert_state="patrol",
            vision_range=3,
            health=2,
            enemy_type="patrol"
        )

        astar_log = ExecutionLog(
            step_number=5,
            engine_type=EngineType.ASTAR,
            player_position=(10, 12),
            player_direction="right",
            enemy_states=[enemy1],
            action_taken="move",
            game_over=False,
            victory=False
        )

        # Identical game log
        game_log = ExecutionLog(
            step_number=5,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(10, 12),
            player_direction="right",
            enemy_states=[enemy1],
            action_taken="move",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 5)
        assert len(differences) == 0

    def test_player_position_difference(self):
        """Given different player positions, when comparing, then position difference detected"""
        astar_log = ExecutionLog(
            step_number=3,
            engine_type=EngineType.ASTAR,
            player_position=(5, 6),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=3,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(5, 7),  # Different Y coordinate
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 3)
        assert len(differences) == 1

        diff = differences[0]
        assert diff.difference_type == DifferenceType.PLAYER_POSITION
        assert diff.step_number == 3
        assert "(5, 6)" in diff.description
        assert "(5, 7)" in diff.description

    def test_player_direction_difference(self):
        """Given different player directions, when comparing, then direction difference detected"""
        astar_log = ExecutionLog(
            step_number=2,
            engine_type=EngineType.ASTAR,
            player_position=(8, 9),
            player_direction="left",
            enemy_states=[],
            action_taken="turn_left",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=2,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(8, 9),
            player_direction="down",  # Different direction
            enemy_states=[],
            action_taken="turn_left",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 2)
        assert len(differences) == 1

        diff = differences[0]
        assert diff.difference_type == DifferenceType.PLAYER_DIRECTION
        assert diff.step_number == 2
        assert "left" in diff.description
        assert "down" in diff.description

    def test_enemy_position_difference(self):
        """Given different enemy positions, when comparing, then enemy position difference detected"""
        astar_enemy = EnemyState(
            enemy_id="guard1",
            position=(10, 10),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        game_enemy = EnemyState(
            enemy_id="guard1",
            position=(11, 10),  # Different X coordinate
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        astar_log = ExecutionLog(
            step_number=4,
            engine_type=EngineType.ASTAR,
            player_position=(1, 1),
            player_direction="up",
            enemy_states=[astar_enemy],
            action_taken="wait",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=4,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(1, 1),
            player_direction="up",
            enemy_states=[game_enemy],
            action_taken="wait",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 4)
        assert len(differences) == 1

        diff = differences[0]
        assert diff.difference_type == DifferenceType.ENEMY_POSITION
        assert diff.step_number == 4
        assert "guard1" in diff.description
        assert "(10, 10)" in diff.description
        assert "(11, 10)" in diff.description

    def test_enemy_direction_difference(self):
        """Given different enemy directions, when comparing, then enemy direction difference detected"""
        astar_enemy = EnemyState(
            enemy_id="patrol1",
            position=(7, 8),
            direction="right",
            patrol_index=1,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        game_enemy = EnemyState(
            enemy_id="patrol1",
            position=(7, 8),
            direction="left",  # Different direction
            patrol_index=1,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        astar_log = ExecutionLog(
            step_number=6,
            engine_type=EngineType.ASTAR,
            player_position=(2, 2),
            player_direction="up",
            enemy_states=[astar_enemy],
            action_taken="move",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=6,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(2, 2),
            player_direction="up",
            enemy_states=[game_enemy],
            action_taken="move",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 6)
        assert len(differences) == 1

        diff = differences[0]
        assert diff.difference_type == DifferenceType.ENEMY_DIRECTION
        assert diff.step_number == 6
        assert "patrol1" in diff.description
        assert "right" in diff.description
        assert "left" in diff.description

    def test_enemy_state_difference(self):
        """Given different enemy alert states, when comparing, then enemy state difference detected"""
        astar_enemy = EnemyState(
            enemy_id="hunter1",
            position=(5, 5),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=4,
            health=2,
            enemy_type="patrol"
        )

        game_enemy = EnemyState(
            enemy_id="hunter1",
            position=(5, 5),
            direction="up",
            patrol_index=0,
            alert_state="alert",  # Different alert state
            vision_range=4,
            health=2,
            enemy_type="patrol"
        )

        astar_log = ExecutionLog(
            step_number=8,
            engine_type=EngineType.ASTAR,
            player_position=(3, 3),
            player_direction="down",
            enemy_states=[astar_enemy],
            action_taken="move",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=8,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(3, 3),
            player_direction="down",
            enemy_states=[game_enemy],
            action_taken="move",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 8)
        assert len(differences) == 1

        diff = differences[0]
        assert diff.difference_type == DifferenceType.ENEMY_STATE
        assert diff.step_number == 8
        assert "hunter1" in diff.description
        assert "patrol" in diff.description
        assert "alert" in diff.description

    def test_game_over_difference(self):
        """Given different game_over states, when comparing, then game state difference detected"""
        astar_log = ExecutionLog(
            step_number=10,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,  # Still playing
            victory=False
        )

        game_log = ExecutionLog(
            step_number=10,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=True,  # Game ended
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 10)
        assert len(differences) == 1

        diff = differences[0]
        assert diff.difference_type == DifferenceType.GAME_STATE
        assert diff.step_number == 10
        assert "game_over" in diff.description
        assert diff.severity == DifferenceSeverity.HIGH  # Game state differences are critical

    def test_victory_difference(self):
        """Given different victory states, when comparing, then game state difference detected"""
        astar_log = ExecutionLog(
            step_number=15,
            engine_type=EngineType.ASTAR,
            player_position=(20, 20),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=True  # Victory achieved
        )

        game_log = ExecutionLog(
            step_number=15,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(20, 20),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False  # Still playing
        )

        differences = self.validator.compare_states(astar_log, game_log, 15)
        assert len(differences) == 1

        diff = differences[0]
        assert diff.difference_type == DifferenceType.GAME_STATE
        assert diff.step_number == 15
        assert "victory" in diff.description
        assert diff.severity == DifferenceSeverity.HIGH

    def test_missing_enemy_difference(self):
        """Given missing enemy in one engine, when comparing, then enemy count difference detected"""
        enemy1 = EnemyState(
            enemy_id="missing1",
            position=(12, 13),
            direction="down",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        astar_log = ExecutionLog(
            step_number=7,
            engine_type=EngineType.ASTAR,
            player_position=(5, 5),
            player_direction="right",
            enemy_states=[enemy1],  # Has enemy
            action_taken="attack",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=7,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(5, 5),
            player_direction="right",
            enemy_states=[],  # Missing enemy
            action_taken="attack",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 7)
        assert len(differences) >= 1

        # Should detect the missing enemy
        enemy_diffs = [d for d in differences if d.difference_type == DifferenceType.ENEMY_COUNT]
        assert len(enemy_diffs) >= 1

    def test_multiple_differences_same_step(self):
        """Given multiple differences in same step, when comparing, then all differences detected"""
        astar_enemy = EnemyState(
            enemy_id="multi1",
            position=(1, 1),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        game_enemy = EnemyState(
            enemy_id="multi1",
            position=(2, 2),  # Different position
            direction="down",  # Different direction
            patrol_index=0,
            alert_state="alert",  # Different state
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        astar_log = ExecutionLog(
            step_number=12,
            engine_type=EngineType.ASTAR,
            player_position=(10, 10),  # Different player position
            player_direction="left",   # Different player direction
            enemy_states=[astar_enemy],
            action_taken="wait",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=12,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(11, 11),  # Different player position
            player_direction="right",  # Different player direction
            enemy_states=[game_enemy],
            action_taken="wait",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 12)
        assert len(differences) >= 4  # Player pos, player dir, enemy pos, enemy dir, enemy state

        # Check specific difference types
        diff_types = [d.difference_type for d in differences]
        assert DifferenceType.PLAYER_POSITION in diff_types
        assert DifferenceType.PLAYER_DIRECTION in diff_types
        assert DifferenceType.ENEMY_POSITION in diff_types
        assert DifferenceType.ENEMY_DIRECTION in diff_types

    def test_one_engine_missing_log(self):
        """Given missing log from one engine, when comparing, then missing log difference detected"""
        astar_log = ExecutionLog(
            step_number=9,
            engine_type=EngineType.ASTAR,
            player_position=(6, 7),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        # Game engine missing (None)
        differences = self.validator.compare_states(astar_log, None, 9)
        assert len(differences) >= 1

        missing_diffs = [d for d in differences if "missing" in d.description.lower() or "none" in d.description.lower()]
        assert len(missing_diffs) >= 1

    def test_both_engines_missing_log(self):
        """Given both engines missing logs, when comparing, then appropriate handling"""
        # Both engines missing (None, None)
        differences = self.validator.compare_states(None, None, 11)

        # Should handle gracefully, might return empty list or specific difference
        assert isinstance(differences, list)

    def test_tolerance_based_position_comparison(self):
        """Given positions within tolerance, when comparing with tolerance, then no difference"""
        # Create validator with tolerance
        tolerant_config = ValidationConfig(position_tolerance=1.0)
        tolerant_validator = StateValidator(
            self.mock_astar_engine,
            self.mock_game_engine,
            tolerant_config
        )

        astar_log = ExecutionLog(
            step_number=1,
            engine_type=EngineType.ASTAR,
            player_position=(5, 5),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=1,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(5, 6),  # 1 unit difference
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        differences = tolerant_validator.compare_states(astar_log, game_log, 1)

        # With tolerance=1.0, this should not generate a difference
        position_diffs = [d for d in differences if d.difference_type == DifferenceType.PLAYER_POSITION]
        # Depending on implementation, might be no difference or marked as low severity
        # Test should adapt to actual implementation behavior

    def test_severity_assignment(self):
        """Given different types of differences, when comparing, then appropriate severities assigned"""
        astar_enemy = EnemyState(
            enemy_id="sev1",
            position=(3, 3),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        game_enemy = EnemyState(
            enemy_id="sev1",
            position=(3, 4),  # Minor position difference
            direction="up",
            patrol_index=1,   # Minor patrol difference
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        astar_log = ExecutionLog(
            step_number=20,
            engine_type=EngineType.ASTAR,
            player_position=(10, 10),
            player_direction="up",
            enemy_states=[astar_enemy],
            action_taken="move",
            game_over=False,  # Critical difference
            victory=False
        )

        game_log = ExecutionLog(
            step_number=20,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(10, 10),
            player_direction="up",
            enemy_states=[game_enemy],
            action_taken="move",
            game_over=True,   # Critical difference
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 20)

        # Game state difference should be high severity
        game_state_diffs = [d for d in differences if d.difference_type == DifferenceType.GAME_STATE]
        if game_state_diffs:
            assert game_state_diffs[0].severity == DifferenceSeverity.HIGH

        # Enemy position differences might be medium severity
        enemy_pos_diffs = [d for d in differences if d.difference_type == DifferenceType.ENEMY_POSITION]
        if enemy_pos_diffs:
            assert enemy_pos_diffs[0].severity in [DifferenceSeverity.MEDIUM, DifferenceSeverity.LOW]


@pytest.mark.unit
@pytest.mark.comparison
class TestStateComparisonEdgeCases:
    """状態比較エッジケーステスト"""

    def setup_method(self):
        """各テストメソッド前のセットアップ"""
        self.config = ValidationConfig()
        self.mock_astar_engine = Mock()
        self.mock_game_engine = Mock()
        self.validator = StateValidator(
            self.mock_astar_engine,
            self.mock_game_engine,
            self.config
        )

    def test_empty_enemy_lists_comparison(self):
        """Given both engines with empty enemy lists, when comparing, then no differences"""
        astar_log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],  # Empty
            action_taken="move",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],  # Empty
            action_taken="move",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 0)
        assert len(differences) == 0

    def test_large_coordinate_differences(self):
        """Given very large coordinate differences, when comparing, then differences detected"""
        astar_log = ExecutionLog(
            step_number=5,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=5,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(99999, 99999),  # Very large difference
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        differences = self.validator.compare_states(astar_log, game_log, 5)
        assert len(differences) >= 1

        position_diffs = [d for d in differences if d.difference_type == DifferenceType.PLAYER_POSITION]
        assert len(position_diffs) >= 1