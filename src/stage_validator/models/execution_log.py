"""
ExecutionLog Data Model

プレイヤーと敵の各ステップでの位置・向き情報を記録するデータモデル。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple, Optional, Union
from enum import Enum


class EngineType(Enum):
    """実行エンジン種別"""
    ASTAR = "astar"
    GAME_ENGINE = "game_engine"


@dataclass
class EnemyState:
    """敵状態情報"""
    enemy_id: str
    position: Tuple[int, int]
    direction: str
    patrol_index: int
    alert_state: str
    vision_range: int
    health: int
    enemy_type: str

    def __post_init__(self):
        """バリデーション"""
        valid_directions = {"up", "down", "left", "right"}
        if self.direction not in valid_directions:
            raise ValueError(f"Invalid direction: {self.direction}")

        valid_alert_states = {"patrol", "alert", "chase"}
        if self.alert_state not in valid_alert_states:
            raise ValueError(f"Invalid alert_state: {self.alert_state}")

        valid_enemy_types = {"patrol", "static", "large"}
        if self.enemy_type not in valid_enemy_types:
            raise ValueError(f"Invalid enemy_type: {self.enemy_type}")

        if self.patrol_index < 0:
            raise ValueError("patrol_index must be non-negative")

        if self.vision_range < 0:
            raise ValueError("vision_range must be non-negative")

        if self.health < 0:
            raise ValueError("health must be non-negative")


@dataclass
class ExecutionLog:
    """実行ログエントリ"""
    step_number: int
    engine_type: EngineType
    player_position: Tuple[int, int]
    player_direction: str
    enemy_states: List[EnemyState]
    action_taken: str
    game_over: bool
    victory: bool
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """バリデーション"""
        if self.step_number < 0:
            raise ValueError("step_number must be non-negative")

        valid_directions = {"up", "down", "left", "right"}
        if self.player_direction not in valid_directions:
            raise ValueError(f"Invalid player_direction: {self.player_direction}")

        valid_actions = {"move", "turn_left", "turn_right", "attack", "pickup", "wait", "dispose", "none"}
        if self.action_taken not in valid_actions:
            raise ValueError(f"Invalid action_taken: {self.action_taken}")

        # player_position座標チェック
        x, y = self.player_position
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("player_position coordinates must be integers")

        # enemy_states型チェック
        if not isinstance(self.enemy_states, list):
            raise ValueError("enemy_states must be a list")

        for enemy_state in self.enemy_states:
            if not isinstance(enemy_state, EnemyState):
                raise ValueError("All items in enemy_states must be EnemyState instances")

    @property
    def is_terminal_state(self) -> bool:
        """ゲーム終了状態かどうか"""
        return self.game_over or self.victory

    def get_enemy_by_id(self, enemy_id: str) -> Optional[EnemyState]:
        """IDで敵を検索"""
        for enemy in self.enemy_states:
            if enemy.enemy_id == enemy_id:
                return enemy
        return None

    def get_enemies_by_type(self, enemy_type: str) -> List[EnemyState]:
        """タイプで敵を検索"""
        return [enemy for enemy in self.enemy_states if enemy.enemy_type == enemy_type]

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "step_number": self.step_number,
            "engine_type": self.engine_type.value,
            "player_position": self.player_position,
            "player_direction": self.player_direction,
            "enemy_states": [
                {
                    "enemy_id": enemy.enemy_id,
                    "position": enemy.position,
                    "direction": enemy.direction,
                    "patrol_index": enemy.patrol_index,
                    "alert_state": enemy.alert_state,
                    "vision_range": enemy.vision_range,
                    "health": enemy.health,
                    "enemy_type": enemy.enemy_type
                }
                for enemy in self.enemy_states
            ],
            "action_taken": self.action_taken,
            "game_over": self.game_over,
            "victory": self.victory,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ExecutionLog':
        """辞書から作成"""
        enemy_states = [
            EnemyState(
                enemy_id=enemy_data["enemy_id"],
                position=tuple(enemy_data["position"]),
                direction=enemy_data["direction"],
                patrol_index=enemy_data["patrol_index"],
                alert_state=enemy_data["alert_state"],
                vision_range=enemy_data["vision_range"],
                health=enemy_data["health"],
                enemy_type=enemy_data["enemy_type"]
            )
            for enemy_data in data["enemy_states"]
        ]

        timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()

        return cls(
            step_number=data["step_number"],
            engine_type=EngineType(data["engine_type"]),
            player_position=tuple(data["player_position"]),
            player_direction=data["player_direction"],
            enemy_states=enemy_states,
            action_taken=data["action_taken"],
            game_over=data["game_over"],
            victory=data["victory"],
            timestamp=timestamp
        )