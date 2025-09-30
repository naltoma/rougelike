"""
StateValidator Implementation

A*とゲームエンジンの状態比較を行うメインクラス。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import uuid

from .models import (
    ExecutionLog, StateDifference, SolutionPath, ValidationConfig,
    DifferenceType, Severity, DifferenceReport,
    get_global_config
)
from .execution_engine import ExecutionEngine


class StateValidator:
    """A*とゲームエンジンの状態比較実装"""

    def __init__(self,
                 astar_engine: Optional[ExecutionEngine] = None,
                 game_engine: Optional[ExecutionEngine] = None,
                 config: Optional[ValidationConfig] = None):
        self.astar_engine = astar_engine
        self.game_engine = game_engine
        self.config = config or get_global_config()
        self.logger = self._setup_logger()

        # 実行状態
        self.current_stage_file: Optional[str] = None
        self.comparison_sessions: Dict[str, List[StateDifference]] = {}

    def _setup_logger(self) -> logging.Logger:
        """ロガーセットアップ"""
        logger = logging.getLogger(f"StateValidator.{id(self)}")

        if not logger.handlers:
            handler = logging.StreamHandler()

            if self.config.log_detail_level.value == "debug":
                level = logging.DEBUG
                format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            elif self.config.log_detail_level.value == "detailed":
                level = logging.INFO
                format_str = "%(asctime)s - %(levelname)s - %(message)s"
            else:  # minimal
                level = logging.WARNING
                format_str = "%(levelname)s - %(message)s"

            handler.setFormatter(logging.Formatter(format_str))
            logger.addHandler(handler)
            logger.setLevel(level)

        return logger

    def validate_turn_by_turn(self, solution_path: List[str]) -> List[StateDifference]:
        """
        解法例を両エンジンで実行し、各ステップの状態を比較する
        """
        # Enhanced error handling and edge case coverage - v1.2.12
        if not self.astar_engine or not self.game_engine:
            raise ValueError("Both astar_engine and game_engine must be set")

        if not solution_path:
            raise ValueError("solution_path cannot be empty")

        if not isinstance(solution_path, list):
            raise TypeError("solution_path must be a list of strings")

        if not all(isinstance(action, str) for action in solution_path):
            invalid_actions = [action for action in solution_path if not isinstance(action, str)]
            raise TypeError(f"All actions must be strings, found invalid: {invalid_actions[:5]}")

        if len(solution_path) > self.config.max_solution_steps:
            raise ValueError(f"Solution too long: {len(solution_path)} > {self.config.max_solution_steps}")

        comparison_id = str(uuid.uuid4())[:8]
        self.logger.info(f"Starting validation {comparison_id} with {len(solution_path)} steps")

        try:
            # Enhanced engine execution with error handling
            astar_logs = self._execute_engine_safely(self.astar_engine, solution_path, "A*")
            game_logs = self._execute_engine_safely(self.game_engine, solution_path, "GameEngine")

            self.logger.debug(f"A* generated {len(astar_logs)} logs, Game engine generated {len(game_logs)} logs")

            # ステップ毎比較
            differences = []
            max_steps = max(len(astar_logs), len(game_logs))

            for step in range(max_steps):
                astar_log = astar_logs[step] if step < len(astar_logs) else None
                game_log = game_logs[step] if step < len(game_logs) else None

                step_differences = self.compare_states(astar_log, game_log, step)
                differences.extend(step_differences)

                # 早期終了条件
                if self._should_stop_comparison(differences, step):
                    self.logger.warning(f"Stopping comparison at step {step} due to critical differences")
                    break

            # 結果保存
            self.comparison_sessions[comparison_id] = differences

            self.logger.info(f"Validation {comparison_id} completed: {len(differences)} differences found")
            return differences

        except Exception as e:
            self.logger.error(f"Validation {comparison_id} failed: {e}")
            raise

    def _execute_engine_safely(self, engine: 'ExecutionEngine', solution_path: List[str], engine_name: str) -> List['ExecutionLog']:
        """
        エンジン実行の安全なラッパー - v1.2.12
        """
        try:
            if not hasattr(engine, 'execute_solution'):
                raise AttributeError(f"{engine_name} engine missing execute_solution method")

            # Check if engine is initialized
            if hasattr(engine, 'is_initialized') and not engine.is_initialized:
                raise RuntimeError(f"{engine_name} engine not initialized. Call reset_stage() first.")

            logs = engine.execute_solution(solution_path)

            if not isinstance(logs, list):
                raise TypeError(f"{engine_name} engine returned non-list: {type(logs)}")

            if not logs:
                self.logger.warning(f"{engine_name} engine returned empty logs for {len(solution_path)} steps")
                return []

            # Validate log structure
            for i, log in enumerate(logs):
                if not hasattr(log, 'step_number'):
                    raise AttributeError(f"{engine_name} engine log {i} missing step_number")
                if not hasattr(log, 'player_position'):
                    raise AttributeError(f"{engine_name} engine log {i} missing player_position")

            return logs

        except Exception as e:
            self.logger.error(f"Safe execution failed for {engine_name}: {e}")
            # Return empty logs to allow graceful degradation
            return []

    def compare_states(self, astar_log: Optional[ExecutionLog],
                      game_log: Optional[ExecutionLog],
                      step_number: Optional[int] = None) -> List[StateDifference]:
        """
        同一ステップの両エンジン状態を比較する - Enhanced error handling v1.2.12
        """
        differences = []

        # ログ存在チェック with enhanced error handling
        if astar_log is None and game_log is None:
            if step_number is not None:
                self.logger.warning(f"Both engines missing logs for step {step_number}")
            return differences

        if step_number is None:
            try:
                step_number = astar_log.step_number if astar_log else game_log.step_number
            except (AttributeError, TypeError) as e:
                self.logger.error(f"Failed to get step_number from logs: {e}")
                step_number = 0  # Fallback

        # Validate step_number
        if not isinstance(step_number, int) or step_number < 0:
            self.logger.warning(f"Invalid step_number: {step_number}, using 0")
            step_number = 0

        # 片方のエンジンでのみ終了
        if astar_log is None:
            diff = StateDifference(
                step_number=step_number,
                difference_type=DifferenceType.GAME_STATE,
                astar_value=None,
                engine_value="running",
                severity=Severity.CRITICAL,
                description=f"A* engine terminated early at step {step_number}"
            )
            differences.append(diff)
            return differences

        if game_log is None:
            diff = StateDifference(
                step_number=step_number,
                difference_type=DifferenceType.GAME_STATE,
                astar_value="running",
                engine_value=None,
                severity=Severity.CRITICAL,
                description=f"Game engine terminated early at step {step_number}"
            )
            differences.append(diff)
            return differences

        # プレイヤー位置比較
        if astar_log.player_position != game_log.player_position:
            severity = Severity.CRITICAL if self.config.strict_position_matching else Severity.MAJOR
            diff = StateDifference.create_position_difference(
                step_number, astar_log.player_position, game_log.player_position,
                "player", severity
            )
            differences.append(diff)

        # プレイヤー向き比較
        if astar_log.player_direction != game_log.player_direction:
            diff = StateDifference(
                step_number=step_number,
                difference_type=DifferenceType.PLAYER_POSITION,
                astar_value=astar_log.player_direction,
                engine_value=game_log.player_direction,
                severity=Severity.MINOR,
                description=f"Player direction mismatch at step {step_number}"
            )
            differences.append(diff)

        # 敵状態比較
        enemy_diffs = self._compare_enemy_states(astar_log.enemy_states, game_log.enemy_states, step_number)
        differences.extend(enemy_diffs)

        # ゲーム終了状態比較
        if astar_log.game_over != game_log.game_over or astar_log.victory != game_log.victory:
            astar_state = "victory" if astar_log.victory else ("game_over" if astar_log.game_over else "running")
            engine_state = "victory" if game_log.victory else ("game_over" if game_log.game_over else "running")

            diff = StateDifference.create_game_state_difference(step_number, astar_state, engine_state)
            differences.append(diff)

        # アクション比較
        if astar_log.action_taken != game_log.action_taken and not self.config.ignore_cosmetic_differences:
            diff = StateDifference(
                step_number=step_number,
                difference_type=DifferenceType.ACTION_RESULT,
                astar_value=astar_log.action_taken,
                engine_value=game_log.action_taken,
                severity=Severity.MINOR,
                description=f"Action mismatch at step {step_number}"
            )
            differences.append(diff)

        return differences

    def _compare_enemy_states(self, astar_enemies: List, game_enemies: List, step_number: int) -> List[StateDifference]:
        """敵状態比較"""
        differences = []

        # 敵数比較
        if len(astar_enemies) != len(game_enemies):
            diff = StateDifference(
                step_number=step_number,
                difference_type=DifferenceType.ENEMY_POSITION,
                astar_value=len(astar_enemies),
                engine_value=len(game_enemies),
                severity=Severity.CRITICAL,
                description=f"Enemy count mismatch at step {step_number}"
            )
            differences.append(diff)
            return differences

        # 敵ID別比較
        astar_enemies_by_id = {enemy.enemy_id: enemy for enemy in astar_enemies}
        game_enemies_by_id = {enemy.enemy_id: enemy for enemy in game_enemies}

        all_enemy_ids = set(astar_enemies_by_id.keys()) | set(game_enemies_by_id.keys())

        for enemy_id in all_enemy_ids:
            astar_enemy = astar_enemies_by_id.get(enemy_id)
            game_enemy = game_enemies_by_id.get(enemy_id)

            if not astar_enemy or not game_enemy:
                diff = StateDifference(
                    step_number=step_number,
                    difference_type=DifferenceType.ENEMY_POSITION,
                    astar_value=bool(astar_enemy),
                    engine_value=bool(game_enemy),
                    severity=Severity.CRITICAL,
                    description=f"Enemy {enemy_id} existence mismatch at step {step_number}"
                )
                differences.append(diff)
                continue

            # 位置比較
            if astar_enemy.position != game_enemy.position:
                diff = StateDifference.create_position_difference(
                    step_number, astar_enemy.position, game_enemy.position,
                    f"enemy_{enemy_id}", Severity.MAJOR
                )
                differences.append(diff)

            # 向き比較
            if astar_enemy.direction != game_enemy.direction:
                diff = StateDifference(
                    step_number=step_number,
                    difference_type=DifferenceType.ENEMY_POSITION,
                    astar_value=astar_enemy.direction,
                    engine_value=game_enemy.direction,
                    severity=Severity.MINOR,
                    description=f"Enemy {enemy_id} direction mismatch at step {step_number}"
                )
                differences.append(diff)

            # パトロール状態比較
            if astar_enemy.patrol_index != game_enemy.patrol_index:
                diff = StateDifference(
                    step_number=step_number,
                    difference_type=DifferenceType.PATROL_STATE,
                    astar_value=astar_enemy.patrol_index,
                    engine_value=game_enemy.patrol_index,
                    severity=Severity.MAJOR,
                    description=f"Enemy {enemy_id} patrol index mismatch at step {step_number}"
                )
                differences.append(diff)

            # 警戒状態比較
            if astar_enemy.alert_state != game_enemy.alert_state:
                diff = StateDifference(
                    step_number=step_number,
                    difference_type=DifferenceType.VISION_STATE,
                    astar_value=astar_enemy.alert_state,
                    engine_value=game_enemy.alert_state,
                    severity=Severity.MAJOR,
                    description=f"Enemy {enemy_id} alert state mismatch at step {step_number}"
                )
                differences.append(diff)

        return differences

    def _should_stop_comparison(self, differences: List[StateDifference], current_step: int) -> bool:
        """比較を早期終了すべきかどうか"""
        critical_count = sum(1 for d in differences if d.severity == Severity.CRITICAL)

        # 重要な差異が多い場合は終了
        if critical_count >= 3:
            return True

        # ゲーム終了状態で差異がある場合は終了
        game_state_diffs = [d for d in differences if d.difference_type == DifferenceType.GAME_STATE]
        if game_state_diffs and current_step > 5:
            return True

        return False

    def generate_debug_report(self, differences: List[StateDifference]) -> str:
        """
        差異情報から詳細なデバッグレポートを生成する
        """
        if not differences:
            return "✅ No differences found - engines are perfectly synchronized"

        report = DifferenceReport.from_differences(differences)

        lines = [
            "🔍 State Validation Debug Report",
            "=" * 50,
            f"Generated: {report.generation_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Comparison ID: {report.comparison_id}",
            "",
            "📊 Summary:",
            f"  Total differences: {report.total_differences}",
            f"  🔴 Critical: {report.critical_count}",
            f"  🟠 Major: {report.major_count}",
            f"  🟡 Minor: {report.minor_count}",
            f"  Status: {report.get_summary()}",
            ""
        ]

        if report.has_critical_issues:
            lines.extend([
                "❗ CRITICAL ISSUES DETECTED",
                "These differences prevent A* solutions from working in the game engine:",
                ""
            ])

        # 重要度別にグループ化
        for severity in [Severity.CRITICAL, Severity.MAJOR, Severity.MINOR]:
            severity_diffs = [d for d in differences if d.severity == severity]
            if not severity_diffs:
                continue

            severity_names = {
                Severity.CRITICAL: "🔴 CRITICAL",
                Severity.MAJOR: "🟠 MAJOR",
                Severity.MINOR: "🟡 MINOR"
            }

            lines.extend([
                f"{severity_names[severity]} ({len(severity_diffs)} issues):",
                "-" * 30
            ])

            for diff in severity_diffs[:10]:  # 最初の10件
                lines.append(f"  Step {diff.step_number:3d}: {diff.description}")
                if self.config.log_detail_level.value == "debug":
                    lines.append(f"              A*: {diff.astar_value}")
                    lines.append(f"              Engine: {diff.engine_value}")
                    if diff.context:
                        lines.append(f"              Context: {diff.context}")

            if len(severity_diffs) > 10:
                lines.append(f"  ... and {len(severity_diffs) - 10} more {severity.value} differences")

            lines.append("")

        # 推奨事項
        lines.extend([
            "💡 Recommendations:",
            "- Check enemy movement logic synchronization",
            "- Verify patrol index advancement timing",
            "- Review vision system timing differences",
            "- Ensure rotation delay consistency"
        ])

        return "\n".join(lines)

    def set_stage_file(self, stage_file: str) -> None:
        """ステージファイルを設定"""
        self.current_stage_file = stage_file

        if self.astar_engine:
            self.astar_engine.reset_stage(stage_file)
        if self.game_engine:
            self.game_engine.reset_stage(stage_file)

    def get_last_comparison_report(self) -> Optional[DifferenceReport]:
        """最新の比較レポートを取得"""
        if not self.comparison_sessions:
            return None

        latest_id = max(self.comparison_sessions.keys())
        differences = self.comparison_sessions[latest_id]
        return DifferenceReport.from_differences(differences, latest_id)