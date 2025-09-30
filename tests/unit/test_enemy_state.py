"""
Unit tests for EnemyState transitions - v1.2.12

EnemyStateモデルの遷移ロジックとバリデーションをテストする。
"""

import pytest
from dataclasses import FrozenInstanceError

# プロジェクトルートをパスに追加
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.stage_validator.models import EnemyState


@pytest.mark.unit
@pytest.mark.enemy
class TestEnemyStateValidation:
    """EnemyState バリデーションテスト"""

    def test_valid_enemy_state_creation(self):
        """Given valid parameters, when creating EnemyState, then created successfully"""
        enemy = EnemyState(
            enemy_id="test_enemy_1",
            position=(5, 7),
            direction="left",
            patrol_index=2,
            alert_state="chase",
            vision_range=4,
            health=3,
            enemy_type="patrol"
        )

        assert enemy.enemy_id == "test_enemy_1"
        assert enemy.position == (5, 7)
        assert enemy.direction == "left"
        assert enemy.patrol_index == 2
        assert enemy.alert_state == "chase"
        assert enemy.vision_range == 4
        assert enemy.health == 3
        assert enemy.enemy_type == "patrol"

    def test_invalid_direction(self):
        """Given invalid direction, when creating EnemyState, then raises ValueError"""
        with pytest.raises(ValueError, match="Invalid direction"):
            EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="invalid_direction",
                patrol_index=0,
                alert_state="patrol",
                vision_range=3,
                health=1,
                enemy_type="patrol"
            )

    def test_invalid_alert_state(self):
        """Given invalid alert_state, when creating EnemyState, then raises ValueError"""
        with pytest.raises(ValueError, match="Invalid alert_state"):
            EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="up",
                patrol_index=0,
                alert_state="invalid_state",
                vision_range=3,
                health=1,
                enemy_type="patrol"
            )

    def test_invalid_enemy_type(self):
        """Given invalid enemy_type, when creating EnemyState, then raises ValueError"""
        with pytest.raises(ValueError, match="Invalid enemy_type"):
            EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="up",
                patrol_index=0,
                alert_state="patrol",
                vision_range=3,
                health=1,
                enemy_type="invalid_type"
            )

    def test_negative_patrol_index(self):
        """Given negative patrol_index, when creating EnemyState, then raises ValueError"""
        with pytest.raises(ValueError, match="patrol_index must be non-negative"):
            EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="up",
                patrol_index=-1,
                alert_state="patrol",
                vision_range=3,
                health=1,
                enemy_type="patrol"
            )

    def test_negative_vision_range(self):
        """Given negative vision_range, when creating EnemyState, then raises ValueError"""
        with pytest.raises(ValueError, match="vision_range must be non-negative"):
            EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="up",
                patrol_index=0,
                alert_state="patrol",
                vision_range=-1,
                health=1,
                enemy_type="patrol"
            )

    def test_negative_health(self):
        """Given negative health, when creating EnemyState, then raises ValueError"""
        with pytest.raises(ValueError, match="health must be non-negative"):
            EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="up",
                patrol_index=0,
                alert_state="patrol",
                vision_range=3,
                health=-1,
                enemy_type="patrol"
            )


@pytest.mark.unit
@pytest.mark.enemy
class TestEnemyStateTransitions:
    """EnemyState 遷移テスト"""

    def test_all_valid_directions(self):
        """Given all valid directions, when creating EnemyState, then all succeed"""
        valid_directions = ["up", "down", "left", "right"]

        for direction in valid_directions:
            enemy = EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction=direction,
                patrol_index=0,
                alert_state="patrol",
                vision_range=3,
                health=1,
                enemy_type="patrol"
            )
            assert enemy.direction == direction

    def test_all_valid_alert_states(self):
        """Given all valid alert_states, when creating EnemyState, then all succeed"""
        valid_alert_states = ["patrol", "alert", "chase"]

        for alert_state in valid_alert_states:
            enemy = EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="up",
                patrol_index=0,
                alert_state=alert_state,
                vision_range=3,
                health=1,
                enemy_type="patrol"
            )
            assert enemy.alert_state == alert_state

    def test_all_valid_enemy_types(self):
        """Given all valid enemy_types, when creating EnemyState, then all succeed"""
        valid_enemy_types = ["patrol", "static", "large"]

        for enemy_type in valid_enemy_types:
            enemy = EnemyState(
                enemy_id="test",
                position=(0, 0),
                direction="up",
                patrol_index=0,
                alert_state="patrol",
                vision_range=3,
                health=1,
                enemy_type=enemy_type
            )
            assert enemy.enemy_type == enemy_type

    def test_patrol_to_alert_transition(self):
        """Given patrol enemy, when transitioning to alert, then state changes correctly"""
        # Original patrol state
        patrol_enemy = EnemyState(
            enemy_id="patrol1",
            position=(5, 5),
            direction="up",
            patrol_index=2,
            alert_state="patrol",
            vision_range=3,
            health=2,
            enemy_type="patrol"
        )

        # Transition to alert (create new instance due to dataclass immutability)
        alert_enemy = EnemyState(
            enemy_id=patrol_enemy.enemy_id,
            position=patrol_enemy.position,
            direction=patrol_enemy.direction,
            patrol_index=patrol_enemy.patrol_index,
            alert_state="alert",  # Changed state
            vision_range=patrol_enemy.vision_range,
            health=patrol_enemy.health,
            enemy_type=patrol_enemy.enemy_type
        )

        assert patrol_enemy.alert_state == "patrol"
        assert alert_enemy.alert_state == "alert"
        assert alert_enemy.enemy_id == patrol_enemy.enemy_id
        assert alert_enemy.position == patrol_enemy.position

    def test_alert_to_chase_transition(self):
        """Given alert enemy, when transitioning to chase, then state changes correctly"""
        # Alert state
        alert_enemy = EnemyState(
            enemy_id="guard1",
            position=(8, 12),
            direction="right",
            patrol_index=1,
            alert_state="alert",
            vision_range=4,
            health=3,
            enemy_type="patrol"
        )

        # Transition to chase
        chase_enemy = EnemyState(
            enemy_id=alert_enemy.enemy_id,
            position=alert_enemy.position,
            direction=alert_enemy.direction,
            patrol_index=alert_enemy.patrol_index,
            alert_state="chase",  # Changed state
            vision_range=alert_enemy.vision_range,
            health=alert_enemy.health,
            enemy_type=alert_enemy.enemy_type
        )

        assert alert_enemy.alert_state == "alert"
        assert chase_enemy.alert_state == "chase"
        assert chase_enemy.enemy_id == alert_enemy.enemy_id

    def test_chase_to_patrol_cooldown(self):
        """Given chase enemy, when cooling down, then returns to patrol state"""
        # Chase state
        chase_enemy = EnemyState(
            enemy_id="hunter1",
            position=(10, 8),
            direction="down",
            patrol_index=3,
            alert_state="chase",
            vision_range=5,
            health=4,
            enemy_type="patrol"
        )

        # Cooldown to patrol
        patrol_enemy = EnemyState(
            enemy_id=chase_enemy.enemy_id,
            position=chase_enemy.position,
            direction=chase_enemy.direction,
            patrol_index=chase_enemy.patrol_index,
            alert_state="patrol",  # Cooled down
            vision_range=chase_enemy.vision_range,
            health=chase_enemy.health,
            enemy_type=chase_enemy.enemy_type
        )

        assert chase_enemy.alert_state == "chase"
        assert patrol_enemy.alert_state == "patrol"

    def test_enemy_movement_transition(self):
        """Given enemy, when moving, then position changes correctly"""
        original_enemy = EnemyState(
            enemy_id="mover1",
            position=(3, 4),
            direction="right",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        # Move right (3, 4) → (4, 4)
        moved_enemy = EnemyState(
            enemy_id=original_enemy.enemy_id,
            position=(4, 4),  # Changed position
            direction=original_enemy.direction,
            patrol_index=original_enemy.patrol_index,
            alert_state=original_enemy.alert_state,
            vision_range=original_enemy.vision_range,
            health=original_enemy.health,
            enemy_type=original_enemy.enemy_type
        )

        assert original_enemy.position == (3, 4)
        assert moved_enemy.position == (4, 4)
        assert moved_enemy.direction == "right"

    def test_enemy_rotation_transition(self):
        """Given enemy, when rotating, then direction changes correctly"""
        original_enemy = EnemyState(
            enemy_id="turner1",
            position=(6, 7),
            direction="up",
            patrol_index=1,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        # Turn right: up → right
        rotated_enemy = EnemyState(
            enemy_id=original_enemy.enemy_id,
            position=original_enemy.position,
            direction="right",  # Changed direction
            patrol_index=original_enemy.patrol_index,
            alert_state=original_enemy.alert_state,
            vision_range=original_enemy.vision_range,
            health=original_enemy.health,
            enemy_type=original_enemy.enemy_type
        )

        assert original_enemy.direction == "up"
        assert rotated_enemy.direction == "right"
        assert rotated_enemy.position == original_enemy.position

    def test_enemy_damage_transition(self):
        """Given enemy with health, when damaged, then health decreases"""
        healthy_enemy = EnemyState(
            enemy_id="target1",
            position=(9, 11),
            direction="left",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=3,
            enemy_type="patrol"
        )

        # Take damage
        damaged_enemy = EnemyState(
            enemy_id=healthy_enemy.enemy_id,
            position=healthy_enemy.position,
            direction=healthy_enemy.direction,
            patrol_index=healthy_enemy.patrol_index,
            alert_state=healthy_enemy.alert_state,
            vision_range=healthy_enemy.vision_range,
            health=2,  # Reduced health
            enemy_type=healthy_enemy.enemy_type
        )

        assert healthy_enemy.health == 3
        assert damaged_enemy.health == 2

    def test_enemy_death_transition(self):
        """Given enemy with low health, when receiving fatal damage, then health becomes 0"""
        dying_enemy = EnemyState(
            enemy_id="victim1",
            position=(12, 13),
            direction="down",
            patrol_index=0,
            alert_state="chase",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        # Fatal damage
        dead_enemy = EnemyState(
            enemy_id=dying_enemy.enemy_id,
            position=dying_enemy.position,
            direction=dying_enemy.direction,
            patrol_index=dying_enemy.patrol_index,
            alert_state=dying_enemy.alert_state,
            vision_range=dying_enemy.vision_range,
            health=0,  # Dead
            enemy_type=dying_enemy.enemy_type
        )

        assert dying_enemy.health == 1
        assert dead_enemy.health == 0

    def test_patrol_index_advancement(self):
        """Given patrol enemy, when advancing patrol, then patrol_index increases"""
        enemy = EnemyState(
            enemy_id="patroller1",
            position=(2, 3),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        # Advance patrol route
        advanced_enemy = EnemyState(
            enemy_id=enemy.enemy_id,
            position=enemy.position,
            direction=enemy.direction,
            patrol_index=1,  # Advanced
            alert_state=enemy.alert_state,
            vision_range=enemy.vision_range,
            health=enemy.health,
            enemy_type=enemy.enemy_type
        )

        assert enemy.patrol_index == 0
        assert advanced_enemy.patrol_index == 1


@pytest.mark.unit
@pytest.mark.enemy
class TestEnemyStateEdgeCases:
    """EnemyState エッジケーステスト"""

    def test_zero_health_enemy(self):
        """Given 0 health, when creating EnemyState, then succeeds"""
        dead_enemy = EnemyState(
            enemy_id="dead1",
            position=(0, 0),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=0,  # Dead
            enemy_type="patrol"
        )

        assert dead_enemy.health == 0

    def test_zero_vision_range(self):
        """Given 0 vision_range, when creating EnemyState, then succeeds (blind enemy)"""
        blind_enemy = EnemyState(
            enemy_id="blind1",
            position=(0, 0),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=0,  # Blind
            health=1,
            enemy_type="patrol"
        )

        assert blind_enemy.vision_range == 0

    def test_large_patrol_index(self):
        """Given large patrol_index, when creating EnemyState, then succeeds"""
        enemy = EnemyState(
            enemy_id="long_patroller",
            position=(0, 0),
            direction="up",
            patrol_index=999,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        assert enemy.patrol_index == 999

    def test_large_vision_range(self):
        """Given large vision_range, when creating EnemyState, then succeeds"""
        eagle_eye = EnemyState(
            enemy_id="eagle_eye",
            position=(0, 0),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=100,  # Very far sight
            health=1,
            enemy_type="patrol"
        )

        assert eagle_eye.vision_range == 100

    def test_large_coordinates(self):
        """Given large coordinates, when creating EnemyState, then succeeds"""
        distant_enemy = EnemyState(
            enemy_id="distant1",
            position=(99999, -99999),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        assert distant_enemy.position == (99999, -99999)

    def test_static_enemy_in_different_states(self):
        """Given static enemy, when in different alert states, then all valid"""
        alert_states = ["patrol", "alert", "chase"]

        for alert_state in alert_states:
            static_enemy = EnemyState(
                enemy_id="static1",
                position=(5, 5),
                direction="up",
                patrol_index=0,  # Static enemies don't patrol, but index still valid
                alert_state=alert_state,
                vision_range=4,
                health=2,
                enemy_type="static"
            )
            assert static_enemy.enemy_type == "static"
            assert static_enemy.alert_state == alert_state

    def test_large_enemy_characteristics(self):
        """Given large enemy, when created with typical characteristics, then succeeds"""
        large_enemy = EnemyState(
            enemy_id="boss1",
            position=(10, 10),
            direction="down",
            patrol_index=0,
            alert_state="chase",
            vision_range=6,  # Typically larger vision
            health=10,  # Typically more health
            enemy_type="large"
        )

        assert large_enemy.enemy_type == "large"
        assert large_enemy.health == 10
        assert large_enemy.vision_range == 6

    def test_enemy_state_equality_comparison(self):
        """Given two identical EnemyStates, when compared, then equal"""
        enemy1 = EnemyState(
            enemy_id="same_enemy",
            position=(7, 8),
            direction="right",
            patrol_index=2,
            alert_state="alert",
            vision_range=4,
            health=3,
            enemy_type="patrol"
        )

        enemy2 = EnemyState(
            enemy_id="same_enemy",
            position=(7, 8),
            direction="right",
            patrol_index=2,
            alert_state="alert",
            vision_range=4,
            health=3,
            enemy_type="patrol"
        )

        assert enemy1 == enemy2

    def test_enemy_state_inequality_comparison(self):
        """Given two different EnemyStates, when compared, then not equal"""
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
            enemy_id="enemy2",  # Different ID
            position=(1, 1),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        assert enemy1 != enemy2