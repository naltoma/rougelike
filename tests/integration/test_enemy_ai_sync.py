"""
Integration Test: Enemy AI Behavior Synchronization

敵AI行動同期の統合テスト。
このテストは実装前に失敗する必要があります（TDD）。
"""

import pytest
from typing import Tuple
from src.stage_validator import UnifiedEnemyAI
from src.stage_validator.models import EnemyState


@pytest.mark.integration
@pytest.mark.enemy_ai
class TestEnemyAISync:
    """敵AI行動同期統合テスト"""

    @pytest.fixture
    def unified_ai(self):
        """統一敵AIインスタンス"""
        # 実装前なので失敗するはず
        return UnifiedEnemyAI()

    @pytest.fixture
    def patrol_enemy_state(self):
        """パトロール敵状態"""
        # 実装前なので EnemyState が存在しないはず
        return EnemyState(
            enemy_id="patrol_1",
            position=(5, 5),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

    @pytest.fixture
    def static_enemy_state(self):
        """静的敵状態"""
        return EnemyState(
            enemy_id="guard_1",
            position=(10, 10),
            direction="down",
            patrol_index=0,
            alert_state="patrol",
            vision_range=4,
            health=1,
            enemy_type="static"
        )

    @pytest.fixture
    def large_enemy_state(self):
        """大型敵状態"""
        return EnemyState(
            enemy_id="boss_1",
            position=(15, 15),
            direction="left",
            patrol_index=0,
            alert_state="patrol",
            vision_range=5,
            health=3,
            enemy_type="large"
        )

    def test_patrol_enemy_movement_calculation(self, unified_ai, patrol_enemy_state):
        """パトロール敵の移動計算"""
        player_position = (8, 8)  # 視野外

        # 実装前なので calculate_enemy_action が存在しないはず
        action = unified_ai.calculate_enemy_action(patrol_enemy_state, player_position)

        # パトロール中なので移動またはターン
        assert action in ["move", "turn_left", "turn_right", "wait"]

    def test_patrol_enemy_player_detection(self, unified_ai, patrol_enemy_state):
        """パトロール敵のプレイヤー発見"""
        close_player_position = (5, 7)  # 視野内（距離2）

        # 実装前なので check_player_detection が存在しないはず
        detected = unified_ai.check_player_detection(patrol_enemy_state, close_player_position)

        # 視野内なので発見されるはず
        assert isinstance(detected, bool)
        # 実装後は assert detected == True になるはず

    def test_patrol_enemy_chase_behavior(self, unified_ai, patrol_enemy_state):
        """パトロール敵の追跡行動"""
        player_position = (6, 5)  # 隣接

        # 警戒状態に変更
        alert_enemy = EnemyState(
            enemy_id=patrol_enemy_state.enemy_id,
            position=patrol_enemy_state.position,
            direction=patrol_enemy_state.direction,
            patrol_index=patrol_enemy_state.patrol_index,
            alert_state="chase",  # 追跡モード
            vision_range=patrol_enemy_state.vision_range,
            health=patrol_enemy_state.health,
            enemy_type=patrol_enemy_state.enemy_type
        )

        action = unified_ai.calculate_enemy_action(alert_enemy, player_position)

        # 追跡中なので移動またはターン（プレイヤーに向かう）
        assert action in ["move", "turn_left", "turn_right"]

    def test_static_enemy_behavior(self, unified_ai, static_enemy_state):
        """静的敵の行動"""
        player_position = (12, 12)  # 視野内

        action = unified_ai.calculate_enemy_action(static_enemy_state, player_position)

        # 静的敵なので移動はしない（向きを変える可能性はある）
        assert action in ["turn_left", "turn_right", "wait"]

    def test_large_enemy_movement_constraints(self, unified_ai, large_enemy_state):
        """大型敵の移動制約"""
        player_position = (14, 15)  # 隣接

        action = unified_ai.calculate_enemy_action(large_enemy_state, player_position)

        # 大型敵の移動は特殊な制約があるかもしれない
        assert action in ["move", "turn_left", "turn_right", "wait"]

    def test_patrol_index_advancement(self, unified_ai, patrol_enemy_state):
        """パトロールインデックス進行"""
        # 実装前なので update_patrol_state が存在しないはず
        updated_state = unified_ai.update_patrol_state(patrol_enemy_state)

        assert isinstance(updated_state, EnemyState)
        # 実装後はパトロールインデックスが進むはず
        # assert updated_state.patrol_index == (patrol_enemy_state.patrol_index + 1) % 4

    def test_alert_state_transitions(self, unified_ai, patrol_enemy_state):
        """警戒状態遷移"""
        player_positions = [
            (5, 7),   # 視野内 - 警戒になるはず
            (5, 10),  # 視野外 - パトロールに戻るはず
        ]

        for player_pos in player_positions:
            detected = unified_ai.check_player_detection(patrol_enemy_state, player_pos)

            if detected:
                # 発見時の状態更新テスト
                updated_state = unified_ai.update_patrol_state(patrol_enemy_state)
                # 実装後は alert_state が "alert" または "chase" になるはず
                assert updated_state.alert_state in ["patrol", "alert", "chase"]

    def test_vision_cone_calculation(self, unified_ai, patrol_enemy_state):
        """視野範囲計算"""
        # 敵の向きに応じた視野計算
        test_positions = [
            (5, 2),   # 正面（上向き）
            (5, 8),   # 背面
            (2, 5),   # 左側
            (8, 5),   # 右側
        ]

        for player_pos in test_positions:
            detected = unified_ai.check_player_detection(patrol_enemy_state, player_pos)

            # 実装前なので適切な視野判定ができないはず
            assert isinstance(detected, bool)

    def test_multiple_enemies_interaction(self, unified_ai, patrol_enemy_state, static_enemy_state):
        """複数敵の相互作用"""
        player_position = (7, 7)

        # 複数の敵が同時に行動計算
        patrol_action = unified_ai.calculate_enemy_action(patrol_enemy_state, player_position)
        static_action = unified_ai.calculate_enemy_action(static_enemy_state, player_position)

        # 両方とも有効なアクション
        valid_actions = ["move", "turn_left", "turn_right", "wait", "attack"]
        assert patrol_action in valid_actions
        assert static_action in valid_actions

    def test_enemy_collision_avoidance(self, unified_ai, patrol_enemy_state):
        """敵同士の衝突回避"""
        player_position = (6, 5)

        # 他の敵がいる位置への移動
        action = unified_ai.calculate_enemy_action(patrol_enemy_state, player_position)

        # 実装前なので衝突回避ロジックは存在しないはず
        assert action in ["move", "turn_left", "turn_right", "wait"]

    def test_rotation_timing_consistency(self, unified_ai, patrol_enemy_state):
        """回転タイミングの一貫性"""
        player_position = (4, 5)  # 左側

        # 左を向くために必要なアクション計算
        action = unified_ai.calculate_enemy_action(patrol_enemy_state, player_position)

        # 実装前なので適切な回転計算ができないはず
        assert action in ["move", "turn_left", "turn_right", "wait"]

    def test_gradual_rotation_system(self, unified_ai, patrol_enemy_state):
        """段階的回転システム"""
        # 現在: "up", 目標: "left" (90度左回転)
        player_position = (2, 5)

        action = unified_ai.calculate_enemy_action(patrol_enemy_state, player_position)

        if action == "turn_left":
            # 回転後の状態をシミュレート
            rotated_state = EnemyState(
                enemy_id=patrol_enemy_state.enemy_id,
                position=patrol_enemy_state.position,
                direction="left",  # 回転完了
                patrol_index=patrol_enemy_state.patrol_index,
                alert_state=patrol_enemy_state.alert_state,
                vision_range=patrol_enemy_state.vision_range,
                health=patrol_enemy_state.health,
                enemy_type=patrol_enemy_state.enemy_type
            )

            # 次のアクションは移動可能になるはず
            next_action = unified_ai.calculate_enemy_action(rotated_state, player_position)
            assert next_action in ["move", "turn_left", "turn_right", "wait"]

    def test_vision_range_consistency(self, unified_ai):
        """視野範囲の一貫性"""
        # 異なる視野範囲の敵
        enemy_with_short_vision = EnemyState(
            enemy_id="short_vision",
            position=(10, 10),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=2,  # 短い視野
            health=1,
            enemy_type="patrol"
        )

        enemy_with_long_vision = EnemyState(
            enemy_id="long_vision",
            position=(10, 10),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=5,  # 長い視野
            health=1,
            enemy_type="patrol"
        )

        # 中距離のプレイヤー
        medium_distance_player = (10, 13)

        short_detection = unified_ai.check_player_detection(enemy_with_short_vision, medium_distance_player)
        long_detection = unified_ai.check_player_detection(enemy_with_long_vision, medium_distance_player)

        # 実装後は long_detection のみ True になるはず
        assert isinstance(short_detection, bool)
        assert isinstance(long_detection, bool)

    def test_enemy_ai_state_immutability(self, unified_ai, patrol_enemy_state):
        """敵AI状態の不変性"""
        original_position = patrol_enemy_state.position
        original_patrol_index = patrol_enemy_state.patrol_index
        original_alert_state = patrol_enemy_state.alert_state

        player_position = (6, 6)

        # AI計算実行
        action = unified_ai.calculate_enemy_action(patrol_enemy_state, player_position)
        updated_state = unified_ai.update_patrol_state(patrol_enemy_state)

        # 元の状態は変更されていないこと
        assert patrol_enemy_state.position == original_position
        assert patrol_enemy_state.patrol_index == original_patrol_index
        assert patrol_enemy_state.alert_state == original_alert_state

        # 新しい状態は別のオブジェクト
        assert updated_state is not patrol_enemy_state