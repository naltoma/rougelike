"""
StateDifference Data Model

両エンジン間の実行結果比較差異情報のデータモデル。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List, Dict
from enum import Enum
import json


class DifferenceType(Enum):
    """差異種別"""
    PLAYER_POSITION = "player_position"
    ENEMY_POSITION = "enemy_position"
    GAME_STATE = "game_state"
    ACTION_RESULT = "action_result"
    ITEM_STATE = "item_state"
    VISION_STATE = "vision_state"
    PATROL_STATE = "patrol_state"


class Severity(Enum):
    """重要度"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class StateDifference:
    """状態差異データモデル"""
    step_number: int
    difference_type: DifferenceType
    astar_value: Any
    engine_value: Any
    severity: Severity
    description: str
    comparison_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """バリデーション"""
        if self.step_number < 0:
            raise ValueError("step_number must be non-negative")

        if not self.description:
            raise ValueError("description cannot be empty")

        if self.context is None:
            self.context = {}

    @property
    def is_critical(self) -> bool:
        """重要な差異かどうか"""
        return self.severity == Severity.CRITICAL

    @property
    def is_position_difference(self) -> bool:
        """位置関連の差異かどうか"""
        return self.difference_type in [
            DifferenceType.PLAYER_POSITION,
            DifferenceType.ENEMY_POSITION
        ]

    @property
    def is_state_difference(self) -> bool:
        """状態関連の差異かどうか"""
        return self.difference_type in [
            DifferenceType.GAME_STATE,
            DifferenceType.VISION_STATE,
            DifferenceType.PATROL_STATE,
            DifferenceType.ITEM_STATE
        ]

    def get_value_difference_summary(self) -> str:
        """値の差異サマリー"""
        if isinstance(self.astar_value, (int, float)) and isinstance(self.engine_value, (int, float)):
            diff = abs(self.astar_value - self.engine_value)
            return f"Numeric difference: {diff}"

        if isinstance(self.astar_value, (tuple, list)) and isinstance(self.engine_value, (tuple, list)):
            if len(self.astar_value) == len(self.engine_value) == 2:
                # 座標の差異
                dx = abs(self.astar_value[0] - self.engine_value[0])
                dy = abs(self.astar_value[1] - self.engine_value[1])
                return f"Position difference: dx={dx}, dy={dy}"

        if self.astar_value != self.engine_value:
            return f"Value mismatch: '{self.astar_value}' vs '{self.engine_value}'"

        return "No difference"

    def add_context(self, key: str, value: Any) -> None:
        """コンテキスト情報を追加"""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """コンテキスト情報を取得"""
        return self.context.get(key, default)

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "step_number": self.step_number,
            "difference_type": self.difference_type.value,
            "astar_value": self._serialize_value(self.astar_value),
            "engine_value": self._serialize_value(self.engine_value),
            "severity": self.severity.value,
            "description": self.description,
            "comparison_id": self.comparison_id,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "value_difference_summary": self.get_value_difference_summary()
        }

    def _serialize_value(self, value: Any) -> Any:
        """値をシリアライズ可能な形式に変換"""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return list(value)
        elif isinstance(value, dict):
            return value
        else:
            return str(value)

    @classmethod
    def from_dict(cls, data: dict) -> 'StateDifference':
        """辞書から作成"""
        timestamp = datetime.fromisoformat(data["timestamp"])

        return cls(
            step_number=data["step_number"],
            difference_type=DifferenceType(data["difference_type"]),
            astar_value=data["astar_value"],
            engine_value=data["engine_value"],
            severity=Severity(data["severity"]),
            description=data["description"],
            comparison_id=data.get("comparison_id"),
            timestamp=timestamp,
            context=data.get("context", {})
        )

    @classmethod
    def create_position_difference(cls, step: int, astar_pos: tuple, engine_pos: tuple,
                                 entity_type: str = "player", severity: Severity = Severity.MAJOR) -> 'StateDifference':
        """位置差異を作成"""
        diff_type = DifferenceType.PLAYER_POSITION if entity_type == "player" else DifferenceType.ENEMY_POSITION
        description = f"{entity_type.capitalize()} position mismatch at step {step}"

        return cls(
            step_number=step,
            difference_type=diff_type,
            astar_value=astar_pos,
            engine_value=engine_pos,
            severity=severity,
            description=description,
            context={"entity_type": entity_type}
        )

    @classmethod
    def create_game_state_difference(cls, step: int, astar_state: str, engine_state: str,
                                   severity: Severity = Severity.CRITICAL) -> 'StateDifference':
        """ゲーム状態差異を作成"""
        description = f"Game state mismatch at step {step}: A* shows '{astar_state}', Engine shows '{engine_state}'"

        return cls(
            step_number=step,
            difference_type=DifferenceType.GAME_STATE,
            astar_value=astar_state,
            engine_value=engine_state,
            severity=severity,
            description=description
        )

    def __str__(self) -> str:
        """文字列表現"""
        severity_icon = {"critical": "🔴", "major": "🟠", "minor": "🟡"}
        icon = severity_icon.get(self.severity.value, "⚪")
        return f"{icon} Step {self.step_number}: {self.description}"

    def __repr__(self) -> str:
        """デバッグ表現"""
        return (f"StateDifference(step={self.step_number}, type={self.difference_type.value}, "
                f"severity={self.severity.value}, astar={self.astar_value}, engine={self.engine_value})")


@dataclass
class DifferenceReport:
    """差異レポート集約"""
    comparison_id: str
    total_differences: int
    critical_count: int
    major_count: int
    minor_count: int
    differences: List[StateDifference]
    generation_time: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_differences(cls, differences: List[StateDifference], comparison_id: str = None) -> 'DifferenceReport':
        """差異リストから作成"""
        if comparison_id is None:
            comparison_id = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        critical_count = sum(1 for d in differences if d.severity == Severity.CRITICAL)
        major_count = sum(1 for d in differences if d.severity == Severity.MAJOR)
        minor_count = sum(1 for d in differences if d.severity == Severity.MINOR)

        return cls(
            comparison_id=comparison_id,
            total_differences=len(differences),
            critical_count=critical_count,
            major_count=major_count,
            minor_count=minor_count,
            differences=differences
        )

    @property
    def has_critical_issues(self) -> bool:
        """重要な問題があるかどうか"""
        return self.critical_count > 0

    @property
    def is_acceptable(self) -> bool:
        """許容可能な差異レベルかどうか"""
        return self.critical_count == 0 and self.major_count <= 2

    def get_summary(self) -> str:
        """サマリーテキスト"""
        if self.total_differences == 0:
            return "✅ No differences found - engines are synchronized"

        status = "❌ Critical issues" if self.has_critical_issues else "⚠️ Minor differences"
        return (f"{status}: {self.total_differences} total "
                f"({self.critical_count} critical, {self.major_count} major, {self.minor_count} minor)")

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "comparison_id": self.comparison_id,
            "total_differences": self.total_differences,
            "critical_count": self.critical_count,
            "major_count": self.major_count,
            "minor_count": self.minor_count,
            "generation_time": self.generation_time.isoformat(),
            "summary": self.get_summary(),
            "has_critical_issues": self.has_critical_issues,
            "is_acceptable": self.is_acceptable,
            "differences": [d.to_dict() for d in self.differences]
        }