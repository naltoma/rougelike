#!/usr/bin/env python3
"""
メインゲームループ統合システム
全機能を統合した包括的なゲーム実行環境
"""

import time
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

from . import Position, Direction, GameStatus
from .advanced_game_state import AdvancedGameStateManager, AdvancedGameState
from .stage_loader import StageLoader
from .renderer import RendererFactory
from .progression import ProgressionManager
from .session_logging import SessionLogger
from .educational_errors import ErrorHandler
from .quality_assurance import QualityAssuranceManager
from .progress_analytics import ProgressAnalyzer
from .educational_feedback import EducationalFeedbackGenerator, AdaptiveHintSystem
from .data_uploader import get_data_uploader
from .enemy_system import EnemyFactory
from .item_system import ItemManager
from .commands import MoveCommand, TurnLeftCommand, TurnRightCommand, AttackCommand, PickupCommand


class GameMode(Enum):
    """ゲームモード"""
    TUTORIAL = "tutorial"           # チュートリアル
    PRACTICE = "practice"           # 練習モード
    CHALLENGE = "challenge"         # 挑戦モード
    FREE_PLAY = "free_play"        # 自由プレイ
    ASSESSMENT = "assessment"       # 評価モード


class GamePhase(Enum):
    """ゲーム段階"""
    INITIALIZATION = "initialization"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    RESULTS = "results"


@dataclass
class GameConfiguration:
    """ゲーム設定"""
    mode: GameMode = GameMode.PRACTICE
    renderer_type: str = "cui"
    enable_hints: bool = True
    enable_progression_tracking: bool = True
    enable_session_logging: bool = True
    enable_educational_errors: bool = True
    enable_quality_assurance: bool = True
    enable_analytics: bool = True
    enable_feedback: bool = True
    enable_data_upload: bool = False
    auto_save_interval: int = 300  # 5分
    max_session_time: int = 3600   # 1時間


class GameLoop:
    """統合ゲームループシステム"""
    
    def __init__(self, config: GameConfiguration = None):
        self.config = config or GameConfiguration()
        self.current_phase = GamePhase.INITIALIZATION
        
        # コアシステム
        self.game_manager = AdvancedGameStateManager()
        self.stage_loader = StageLoader()
        self.renderer = None
        
        # 進捗・学習システム
        self.progression_manager: Optional[ProgressionManager] = None
        self.session_logger: Optional[SessionLogger] = None
        self.error_handler: Optional[ErrorHandler] = None
        self.quality_manager: Optional[QualityAssuranceManager] = None
        self.progress_analyzer: Optional[ProgressAnalyzer] = None
        self.feedback_generator: Optional[EducationalFeedbackGenerator] = None
        self.hint_system: Optional[AdaptiveHintSystem] = None
        
        # ゲーム状態
        self.current_stage_id: Optional[str] = None
        self.student_id: Optional[str] = None
        self.session_start_time: Optional[float] = None
        self.last_auto_save: float = 0
        self.turn_start_time: Optional[float] = None
        
        # 統計・メトリクス
        self.session_metrics: Dict[str, Any] = {}
        self.performance_data: List[Dict[str, Any]] = []
        self.user_interactions: List[Dict[str, Any]] = []
        
        # イベントハンドラー
        self.event_handlers: Dict[str, List[Callable]] = {
            "game_start": [],
            "turn_start": [],
            "turn_end": [],
            "stage_complete": [],
            "game_over": [],
            "session_end": []
        }
        
        self._initialize_systems()
    
    def _initialize_systems(self) -> None:
        """システム初期化"""
        # 進捗管理システム
        if self.config.enable_progression_tracking:
            self.progression_manager = ProgressionManager()
        
        # セッションログ
        if self.config.enable_session_logging:
            self.session_logger = SessionLogger()
        
        # 教育的エラーハンドリング
        if self.config.enable_educational_errors:
            self.error_handler = ErrorHandler()
        
        # 品質保証
        if self.config.enable_quality_assurance:
            self.quality_manager = QualityAssuranceManager()
        
        # 進歩分析
        if self.config.enable_analytics:
            self.progress_analyzer = ProgressAnalyzer()
        
        # 教育フィードバック
        if self.config.enable_feedback:
            self.feedback_generator = EducationalFeedbackGenerator()
            self.hint_system = AdaptiveHintSystem()
        
        # レンダラー
        self.renderer = RendererFactory.create_renderer(self.config.renderer_type)
    
    def start_session(self, student_id: str, stage_id: str) -> bool:
        """セッション開始"""
        try:
            self.student_id = student_id
            self.current_stage_id = stage_id
            self.session_start_time = time.time()
            
            # ステージ読み込み
            stage = self.stage_loader.load_stage(stage_id)
            if not stage:
                print(f"❌ ステージ '{stage_id}' の読み込みに失敗しました")
                return False
            
            # ゲーム初期化
            self._initialize_game_state(stage)
            
            # セッション開始イベント
            self._trigger_event("game_start", {
                "student_id": student_id,
                "stage_id": stage_id,
                "mode": self.config.mode.value
            })
            
            # セッション記録開始
            if self.session_logger:
                self.session_logger.start_session(student_id, stage_id)
            
            # 進捗追跡開始
            if self.progression_manager:
                self.progression_manager.start_tracking(stage_id)
            
            self.current_phase = GamePhase.PLAYING
            print(f"🎮 セッション開始: 学生ID={student_id}, ステージ={stage_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ セッション開始エラー: {e}")
            return False
    
    def _initialize_game_state(self, stage) -> None:
        """ゲーム状態初期化"""
        # 基本ボード作成
        from . import Board
        board = Board(
            width=stage.board_size[0],
            height=stage.board_size[1],
            walls=stage.walls,
            forbidden_cells=stage.forbidden_cells
        )
        
        # 敵作成
        enemies = []
        for enemy_data in stage.enemies:
            enemy = EnemyFactory.create_basic_enemy(
                Position(*enemy_data["position"])
            )
            # AI設定をカスタマイズ
            if enemy_data.get("behavior"):
                from .enemy_system import BehaviorPattern
                if hasattr(BehaviorPattern, enemy_data["behavior"].upper()):
                    enemy.ai_config.behavior_pattern = getattr(BehaviorPattern, enemy_data["behavior"].upper())
            
            enemies.append(enemy)
        
        # アイテム作成
        items = []
        for item_data in stage.items:
            from . import Item
            item = Item(
                position=Position(*item_data["position"]),
                item_type=getattr(__import__('engine', fromlist=['ItemType']).ItemType, item_data["type"].upper()),
                name=item_data["name"],
                effect=item_data.get("effect", {})
            )
            items.append(item)
        
        # ゲーム状態初期化
        game_state = self.game_manager.initialize_game(
            player_start=stage.player_start,
            player_direction=stage.player_direction,
            board=board,
            enemies=enemies,
            items=items,
            goal_position=stage.goal_position,
            max_turns=stage.constraints.get("max_turns", 100)
        )
        
        # レンダラー初期化
        if self.renderer:
            self.renderer.initialize(board.width, board.height)
    
    def execute_turn(self, command_name: str, **kwargs) -> Dict[str, Any]:
        """ターン実行"""
        if self.current_phase != GamePhase.PLAYING:
            return {"success": False, "message": "ゲームが実行中ではありません"}
        
        self.turn_start_time = time.time()
        
        # ターン開始イベント
        self._trigger_event("turn_start", {"command": command_name})
        
        try:
            # コマンド作成と実行
            result = self._execute_command(command_name, **kwargs)
            
            # ゲーム状態の更新
            if result["success"]:
                self._update_game_metrics()
                self._check_game_conditions()
            
            # ターン終了処理
            self._process_turn_end(result)
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "message": f"ターン実行エラー: {str(e)}",
                "error_type": type(e).__name__
            }
            
            # 教育的エラー処理
            if self.error_handler:
                error_feedback = self.error_handler.handle_error(e, {"command": command_name})
                error_result["educational_feedback"] = error_feedback
            
            return error_result
    
    def _execute_command(self, command_name: str, **kwargs) -> Dict[str, Any]:
        """コマンド実行"""
        game_state = self.game_manager.get_advanced_state()
        if not game_state:
            return {"success": False, "message": "ゲーム状態が無効です"}
        
        # コマンド作成
        command = None
        if command_name == "move":
            command = MoveCommand()
        elif command_name == "turn_left":
            command = TurnLeftCommand()
        elif command_name == "turn_right":
            command = TurnRightCommand()
        elif command_name == "attack":
            command = AttackCommand()
        elif command_name == "pickup":
            command = PickupCommand()
        else:
            return {"success": False, "message": f"未知のコマンド: {command_name}"}
        
        # コマンド実行
        execution_result = self.game_manager.execute_command(command)
        
        # 結果構築
        result = {
            "success": execution_result.is_success,
            "message": execution_result.message,
            "game_state": game_state.get_game_info(),
            "turn": game_state.turn_count
        }
        
        # 追加情報
        if not execution_result.is_success:
            result["error_type"] = "command_failure"
            
            # 教育的エラーフィードバック
            if self.error_handler:
                feedback = self.error_handler.provide_feedback(command_name, execution_result.message)
                result["educational_feedback"] = feedback
        
        return result
    
    def _update_game_metrics(self) -> None:
        """ゲームメトリクス更新"""
        if not self.turn_start_time:
            return
        
        turn_time = time.time() - self.turn_start_time
        
        # パフォーマンスデータ記録
        performance_entry = {
            "turn": self.game_manager.current_state.turn_count,
            "turn_time": turn_time,
            "timestamp": time.time(),
            "player_hp": self.game_manager.current_state.player.hp
        }
        
        self.performance_data.append(performance_entry)
        
        # メトリクス更新
        self.session_metrics.update({
            "total_turns": self.game_manager.current_state.turn_count,
            "average_turn_time": sum(p["turn_time"] for p in self.performance_data) / len(self.performance_data),
            "session_duration": time.time() - (self.session_start_time or time.time())
        })
    
    def _check_game_conditions(self) -> None:
        """ゲーム終了条件チェック"""
        game_state = self.game_manager.get_advanced_state()
        if not game_state:
            return
        
        if game_state.status != GameStatus.PLAYING:
            self.current_phase = GamePhase.GAME_OVER
            
            # ゲーム終了イベント
            self._trigger_event("game_over", {
                "status": game_state.status.value,
                "turns": game_state.turn_count,
                "duration": time.time() - (self.session_start_time or time.time())
            })
    
    def _process_turn_end(self, result: Dict[str, Any]) -> None:
        """ターン終了処理"""
        # 進捗記録
        if self.progression_manager:
            action_desc = f"Command executed: {result.get('success', False)}"
            self.progression_manager.record_action(action_desc)
        
        # セッションログ
        if self.session_logger:
            self.session_logger.log_action(
                action=result.get("command", "unknown"),
                success=result.get("success", False),
                message=result.get("message", ""),
                turn_number=result.get("turn", 0)
            )
        
        # 自動ヒントチェック
        if self.hint_system and self.config.enable_hints:
            self._check_auto_hints()
        
        # データアップロード
        if self.config.enable_data_upload:
            self._upload_turn_data(result)
        
        # 自動保存
        self._check_auto_save()
        
        # ターン終了イベント
        self._trigger_event("turn_end", result)
    
    def _check_auto_hints(self) -> None:
        """自動ヒントチェック"""
        if not self.hint_system or not self.student_id:
            return
        
        # 条件チェック（連続失敗、時間経過など）
        session_duration = time.time() - (self.session_start_time or time.time())
        
        should_hint = self.hint_system.should_provide_hint(
            self.student_id,
            session_duration,
            0,  # 連続失敗回数（実装に応じて調整）
            []  # API履歴（実装に応じて調整）
        )
        
        if should_hint:
            hint = self.hint_system.provide_contextual_hint(
                self.student_id,
                self.current_stage_id or "",
                {"situation": "auto_hint"},
                []
            )
            
            if hint:
                print(f"💡 ヒント: {hint.title}")
                print(f"   {hint.message}")
    
    def _upload_turn_data(self, result: Dict[str, Any]) -> None:
        """ターンデータアップロード"""
        uploader = get_data_uploader()
        if uploader and self.student_id:
            turn_data = {
                "student_id": self.student_id,
                "turn": result.get("turn", 0),
                "success": result.get("success", False),
                "command": result.get("command", "unknown"),
                "message": result.get("message", ""),
                "timestamp": time.time()
            }
            
            uploader.queue_session_log(f"session_{self.student_id}", turn_data)
    
    def _check_auto_save(self) -> None:
        """自動保存チェック"""
        current_time = time.time()
        if current_time - self.last_auto_save >= self.config.auto_save_interval:
            self.save_session()
            self.last_auto_save = current_time
    
    def save_session(self) -> bool:
        """セッション保存"""
        try:
            if self.progression_manager:
                self.progression_manager.save_progress()
            
            if self.session_logger:
                self.session_logger.end_session()
            
            # 品質レポート生成
            if self.quality_manager:
                report = self.quality_manager.generate_comprehensive_report(
                    self.student_id or "unknown",
                    self.current_stage_id or "unknown"
                )
                print(f"📊 品質レポート生成: スコア {report.get('overall_score', 0):.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ セッション保存エラー: {e}")
            return False
    
    def end_session(self) -> Dict[str, Any]:
        """セッション終了"""
        try:
            # セッション保存
            self.save_session()
            
            # 最終メトリクス計算
            session_duration = time.time() - (self.session_start_time or time.time())
            final_metrics = self._calculate_final_metrics(session_duration)
            
            # セッション終了イベント
            self._trigger_event("session_end", final_metrics)
            
            # データアップロード
            if self.config.enable_data_upload:
                self._upload_final_data(final_metrics)
            
            self.current_phase = GamePhase.RESULTS
            
            return {
                "success": True,
                "metrics": final_metrics,
                "message": "セッションが正常に終了しました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"セッション終了エラー: {str(e)}"
            }
    
    def _calculate_final_metrics(self, session_duration: float) -> Dict[str, Any]:
        """最終メトリクス計算"""
        game_state = self.game_manager.get_advanced_state()
        
        metrics = {
            "session_duration": session_duration,
            "total_turns": game_state.turn_count if game_state else 0,
            "game_status": game_state.status.value if game_state else "unknown",
            "student_id": self.student_id,
            "stage_id": self.current_stage_id,
            "mode": self.config.mode.value
        }
        
        # パフォーマンス統計
        if self.performance_data:
            metrics.update({
                "average_turn_time": sum(p["turn_time"] for p in self.performance_data) / len(self.performance_data),
                "total_interactions": len(self.user_interactions),
                "completion_rate": 1.0 if game_state and game_state.status == GameStatus.WON else 0.0
            })
        
        # 品質メトリクス
        if self.quality_manager:
            quality_data = self.quality_manager.get_current_metrics()
            metrics["quality_score"] = quality_data.get("overall_score", 0.0)
        
        # 学習分析
        if self.progress_analyzer:
            learning_data = self.progress_analyzer.analyze_session_progress(
                self.student_id or "unknown"
            )
            metrics["learning_progress"] = learning_data
        
        return metrics
    
    def _upload_final_data(self, metrics: Dict[str, Any]) -> None:
        """最終データアップロード"""
        uploader = get_data_uploader()
        if uploader and self.student_id:
            uploader.queue_student_progress(self.student_id, metrics)
            uploader.force_upload()
    
    def add_event_handler(self, event: str, handler: Callable) -> None:
        """イベントハンドラー追加"""
        if event in self.event_handlers:
            self.event_handlers[event].append(handler)
    
    def _trigger_event(self, event: str, data: Dict[str, Any]) -> None:
        """イベント発火"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"⚠️ イベントハンドラーエラー ({event}): {e}")
    
    def get_current_state_info(self) -> Dict[str, Any]:
        """現在の状態情報取得"""
        game_state = self.game_manager.get_advanced_state()
        
        info = {
            "phase": self.current_phase.value,
            "student_id": self.student_id,
            "stage_id": self.current_stage_id,
            "session_duration": time.time() - (self.session_start_time or time.time()) if self.session_start_time else 0,
            "metrics": self.session_metrics.copy()
        }
        
        if game_state:
            info.update(game_state.get_game_info())
        
        return info
    
    def pause_game(self) -> bool:
        """ゲーム一時停止"""
        if self.current_phase == GamePhase.PLAYING:
            self.current_phase = GamePhase.PAUSED
            return True
        return False
    
    def resume_game(self) -> bool:
        """ゲーム再開"""
        if self.current_phase == GamePhase.PAUSED:
            self.current_phase = GamePhase.PLAYING
            return True
        return False
    
    def reset_game(self) -> bool:
        """ゲームリセット"""
        try:
            # ゲーム状態リセット
            if hasattr(self.game_manager, 'reset_to_initial_state'):
                self.game_manager.reset_to_initial_state()
            
            # メトリクスリセット
            self.performance_data.clear()
            self.user_interactions.clear()
            self.session_metrics.clear()
            
            self.current_phase = GamePhase.PLAYING
            return True
            
        except Exception as e:
            print(f"❌ ゲームリセットエラー: {e}")
            return False


# ゲームループファクトリー
class GameLoopFactory:
    """ゲームループファクトリー"""
    
    @staticmethod
    def create_tutorial_loop() -> GameLoop:
        """チュートリアル用ゲームループ"""
        config = GameConfiguration(
            mode=GameMode.TUTORIAL,
            enable_hints=True,
            enable_educational_errors=True,
            enable_progression_tracking=True
        )
        return GameLoop(config)
    
    @staticmethod
    def create_practice_loop() -> GameLoop:
        """練習用ゲームループ"""
        config = GameConfiguration(
            mode=GameMode.PRACTICE,
            enable_hints=True,
            enable_quality_assurance=True,
            enable_analytics=True
        )
        return GameLoop(config)
    
    @staticmethod
    def create_assessment_loop() -> GameLoop:
        """評価用ゲームループ"""
        config = GameConfiguration(
            mode=GameMode.ASSESSMENT,
            enable_hints=False,
            enable_progression_tracking=True,
            enable_session_logging=True,
            enable_quality_assurance=True,
            enable_data_upload=True
        )
        return GameLoop(config)
    
    @staticmethod
    def create_custom_loop(config: GameConfiguration) -> GameLoop:
        """カスタムゲームループ"""
        return GameLoop(config)