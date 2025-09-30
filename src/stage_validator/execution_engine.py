"""
ExecutionEngine Base Implementation

ゲーム実行エンジンの抽象基底クラス。
A*エンジンとゲームエンジンの統一インターフェース。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

from .models import ExecutionLog, EnemyState, ValidationConfig, get_global_config


class ExecutionEngine(ABC):
    """ゲーム実行エンジンの抽象基底クラス"""

    def __init__(self, engine_name: str, config: Optional[ValidationConfig] = None):
        self.engine_name = engine_name
        self.config = config or get_global_config()
        self.logger = self._setup_logger()

        # 実行状態
        self.current_stage_file: Optional[str] = None
        self.is_initialized: bool = False
        self.execution_logs: List[ExecutionLog] = []
        self.current_step: int = 0

    def _setup_logger(self) -> logging.Logger:
        """ロガーセットアップ"""
        logger = logging.getLogger(f"{self.engine_name}.{id(self)}")

        if not logger.handlers:
            handler = logging.StreamHandler()

            if self.config.log_detail_level.value == "debug":
                level = logging.DEBUG
            elif self.config.log_detail_level.value == "detailed":
                level = logging.INFO
            else:
                level = logging.WARNING

            handler.setFormatter(logging.Formatter(
                f"%(asctime)s - {self.engine_name} - %(levelname)s - %(message)s"
            ))
            logger.addHandler(handler)
            logger.setLevel(level)

        return logger

    @abstractmethod
    def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
        """
        解法例を実行し、各ステップの状態ログを返す

        Args:
            solution_path: 実行するアクション列

        Returns:
            各ステップの実行ログリスト

        Raises:
            ValueError: 無効なアクション
            RuntimeError: 実行エラー
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

        Raises:
            FileNotFoundError: ステージファイルが存在しない
            ValueError: 無効なステージファイル
        """
        pass

    def validate_stage_file(self, stage_file: str) -> None:
        """ステージファイルの検証"""
        if not stage_file:
            raise ValueError("stage_file cannot be empty")

        stage_path = Path(stage_file)
        if not stage_path.exists():
            raise FileNotFoundError(f"Stage file not found: {stage_file}")

        if not stage_path.suffix.lower() in ['.yml', '.yaml']:
            raise ValueError(f"Invalid stage file format: {stage_file}")

    def validate_action(self, action: str) -> None:
        """アクションの検証"""
        valid_actions = {"move", "turn_left", "turn_right", "attack", "pickup", "wait", "dispose", "none"}
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Valid actions: {valid_actions}")

    def validate_solution_path(self, solution_path: List[str]) -> None:
        """解法例の検証"""
        if not solution_path:
            raise ValueError("solution_path cannot be empty")

        if len(solution_path) > self.config.max_solution_steps:
            raise ValueError(f"Solution too long: {len(solution_path)} > {self.config.max_solution_steps}")

        for i, action in enumerate(solution_path):
            try:
                self.validate_action(action)
            except ValueError as e:
                raise ValueError(f"Invalid action at step {i}: {e}")

    def clear_logs(self) -> None:
        """実行ログをクリア"""
        self.execution_logs.clear()
        self.current_step = 0

    def get_execution_summary(self) -> Dict[str, Any]:
        """実行サマリーを取得"""
        if not self.execution_logs:
            return {"status": "no_execution", "steps": 0}

        last_log = self.execution_logs[-1]
        total_steps = len(self.execution_logs)

        status = "running"
        if last_log.victory:
            status = "victory"
        elif last_log.game_over:
            status = "game_over"

        # アクション統計
        action_counts = {}
        for log in self.execution_logs:
            action = log.action_taken
            action_counts[action] = action_counts.get(action, 0) + 1

        # 敵関連統計
        enemy_count = len(last_log.enemy_states) if last_log.enemy_states else 0
        enemy_types = set()
        for log in self.execution_logs:
            for enemy in log.enemy_states:
                enemy_types.add(enemy.enemy_type)

        return {
            "status": status,
            "steps": total_steps,
            "final_player_position": last_log.player_position,
            "final_player_direction": last_log.player_direction,
            "enemy_count": enemy_count,
            "enemy_types": list(enemy_types),
            "action_counts": action_counts,
            "stage_file": self.current_stage_file,
            "engine": self.engine_name
        }

    def get_step_log(self, step_number: int) -> Optional[ExecutionLog]:
        """指定ステップのログを取得"""
        for log in self.execution_logs:
            if log.step_number == step_number:
                return log
        return None

    def get_logs_in_range(self, start_step: int, end_step: int) -> List[ExecutionLog]:
        """指定範囲のログを取得"""
        return [log for log in self.execution_logs
                if start_step <= log.step_number <= end_step]

    def has_enemy_conflicts(self, player_pos: Tuple[int, int],
                          enemy_states: List[EnemyState]) -> bool:
        """プレイヤーと敵の衝突チェック"""
        for enemy in enemy_states:
            if enemy.position == player_pos:
                return True

            # 大型敵の場合は複数セルチェック
            if enemy.enemy_type == "large":
                # 2x2の大型敵の場合
                large_positions = [
                    enemy.position,
                    (enemy.position[0] + 1, enemy.position[1]),
                    (enemy.position[0], enemy.position[1] + 1),
                    (enemy.position[0] + 1, enemy.position[1] + 1)
                ]
                if player_pos in large_positions:
                    return True

        return False

    def calculate_next_position(self, current_pos: Tuple[int, int], direction: str) -> Tuple[int, int]:
        """次の位置を計算"""
        x, y = current_pos

        direction_map = {
            "up": (x, y - 1),
            "down": (x, y + 1),
            "left": (x - 1, y),
            "right": (x + 1, y)
        }

        return direction_map.get(direction, current_pos)

    def rotate_direction(self, current_direction: str, rotation: str) -> str:
        """向きを回転"""
        directions = ["up", "right", "down", "left"]
        current_index = directions.index(current_direction)

        if rotation == "turn_right":
            new_index = (current_index + 1) % 4
        elif rotation == "turn_left":
            new_index = (current_index - 1) % 4
        else:
            return current_direction

        return directions[new_index]

    def __str__(self) -> str:
        return f"{self.engine_name}Engine(stage={self.current_stage_file}, steps={len(self.execution_logs)})"

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(name='{self.engine_name}', "
                f"initialized={self.is_initialized}, steps={len(self.execution_logs)})")


class MockExecutionEngine(ExecutionEngine):
    """テスト用のモック実行エンジン"""

    def __init__(self, engine_name: str = "Mock", config: Optional[ValidationConfig] = None):
        super().__init__(engine_name, config)
        self.mock_player_pos = (1, 1)
        self.mock_player_dir = "up"
        self.mock_enemies = []
        self.mock_game_over = False
        self.mock_victory = False

    def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
        """モック実行"""
        self.validate_solution_path(solution_path)
        self.clear_logs()

        for step, action in enumerate(solution_path):
            # シンプルなモック動作
            if action == "move":
                self.mock_player_pos = self.calculate_next_position(self.mock_player_pos, self.mock_player_dir)
            elif action in ["turn_left", "turn_right"]:
                self.mock_player_dir = self.rotate_direction(self.mock_player_dir, action)

            # ログ作成
            log = ExecutionLog(
                step_number=step,
                engine_type=self.config.engine_type if hasattr(self.config, 'engine_type') else "mock",
                player_position=self.mock_player_pos,
                player_direction=self.mock_player_dir,
                enemy_states=self.mock_enemies.copy(),
                action_taken=action,
                game_over=self.mock_game_over,
                victory=self.mock_victory
            )
            self.execution_logs.append(log)

            # 勝利条件チェック（モック）
            if self.mock_player_pos == (10, 10):
                self.mock_victory = True
                break

        return self.execution_logs

    def get_current_state(self) -> ExecutionLog:
        """現在状態を取得"""
        if self.execution_logs:
            return self.execution_logs[-1]

        # 初期状態
        return ExecutionLog(
            step_number=0,
            engine_type="mock",
            player_position=self.mock_player_pos,
            player_direction=self.mock_player_dir,
            enemy_states=self.mock_enemies,
            action_taken="none",
            game_over=False,
            victory=False
        )

    def reset_stage(self, stage_file: str) -> None:
        """ステージリセット"""
        self.validate_stage_file(stage_file)
        self.current_stage_file = stage_file

        # モック初期化
        self.mock_player_pos = (1, 1)
        self.mock_player_dir = "up"
        self.mock_enemies = []
        self.mock_game_over = False
        self.mock_victory = False
        self.clear_logs()
        self.is_initialized = True

        self.logger.info(f"Mock engine reset with stage: {stage_file}")


# エクスポート用のファクトリー関数
def create_mock_engine(config: Optional[ValidationConfig] = None) -> MockExecutionEngine:
    """モックエンジン作成"""
    return MockExecutionEngine(config=config)