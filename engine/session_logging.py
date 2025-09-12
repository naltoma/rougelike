"""
セッション詳細ログシステム
Session Logging System for Educational Framework
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import threading
from pathlib import Path
import uuid
import sys
import traceback

from . import GameState, Position, Direction, GameStatus


class LogLevel(Enum):
    """ログレベル"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(Enum):
    """イベントタイプ"""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    STAGE_START = "stage_start"
    STAGE_END = "stage_end"
    ACTION_EXECUTED = "action_executed"
    ERROR_OCCURRED = "error_occurred"
    HINT_USED = "hint_used"
    STATE_CHANGED = "state_changed"
    USER_INPUT = "user_input"
    SYSTEM_MESSAGE = "system_message"
    PERFORMANCE_METRIC = "performance_metric"
    DEBUG_INFO = "debug_info"
    # 🚀 v1.2.5: 7段階速度制御イベント
    SPEED_CONTROL_CHANGED = "speed_control_changed"
    ULTRA_HIGH_SPEED_ENABLED = "ultra_high_speed_enabled"
    SPEED_PRECISION_MEASURED = "speed_precision_measured"
    SPEED_DEGRADATION_OCCURRED = "speed_degradation_occurred"


@dataclass
class LogEntry:
    """ログエントリー"""
    timestamp: datetime
    session_id: str
    student_id: str
    event_type: EventType
    level: LogLevel
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    stage_id: Optional[str] = None
    turn_number: Optional[int] = None
    game_state: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "student_id": self.student_id,
            "event_type": self.event_type.value,
            "level": self.level.value,
            "message": self.message,
            "data": self.data,
            "stage_id": self.stage_id,
            "turn_number": self.turn_number,
            "game_state": self.game_state,
            "stack_trace": self.stack_trace
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """辞書から復元"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"],
            student_id=data["student_id"],
            event_type=EventType(data["event_type"]),
            level=LogLevel(data["level"]),
            message=data["message"],
            data=data.get("data", {}),
            stage_id=data.get("stage_id"),
            turn_number=data.get("turn_number"),
            game_state=data.get("game_state"),
            stack_trace=data.get("stack_trace")
        )


@dataclass
class SessionSummary:
    """セッションサマリー"""
    session_id: str
    student_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    stages_attempted: List[str] = field(default_factory=list)
    total_actions: int = 0
    total_errors: int = 0
    # v1.2.7 pickup初回使用記録拡張
    first_pickup_timestamp: Optional[datetime] = None
    hints_used: int = 0
    successful_stages: int = 0
    total_play_time: timedelta = field(default_factory=lambda: timedelta())
    
    # 🚀 v1.2.5: 7段階速度制御メトリクス
    speed_changes: int = 0
    speed_usage_time: Dict[int, float] = field(default_factory=dict)  # {multiplier: seconds}
    max_speed_used: int = 1
    ultra_high_speed_usage: float = 0.0  # seconds
    precision_measurements: int = 0
    precision_failures: int = 0
    speed_degradations: int = 0
    
    @property
    def duration(self) -> Optional[timedelta]:
        """セッション時間"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if len(self.stages_attempted) == 0:
            return 0.0
        return self.successful_stages / len(self.stages_attempted)
    
    @property
    def error_rate(self) -> float:
        """エラー率"""
        if self.total_actions == 0:
            return 0.0
        return self.total_errors / self.total_actions
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "stages_attempted": self.stages_attempted,
            "total_actions": self.total_actions,
            "total_errors": self.total_errors,
            "first_pickup_timestamp": self.first_pickup_timestamp.isoformat() if self.first_pickup_timestamp else None,
            "hints_used": self.hints_used,
            "successful_stages": self.successful_stages,
            "total_play_time": str(self.total_play_time),
            # 🚀 v1.2.5: 7段階速度制御メトリクス
            "speed_changes": self.speed_changes,
            "speed_usage_time": self.speed_usage_time,
            "max_speed_used": self.max_speed_used,
            "ultra_high_speed_usage": self.ultra_high_speed_usage,
            "precision_measurements": self.precision_measurements,
            "precision_failures": self.precision_failures,
            "speed_degradations": self.speed_degradations
        }


class SessionLogger:
    """セッションロガー"""
    
    def __init__(self, log_dir: str = "data/sessions", max_log_files: int = 100):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_log_files = max_log_files
        self.current_session: Optional[SessionSummary] = None
        self.current_session_id: Optional[str] = None
        self.current_student_id: Optional[str] = None
        
        # ログエントリーのバッファ
        self.log_buffer: List[LogEntry] = []
        self.buffer_size = 1000
        self.auto_flush_interval = 30  # 秒
        
        # スレッド安全性
        self._lock = threading.Lock()
        self._flush_timer: Optional[threading.Timer] = None
        
        # システムロガーセットアップ（簡易版）
        self.system_logger = logging.getLogger("rougelike_framework")
        self.system_logger.setLevel(logging.INFO)
        
        print(f"📝 セッションロガー初期化: {self.log_dir}")
    
    def _setup_system_logger(self) -> None:
        """システムロガーをセットアップ"""
        log_file = self.log_dir / "system.log"
        
        # ログフォーマット
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # ロガー設定
        self.system_logger = logging.getLogger("rougelike_framework")
        self.system_logger.setLevel(logging.DEBUG)
        self.system_logger.addHandler(file_handler)
        
        # 既存ハンドラーをクリア（重複防止）
        if self.system_logger.handlers:
            self.system_logger.handlers = [file_handler]
    
    def start_session(self, student_id: str) -> str:
        """セッションを開始"""
        with self._lock:
            # 現在のセッションが存在する場合は終了
            if self.current_session:
                self.end_session()
            
            # 新しいセッション作成
            session_id = str(uuid.uuid4())[:8]  # 短縮UUID
            self.current_session_id = session_id
            self.current_student_id = student_id
            
            self.current_session = SessionSummary(
                session_id=session_id,
                student_id=student_id,
                start_time=datetime.now()
            )
            
            # セッション開始ログ
            self.log(
                event_type=EventType.SESSION_START,
                level=LogLevel.INFO,
                message=f"学習セッション開始: {student_id}",
                data={
                    "student_id": student_id,
                    "python_version": sys.version,
                    "framework_version": "1.0.0"
                }
            )
            
            # 自動フラッシュタイマー開始
            self._start_auto_flush()
            
            print(f"📝 セッション開始: {session_id} (学生: {student_id})")
            return session_id
    
    def end_session(self) -> Optional[SessionSummary]:
        """セッションを終了"""
        if not self.current_session:
            return None
        
        with self._lock:
            # セッション終了時刻を記録
            self.current_session.end_time = datetime.now()
            
            # セッション終了ログ
            self.log(
                event_type=EventType.SESSION_END,
                level=LogLevel.INFO,
                message=f"学習セッション終了",
                data={
                    "duration_seconds": self.current_session.duration.total_seconds() if self.current_session.duration else 0,
                    "stages_attempted": len(self.current_session.stages_attempted),
                    "success_rate": self.current_session.success_rate,
                    "error_rate": self.current_session.error_rate
                }
            )
            
            # ログをフラッシュ
            self._flush_logs()
            
            # 自動フラッシュタイマー停止
            self._stop_auto_flush()
            
            # セッションサマリーを保存
            self._save_session_summary()
            
            summary = self.current_session
            
            print(f"📝 セッション終了: {summary.session_id}")
            print(f"   時間: {summary.duration}")
            print(f"   ステージ: {len(summary.stages_attempted)}")
            print(f"   成功率: {summary.success_rate:.1%}")
            
            # クリーンアップ
            self.current_session = None
            self.current_session_id = None
            self.current_student_id = None
            
            return summary
    
    def log_stage_start(self, stage_id: str) -> None:
        """ステージ開始をログ"""
        if self.current_session and stage_id not in self.current_session.stages_attempted:
            self.current_session.stages_attempted.append(stage_id)
        
        self.log(
            event_type=EventType.STAGE_START,
            level=LogLevel.INFO,
            message=f"ステージ開始: {stage_id}",
            stage_id=stage_id,
            data={"stage_id": stage_id}
        )
    
    def log_stage_end(self, stage_id: str, success: bool, game_state: Optional[GameState] = None) -> None:
        """ステージ終了をログ"""
        if self.current_session and success:
            self.current_session.successful_stages += 1
        
        self.log(
            event_type=EventType.STAGE_END,
            level=LogLevel.INFO,
            message=f"ステージ終了: {stage_id} ({'成功' if success else '失敗'})",
            stage_id=stage_id,
            game_state=self._serialize_game_state(game_state) if game_state else None,
            data={
                "stage_id": stage_id,
                "success": success,
                "turns_used": game_state.turn_count if game_state else None,
                "max_turns": game_state.max_turns if game_state else None
            }
        )
    
    def log_action(self, action: str, success: bool, message: str, 
                   turn_number: Optional[int] = None, game_state: Optional[GameState] = None) -> None:
        """アクション実行をログ - v1.2.7 pickup初回使用記録拡張"""
        if self.current_session:
            self.current_session.total_actions += 1
            if not success:
                self.current_session.total_errors += 1
            
            # pickup初回使用記録
            if action == "pickup" and success and self.current_session.first_pickup_timestamp is None:
                self.current_session.first_pickup_timestamp = datetime.now()
                # pickup初回使用の特別なログエントリ
                self.log(
                    event_type=EventType.USER_INPUT,
                    level=LogLevel.INFO,
                    message="pickup()機能を初めて使用しました",
                    data={"first_usage": True, "learning_milestone": "pickup_introduction"}
                )
        
        self.log(
            event_type=EventType.ACTION_EXECUTED,
            level=LogLevel.INFO if success else LogLevel.WARNING,
            message=f"アクション: {action} - {message}",
            turn_number=turn_number,
            game_state=self._serialize_game_state(game_state) if game_state else None,
            data={
                "action": action,
                "success": success,
                "result_message": message
            }
        )
    
    def log_error(self, error: Exception, context: str = "", 
                  game_state: Optional[GameState] = None) -> None:
        """エラーをログ"""
        if self.current_session:
            self.current_session.total_errors += 1
        
        # スタックトレース取得
        stack_trace = ''.join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))
        
        self.log(
            event_type=EventType.ERROR_OCCURRED,
            level=LogLevel.ERROR,
            message=f"エラー発生: {str(error)}",
            game_state=self._serialize_game_state(game_state) if game_state else None,
            stack_trace=stack_trace,
            data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context
            }
        )
    
    def log_hint_used(self, hint_message: str) -> None:
        """ヒント使用をログ"""
        if self.current_session:
            self.current_session.hints_used += 1
        
        self.log(
            event_type=EventType.HINT_USED,
            level=LogLevel.INFO,
            message=f"ヒント使用: {hint_message}",
            data={"hint_message": hint_message}
        )
    
    def log_user_input(self, input_data: str, context: str = "") -> None:
        """ユーザー入力をログ"""
        self.log(
            event_type=EventType.USER_INPUT,
            level=LogLevel.DEBUG,
            message=f"ユーザー入力: {input_data}",
            data={
                "input": input_data,
                "context": context
            }
        )
    
    def log_system_message(self, message: str, data: Dict[str, Any] = None) -> None:
        """システムメッセージをログ"""
        self.log(
            event_type=EventType.SYSTEM_MESSAGE,
            level=LogLevel.INFO,
            message=message,
            data=data or {}
        )
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              unit: str = "", context: str = "") -> None:
        """パフォーマンスメトリックをログ"""
        self.log(
            event_type=EventType.PERFORMANCE_METRIC,
            level=LogLevel.INFO,
            message=f"パフォーマンス: {metric_name} = {value}{unit}",
            data={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "context": context
            }
        )
    
    def log_debug(self, message: str, data: Dict[str, Any] = None) -> None:
        """デバッグ情報をログ"""
        self.log(
            event_type=EventType.DEBUG_INFO,
            level=LogLevel.DEBUG,
            message=message,
            data=data or {}
        )
    
    def log(self, event_type: EventType, level: LogLevel, message: str,
            stage_id: Optional[str] = None, turn_number: Optional[int] = None,
            game_state: Optional[Dict[str, Any]] = None, 
            stack_trace: Optional[str] = None,
            data: Dict[str, Any] = None) -> None:
        """汎用ログメソッド"""
        if not self.current_session_id or not self.current_student_id:
            return
        
        entry = LogEntry(
            timestamp=datetime.now(),
            session_id=self.current_session_id,
            student_id=self.current_student_id,
            event_type=event_type,
            level=level,
            message=message,
            stage_id=stage_id,
            turn_number=turn_number,
            game_state=game_state,
            stack_trace=stack_trace,
            data=data or {}
        )
        
        with self._lock:
            self.log_buffer.append(entry)
            
            # バッファが満杯になったら自動フラッシュ
            if len(self.log_buffer) >= self.buffer_size:
                self._flush_logs()
        
        # システムロガーにも記録
        log_level = getattr(logging, level.value.upper())
        self.system_logger.log(log_level, f"[{event_type.value}] {message}")
    
    def _serialize_game_state(self, game_state: GameState) -> Dict[str, Any]:
        """GameStateを辞書形式にシリアライズ"""
        return {
            "player_position": {
                "x": game_state.player.position.x,
                "y": game_state.player.position.y
            },
            "player_direction": game_state.player.direction.value,
            "player_hp": game_state.player.hp,
            "turn_count": game_state.turn_count,
            "max_turns": game_state.max_turns,
            "status": game_state.status.value,
            "goal_position": {
                "x": game_state.goal_position.x,
                "y": game_state.goal_position.y
            } if game_state.goal_position else None,
            "enemies_count": len(game_state.enemies),
            "items_count": len(game_state.items)
        }
    
    def _flush_logs(self) -> None:
        """ログバッファをファイルに書き出し"""
        if not self.log_buffer:
            return
        
        # セッション別ログファイル
        if self.current_session_id:
            log_file = self.log_dir / f"session_{self.current_session_id}.jsonl"
            
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    for entry in self.log_buffer:
                        json.dump(entry.to_dict(), f, ensure_ascii=False)
                        f.write("\n")
                
                self.log_buffer.clear()
                
            except Exception as e:
                self.system_logger.error(f"ログフラッシュエラー: {e}")
    
    def _save_session_summary(self) -> None:
        """セッションサマリーを保存"""
        if not self.current_session:
            return
        
        summary_file = self.log_dir / f"summary_{self.current_session.session_id}.json"
        
        try:
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(self.current_session.to_dict(), f, 
                         ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.system_logger.error(f"セッションサマリー保存エラー: {e}")
    
    def _start_auto_flush(self) -> None:
        """自動フラッシュタイマーを開始"""
        self._stop_auto_flush()  # 既存のタイマーをクリア
        
        def auto_flush():
            try:
                with self._lock:
                    if self.log_buffer:
                        self._flush_logs()
                
                # 現在のセッションが有効な場合のみ再スケジュール（適切な間隔で）
                if self.current_session:
                    self._flush_timer = threading.Timer(self.auto_flush_interval, auto_flush)
                    self._flush_timer.daemon = True
                    self._flush_timer.start()
            except Exception as e:
                self.system_logger.error(f"自動フラッシュエラー: {e}")
                # エラー時はタイマーをクリア
                self._flush_timer = None
        
        self._flush_timer = threading.Timer(self.auto_flush_interval, auto_flush)
        self._flush_timer.daemon = True
        self._flush_timer.start()
    
    def _stop_auto_flush(self) -> None:
        """自動フラッシュタイマーを停止"""
        if self._flush_timer:
            self._flush_timer.cancel()
            self._flush_timer = None
    
    def get_session_logs(self, session_id: str) -> List[LogEntry]:
        """指定セッションのログを取得"""
        log_file = self.log_dir / f"session_{session_id}.jsonl"
        
        if not log_file.exists():
            return []
        
        logs = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        logs.append(LogEntry.from_dict(data))
        
        except Exception as e:
            self.system_logger.error(f"ログ読み込みエラー: {e}")
        
        return logs
    
    def get_session_summary(self, session_id: str) -> Optional[SessionSummary]:
        """セッションサマリーを取得"""
        summary_file = self.log_dir / f"summary_{session_id}.json"
        
        if not summary_file.exists():
            return None
        
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                return SessionSummary(
                    session_id=data["session_id"],
                    student_id=data["student_id"],
                    start_time=datetime.fromisoformat(data["start_time"]),
                    end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
                    stages_attempted=data.get("stages_attempted", []),
                    total_actions=data.get("total_actions", 0),
                    total_errors=data.get("total_errors", 0),
                    first_pickup_timestamp=datetime.fromisoformat(data["first_pickup_timestamp"]) if data.get("first_pickup_timestamp") else None,
                    hints_used=data.get("hints_used", 0),
                    successful_stages=data.get("successful_stages", 0)
                )
        
        except Exception as e:
            self.system_logger.error(f"セッションサマリー読み込みエラー: {e}")
            return None
    
    def list_sessions(self, student_id: Optional[str] = None) -> List[str]:
        """セッションIDリストを取得"""
        sessions = []
        
        for summary_file in self.log_dir.glob("summary_*.json"):
            session_id = summary_file.stem.replace("summary_", "")
            
            # 学生IDでフィルター
            if student_id:
                summary = self.get_session_summary(session_id)
                if summary and summary.student_id == student_id:
                    sessions.append(session_id)
            else:
                sessions.append(session_id)
        
        return sorted(sessions)
    
    def cleanup_old_logs(self) -> None:
        """古いログファイルをクリーンアップ"""
        log_files = list(self.log_dir.glob("session_*.jsonl"))
        summary_files = list(self.log_dir.glob("summary_*.json"))
        
        all_files = log_files + summary_files
        
        if len(all_files) <= self.max_log_files:
            return
        
        # 作成時刻でソートして古いファイルを削除
        all_files.sort(key=lambda f: f.stat().st_ctime)
        files_to_delete = all_files[:-self.max_log_files]
        
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                self.system_logger.info(f"古いログファイルを削除: {file_path}")
            except Exception as e:
                self.system_logger.error(f"ログファイル削除エラー: {e}")
    
    def export_session_data(self, session_id: str, output_file: str) -> bool:
        """セッションデータをエクスポート"""
        logs = self.get_session_logs(session_id)
        summary = self.get_session_summary(session_id)
        
        if not logs or not summary:
            return False
        
        try:
            export_data = {
                "summary": summary.to_dict(),
                "logs": [log.to_dict() for log in logs]
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"📤 セッションデータをエクスポート: {output_file}")
            return True
        
        except Exception as e:
            self.system_logger.error(f"エクスポートエラー: {e}")
            return False
    
    # 🚀 v1.2.5: 7段階速度制御専用ログ機能
    
    def log_speed_control_change(self, from_multiplier: int, to_multiplier: int, 
                                success: bool, transition_time_ms: float = None):
        """速度制御変更ログ"""
        if not self.current_session:
            return
        
        data = {
            "from_multiplier": from_multiplier,
            "to_multiplier": to_multiplier,
            "success": success,
            "is_ultra_high_speed": to_multiplier in [10, 50],
            "transition_time_ms": transition_time_ms
        }
        
        message = f"速度変更: x{from_multiplier} → x{to_multiplier} ({'成功' if success else '失敗'})"
        if transition_time_ms:
            message += f" ({transition_time_ms:.1f}ms)"
        
        self.log_event(
            EventType.SPEED_CONTROL_CHANGED,
            LogLevel.INFO,
            message,
            data
        )
        
        # サマリー更新
        with self._lock:
            if success:
                self.current_session.speed_changes += 1
                self.current_session.max_speed_used = max(
                    self.current_session.max_speed_used, to_multiplier
                )
    
    def log_ultra_high_speed_enabled(self, multiplier: int, target_interval_ms: float):
        """超高速モード有効化ログ"""
        if not self.current_session:
            return
        
        data = {
            "multiplier": multiplier,
            "target_interval_ms": target_interval_ms,
            "precision_tolerance_ms": 5.0 if multiplier == 50 else 10.0
        }
        
        message = f"超高速モード有効化: x{multiplier} ({target_interval_ms}ms間隔)"
        
        self.log_event(
            EventType.ULTRA_HIGH_SPEED_ENABLED,
            LogLevel.INFO,
            message,
            data
        )
    
    def log_speed_precision_measurement(self, multiplier: int, target_interval_ms: float, 
                                      actual_interval_ms: float, deviation_ms: float, 
                                      within_tolerance: bool):
        """速度精度測定ログ"""
        if not self.current_session:
            return
        
        data = {
            "multiplier": multiplier,
            "target_interval_ms": target_interval_ms,
            "actual_interval_ms": actual_interval_ms,
            "deviation_ms": deviation_ms,
            "within_tolerance": within_tolerance,
            "precision_percentage": ((target_interval_ms - abs(deviation_ms)) / target_interval_ms) * 100
        }
        
        status = "精度OK" if within_tolerance else "精度NG"
        message = f"速度精度測定 x{multiplier}: {actual_interval_ms:.1f}ms (偏差{deviation_ms:+.1f}ms) - {status}"
        
        self.log_event(
            EventType.SPEED_PRECISION_MEASURED,
            LogLevel.DEBUG if within_tolerance else LogLevel.WARNING,
            message,
            data
        )
        
        # サマリー更新
        with self._lock:
            self.current_session.precision_measurements += 1
            if not within_tolerance:
                self.current_session.precision_failures += 1
    
    def log_speed_degradation(self, original_multiplier: int, degraded_multiplier: int, 
                            reason: str, failure_count: int):
        """速度性能低下ログ"""
        if not self.current_session:
            return
        
        data = {
            "original_multiplier": original_multiplier,
            "degraded_multiplier": degraded_multiplier,
            "reason": reason,
            "failure_count": failure_count,
            "speed_drop": original_multiplier - degraded_multiplier
        }
        
        message = f"速度性能低下: x{original_multiplier} → x{degraded_multiplier} (理由: {reason}, 失敗{failure_count}回)"
        
        self.log_event(
            EventType.SPEED_DEGRADATION_OCCURRED,
            LogLevel.WARNING,
            message,
            data
        )
        
        # サマリー更新
        with self._lock:
            self.current_session.speed_degradations += 1
    
    def update_speed_usage_time(self, multiplier: int, usage_seconds: float):
        """速度使用時間更新"""
        if not self.current_session:
            return
        
        with self._lock:
            current_time = self.current_session.speed_usage_time.get(multiplier, 0.0)
            self.current_session.speed_usage_time[multiplier] = current_time + usage_seconds
            
            # 超高速使用時間
            if multiplier in [10, 50]:
                self.current_session.ultra_high_speed_usage += usage_seconds
    
    def get_7stage_speed_metrics(self) -> Dict[str, Any]:
        """7段階速度制御メトリクス取得"""
        if not self.current_session:
            return {}
        
        with self._lock:
            session = self.current_session
            total_speed_time = sum(session.speed_usage_time.values())
            
            metrics = {
                "speed_changes": session.speed_changes,
                "max_speed_used": session.max_speed_used,
                "ultra_high_speed_usage_seconds": session.ultra_high_speed_usage,
                "precision_measurements": session.precision_measurements,
                "precision_failures": session.precision_failures,
                "precision_success_rate": (
                    (session.precision_measurements - session.precision_failures) / session.precision_measurements
                    if session.precision_measurements > 0 else 0.0
                ),
                "speed_degradations": session.speed_degradations,
                "speed_usage_distribution": session.speed_usage_time.copy(),
                "average_speed": (
                    sum(speed * time for speed, time in session.speed_usage_time.items()) / total_speed_time
                    if total_speed_time > 0 else 1.0
                ),
                "ultra_speed_usage_percentage": (
                    session.ultra_high_speed_usage / total_speed_time * 100
                    if total_speed_time > 0 else 0.0
                )
            }
            
            return metrics
    
    def __del__(self):
        """デストラクタ - リソースクリーンアップ"""
        if self.current_session:
            self.end_session()
        
        self._stop_auto_flush()
        
        # 残りのログをフラッシュ
        if self.log_buffer:
            self._flush_logs()


# エクスポート用
__all__ = [
    "LogLevel", "EventType", "LogEntry", "SessionSummary", "SessionLogger"
]