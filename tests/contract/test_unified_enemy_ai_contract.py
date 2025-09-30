"""
Contract Test: UnifiedEnemyAI Interface

統一敵AIロジックインターフェースの契約テスト。
このテストは実装前に失敗する必要があります（TDD）。
"""

import pytest
from typing import Tuple
from src.stage_validator import UnifiedEnemyAI
from src.stage_validator.models import EnemyState


@pytest.mark.contract
@pytest.mark.enemy_ai
class TestUnifiedEnemyAIContract:
    """UnifiedEnemyAIインターフェースの契約テスト"""

    def test_unified_enemy_ai_can_be_imported(self):
        """UnifiedEnemyAIクラスをインポート可能であること"""
        # このテストは実装が存在しないため失敗するはず
        assert UnifiedEnemyAI is not None

    def test_unified_enemy_ai_is_abstract(self):
        """UnifiedEnemyAIが抽象クラスであること"""
        # 抽象クラスなので直接インスタンス化はできないはず
        with pytest.raises(TypeError):
            UnifiedEnemyAI()

    def test_calculate_enemy_action_method_exists(self):
        """calculate_enemy_action メソッドが抽象メソッドとして定義されていること"""
        assert hasattr(UnifiedEnemyAI, 'calculate_enemy_action')

        method = getattr(UnifiedEnemyAI, 'calculate_enemy_action')
        assert hasattr(method, '__isabstractmethod__')

    def test_update_patrol_state_method_exists(self):
        """update_patrol_state メソッドが抽象メソッドとして定義されていること"""
        assert hasattr(UnifiedEnemyAI, 'update_patrol_state')

        method = getattr(UnifiedEnemyAI, 'update_patrol_state')
        assert hasattr(method, '__isabstractmethod__')

    def test_check_player_detection_method_exists(self):
        """check_player_detection メソッドが抽象メソッドとして定義されていること"""
        assert hasattr(UnifiedEnemyAI, 'check_player_detection')

        method = getattr(UnifiedEnemyAI, 'check_player_detection')
        assert hasattr(method, '__isabstractmethod__')

    def test_concrete_implementation_required(self):
        """具象実装が必要であること"""

        class IncompleteAI(UnifiedEnemyAI):
            # calculate_enemy_action のみ実装
            def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
                return "wait"

        # 抽象メソッドが未実装なのでインスタンス化できないはず
        with pytest.raises(TypeError):
            IncompleteAI()

    def test_complete_implementation_possible(self):
        """完全な実装が可能であること"""

        class CompleteAI(UnifiedEnemyAI):
            def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
                return "move"

            def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
                # 実装前なので EnemyState が存在しないはず
                return EnemyState(
                    enemy_id=enemy_state.enemy_id,
                    position=enemy_state.position,
                    direction=enemy_state.direction,
                    patrol_index=enemy_state.patrol_index + 1,
                    alert_state=enemy_state.alert_state,
                    vision_range=enemy_state.vision_range,
                    health=enemy_state.health,
                    enemy_type=enemy_state.enemy_type
                )

            def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
                return False

        # 完全実装なのでインスタンス化可能
        ai = CompleteAI()
        assert ai is not None

    def test_calculate_enemy_action_signature(self):
        """calculate_enemy_action メソッドのシグネチャ"""

        class TestAI(UnifiedEnemyAI):
            def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
                valid_actions = ["move", "turn_left", "turn_right", "wait"]

                # 簡単なルール: プレイヤーが近くにいれば追跡、遠ければパトロール
                enemy_pos = enemy_state.position
                distance = abs(enemy_pos[0] - player_position[0]) + abs(enemy_pos[1] - player_position[1])

                if distance <= 3:
                    return "move"  # 追跡
                else:
                    return "wait"  # パトロール継続

            def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
                return enemy_state

            def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
                return False

        ai = TestAI()

        # 実装前なので EnemyState が存在しないはず
        enemy_state = EnemyState(
            enemy_id="enemy_1",
            position=(5, 5),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        player_position = (6, 5)

        action = ai.calculate_enemy_action(enemy_state, player_position)
        assert isinstance(action, str)
        assert action in ["move", "turn_left", "turn_right", "wait"]

    def test_update_patrol_state_signature(self):
        """update_patrol_state メソッドのシグネチャ"""

        class TestAI(UnifiedEnemyAI):
            def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
                return "wait"

            def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
                # パトロールインデックスを進める
                new_patrol_index = (enemy_state.patrol_index + 1) % 4

                return EnemyState(
                    enemy_id=enemy_state.enemy_id,
                    position=enemy_state.position,
                    direction=enemy_state.direction,
                    patrol_index=new_patrol_index,
                    alert_state=enemy_state.alert_state,
                    vision_range=enemy_state.vision_range,
                    health=enemy_state.health,
                    enemy_type=enemy_state.enemy_type
                )

            def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
                return False

        ai = TestAI()

        enemy_state = EnemyState(
            enemy_id="patrol_enemy",
            position=(3, 4),
            direction="right",
            patrol_index=1,
            alert_state="patrol",
            vision_range=2,
            health=1,
            enemy_type="patrol"
        )

        updated_state = ai.update_patrol_state(enemy_state)

        assert isinstance(updated_state, EnemyState)
        assert updated_state.enemy_id == enemy_state.enemy_id
        assert updated_state.patrol_index == 2  # インクリメントされた

    def test_check_player_detection_signature(self):
        """check_player_detection メソッドのシグネチャ"""

        class TestAI(UnifiedEnemyAI):
            def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
                return "wait"

            def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
                return enemy_state

            def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
                # 簡単な視野判定
                enemy_pos = enemy_state.position
                vision_range = enemy_state.vision_range

                # 距離計算
                distance = abs(enemy_pos[0] - player_position[0]) + abs(enemy_pos[1] - player_position[1])

                return distance <= vision_range

        ai = TestAI()

        enemy_state = EnemyState(
            enemy_id="guard",
            position=(10, 10),
            direction="down",
            patrol_index=0,
            alert_state="patrol",
            vision_range=4,
            health=1,
            enemy_type="static"
        )

        # 視野内のプレイヤー
        close_player_pos = (12, 10)
        detected = ai.check_player_detection(enemy_state, close_player_pos)
        assert isinstance(detected, bool)

        # 視野外のプレイヤー
        far_player_pos = (20, 20)
        not_detected = ai.check_player_detection(enemy_state, far_player_pos)
        assert isinstance(not_detected, bool)

    def test_enemy_state_immutability_principle(self):
        """敵状態の不変性原則（新しいインスタンスを返す）"""

        class TestAI(UnifiedEnemyAI):
            def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
                return "turn_left"

            def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
                # 元の状態は変更せず、新しいインスタンスを返す
                return EnemyState(
                    enemy_id=enemy_state.enemy_id,
                    position=enemy_state.position,
                    direction=enemy_state.direction,
                    patrol_index=enemy_state.patrol_index + 1,
                    alert_state="alert",  # 状態変更
                    vision_range=enemy_state.vision_range,
                    health=enemy_state.health,
                    enemy_type=enemy_state.enemy_type
                )

            def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
                return True

        ai = TestAI()

        original_state = EnemyState(
            enemy_id="test_enemy",
            position=(1, 1),
            direction="up",
            patrol_index=0,
            alert_state="patrol",
            vision_range=3,
            health=1,
            enemy_type="patrol"
        )

        updated_state = ai.update_patrol_state(original_state)

        # 元の状態は変更されていないこと
        assert original_state.alert_state == "patrol"
        assert original_state.patrol_index == 0

        # 新しい状態は変更されていること
        assert updated_state.alert_state == "alert"
        assert updated_state.patrol_index == 1

        # 異なるオブジェクトであること
        assert original_state is not updated_state