"""
Unit tests for ExecutionLog validation - v1.2.12

ExecutionLogモデルのバリデーションとメソッドをテストする。
"""

import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError

# プロジェクトルートをパスに追加
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.stage_validator.models import ExecutionLog, EnemyState, EngineType


@pytest.mark.unit
@pytest.mark.validation
class TestExecutionLogValidation:
    """ExecutionLog バリデーションテスト"""

    def test_valid_execution_log_creation(self):
        """Given valid parameters, when creating ExecutionLog, then created successfully"""
        enemy = EnemyState(
            enemy_id="test_enemy",
            position=(3, 4),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        log = ExecutionLog(
            step_number=5,
            engine_type=EngineType.ASTAR,
            player_position=(10, 15),
            player_direction="right",
            enemy_states=[enemy],
            action_taken="move",
            game_over=False,
            victory=True
        )

        assert log.step_number == 5
        assert log.engine_type == EngineType.ASTAR
        assert log.player_position == (10, 15)
        assert log.player_direction == "right"
        assert len(log.enemy_states) == 1
        assert log.enemy_states[0].enemy_id == "test_enemy"
        assert log.action_taken == "move"
        assert log.game_over is False
        assert log.victory is True
        assert isinstance(log.timestamp, datetime)

    def test_invalid_step_number_negative(self):
        """Given negative step_number, when creating ExecutionLog, then raises ValueError"""
        with pytest.raises(ValueError, match="step_number must be non-negative"):
            ExecutionLog(
                step_number=-1,
                engine_type=EngineType.ASTAR,
                player_position=(0, 0),
                player_direction="up",
                enemy_states=[],
                action_taken="move",
                game_over=False,
                victory=False
            )

    def test_invalid_player_direction(self):
        """Given invalid player_direction, when creating ExecutionLog, then raises ValueError"""
        with pytest.raises(ValueError, match="Invalid player_direction"):
            ExecutionLog(
                step_number=0,
                engine_type=EngineType.ASTAR,
                player_position=(0, 0),
                player_direction="invalid_direction",
                enemy_states=[],
                action_taken="move",
                game_over=False,
                victory=False
            )

    def test_invalid_action_taken(self):
        """Given invalid action, when creating ExecutionLog, then raises ValueError"""
        with pytest.raises(ValueError, match="Invalid action_taken"):
            ExecutionLog(
                step_number=0,
                engine_type=EngineType.ASTAR,
                player_position=(0, 0),
                player_direction="up",
                enemy_states=[],
                action_taken="invalid_action",
                game_over=False,
                victory=False
            )

    def test_invalid_player_position_coordinates(self):
        """Given non-integer position coordinates, when creating ExecutionLog, then raises ValueError"""
        with pytest.raises(ValueError, match="player_position coordinates must be integers"):
            ExecutionLog(
                step_number=0,
                engine_type=EngineType.ASTAR,
                player_position=(1.5, 2.7),  # Non-integer coordinates
                player_direction="up",
                enemy_states=[],
                action_taken="move",
                game_over=False,
                victory=False
            )

    def test_invalid_enemy_states_type(self):
        """Given non-list enemy_states, when creating ExecutionLog, then raises ValueError"""
        with pytest.raises(ValueError, match="enemy_states must be a list"):
            ExecutionLog(
                step_number=0,
                engine_type=EngineType.ASTAR,
                player_position=(0, 0),
                player_direction="up",
                enemy_states="not_a_list",
                action_taken="move",
                game_over=False,
                victory=False
            )

    def test_invalid_enemy_states_content(self):
        """Given enemy_states with non-EnemyState objects, when creating ExecutionLog, then raises ValueError"""
        with pytest.raises(ValueError, match="All items in enemy_states must be EnemyState instances"):
            ExecutionLog(
                step_number=0,
                engine_type=EngineType.ASTAR,
                player_position=(0, 0),
                player_direction="up",
                enemy_states=["not_an_enemy_state"],
                action_taken="move",
                game_over=False,
                victory=False
            )


@pytest.mark.unit
@pytest.mark.validation
class TestExecutionLogProperties:
    """ExecutionLog プロパティとメソッドテスト"""

    def test_is_terminal_state_game_over(self):
        """Given game_over=True, when checking is_terminal_state, then returns True"""
        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=True,
            victory=False
        )

        assert log.is_terminal_state is True

    def test_is_terminal_state_victory(self):
        """Given victory=True, when checking is_terminal_state, then returns True"""
        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=True
        )

        assert log.is_terminal_state is True

    def test_is_terminal_state_false(self):
        """Given game_over=False and victory=False, when checking is_terminal_state, then returns False"""
        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        assert log.is_terminal_state is False

    def test_get_enemy_by_id_found(self):
        """Given enemy with specific ID, when searching by ID, then returns enemy"""
        enemy1 = EnemyState(
            enemy_id="enemy1",
            position=(1, 1),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        enemy2 = EnemyState(
            enemy_id="enemy2",
            position=(2, 2),
            direction="down",
            patrol_index=1,
            alert_state="alert",
            vision_range=4,
            health=2,
            enemy_type="static"
        )

        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[enemy1, enemy2],
            action_taken="move",
            game_over=False,
            victory=False
        )

        found_enemy = log.get_enemy_by_id("enemy2")
        assert found_enemy is not None
        assert found_enemy.enemy_id == "enemy2"
        assert found_enemy.position == (2, 2)

    def test_get_enemy_by_id_not_found(self):
        """Given no enemy with specific ID, when searching by ID, then returns None"""
        enemy = EnemyState(
            enemy_id="enemy1",
            position=(1, 1),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[enemy],
            action_taken="move",
            game_over=False,
            victory=False
        )

        found_enemy = log.get_enemy_by_id("nonexistent_enemy")
        assert found_enemy is None

    def test_get_enemies_by_type(self):
        """Given enemies of different types, when filtering by type, then returns correct enemies"""
        patrol_enemy = EnemyState(
            enemy_id="patrol1",
            position=(1, 1),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        static_enemy1 = EnemyState(
            enemy_id="static1",
            position=(2, 2),
            direction="down",
            patrol_index=0,
            alert_state="patrol",
            vision_range=2,
            health=1,
            enemy_type="static"
        )

        static_enemy2 = EnemyState(
            enemy_id="static2",
            position=(3, 3),
            direction="left",
            patrol_index=0,
            alert_state="patrol",
            vision_range=2,
            health=1,
            enemy_type="static"
        )

        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[patrol_enemy, static_enemy1, static_enemy2],
            action_taken="move",
            game_over=False,
            victory=False
        )

        static_enemies = log.get_enemies_by_type("static")
        assert len(static_enemies) == 2
        assert all(enemy.enemy_type == "static" for enemy in static_enemies)

        patrol_enemies = log.get_enemies_by_type("patrol")
        assert len(patrol_enemies) == 1
        assert patrol_enemies[0].enemy_id == "patrol1"

    def test_to_dict_serialization(self):
        """Given ExecutionLog, when serialized to dict, then includes all fields"""
        enemy = EnemyState(
            enemy_id="test_enemy",
            position=(5, 6),
            direction="right",
            patrol_index=2,
            alert_state="chase",
            vision_range=4,
            health=3,
            enemy_type="large"
        )

        log = ExecutionLog(
            step_number=10,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(20, 25),
            player_direction="left",
            enemy_states=[enemy],
            action_taken="attack",
            game_over=False,
            victory=True
        )

        result_dict = log.to_dict()

        assert result_dict["step_number"] == 10
        assert result_dict["engine_type"] == "game_engine"
        assert result_dict["player_position"] == (20, 25)
        assert result_dict["player_direction"] == "left"
        assert result_dict["action_taken"] == "attack"
        assert result_dict["game_over"] is False
        assert result_dict["victory"] is True
        assert "timestamp" in result_dict

        # Enemy state serialization
        assert len(result_dict["enemy_states"]) == 1
        enemy_dict = result_dict["enemy_states"][0]
        assert enemy_dict["enemy_id"] == "test_enemy"
        assert enemy_dict["position"] == (5, 6)
        assert enemy_dict["enemy_type"] == "large"

    def test_from_dict_deserialization(self):
        """Given dict data, when creating ExecutionLog from dict, then creates valid object"""
        data = {
            "step_number": 15,
            "engine_type": "astar",
            "player_position": (30, 35),
            "player_direction": "down",
            "enemy_states": [
                {
                    "enemy_id": "deserial_enemy",
                    "position": (7, 8),
                    "direction": "up",
                    "patrol_index": 3,
                    "alert_state": "alert",
                    "vision_range": 5,
                    "health": 2,
                    "enemy_type": "patrol"
                }
            ],
            "action_taken": "pickup",
            "game_over": True,
            "victory": False,
            "timestamp": "2025-01-01T12:00:00"
        }

        log = ExecutionLog.from_dict(data)

        assert log.step_number == 15
        assert log.engine_type == EngineType.ASTAR
        assert log.player_position == (30, 35)
        assert log.player_direction == "down"
        assert log.action_taken == "pickup"
        assert log.game_over is True
        assert log.victory is False

        assert len(log.enemy_states) == 1
        enemy = log.enemy_states[0]
        assert enemy.enemy_id == "deserial_enemy"
        assert enemy.position == (7, 8)
        assert enemy.vision_range == 5


@pytest.mark.unit
@pytest.mark.validation
class TestExecutionLogEdgeCases:
    """ExecutionLog エッジケーステスト"""

    def test_empty_enemy_states_list(self):
        """Given empty enemy_states list, when creating ExecutionLog, then succeeds"""
        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="wait",
            game_over=False,
            victory=False
        )

        assert len(log.enemy_states) == 0
        assert log.get_enemies_by_type("patrol") == []
        assert log.get_enemy_by_id("any_id") is None

    def test_large_step_number(self):
        """Given large step_number, when creating ExecutionLog, then succeeds"""
        log = ExecutionLog(
            step_number=999999,
            engine_type=EngineType.ASTAR,
            player_position=(0, 0),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        assert log.step_number == 999999

    def test_large_coordinate_values(self):
        """Given large coordinate values, when creating ExecutionLog, then succeeds"""
        log = ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=(99999, -99999),
            player_direction="up",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        assert log.player_position == (99999, -99999)

    def test_all_valid_directions(self):
        """Given all valid directions, when creating ExecutionLog, then all succeed"""
        valid_directions = ["up", "down", "left", "right"]

        for direction in valid_directions:
            log = ExecutionLog(
                step_number=0,
                engine_type=EngineType.ASTAR,
                player_position=(0, 0),
                player_direction=direction,
                enemy_states=[],
                action_taken="move",
                game_over=False,
                victory=False
            )
            assert log.player_direction == direction

    def test_all_valid_actions(self):
        """Given all valid actions, when creating ExecutionLog, then all succeed"""
        valid_actions = ["move", "turn_left", "turn_right", "attack", "pickup", "wait", "dispose", "none"]

        for action in valid_actions:
            log = ExecutionLog(
                step_number=0,
                engine_type=EngineType.ASTAR,
                player_position=(0, 0),
                player_direction="up",
                enemy_states=[],
                action_taken=action,
                game_over=False,
                victory=False
            )
            assert log.action_taken == action

    def test_from_dict_with_missing_timestamp(self):
        """Given dict without timestamp, when creating from dict, then uses current time"""
        data = {
            "step_number": 0,
            "engine_type": "astar",
            "player_position": (0, 0),
            "player_direction": "up",
            "enemy_states": [],
            "action_taken": "move",
            "game_over": False,
            "victory": False
        }

        log = ExecutionLog.from_dict(data)
        assert isinstance(log.timestamp, datetime)
        # Timestamp should be recent (within last 5 seconds)
        time_diff = datetime.now() - log.timestamp
        assert time_diff.total_seconds() < 5