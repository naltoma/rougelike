"""
State Validator Contract - A*とゲームエンジンの状態比較インターフェース
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EngineType(Enum):
    ASTAR = "astar"
    GAME_ENGINE = "game_engine"


class DifferenceType(Enum):
    PLAYER_POSITION = "player_position"
    ENEMY_POSITION = "enemy_position"
    GAME_STATE = "game_state"
    ACTION_RESULT = "action_result"


class Severity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class EnemyState:
    enemy_id: str
    position: Tuple[int, int]
    direction: str
    patrol_index: int
    alert_state: str
    vision_range: int
    health: int
    enemy_type: str


@dataclass
class ExecutionLog:
    step_number: int
    engine_type: EngineType
    player_position: Tuple[int, int]
    player_direction: str
    enemy_states: List[EnemyState]
    action_taken: str
    game_over: bool
    victory: bool


@dataclass
class StateDifference:
    step_number: int
    difference_type: DifferenceType
    astar_value: Any
    engine_value: Any
    severity: Severity
    description: str


class StateValidator(ABC):
    """A*とゲームエンジンの状態比較を行うインターフェース"""

    @abstractmethod
    def validate_turn_by_turn(self, solution_path: List[str]) -> List[StateDifference]:
        """
        解法例を両エンジンで実行し、各ステップの状態を比較する

        Args:
            solution_path: アクション列 ["move", "turn_left", "attack", ...]

        Returns:
            検出された差異のリスト

        Raises:
            ValidationError: 検証処理中のエラー
        """
        pass

    @abstractmethod
    def compare_states(self, astar_log: ExecutionLog, engine_log: ExecutionLog) -> List[StateDifference]:
        """
        同一ステップの両エンジン状態を比較する

        Args:
            astar_log: A*エンジンの実行ログ
            engine_log: ゲームエンジンの実行ログ

        Returns:
            差異リスト
        """
        pass

    @abstractmethod
    def generate_debug_report(self, differences: List[StateDifference]) -> str:
        """
        差異情報から詳細なデバッグレポートを生成する

        Args:
            differences: 検出された差異リスト

        Returns:
            フォーマットされたデバッグレポート文字列
        """
        pass


class ExecutionEngine(ABC):
    """ゲーム実行エンジンの抽象インターフェース"""

    @abstractmethod
    def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
        """
        解法例を実行し、各ステップの状態ログを返す

        Args:
            solution_path: 実行するアクション列

        Returns:
            各ステップの実行ログリスト
        """
        pass

    @abstractmethod
    def get_current_state(self) -> ExecutionLog:
        """
        現在の状態を取得する

        Returns:
            現在の実行状態ログ
        """
        pass

    @abstractmethod
    def reset_stage(self, stage_file: str) -> None:
        """
        ステージを初期状態にリセットする

        Args:
            stage_file: ステージファイルパス
        """
        pass


class UnifiedEnemyAI(ABC):
    """統一敵AIロジックインターフェース"""

    @abstractmethod
    def calculate_enemy_action(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> str:
        """
        敵の次アクションを計算する（両エンジン共通ロジック）

        Args:
            enemy_state: 敵の現在状態
            player_position: プレイヤー位置

        Returns:
            敵のアクション ("move", "turn_left", "turn_right", "wait")
        """
        pass

    @abstractmethod
    def update_patrol_state(self, enemy_state: EnemyState) -> EnemyState:
        """
        パトロール状態を更新する

        Args:
            enemy_state: 更新前の敵状態

        Returns:
            更新後の敵状態
        """
        pass

    @abstractmethod
    def check_player_detection(self, enemy_state: EnemyState, player_position: Tuple[int, int]) -> bool:
        """
        プレイヤー発見判定を行う

        Args:
            enemy_state: 敵状態
            player_position: プレイヤー位置

        Returns:
            プレイヤーを発見した場合True
        """
        pass


# Contract Tests Interface
def test_state_validator_contract():
    """StateValidatorの契約テスト"""
    # テスト実装は後続のフェーズで作成
    pass


def test_execution_engine_contract():
    """ExecutionEngineの契約テスト"""
    # テスト実装は後続のフェーズで作成
    pass


def test_unified_enemy_ai_contract():
    """UnifiedEnemyAIの契約テスト"""
    # テスト実装は後続のフェーズで作成
    pass