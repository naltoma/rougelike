"""
Stage Validator Data Models

ゲーム状態比較用のデータモデル定義。
"""

from .execution_log import ExecutionLog, EnemyState, EngineType
from .solution_path import SolutionPath, analyze_solution_patterns
from .state_difference import StateDifference, DifferenceType, Severity, DifferenceReport
from .validation_config import ValidationConfig, VisionCheckTiming, PatrolAdvancementRule, LogDetailLevel
from .validation_config import get_global_config, set_global_config, reset_global_config

__all__ = [
    # Core models
    "ExecutionLog",
    "EnemyState",
    "SolutionPath",
    "StateDifference",
    "ValidationConfig",
    "DifferenceReport",

    # Enums
    "EngineType",
    "DifferenceType",
    "Severity",
    "VisionCheckTiming",
    "PatrolAdvancementRule",
    "LogDetailLevel",

    # Utility functions
    "analyze_solution_patterns",
    "get_global_config",
    "set_global_config",
    "reset_global_config"
]