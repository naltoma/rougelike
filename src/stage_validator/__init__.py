"""
Stage Validator Library

A*アルゴリズムとゲームエンジンの動作差異を検出・修正するライブラリ。
ステップ毎の状態比較と敵移動ロジック同期を提供。
"""

from .state_validator import StateValidator
from .execution_engine import ExecutionEngine, MockExecutionEngine
from .astar_engine import AStarEngine
from .game_engine_wrapper import GameEngineWrapper
from .unified_enemy_ai import UnifiedEnemyAI, StandardEnemyAI

# Factory functions
from .execution_engine import create_mock_engine
from .unified_enemy_ai import create_standard_enemy_ai
from .debug_logger import create_debug_logger

__version__ = "1.2.12"
__all__ = [
    # Core classes
    "StateValidator",
    "ExecutionEngine",
    "UnifiedEnemyAI",

    # Concrete implementations
    "AStarEngine",
    "GameEngineWrapper",
    "MockExecutionEngine",
    "StandardEnemyAI",

    # Factory functions
    "create_mock_engine",
    "create_standard_enemy_ai",
    "create_debug_logger"
]