"""
Debug Logger Implementation for Stage Validator - v1.2.12

詳細なデバッグ情報とレポート生成機能を提供する。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .models import ExecutionLog, StateDifference, ValidationConfig, get_global_config


class DebugLogger:
    """デバッグ情報の詳細ログ出力とレポート生成"""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or get_global_config()
        self.logger = self._setup_logger()
        self.session_data: Dict[str, Any] = {}

    def _setup_logger(self) -> logging.Logger:
        """デバッグ専用ロガー設定"""
        logger = logging.getLogger(f"DebugLogger.{id(self)}")

        if not logger.handlers:
            # コンソール出力
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter(
                "🔍 %(asctime)s - DEBUG - %(message)s"
            )
            console_handler.setFormatter(console_format)
            logger.addHandler(console_handler)

            # ファイル出力（オプション）
            if self.config.enable_debug_file_logging:
                log_file = Path("stage_validator_debug.log")
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_format = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                file_handler.setFormatter(file_format)
                logger.addHandler(file_handler)

            logger.setLevel(logging.DEBUG)

        return logger

    def start_comparison_session(self, stage_file: str, solution_path: List[str]) -> str:
        """比較セッション開始"""
        session_id = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.session_data[session_id] = {
            "start_time": datetime.now().isoformat(),
            "stage_file": stage_file,
            "solution_path": solution_path,
            "solution_length": len(solution_path),
            "astar_logs": [],
            "game_logs": [],
            "differences": [],
            "metadata": {
                "engine_versions": {"astar": "v1.2.12", "game": "v1.2.12"},
                "config": asdict(self.config)
            }
        }

        self.logger.info(f"Started comparison session {session_id}")
        self.logger.info(f"  Stage: {stage_file}")
        self.logger.info(f"  Solution steps: {len(solution_path)}")
        self.logger.debug(f"  Solution path: {' → '.join(solution_path)}")

        return session_id

    def log_engine_execution(self, session_id: str, engine_type: str,
                           execution_logs: List[ExecutionLog]) -> None:
        """エンジン実行ログの記録"""
        if session_id not in self.session_data:
            self.logger.error(f"Unknown session: {session_id}")
            return

        log_key = f"{engine_type.lower()}_logs"
        self.session_data[session_id][log_key] = [
            self._serialize_execution_log(log) for log in execution_logs
        ]

        self.logger.info(f"{engine_type} execution completed: {len(execution_logs)} steps")

        # ステップ毎の詳細ログ
        for i, log in enumerate(execution_logs):
            self.logger.debug(f"  Step {i}: {log.action_taken} → "
                            f"Player@{log.player_position} facing {log.player_direction}")
            if log.enemy_states:
                enemy_summary = [f"{e.enemy_id}@{e.position}" for e in log.enemy_states]
                self.logger.debug(f"    Enemies: {', '.join(enemy_summary)}")

    def log_differences(self, session_id: str, differences: List[StateDifference]) -> None:
        """差異ログの記録"""
        if session_id not in self.session_data:
            self.logger.error(f"Unknown session: {session_id}")
            return

        self.session_data[session_id]["differences"] = [
            asdict(diff) for diff in differences
        ]
        self.session_data[session_id]["total_differences"] = len(differences)

        self.logger.info(f"Differences detected: {len(differences)}")

        # 差異の詳細表示
        for i, diff in enumerate(differences):
            self.logger.info(f"  Difference {i+1}: Step {diff.step_number}")
            self.logger.info(f"    Type: {diff.difference_type}")
            self.logger.info(f"    Description: {diff.description}")
            if diff.severity.value != "low":
                self.logger.warning(f"    ⚠️ Severity: {diff.severity.value}")

    def complete_session(self, session_id: str) -> Dict[str, Any]:
        """セッション完了とレポート生成"""
        if session_id not in self.session_data:
            self.logger.error(f"Unknown session: {session_id}")
            return {}

        session = self.session_data[session_id]
        session["end_time"] = datetime.now().isoformat()
        session["duration_seconds"] = (
            datetime.fromisoformat(session["end_time"]) -
            datetime.fromisoformat(session["start_time"])
        ).total_seconds()

        self.logger.info(f"Session {session_id} completed in {session['duration_seconds']:.2f}s")

        # サマリー表示
        total_diffs = session.get("total_differences", 0)
        if total_diffs == 0:
            self.logger.info("✅ No differences found - engines are perfectly synchronized!")
        else:
            self.logger.warning(f"⚠️ Found {total_diffs} differences between engines")

        return session

    def export_detailed_report(self, session_id: str, output_path: Optional[str] = None) -> str:
        """詳細レポートのエクスポート"""
        if session_id not in self.session_data:
            raise ValueError(f"Unknown session: {session_id}")

        session = self.session_data[session_id]

        if output_path is None:
            output_path = f"debug_report_{session_id}.json"

        report_path = Path(output_path)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Detailed report exported: {report_path}")
        return str(report_path)

    def generate_summary_report(self, session_id: str) -> str:
        """サマリーレポートの生成"""
        if session_id not in self.session_data:
            raise ValueError(f"Unknown session: {session_id}")

        session = self.session_data[session_id]
        differences = session.get("differences", [])

        report = []
        report.append("="*60)
        report.append("🔍 STAGE VALIDATOR DEBUG REPORT")
        report.append("="*60)
        report.append(f"Session: {session_id}")
        report.append(f"Stage: {session['stage_file']}")
        report.append(f"Duration: {session.get('duration_seconds', 0):.2f}s")
        report.append(f"Solution Steps: {session['solution_length']}")
        report.append(f"Total Differences: {len(differences)}")
        report.append("")

        if differences:
            report.append("📋 DIFFERENCES SUMMARY:")
            report.append("-" * 40)

            # 重要度別集計
            severity_counts = {}
            type_counts = {}

            for diff in differences:
                severity = diff.get("severity", "unknown")
                diff_type = diff.get("difference_type", "unknown")

                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                type_counts[diff_type] = type_counts.get(diff_type, 0) + 1

            report.append("By Severity:")
            for severity, count in severity_counts.items():
                report.append(f"  {severity}: {count}")

            report.append("\nBy Type:")
            for diff_type, count in type_counts.items():
                report.append(f"  {diff_type}: {count}")

            report.append("\n📝 DETAILED DIFFERENCES:")
            report.append("-" * 40)
            for i, diff in enumerate(differences[:10]):  # Show first 10
                report.append(f"{i+1}. Step {diff.get('step_number', '?')} - {diff.get('difference_type', 'Unknown')}")
                report.append(f"   {diff.get('description', 'No description')}")

            if len(differences) > 10:
                report.append(f"... and {len(differences) - 10} more differences")
        else:
            report.append("✅ No differences found - perfect synchronization!")

        report.append("")
        report.append("="*60)

        return "\n".join(report)

    def _serialize_execution_log(self, log: ExecutionLog) -> Dict[str, Any]:
        """ExecutionLogをシリアライズ"""
        return {
            "step_number": log.step_number,
            "engine_type": log.engine_type.value,
            "player_position": log.player_position,
            "player_direction": log.player_direction,
            "enemy_states": [asdict(enemy) for enemy in log.enemy_states],
            "action_taken": log.action_taken,
            "game_over": log.game_over,
            "victory": log.victory,
            "timestamp": log.timestamp.isoformat()
        }

    def cleanup_old_sessions(self, keep_last_n: int = 5) -> None:
        """古いセッションデータのクリーンアップ"""
        if len(self.session_data) <= keep_last_n:
            return

        # 時系列でソートして古いものを削除
        sessions_by_time = sorted(
            self.session_data.items(),
            key=lambda x: x[1].get("start_time", ""),
            reverse=True
        )

        sessions_to_keep = dict(sessions_by_time[:keep_last_n])
        removed_count = len(self.session_data) - len(sessions_to_keep)

        self.session_data = sessions_to_keep
        self.logger.info(f"Cleaned up {removed_count} old debug sessions")


# ファクトリー関数
def create_debug_logger(config: Optional[ValidationConfig] = None) -> DebugLogger:
    """デバッグロガー作成"""
    return DebugLogger(config)