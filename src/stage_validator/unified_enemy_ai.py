"""
UnifiedEnemyAI Implementation

A*とゲームエンジンで統一された敵AIロジック。
設定一元化による動作同期を実現。
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any, Optional
import math
import logging

from .models import EnemyState, ValidationConfig, get_global_config


class UnifiedEnemyAI(ABC):
    """統一敵AIロジックの抽象基底クラス"""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or get_global_config()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"UnifiedEnemyAI.{id(self)}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @abstractmethod
    def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """敵の次アクションを計算する"""
        pass

    @abstractmethod
    def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
        """パトロール状態を更新する"""
        pass

    @abstractmethod
    def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
        """プレイヤー発見判定を行う"""
        pass


class StandardEnemyAI(UnifiedEnemyAI):
    """標準統一敵AI実装"""

    def __init__(self, config: Optional[ValidationConfig] = None):
        super().__init__(config)

        # AIの内部状態
        self.enemy_memory: Dict[str, Dict] = {}
        self.turn_counter = 0

    def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """敵の次アクションを計算"""
        try:
            self.logger.debug(f"Calculating action for {enemy_state.enemy_id} at {enemy_state.position}")

            # 敵タイプ別処理
            if enemy_state.enemy_type == "static":
                return self._calculate_static_enemy_action(enemy_state, player_position)
            elif enemy_state.enemy_type == "patrol":
                return self._calculate_patrol_enemy_action(enemy_state, player_position)
            elif enemy_state.enemy_type == "large":
                return self._calculate_large_enemy_action(enemy_state, player_position)
            else:
                self.logger.warning(f"Unknown enemy type: {enemy_state.enemy_type}")
                return "wait"

        except Exception as e:
            self.logger.error(f"Action calculation failed for {enemy_state.enemy_id}: {e}")
            return "wait"

    def _calculate_static_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """静的敵のアクション計算"""
        # プレイヤー発見チェック
        if self.check_player_detection(enemy_state, player_position):
            # プレイヤーの方向を向く
            desired_direction = self._get_direction_to_target(enemy_state.position, player_position)
            if enemy_state.direction != desired_direction:
                return self._get_turn_action(enemy_state.direction, desired_direction)

        # 基本的にはその場で待機
        return "wait"

    def _calculate_patrol_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """パトロール敵のアクション計算"""
        # 警戒状態別の行動
        if enemy_state.alert_state == "chase":
            return self._calculate_chase_action(enemy_state, player_position)
        elif enemy_state.alert_state == "alert":
            return self._calculate_alert_action(enemy_state, player_position)
        else:  # patrol
            return self._calculate_patrol_action(enemy_state, player_position)

    def _calculate_large_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """大型敵のアクション計算"""
        # 大型敵は移動に制約がある
        if self.check_player_detection(enemy_state, player_position):
            # 大型敵は回転のみ（移動は慎重）
            desired_direction = self._get_direction_to_target(enemy_state.position, player_position)
            if enemy_state.direction != desired_direction:
                return self._get_turn_action(enemy_state.direction, desired_direction)
            else:
                # 向きが合っている場合、慎重に移動
                if self._is_safe_to_move_large_enemy(enemy_state):
                    return "move"

        return "wait"

    def _calculate_chase_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """追跡アクション計算"""
        # プレイヤーに向かう最適な行動を計算
        desired_direction = self._get_direction_to_target(enemy_state.position, player_position)

        # 段階的回転システム適用
        if enemy_state.direction != desired_direction:
            if self._should_delay_rotation(enemy_state):
                return "wait"
            return self._get_turn_action(enemy_state.direction, desired_direction)

        # 向きが合っている場合は移動
        return "move"

    def _calculate_alert_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """警戒アクション計算"""
        # プレイヤーを再発見できるかチェック
        if self.check_player_detection(enemy_state, player_position):
            # 発見した場合は追跡モードに移行（状態はupdate_patrol_stateで更新）
            desired_direction = self._get_direction_to_target(enemy_state.position, player_position)
            if enemy_state.direction != desired_direction:
                return self._get_turn_action(enemy_state.direction, desired_direction)
            return "move"

        # 見失った場合は周囲を警戒
        return self._get_alert_search_action(enemy_state)

    def _calculate_patrol_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """パトロールアクション計算"""
        # プレイヤー発見チェック
        if self.check_player_detection(enemy_state, player_position):
            # 発見した場合は向きを合わせる
            desired_direction = self._get_direction_to_target(enemy_state.position, player_position)
            if enemy_state.direction != desired_direction:
                return self._get_turn_action(enemy_state.direction, desired_direction)

        # パトロールルートに基づく行動
        return self._get_patrol_route_action(enemy_state)

    def _should_delay_rotation(self, enemy_state: EnemyState) -> bool:
        """回転を遅延すべきかチェック"""
        enemy_id = enemy_state.enemy_id
        memory = self.enemy_memory.get(enemy_id, {})

        last_rotation_turn = memory.get('last_rotation_turn', 0)
        rotation_delay = self.config.enemy_rotation_delay

        return (self.turn_counter - last_rotation_turn) < rotation_delay

    def _get_turn_action(self, current_direction: str, desired_direction: str) -> str:
        """回転アクションを取得"""
        directions = ["up", "right", "down", "left"]
        current_idx = directions.index(current_direction)
        desired_idx = directions.index(desired_direction)

        # 最短回転方向を計算
        diff = (desired_idx - current_idx) % 4
        if diff == 1 or diff == -3:
            return "turn_right"
        elif diff == 3 or diff == -1:
            return "turn_left"

        return "wait"  # 既に同じ向き

    def _get_direction_to_target(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> str:
        """ターゲット方向を取得"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]

        # より大きい差の方向を優先
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"

    def _get_alert_search_action(self, enemy_state: EnemyState) -> str:
        """警戒時の索敵アクション"""
        # 簡単な左右交互索敵
        enemy_id = enemy_state.enemy_id
        memory = self.enemy_memory.get(enemy_id, {})

        last_search_direction = memory.get('search_direction', 'left')
        next_direction = 'right' if last_search_direction == 'left' else 'left'

        # メモリ更新
        if enemy_id not in self.enemy_memory:
            self.enemy_memory[enemy_id] = {}
        self.enemy_memory[enemy_id]['search_direction'] = next_direction

        return f"turn_{next_direction}"

    def _get_patrol_route_action(self, enemy_state: EnemyState) -> str:
        """パトロールルートアクション"""
        # パトロールインデックスに基づく行動
        directions = ["up", "right", "down", "left"]
        target_direction = directions[enemy_state.patrol_index % 4]

        if enemy_state.direction != target_direction:
            return self._get_turn_action(enemy_state.direction, target_direction)

        # 向きが合っている場合は移動（一定の確率で）
        # または次のパトロールポイントへの回転
        return "move" if self.turn_counter % 3 == 0 else "wait"

    def _is_safe_to_move_large_enemy(self, enemy_state: EnemyState) -> bool:
        """大型敵の移動安全性チェック"""
        # 実装簡略化：基本的に安全とする
        return True

    def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
        """パトロール状態を更新"""
        try:
            # 警戒状態の管理
            new_alert_state = self._update_alert_state(enemy_state)

            # パトロールインデックスの更新
            new_patrol_index = self._update_patrol_index(enemy_state)

            # 新しい状態を返す（不変性保持）
            return EnemyState(
                enemy_id=enemy_state.enemy_id,
                position=enemy_state.position,
                direction=enemy_state.direction,
                patrol_index=new_patrol_index,
                alert_state=new_alert_state,
                vision_range=enemy_state.vision_range,
                health=enemy_state.health,
                enemy_type=enemy_state.enemy_type
            )

        except Exception as e:
            self.logger.error(f"Patrol state update failed for {enemy_state.enemy_id}: {e}")
            return enemy_state

    def _update_alert_state(self, enemy_state: EnemyState) -> str:
        """警戒状態更新"""
        current_state = enemy_state.alert_state
        enemy_id = enemy_state.enemy_id

        # メモリから状態履歴を取得
        memory = self.enemy_memory.get(enemy_id, {})
        state_change_turn = memory.get('alert_state_change_turn', 0)

        if current_state == "alert":
            # 警戒状態のタイムアウトチェック
            if (self.turn_counter - state_change_turn) >= self.config.alert_cooldown_turns:
                return "patrol"

        elif current_state == "chase":
            # 追跡状態のタイムアウトチェック
            if (self.turn_counter - state_change_turn) >= self.config.chase_timeout_turns:
                return "alert"

        return current_state

    def _update_patrol_index(self, enemy_state: EnemyState) -> int:
        """パトロールインデックス更新"""
        if enemy_state.enemy_type != "patrol":
            return enemy_state.patrol_index

        if self.config.patrol_advancement_rule.value == "immediate":
            # 即座にインデックスを進める
            return (enemy_state.patrol_index + 1) % 4
        else:  # delayed
            # 遅延進行
            if self.turn_counter % 2 == 0:
                return (enemy_state.patrol_index + 1) % 4

        return enemy_state.patrol_index

    def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
        """プレイヤー発見判定"""
        try:
            # 距離チェック
            distance = self._calculate_distance(enemy_state.position, player_position)
            if distance > enemy_state.vision_range:
                return False

            # 視野角チェック（敵の向きに基づく）
            if not self._is_in_vision_cone(enemy_state, player_position):
                return False

            # 障害物チェック（簡略化）
            if self._has_line_of_sight(enemy_state.position, player_position):
                return True

            return False

        except Exception as e:
            self.logger.error(f"Player detection check failed: {e}")
            return False

    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """距離計算（マンハッタン距離）"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _is_in_vision_cone(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
        """視野角内判定"""
        enemy_pos = enemy_state.position
        direction = enemy_state.direction

        # 敵の向いている方向のベクトル
        direction_vectors = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }

        dir_vector = direction_vectors[direction]
        to_player = (player_position[0] - enemy_pos[0], player_position[1] - enemy_pos[1])

        # 簡易的な視野角判定（90度の視野角）
        if direction in ["up", "down"]:
            return dir_vector[1] * to_player[1] > 0 and abs(to_player[0]) <= abs(to_player[1])
        else:  # left, right
            return dir_vector[0] * to_player[0] > 0 and abs(to_player[1]) <= abs(to_player[0])

    def _has_line_of_sight(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """視線チェック（障害物なし）"""
        # 簡略化：常にTrueを返す（壁チェックは省略）
        return True

    def advance_turn(self) -> None:
        """ターンを進める"""
        self.turn_counter += 1

        # メモリのクリーンアップ（古いデータを削除）
        if self.turn_counter % 100 == 0:
            self._cleanup_memory()

    def _cleanup_memory(self) -> None:
        """メモリクリーンアップ"""
        # 長時間使用されていないメモリを削除
        current_turn = self.turn_counter
        to_remove = []

        for enemy_id, memory in self.enemy_memory.items():
            last_access = memory.get('last_access_turn', 0)
            if current_turn - last_access > 50:
                to_remove.append(enemy_id)

        for enemy_id in to_remove:
            del self.enemy_memory[enemy_id]

    def get_ai_status(self) -> Dict[str, Any]:
        """AI状態取得"""
        return {
            "turn_counter": self.turn_counter,
            "tracked_enemies": len(self.enemy_memory),
            "config": {
                "rotation_delay": self.config.enemy_rotation_delay,
                "vision_timing": self.config.vision_check_timing.value,
                "patrol_rule": self.config.patrol_advancement_rule.value,
                "alert_cooldown": self.config.alert_cooldown_turns,
                "chase_timeout": self.config.chase_timeout_turns
            }
        }

    def reset(self) -> None:
        """AI状態リセット"""
        self.enemy_memory.clear()
        self.turn_counter = 0
        self.logger.info("UnifiedEnemyAI reset")


# デフォルト実装のファクトリー関数
def create_standard_enemy_ai(config: Optional[ValidationConfig] = None) -> StandardEnemyAI:
    """標準敵AI作成"""
    return StandardEnemyAI(config)