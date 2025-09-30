"""
ValidationConfig Data Model

システム動作設定の一元管理データモデル。
main_*.py編集禁止制約を満たすため、全設定を一箇所に集約。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import os
import json
from pathlib import Path


class VisionCheckTiming(Enum):
    """視覚チェックタイミング"""
    BEFORE_ACTION = "before_action"
    AFTER_ACTION = "after_action"


class PatrolAdvancementRule(Enum):
    """パトロール進行ルール"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"


class LogDetailLevel(Enum):
    """ログ詳細レベル"""
    MINIMAL = "minimal"
    DETAILED = "detailed"
    DEBUG = "debug"


@dataclass
class ValidationConfig:
    """検証設定データモデル"""
    # 敵行動設定
    enemy_rotation_delay: int = 1
    vision_check_timing: VisionCheckTiming = VisionCheckTiming.AFTER_ACTION
    patrol_advancement_rule: PatrolAdvancementRule = PatrolAdvancementRule.IMMEDIATE
    alert_cooldown_turns: int = 3
    chase_timeout_turns: int = 10

    # 実行順序設定
    action_execution_order: List[str] = field(default_factory=lambda: [
        "player_action",
        "enemy_vision_check",
        "enemy_movement",
        "enemy_attack_check",
        "item_collection_check",
        "victory_condition_check"
    ])

    # ログ設定
    log_detail_level: LogDetailLevel = LogDetailLevel.DETAILED
    enable_step_by_step_logging: bool = True
    enable_debug_visualization: bool = False
    log_file_path: Optional[str] = None

    # パフォーマンス設定
    max_solution_steps: int = 1000
    comparison_timeout_seconds: int = 60
    enable_concurrent_validation: bool = False
    memory_optimization_enabled: bool = True

    # バリデーション設定
    strict_position_matching: bool = True
    allow_minor_timing_differences: bool = False
    ignore_cosmetic_differences: bool = True
    position_tolerance: float = 0.0

    # A*固有設定
    astar_search_timeout: int = 30
    astar_max_nodes: int = 10000
    astar_heuristic_weight: float = 1.0

    # ゲームエンジン固有設定
    game_engine_step_delay: float = 0.0
    enable_visual_mode: bool = False
    auto_reset_on_failure: bool = True

    # デバッグ機能
    enable_debug_file_logging: bool = False

    def __post_init__(self):
        """バリデーション"""
        if self.enemy_rotation_delay < 1:
            raise ValueError("enemy_rotation_delay must be at least 1")

        if self.alert_cooldown_turns < 0:
            raise ValueError("alert_cooldown_turns must be non-negative")

        if self.chase_timeout_turns < 1:
            raise ValueError("chase_timeout_turns must be at least 1")

        if self.max_solution_steps <= 0:
            raise ValueError("max_solution_steps must be positive")

        if self.comparison_timeout_seconds <= 0:
            raise ValueError("comparison_timeout_seconds must be positive")

        if not (0.0 <= self.position_tolerance <= 1.0):
            raise ValueError("position_tolerance must be between 0.0 and 1.0")

        if self.astar_search_timeout <= 0:
            raise ValueError("astar_search_timeout must be positive")

        if self.astar_max_nodes <= 0:
            raise ValueError("astar_max_nodes must be positive")

        if self.astar_heuristic_weight <= 0.0:
            raise ValueError("astar_heuristic_weight must be positive")

        # アクション実行順序の検証
        required_phases = {
            "player_action",
            "enemy_vision_check",
            "enemy_movement",
            "victory_condition_check"
        }
        if not required_phases.issubset(set(self.action_execution_order)):
            missing = required_phases - set(self.action_execution_order)
            raise ValueError(f"Missing required execution phases: {missing}")

    @classmethod
    def load_from_file(cls, config_path: str) -> 'ValidationConfig':
        """設定ファイルから読み込み"""
        path = Path(config_path)
        if not path.exists():
            # デフォルト設定を返す
            return cls()

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return cls.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Failed to load config from {config_path}: {e}")

    def save_to_file(self, config_path: str) -> None:
        """設定ファイルに保存"""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise ValueError(f"Failed to save config to {config_path}: {e}")

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "enemy_rotation_delay": self.enemy_rotation_delay,
            "vision_check_timing": self.vision_check_timing.value,
            "patrol_advancement_rule": self.patrol_advancement_rule.value,
            "alert_cooldown_turns": self.alert_cooldown_turns,
            "chase_timeout_turns": self.chase_timeout_turns,
            "action_execution_order": self.action_execution_order,
            "log_detail_level": self.log_detail_level.value,
            "enable_step_by_step_logging": self.enable_step_by_step_logging,
            "enable_debug_visualization": self.enable_debug_visualization,
            "log_file_path": self.log_file_path,
            "max_solution_steps": self.max_solution_steps,
            "comparison_timeout_seconds": self.comparison_timeout_seconds,
            "enable_concurrent_validation": self.enable_concurrent_validation,
            "memory_optimization_enabled": self.memory_optimization_enabled,
            "strict_position_matching": self.strict_position_matching,
            "allow_minor_timing_differences": self.allow_minor_timing_differences,
            "ignore_cosmetic_differences": self.ignore_cosmetic_differences,
            "position_tolerance": self.position_tolerance,
            "astar_search_timeout": self.astar_search_timeout,
            "astar_max_nodes": self.astar_max_nodes,
            "astar_heuristic_weight": self.astar_heuristic_weight,
            "game_engine_step_delay": self.game_engine_step_delay,
            "enable_visual_mode": self.enable_visual_mode,
            "auto_reset_on_failure": self.auto_reset_on_failure
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ValidationConfig':
        """辞書から作成"""
        return cls(
            enemy_rotation_delay=data.get("enemy_rotation_delay", 1),
            vision_check_timing=VisionCheckTiming(data.get("vision_check_timing", "after_action")),
            patrol_advancement_rule=PatrolAdvancementRule(data.get("patrol_advancement_rule", "immediate")),
            alert_cooldown_turns=data.get("alert_cooldown_turns", 3),
            chase_timeout_turns=data.get("chase_timeout_turns", 10),
            action_execution_order=data.get("action_execution_order", [
                "player_action", "enemy_vision_check", "enemy_movement",
                "enemy_attack_check", "item_collection_check", "victory_condition_check"
            ]),
            log_detail_level=LogDetailLevel(data.get("log_detail_level", "detailed")),
            enable_step_by_step_logging=data.get("enable_step_by_step_logging", True),
            enable_debug_visualization=data.get("enable_debug_visualization", False),
            log_file_path=data.get("log_file_path"),
            max_solution_steps=data.get("max_solution_steps", 1000),
            comparison_timeout_seconds=data.get("comparison_timeout_seconds", 60),
            enable_concurrent_validation=data.get("enable_concurrent_validation", False),
            memory_optimization_enabled=data.get("memory_optimization_enabled", True),
            strict_position_matching=data.get("strict_position_matching", True),
            allow_minor_timing_differences=data.get("allow_minor_timing_differences", False),
            ignore_cosmetic_differences=data.get("ignore_cosmetic_differences", True),
            position_tolerance=data.get("position_tolerance", 0.0),
            astar_search_timeout=data.get("astar_search_timeout", 30),
            astar_max_nodes=data.get("astar_max_nodes", 10000),
            astar_heuristic_weight=data.get("astar_heuristic_weight", 1.0),
            game_engine_step_delay=data.get("game_engine_step_delay", 0.0),
            enable_visual_mode=data.get("enable_visual_mode", False),
            auto_reset_on_failure=data.get("auto_reset_on_failure", True)
        )

    @classmethod
    def get_default_config_path(cls) -> str:
        """デフォルト設定ファイルパス"""
        return "src/stage_validator/config/validation_config.json"

    @classmethod
    def load_default(cls) -> 'ValidationConfig':
        """デフォルト設定を読み込み"""
        default_path = cls.get_default_config_path()
        return cls.load_from_file(default_path)

    def create_optimized_for_performance(self) -> 'ValidationConfig':
        """パフォーマンス最適化設定を作成"""
        config = ValidationConfig(
            # 基本設定をコピー
            enemy_rotation_delay=self.enemy_rotation_delay,
            vision_check_timing=self.vision_check_timing,
            patrol_advancement_rule=self.patrol_advancement_rule,

            # パフォーマンス最適化
            log_detail_level=LogDetailLevel.MINIMAL,
            enable_step_by_step_logging=False,
            enable_debug_visualization=False,
            enable_concurrent_validation=True,
            memory_optimization_enabled=True,
            ignore_cosmetic_differences=True,
            allow_minor_timing_differences=True,
            comparison_timeout_seconds=30,
            game_engine_step_delay=0.0
        )
        return config

    def create_optimized_for_debugging(self) -> 'ValidationConfig':
        """デバッグ最適化設定を作成"""
        config = ValidationConfig(
            # 基本設定をコピー
            enemy_rotation_delay=self.enemy_rotation_delay,
            vision_check_timing=self.vision_check_timing,
            patrol_advancement_rule=self.patrol_advancement_rule,

            # デバッグ最適化
            log_detail_level=LogDetailLevel.DEBUG,
            enable_step_by_step_logging=True,
            enable_debug_visualization=True,
            enable_concurrent_validation=False,
            strict_position_matching=True,
            allow_minor_timing_differences=False,
            ignore_cosmetic_differences=False,
            position_tolerance=0.0,
            comparison_timeout_seconds=120,
            auto_reset_on_failure=False
        )
        return config

    def validate_compatibility(self, other: 'ValidationConfig') -> List[str]:
        """他の設定との互換性チェック"""
        issues = []

        if self.enemy_rotation_delay != other.enemy_rotation_delay:
            issues.append(f"Enemy rotation delay mismatch: {self.enemy_rotation_delay} vs {other.enemy_rotation_delay}")

        if self.vision_check_timing != other.vision_check_timing:
            issues.append(f"Vision check timing mismatch: {self.vision_check_timing.value} vs {other.vision_check_timing.value}")

        if self.patrol_advancement_rule != other.patrol_advancement_rule:
            issues.append(f"Patrol advancement rule mismatch: {self.patrol_advancement_rule.value} vs {other.patrol_advancement_rule.value}")

        if self.action_execution_order != other.action_execution_order:
            issues.append("Action execution order mismatch")

        return issues

    def __str__(self) -> str:
        """文字列表現"""
        return (f"ValidationConfig(rotation_delay={self.enemy_rotation_delay}, "
                f"vision_timing={self.vision_check_timing.value}, "
                f"patrol_rule={self.patrol_advancement_rule.value}, "
                f"log_level={self.log_detail_level.value})")

    def __repr__(self) -> str:
        """デバッグ表現"""
        return f"ValidationConfig({self.to_dict()})"


# グローバル設定インスタンス（シングルトンパターン）
_global_config: Optional[ValidationConfig] = None


def get_global_config() -> ValidationConfig:
    """グローバル設定を取得"""
    global _global_config
    if _global_config is None:
        _global_config = ValidationConfig.load_default()
    return _global_config


def set_global_config(config: ValidationConfig) -> None:
    """グローバル設定を設定"""
    global _global_config
    _global_config = config


def reset_global_config() -> None:
    """グローバル設定をリセット"""
    global _global_config
    _global_config = None