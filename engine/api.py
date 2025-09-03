"""
学生向けAPIレイヤー
APILayerクラスとグローバル関数の実装
"""

import threading
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from . import GameState, Position, Direction
from .game_state import GameStateManager
from .stage_loader import StageLoader
from .renderer import CuiRenderer, RendererFactory
from .progression import ProgressionManager
from .session_logging import SessionLogger
from .educational_errors import handle_educational_error, ErrorHandler
from .quality_assurance import QualityAssuranceManager, generate_quality_report
from .progress_analytics import ProgressAnalyzer, analyze_student_progress
from .educational_feedback import (
    EducationalFeedbackGenerator, AdaptiveHintSystem, 
    generate_educational_feedback, detect_infinite_loop
)
from .data_uploader import initialize_data_uploader, get_data_uploader
from .commands import (
    TurnLeftCommand, TurnRightCommand, MoveCommand, 
    AttackCommand, PickupCommand, ExecutionResult
)
from .action_history_tracker import ActionHistoryTracker, ActionTrackingError
from .execution_controller import ExecutionController
from .session_log_manager import SessionLogManager


class APIUsageError(Exception):
    """API使用エラー"""
    pass


class APILayer:
    """学生向けAPI管理クラス"""
    
    def __init__(self, renderer_type: str = "cui", enable_progression: bool = True, 
                 enable_session_logging: bool = True, enable_educational_errors: bool = True,
                 enable_action_tracking: bool = True):
        self.game_manager: Optional[GameStateManager] = None
        self.stage_loader = StageLoader()
        self.renderer = None
        self.renderer_type = renderer_type
        self.current_stage_id: Optional[str] = None
        self.allowed_apis: List[str] = []
        self.call_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self.auto_render = True  # 自動レンダリングフラグ
        
        # GUI拡張機能v1.1 - アクション履歴追跡
        self.action_tracker: Optional[ActionHistoryTracker] = None
        self.action_tracking_enabled = enable_action_tracking
        if enable_action_tracking:
            self.action_tracker = ActionHistoryTracker()
        
        # GUI拡張機能v1.1 - 実行制御システム（外部から設定される）
        self.execution_controller: Optional[ExecutionController] = None
        
        # GUI拡張機能v1.1 - セッションログ管理
        self.session_log_manager: Optional[SessionLogManager] = None
        if enable_session_logging:
            self.session_log_manager = SessionLogManager()
        
        # 進捗管理システム
        self.progression_manager: Optional[ProgressionManager] = None
        if enable_progression:
            self.progression_manager = ProgressionManager()
        
        # セッションログシステム
        self.session_logger: Optional[SessionLogger] = None
        if enable_session_logging:
            self.session_logger = SessionLogger()
        
        # 教育的エラーハンドリング
        self.error_handler: Optional[ErrorHandler] = None
        if enable_educational_errors:
            self.error_handler = ErrorHandler()
        
        # 品質保証システム
        self.quality_manager: Optional[QualityAssuranceManager] = None
        if enable_progression:  # 進捗管理が有効な場合のみ品質保証も有効化
            self.quality_manager = QualityAssuranceManager()
        
        # 進歩分析システム
        self.progress_analyzer: Optional[ProgressAnalyzer] = None
        if enable_progression:
            self.progress_analyzer = ProgressAnalyzer()
        
        # 教育フィードバックシステム
        self.feedback_generator: Optional[EducationalFeedbackGenerator] = None
        self.adaptive_hint_system: Optional[AdaptiveHintSystem] = None
        if enable_educational_errors:
            self.feedback_generator = EducationalFeedbackGenerator()
            self.adaptive_hint_system = AdaptiveHintSystem()
        
        # フィードバック制御
        self.last_action_time: Optional[datetime] = None
        self.consecutive_failures: int = 0
        self.auto_hint_enabled: bool = True
        
        self.student_id: Optional[str] = None
        self.current_session_id: Optional[str] = None
        
        # データアップロードシステム
        self.data_uploader = None
        if enable_progression and self.progression_manager:
            self.data_uploader = initialize_data_uploader(self.progression_manager)
    
    def initialize_stage(self, stage_id: str) -> bool:
        """ステージを初期化"""
        try:
            # ステージ読み込み
            stage = self.stage_loader.load_stage(stage_id)
            
            # GameStateManager初期化
            self.game_manager = GameStateManager()
            
            # レンダラー初期化
            self.renderer = RendererFactory.create_renderer(self.renderer_type)
            board_width, board_height = stage.board_size
            self.renderer.initialize(board_width, board_height)
            
            # 敵とアイテムをオブジェクトに変換
            from . import Enemy, Item, EnemyType, ItemType
            
            enemies = []
            for enemy_data in stage.enemies:
                enemy_type = getattr(EnemyType, enemy_data["type"].upper())
                enemy = Enemy(
                    position=Position(*enemy_data["position"]),
                    direction=getattr(Direction, enemy_data.get("direction", "N")),
                    hp=enemy_data.get("hp", 30),
                    attack_power=enemy_data.get("attack_power", 5),
                    enemy_type=enemy_type
                )
                enemies.append(enemy)
            
            items = []
            for item_data in stage.items:
                item_type = getattr(ItemType, item_data["type"].upper())
                item = Item(
                    position=Position(*item_data["position"]),
                    item_type=item_type,
                    name=item_data["name"],
                    effect=item_data.get("effect", {}),
                    auto_equip=item_data.get("auto_equip", True)
                )
                items.append(item)
            
            # ボード作成
            from . import Board
            board = Board(
                width=stage.board_size[0],
                height=stage.board_size[1],
                walls=stage.walls,
                forbidden_cells=stage.forbidden_cells
            )
            
            # ゲーム初期化
            self.game_manager.initialize_game(
                player_start=stage.player_start,
                player_direction=stage.player_direction,
                board=board,
                enemies=enemies,
                items=items,
                goal_position=stage.goal_position,
                max_turns=stage.constraints.get("max_turns", 100)
            )
            
            # API制限設定
            self.current_stage_id = stage_id
            self.allowed_apis = stage.allowed_apis
            self.call_history.clear()
            
            # 進捗管理: ステージ挑戦開始
            if self.progression_manager and self.student_id:
                self.progression_manager.start_stage_attempt(self.student_id, stage_id)
            
            # セッションログ: ステージ開始
            if self.session_logger:
                self.session_logger.log_stage_start(stage_id)
            
            # GUIレンダラーにExecutionControllerを設定
            if hasattr(self.renderer, 'set_execution_controller') and self.execution_controller:
                self.renderer.set_execution_controller(self.execution_controller)
                
            print(f"✅ {stage_id} を初期化しました")
            print(f"📋 利用可能API: {', '.join(self.allowed_apis)}")
            
            return True
            
        except Exception as e:
            self._handle_error(e, {"stage_id": stage_id, "operation": "stage_initialization"})
            return False
    
    def _check_api_allowed(self, api_name: str) -> None:
        """API使用許可をチェック"""
        if api_name not in self.allowed_apis:
            allowed_str = ", ".join(self.allowed_apis)
            raise APIUsageError(
                f"このステージでは '{api_name}' APIは使用できません。\n"
                f"使用可能なAPI: {allowed_str}"
            )
    
    def _record_call(self, api_name: str, result: ExecutionResult) -> None:
        """API呼び出しを記録"""
        current_time = datetime.now()
        
        with self._lock:
            self.call_history.append({
                "api": api_name,
                "success": result.is_success,
                "message": result.message,
                "timestamp": current_time.isoformat(),
                "turn": self.game_manager.get_turn_count() if self.game_manager else 0
            })
            
            # 進捗管理: アクション記録
            if self.progression_manager:
                self.progression_manager.record_action(f"{api_name}: {result.message}")
                
                # エラーの場合は進捗管理に記録
                if not result.is_success:
                    self.progression_manager.record_error(result.message)
            
            # フィードバック制御を更新
            if result.is_success:
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
            
            # 自動ヒントシステムをチェック
            if self.auto_hint_enabled and self.adaptive_hint_system and self.student_id and self.current_stage_id:
                self._check_auto_hint(current_time)
            
            # 無限ループ検出
            if len(self.call_history) >= 10:
                self._check_infinite_loop()
        
        self.last_action_time = current_time
        
        # セッションログ: アクション記録
        if self.session_logger:
            game_state = self.game_manager.get_current_state() if self.game_manager else None
            turn_number = self.game_manager.get_turn_count() if self.game_manager else None
            
            self.session_logger.log_action(
                action=api_name,
                success=result.is_success,
                message=result.message,
                turn_number=turn_number,
                game_state=game_state
            )
        
        # データアップロード: セッションログ送信
        if self.data_uploader and self.current_session_id:
            log_data = {
                "student_id": self.student_id,
                "api_name": api_name,
                "success": result.is_success,
                "message": result.message,
                "execution_time": getattr(result, 'execution_time', 0.0),
                "error_message": result.message if not result.is_success else "",
                "position": str(game_state.player.position) if game_state else ""
            }
            self.data_uploader.queue_session_log(self.current_session_id, log_data)
    
    def _check_auto_hint(self, current_time: datetime) -> None:
        """自動ヒントシステムをチェック"""
        if not self.adaptive_hint_system or not self.student_id or not self.current_stage_id:
            return
        
        # 前回のアクションからの経過時間
        time_since_last = 0.0
        if self.last_action_time:
            time_since_last = (current_time - self.last_action_time).total_seconds()
        
        # ヒントが必要かチェック
        should_hint = self.adaptive_hint_system.should_provide_hint(
            self.student_id, time_since_last, self.consecutive_failures, self.call_history
        )
        
        if should_hint:
            # 現在の状況を収集
            current_situation = {
                'consecutive_failures': self.consecutive_failures,
                'time_since_last_action': time_since_last,
                'last_action': self.call_history[-1]['api'] if self.call_history else None
            }
            
            # 文脈ヒントを取得
            hint = self.adaptive_hint_system.provide_contextual_hint(
                self.student_id, self.current_stage_id, current_situation, self.call_history
            )
            
            if hint:
                print(f"\n💡 ヒント: {hint.format_message()}")
    
    def _check_infinite_loop(self) -> None:
        """無限ループをチェック"""
        from .educational_feedback import detect_infinite_loop
        
        loop_info = detect_infinite_loop(self.call_history)
        if loop_info:
            print(f"\n⚠️ 無限ループの可能性が検出されました!")
            print(f"パターン: {loop_info.get('pattern', 'N/A')}")
            print(f"💡 適切な終了条件を設定してください")
        
        # 自動レンダリング
        if self.auto_render and self.renderer and self.game_manager:
            self._render_current_state()
        
        # ゲーム終了チェック
        if self.game_manager and self.game_manager.is_game_finished():
            self._handle_game_end()
    
    def _render_current_state(self) -> None:
        """現在の状態をレンダリング"""
        if self.renderer and self.game_manager:
            game_state = self.game_manager.get_current_state()
            if game_state:
                self.renderer.render_complete_view(game_state, show_legend=False)
    
    def _ensure_initialized(self) -> None:
        """初期化確認"""
        if self.game_manager is None:
            raise APIUsageError(
                "ゲームが初期化されていません。\n"
                "まずapi.initialize_stage('stage01')を呼び出してください。"
            )
    
    def turn_left(self) -> bool:
        """左に90度回転"""
        try:
            self._ensure_initialized()
            self._check_api_allowed("turn_left")
            
            # アクション履歴追跡
            if self.action_tracker:
                self.action_tracker.track_action("turn_left")
            
            # 実行制御の待機処理
            if self.execution_controller:
                self.execution_controller.wait_for_action()
            
            command = TurnLeftCommand()
            result = self.game_manager.execute_command(command)
            self._record_call("turn_left", result)
            
            if not result.is_success:
                print(f"❌ 回転失敗: {result.message}")
                return False
            
            return True
        except Exception as e:
            self._handle_error(e, {"action": "turn_left", "operation": "player_rotation"})
            return False
    
    def turn_right(self) -> bool:
        """右に90度回転"""
        try:
            self._ensure_initialized()
            self._check_api_allowed("turn_right")
            
            # アクション履歴追跡
            if self.action_tracker:
                self.action_tracker.track_action("turn_right")
            
            # 実行制御の待機処理
            if self.execution_controller:
                self.execution_controller.wait_for_action()
            
            command = TurnRightCommand()
            result = self.game_manager.execute_command(command)
            self._record_call("turn_right", result)
            
            if not result.is_success:
                print(f"❌ 回転失敗: {result.message}")
                return False
            
            return True
        except Exception as e:
            self._handle_error(e, {"action": "turn_right", "operation": "player_rotation"})
            return False
    
    def move(self) -> bool:
        """正面方向に1マス移動"""
        try:
            self._ensure_initialized()
            self._check_api_allowed("move")
            
            # アクション履歴追跡
            if self.action_tracker:
                self.action_tracker.track_action("move")
            
            # 実行制御の待機処理
            if self.execution_controller:
                self.execution_controller.wait_for_action()
            
            command = MoveCommand()
            result = self.game_manager.execute_command(command)
            self._record_call("move", result)
            
            if not result.is_success:
                print(f"❌ 移動失敗: {result.message}")
                return False
            
            return True
        except Exception as e:
            self._handle_error(e, {"action": "move", "operation": "player_movement"})
            return False
    
    def attack(self) -> bool:
        """正面1マスを攻撃"""
        try:
            self._ensure_initialized()
            self._check_api_allowed("attack")
            
            # アクション履歴追跡
            if self.action_tracker:
                self.action_tracker.track_action("attack")
            
            # 実行制御の待機処理
            if self.execution_controller:
                self.execution_controller.wait_for_action()
            
            command = AttackCommand()
            result = self.game_manager.execute_command(command)
            self._record_call("attack", result)
            
            if not result.is_success:
                print(f"❌ 攻撃失敗: {result.message}")
                return False
            
            print(f"⚔️ {result.message}")
            return True
        except Exception as e:
            self._handle_error(e, {"action": "attack", "operation": "player_combat"})
            return False
    
    def pickup(self) -> bool:
        """足元のアイテムを取得"""
        try:
            self._ensure_initialized()
            self._check_api_allowed("pickup")
            
            # アクション履歴追跡
            if self.action_tracker:
                self.action_tracker.track_action("pickup")
            
            # 実行制御の待機処理
            if self.execution_controller:
                self.execution_controller.wait_for_action()
            
            command = PickupCommand()
            result = self.game_manager.execute_command(command)
            self._record_call("pickup", result)
            
            if not result.is_success:
                print(f"❌ アイテム取得失敗: {result.message}")
                return False
            
            print(f"🎒 {result.message}")
            return True
        except Exception as e:
            self._handle_error(e, {"action": "pickup", "operation": "item_interaction"})
            return False
    
    def see(self) -> Dict[str, Any]:
        """周囲の状況を確認"""
        try:
            self._ensure_initialized()
            self._check_api_allowed("see")
            
            # アクション履歴追跡
            if self.action_tracker:
                self.action_tracker.track_action("see")
            
            # 実行制御の待機処理
            if self.execution_controller:
                self.execution_controller.wait_for_action()
            
            game_state = self.game_manager.get_current_state()
            if game_state is None:
                return {}
            
            player = game_state.player
            current_pos = player.position
            
            # 各方向の情報を取得
            directions = {
                "front": player.direction,
                "left": player.direction.turn_left(),
                "right": player.direction.turn_right(),
                "back": player.direction.turn_left().turn_left()
            }
            
            result = {
                "player": {
                    "position": [current_pos.x, current_pos.y],
                    "direction": player.direction.value,
                    "hp": player.hp,
                    "attack_power": player.attack_power
                },
                "surroundings": {}
            }
            
            # 各方向の状況をチェック
            for dir_name, direction in directions.items():
                check_pos = current_pos.move(direction)
                
                # 境界チェック
                if not game_state.board.is_valid_position(check_pos):
                    result["surroundings"][dir_name] = "boundary"
                    continue
                
                # 壁チェック
                if game_state.board.is_wall(check_pos):
                    result["surroundings"][dir_name] = "wall"
                    continue
                
                # 移動禁止マスチェック
                if game_state.board.is_forbidden(check_pos):
                    result["surroundings"][dir_name] = "forbidden"
                    continue
                
                # 敵チェック
                enemy = game_state.get_enemy_at(check_pos)
                if enemy:
                    result["surroundings"][dir_name] = {
                        "type": "enemy",
                        "enemy_type": enemy.enemy_type.value,
                        "hp": enemy.hp
                    }
                    continue
                
                # アイテムチェック
                item = game_state.get_item_at(check_pos)
                if item:
                    result["surroundings"][dir_name] = {
                        "type": "item",
                        "item_type": item.item_type.value,
                        "name": item.name
                    }
                    continue
                
                # ゴールチェック
                if check_pos == game_state.goal_position:
                    result["surroundings"][dir_name] = "goal"
                    continue
                
                # 空きマス
                result["surroundings"][dir_name] = "empty"
            
            # 足元の情報
            item_at_foot = game_state.get_item_at(current_pos)
            if item_at_foot:
                result["at_foot"] = {
                    "type": "item",
                    "item_type": item_at_foot.item_type.value,
                    "name": item_at_foot.name
                }
            else:
                result["at_foot"] = None
            
            # ゲーム状況
            result["game_status"] = {
                "turn": game_state.turn_count,
                "max_turns": game_state.max_turns,
                "remaining_turns": game_state.max_turns - game_state.turn_count,
                "status": game_state.status.value,
                "is_goal_reached": game_state.check_goal_reached()
            }
            
            from .commands import CommandResult
            self._record_call("see", ExecutionResult(
                result=CommandResult.SUCCESS,
                message="周囲確認完了"
            ))
            
            return result
        except Exception as e:
            self._handle_error(e, {"action": "see", "operation": "environment_observation"})
            return {}
    
    def can_undo(self) -> bool:
        """取り消し可能かチェック"""
        self._ensure_initialized()
        return self.game_manager.can_undo_last_action()
    
    def undo(self) -> bool:
        """最後のアクションを取り消し"""
        self._ensure_initialized()
        
        if not self.game_manager.can_undo_last_action():
            print("❌ 取り消しできるアクションがありません")
            return False
        
        success = self.game_manager.undo_last_action()
        if success:
            print("↩️ 最後のアクションを取り消しました")
        else:
            print("❌ 取り消しに失敗しました")
        
        return success
    
    def is_game_finished(self) -> bool:
        """ゲーム終了判定"""
        self._ensure_initialized()
        return self.game_manager.is_game_finished()
    
    def get_game_result(self) -> str:
        """ゲーム結果を取得"""
        self._ensure_initialized()
        status = self.game_manager.get_game_result()
        
        result_messages = {
            "won": "🎉 ゴール到達！ゲームクリア！",
            "failed": "💀 ゲーム失敗",
            "timeout": "⏰ 時間切れ",
            "playing": "🎮 ゲーム継続中",
            "error": "❌ エラー発生"
        }
        
        return result_messages.get(status.value, "❓ 不明な状態")
    
    def get_call_history(self) -> List[Dict[str, Any]]:
        """API呼び出し履歴を取得"""
        return self.call_history.copy()
    
    def reset_stage(self) -> bool:
        """現在のステージをリセット"""
        self._ensure_initialized()
        
        if self.current_stage_id is None:
            return False
        
        return self.initialize_stage(self.current_stage_id)
    
    def show_current_state(self) -> None:
        """現在の状態を表示"""
        self._ensure_initialized()
        if self.renderer and self.game_manager:
            game_state = self.game_manager.get_current_state()
            if game_state:
                self.renderer.render_complete_view(game_state, show_legend=True)
    
    def set_auto_render(self, enabled: bool) -> None:
        """自動レンダリングの切り替え"""
        self.auto_render = enabled
        if enabled:
            print("🖼️ 自動レンダリング: ON")
        else:
            print("🖼️ 自動レンダリング: OFF")
    
    def show_legend(self) -> None:
        """凡例を表示"""
        if self.renderer:
            self.renderer.render_legend()
    
    def show_action_history(self, limit: int = 10) -> None:
        """アクション履歴を表示"""
        if self.renderer:
            actions = [f"{h['api']}: {h['message']}" for h in self.call_history]
            self.renderer.render_action_history(actions, limit)
    
    def set_student_id(self, student_id: str) -> None:
        """学生IDを設定"""
        self.student_id = student_id
        
        # 進捗管理システム
        if self.progression_manager:
            self.progression_manager.initialize_student(student_id)
        
        # セッションログシステム（後で手動開始）
        # if self.session_logger:
        #     self.current_session_id = self.session_logger.start_session(student_id)
        
        print(f"👤 学生ID設定: {student_id}")
    
    def get_progress_report(self, stage_id: Optional[str] = None) -> Dict[str, Any]:
        """進捗レポートを取得"""
        if not self.progression_manager:
            return {"error": "進捗管理が有効になっていません"}
        
        return self.progression_manager.get_progress_report(stage_id)
    
    def get_learning_recommendations(self) -> List[str]:
        """学習推奨事項を取得"""
        if not self.progression_manager:
            return []
        
        return self.progression_manager.get_recommendations()
    
    def show_progress_summary(self) -> None:
        """進捗サマリーを表示"""
        if not self.progression_manager:
            print("❌ 進捗管理が有効になっていません")
            return
        
        # 全体進捗
        overall = self.get_progress_report()
        if not overall:
            print("📊 進捗データがありません")
            return
        
        print("📊 学習進捗サマリー")
        print("=" * 40)
        print(f"学生ID: {overall.get('student_id', 'N/A')}")
        print(f"挑戦したステージ数: {overall.get('stages_attempted', 0)}")
        print(f"総挑戦回数: {overall.get('total_attempts', 0)}")
        print(f"全体成功率: {overall.get('overall_success_rate', 0):.1%}")
        print(f"総プレイ時間: {overall.get('total_play_time', 'N/A')}")
        
        # スキル情報
        skills = overall.get('skills', {})
        if skills:
            print("\n🎓 スキルレベル:")
            for skill_name, skill_data in skills.items():
                level = skill_data.get('level', 'beginner')
                progress = skill_data.get('progress', 0) * 100
                xp = skill_data.get('xp', 0)
                print(f"  {skill_name}: {level} ({progress:.0f}%, {xp:.0f}XP)")
        
        # 推奨事項
        recommendations = self.get_learning_recommendations()
        if recommendations:
            print("\n💡 学習推奨事項:")
            for rec in recommendations:
                print(f"  {rec}")
        
        print("=" * 40)
    
    def _handle_game_end(self) -> None:
        """ゲーム終了処理"""
        if not self.progression_manager or not self.game_manager:
            return
        
        # 進捗管理: ゲーム結果記録
        game_state = self.game_manager.get_current_state()
        if game_state:
            self.progression_manager.end_stage_attempt(game_state)
            
            # セッションログ: ステージ終了記録
            if self.session_logger and self.current_stage_id:
                success = game_state.status.value == "won"
                self.session_logger.log_stage_end(self.current_stage_id, success, game_state)
            
            # 結果表示
            if game_state.status.value == "won":
                print("\n🎉 ゲームクリア！")
                self._show_performance_feedback(game_state)
            else:
                print(f"\n😔 ゲーム終了: {game_state.status.value}")
    
    def _show_performance_feedback(self, game_state) -> None:
        """パフォーマンスフィードバック表示"""
        if not self.progression_manager:
            return
        
        # 現在のセッション情報
        current_session = self.progression_manager.current_session
        if not current_session:
            return
        
        print("📈 パフォーマンス:")
        print(f"  使用ターン: {game_state.turn_count}/{game_state.max_turns}")
        print(f"  効率性: {current_session.efficiency_score:.1%}")
        print(f"  正確性: {current_session.accuracy_score:.1%}")
        
        if current_session.duration:
            print(f"  実行時間: {current_session.duration.total_seconds():.1f}秒")
        
        # スキルアップ通知は ProgressionManager 内で実行される
    
    def _handle_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """教育的エラーハンドリング"""
        if not self.error_handler:
            # エラーハンドラーが無効の場合は通常のエラー表示
            print(f"❌ エラー: {error}")
            return
        
        # コンテキスト情報を収集
        error_context = context or {}
        
        # ゲーム状態情報を追加
        if self.game_manager:
            game_state = self.game_manager.get_current_state()
            if game_state:
                error_context.update({
                    "game_state": {
                        "player_position": {"x": game_state.player.position.x, "y": game_state.player.position.y},
                        "player_direction": game_state.player.direction.value,
                        "turn_count": game_state.turn_count,
                        "max_turns": game_state.max_turns,
                        "status": game_state.status.value
                    }
                })
        
        # 最近のAPI呼び出し履歴を追加
        if self.call_history:
            recent_calls = [call["api"] for call in self.call_history[-5:]]
            error_context["recent_actions"] = recent_calls
        
        # 学生情報を追加
        if self.student_id:
            error_context["student_id"] = self.student_id
        if self.current_stage_id:
            error_context["stage_id"] = self.current_stage_id
        
        # 教育的エラー分析
        educational_error = self.error_handler.handle_error(error, error_context)
        
        # エラーログ記録
        if self.session_logger:
            self.session_logger.log_error(error, educational_error, error_context)
        
        # 教育的フィードバック表示
        print(f"\n❌ {educational_error.title}")
        print(f"💡 {educational_error.explanation}")
        
        if educational_error.solution:
            print(f"🔧 解決方法: {educational_error.solution}")
        
        if educational_error.example_code:
            print(f"📝 例:\n{educational_error.example_code}")
        
        if educational_error.hints:
            print("💭 ヒント:")
            for hint in educational_error.hints:
                print(f"  • {hint}")
        
        if educational_error.severity == "critical":
            print("\n⚠️ 重要: この問題を解決してから続行してください")
    
    def enable_action_tracking(self) -> None:
        """アクション履歴追跡を有効化"""
        if self.action_tracker:
            self.action_tracker.enable_tracking()
            print("📋 アクション履歴追跡を有効にしました")
        else:
            print("❌ アクション履歴追跡システムが初期化されていません")
    
    def disable_action_tracking(self) -> None:
        """アクション履歴追跡を無効化"""
        if self.action_tracker:
            self.action_tracker.disable_tracking()
            print("📋 アクション履歴追跡を無効にしました")
        else:
            print("❌ アクション履歴追跡システムが初期化されていません")
    
    def show_action_history(self, last_n: Optional[int] = 10) -> None:
        """アクション履歴を表示"""
        if self.action_tracker:
            self.action_tracker.display_action_history(last_n)
        else:
            print("📋 アクション履歴: 追跡システムが無効です")
    
    def reset_action_history(self) -> None:
        """アクション履歴をリセット"""
        if self.action_tracker:
            self.action_tracker.reset_counter()
            print("🔄 アクション履歴をリセットしました")
        else:
            print("❌ アクション履歴追跡システムが初期化されていません")
    
    def get_action_count(self) -> int:
        """実行アクション数を取得"""
        if self.action_tracker:
            return self.action_tracker.get_action_count()
        return 0
    
    def get_action_history_summary(self) -> Dict[str, Any]:
        """アクション履歴サマリーを取得"""
        if self.action_tracker:
            return self.action_tracker.get_history_summary()
        return {
            "total_actions": 0,
            "unique_actions": 0,
            "action_breakdown": {},
            "history_size": 0,
            "last_action": None
        }
    
    def end_session(self) -> None:
        """学習セッションを終了"""
        if self.session_logger:
            summary = self.session_logger.end_session()
            if summary:
                print(f"📝 学習セッション終了")
                print(f"   セッション時間: {summary.duration}")
                print(f"   挑戦ステージ数: {len(summary.stages_attempted)}")
                print(f"   成功率: {summary.success_rate:.1%}")
    
    def get_session_summary(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """セッションサマリーを取得"""
        if not self.session_logger:
            return None
        
        target_session_id = session_id or self.current_session_id
        if not target_session_id:
            return None
        
        summary = self.session_logger.get_session_summary(target_session_id)
        return summary.to_dict() if summary else None
    
    def list_session_history(self, student_id: Optional[str] = None) -> List[str]:
        """セッション履歴リストを取得"""
        if not self.session_logger:
            return []
        
        target_student = student_id or self.student_id
        return self.session_logger.list_sessions(target_student)
    
    def export_session_data(self, session_id: str, output_file: str) -> bool:
        """セッションデータをエクスポート"""
        if not self.session_logger:
            return False
        
        return self.session_logger.export_session_data(session_id, output_file)
    
    def log_system_message(self, message: str, data: Dict[str, Any] = None) -> None:
        """システムメッセージをログ"""
        if self.session_logger:
            self.session_logger.log_system_message(message, data)
    
    def log_user_input(self, input_data: str, context: str = "") -> None:
        """ユーザー入力をログ"""
        if self.session_logger:
            self.session_logger.log_user_input(input_data, context)
    
    def log_debug_info(self, message: str, data: Dict[str, Any] = None) -> None:
        """デバッグ情報をログ"""
        if self.session_logger:
            self.session_logger.log_debug(message, data)
    
    def generate_session_quality_report(self, code_text: str = "") -> Optional[Dict[str, Any]]:
        """現在のセッションの品質レポートを生成"""
        if not self.quality_manager or not self.student_id:
            return None
        
        # API呼び出し履歴を抽出
        api_calls = [call["api"] for call in self.call_history]
        
        # セッションデータを取得
        session_data = []
        if self.session_logger:
            # 簡略化されたセッションデータを生成
            for call in self.call_history:
                session_data.append({
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "action_executed",
                    "data": {
                        "action": call["api"],
                        "success": "成功" in call["message"]
                    }
                })
        
        # 品質レポート生成
        session_id = self.current_session_id or "current_session"
        report = self.quality_manager.generate_quality_report(
            self.student_id, session_id, code_text, api_calls, session_data
        )
        
        return {
            "overall_score": report.overall_score,
            "code_quality": report.code_metrics.overall_quality.value,
            "learning_efficiency": report.learning_metrics.learning_efficiency.value,
            "success_rate": report.learning_metrics.success_rate,
            "recommendations": report.recommendations,
            "achievements": report.achievements
        }
    
    def show_quality_summary(self, code_text: str = "") -> None:
        """品質サマリーを表示"""
        report_data = self.generate_session_quality_report(code_text)
        
        if not report_data:
            print("❌ 品質レポートを生成できませんでした")
            return
        
        print("📊 セッション品質サマリー")
        print("=" * 40)
        print(f"総合スコア: {report_data['overall_score']:.1%}")
        print(f"コード品質: {report_data['code_quality']}")
        print(f"学習効率: {report_data['learning_efficiency']}")
        print(f"成功率: {report_data['success_rate']:.1%}")
        
        if report_data['achievements']:
            print("\n🏆 達成項目:")
            for achievement in report_data['achievements']:
                print(f"  • {achievement}")
        
        if report_data['recommendations']:
            print("\n💡 改善提案:")
            for rec in report_data['recommendations']:
                print(f"  • {rec}")
    
    def get_progress_analytics(self) -> Dict[str, Any]:
        """進捗分析データを取得"""
        if not self.quality_manager or not self.student_id:
            return {}
        
        from .quality_assurance import get_student_progress_summary
        return get_student_progress_summary(self.student_id)
    
    def generate_comprehensive_report(self, code_text: str = "", 
                                    collaborators: List[str] = None,
                                    submission_date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """包括的レポート生成"""
        if not self.progress_analyzer or not self.student_id:
            return None
        
        # API履歴とセッションログ取得
        api_history = [call["api"] for call in self.call_history]
        session_log = []
        
        if self.session_logger:
            # 簡略化されたセッションログ生成
            for call in self.call_history:
                session_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "action_executed",
                    "data": {
                        "action": call["api"],
                        "success": "成功" in call["message"]
                    }
                })
        
        # 包括的レポート生成
        session_id = self.current_session_id or "current_session"
        stage_id = self.current_stage_id or "unknown_stage"
        
        report = self.progress_analyzer.analyze_session(
            self.student_id, stage_id, session_id, code_text, session_log,
            api_history, collaborators, submission_date
        )
        
        return {
            "report_id": report.report_id,
            "overall_score": report.overall_score,
            "learning_grade": report.learning_grade,
            "code_quality_score": report.code_analysis.code_quality_score,
            "learning_efficiency": report.learning_metrics.efficiency_score,
            "success_rate": report.learning_metrics.success_rate,
            "strengths": report.strengths,
            "improvements": report.improvements,
            "recommendations": report.recommendations,
            "sheets_data": report.to_sheets_format()
        }
    
    def show_comprehensive_summary(self, code_text: str = "") -> None:
        """包括的サマリー表示"""
        report_data = self.generate_comprehensive_report(code_text)
        
        if not report_data:
            print("❌ 包括的レポートを生成できませんでした")
            return
        
        print("📊 包括的学習レポート")
        print("=" * 50)
        print(f"学習評価: {report_data['learning_grade']}")
        print(f"総合スコア: {report_data['overall_score']:.1%}")
        print(f"コード品質: {report_data['code_quality_score']:.1%}")
        print(f"学習効率: {report_data['learning_efficiency']:.1%}")
        print(f"成功率: {report_data['success_rate']:.1%}")
        
        if report_data['strengths']:
            print("\n🏆 認められた強み:")
            for strength in report_data['strengths']:
                print(f"  • {strength}")
        
        if report_data['improvements']:
            print("\n🔧 改善が必要な領域:")
            for improvement in report_data['improvements']:
                print(f"  • {improvement}")
        
        if report_data['recommendations']:
            print("\n💡 推奨される次のステップ:")
            for rec in report_data['recommendations']:
                print(f"  • {rec}")
    
    def export_for_sheets(self, code_text: str = "", output_file: str = "") -> Optional[str]:
        """Google Sheets用データをエクスポート"""
        report_data = self.generate_comprehensive_report(code_text)
        
        if not report_data:
            return None
        
        sheets_data = report_data['sheets_data']
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sheets_data, f, ensure_ascii=False, indent=2)
            
            return str(output_path)
        else:
            return json.dumps(sheets_data, ensure_ascii=False, indent=2)
    
    def get_educational_feedback(self) -> List[Dict[str, Any]]:
        """教育フィードバックを取得"""
        if not self.feedback_generator or not self.student_id or not self.current_stage_id:
            return []
        
        from .educational_feedback import generate_educational_feedback
        
        feedback_messages = generate_educational_feedback(
            self.student_id, self.current_stage_id, self.call_history
        )
        
        return [{
            'type': msg.type.value,
            'title': msg.title,
            'message': msg.message,
            'priority': msg.priority,
            'formatted': msg.format_message(self.student_id)
        } for msg in feedback_messages]
    
    def request_hint(self) -> Optional[str]:
        """ヒントを要求"""
        if not self.adaptive_hint_system or not self.student_id or not self.current_stage_id:
            return "ヒント機能が有効になっていません"
        
        current_situation = {
            'consecutive_failures': self.consecutive_failures,
            'manual_request': True,
            'last_action': self.call_history[-1]['api'] if self.call_history else None
        }
        
        hint = self.adaptive_hint_system.provide_contextual_hint(
            self.student_id, self.current_stage_id, current_situation, self.call_history
        )
        
        if hint:
            return hint.format_message(self.student_id)
        else:
            return "現在の状況では適切なヒントがありません。基本的な移動から試してみましょう。"
    
    def toggle_auto_hints(self, enabled: bool) -> None:
        """自動ヒントの有効/無効を切り替え"""
        self.auto_hint_enabled = enabled
        status = "有効" if enabled else "無効"
        print(f"自動ヒントを{status}にしました")
    
    def show_learning_feedback(self) -> None:
        """学習フィードバックを表示"""
        feedback_list = self.get_educational_feedback()
        
        if not feedback_list:
            print("現在、表示するフィードバックはありません")
            return
        
        print("\n📚 学習フィードバック")
        print("=" * 40)
        
        for feedback in feedback_list:
            print(feedback['formatted'])
            print("-" * 30)


# グローバルAPIインスタンス（初期化は initialize_api で行う）
_global_api = None


def initialize_api(renderer_type: str = "cui", enable_progression: bool = True, 
                   enable_session_logging: bool = True, student_id: Optional[str] = None) -> None:
    """グローバルAPIを指定されたレンダラータイプで初期化
    
    Args:
        renderer_type: "cui" または "gui"
        enable_progression: 進捗管理を有効にするか
        enable_session_logging: セッションログを有効にするか
        student_id: 学生ID（指定された場合は自動設定）
    """
    global _global_api
    _global_api = APILayer(renderer_type, enable_progression, enable_session_logging)
    print(f"📺 APIレイヤーを{renderer_type.upper()}モードで初期化しました")
    print(f"🔧 確認: renderer_type = {_global_api.renderer_type}")
    
    if enable_progression:
        print("📊 進捗管理システムが有効になりました")
    
    if enable_session_logging:
        print("📝 セッションログシステムが有効になりました")
        
    if student_id:
        _global_api.set_student_id(student_id)
    else:
        # config から学生IDを取得
        import config
        if hasattr(config, 'STUDENT_ID') and config.STUDENT_ID and config.STUDENT_ID != "000000A":
            _global_api.set_student_id(config.STUDENT_ID)


# グローバル関数（学生が直接使用）
def initialize_stage(stage_id: str) -> bool:
    """ステージを初期化
    
    Args:
        stage_id: ステージID（例: "stage01"）
    
    Returns:
        bool: 初期化成功時True
    """
    if _global_api is None:
        raise APIUsageError(
            "APIが初期化されていません。\n"
            "まず initialize_api() を呼び出してください。"
        )
    return _global_api.initialize_stage(stage_id)


def turn_left() -> bool:
    """左に90度回転
    
    Returns:
        bool: 回転成功時True
    """
    return _global_api.turn_left()


def turn_right() -> bool:
    """右に90度回転
    
    Returns:
        bool: 回転成功時True
    """
    return _global_api.turn_right()


def move() -> bool:
    """正面方向に1マス移動
    
    Returns:
        bool: 移動成功時True
    """
    return _global_api.move()


def attack() -> bool:
    """正面1マスを攻撃
    
    Returns:
        bool: 攻撃成功時True
    """
    return _global_api.attack()


def pickup() -> bool:
    """足元のアイテムを取得
    
    Returns:
        bool: 取得成功時True
    """
    return _global_api.pickup()


def see() -> Dict[str, Any]:
    """周囲の状況を確認
    
    Returns:
        Dict: 周囲の状況情報
    """
    return _global_api.see()


def can_undo() -> bool:
    """取り消し可能かチェック
    
    Returns:
        bool: 取り消し可能時True
    """
    return _global_api.can_undo()


def undo() -> bool:
    """最後のアクションを取り消し
    
    Returns:
        bool: 取り消し成功時True
    """
    return _global_api.undo()


def is_game_finished() -> bool:
    """ゲーム終了判定
    
    Returns:
        bool: ゲーム終了時True
    """
    return _global_api.is_game_finished()


def get_game_result() -> str:
    """ゲーム結果を取得
    
    Returns:
        str: ゲーム結果メッセージ
    """
    return _global_api.get_game_result()


def get_call_history() -> List[Dict[str, Any]]:
    """API呼び出し履歴を取得
    
    Returns:
        List: 呼び出し履歴
    """
    return _global_api.get_call_history()


def reset_stage() -> bool:
    """現在のステージをリセット
    
    Returns:
        bool: リセット成功時True
    """
    return _global_api.reset_stage()


def show_current_state() -> None:
    """現在のゲーム状態を視覚的に表示"""
    _global_api.show_current_state()


def set_auto_render(enabled: bool) -> None:
    """自動レンダリングの切り替え
    
    Args:
        enabled: True で自動レンダリング有効
    """
    _global_api.set_auto_render(enabled)


def show_legend() -> None:
    """ゲーム画面の凡例を表示"""
    _global_api.show_legend()


def show_action_history(limit: int = 10) -> None:
    """アクション履歴を表示
    
    Args:
        limit: 表示する履歴の件数
    """
    _global_api.show_action_history(limit)


def enable_action_tracking() -> None:
    """アクション履歴追跡を有効化"""
    _global_api.enable_action_tracking()


def disable_action_tracking() -> None:
    """アクション履歴追跡を無効化"""
    _global_api.disable_action_tracking()


def reset_action_history() -> None:
    """アクション履歴をリセット"""
    _global_api.reset_action_history()


def get_action_count() -> int:
    """実行アクション数を取得
    
    Returns:
        int: 実行されたアクション数
    """
    return _global_api.get_action_count()


def get_action_history_summary() -> Dict[str, Any]:
    """アクション履歴サマリーを取得
    
    Returns:
        Dict: アクション履歴のサマリー情報
    """
    return _global_api.get_action_history_summary()


def set_student_id(student_id: str) -> None:
    """学生IDを設定
    
    Args:
        student_id: 学生ID
    """
    _global_api.set_student_id(student_id)


def show_progress_summary() -> None:
    """学習進捗サマリーを表示"""
    _global_api.show_progress_summary()


def get_progress_report(stage_id: Optional[str] = None) -> Dict[str, Any]:
    """進捗レポートを取得
    
    Args:
        stage_id: 特定ステージの進捗（省略時は全体進捗）
    
    Returns:
        Dict: 進捗レポート
    """
    return _global_api.get_progress_report(stage_id)


def get_learning_recommendations() -> List[str]:
    """学習推奨事項を取得
    
    Returns:
        List: 推奨事項リスト
    """
    return _global_api.get_learning_recommendations()


def use_hint() -> None:
    """ヒントを使用（進捗記録用）"""
    if _global_api.progression_manager:
        _global_api.progression_manager.use_hint()
    
    if _global_api.session_logger:
        _global_api.session_logger.log_hint_used("ヒント使用")
    
    print("💡 ヒントを使用しました（進捗に記録されます）")


def end_session() -> None:
    """学習セッションを終了"""
    _global_api.end_session()


def get_session_summary(session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """セッションサマリーを取得
    
    Args:
        session_id: セッションID（省略時は現在のセッション）
    
    Returns:
        Dict: セッションサマリー
    """
    return _global_api.get_session_summary(session_id)


def list_session_history(student_id: Optional[str] = None) -> List[str]:
    """セッション履歴リストを取得
    
    Args:
        student_id: 学生ID（省略時は現在の学生）
    
    Returns:
        List: セッションIDリスト
    """
    return _global_api.list_session_history(student_id)


def export_session_data(session_id: str, output_file: str) -> bool:
    """セッションデータをエクスポート
    
    Args:
        session_id: セッションID
        output_file: 出力ファイルパス
    
    Returns:
        bool: エクスポート成功時True
    """
    return _global_api.export_session_data(session_id, output_file)


def log_user_input(input_data: str, context: str = "") -> None:
    """ユーザー入力をログ
    
    Args:
        input_data: 入力データ
        context: コンテキスト情報
    """
    _global_api.log_user_input(input_data, context)


def log_debug_info(message: str, data: Dict[str, Any] = None) -> None:
    """デバッグ情報をログ
    
    Args:
        message: デバッグメッセージ
        data: 追加データ
    """
    _global_api.log_debug_info(message, data)


def get_error_feedback(error_type: str) -> Optional[str]:
    """特定のエラータイプに対するフィードバックを取得
    
    Args:
        error_type: エラータイプ名
    
    Returns:
        str: エラーフィードバック（見つからない場合はNone）
    """
    if not _global_api.error_handler:
        return None
    return _global_api.error_handler.get_error_pattern(error_type)


def show_error_help(error_category: str = None) -> None:
    """エラーヘルプを表示
    
    Args:
        error_category: エラーカテゴリ（省略時は全てのヘルプを表示）
    """
    if not _global_api.error_handler:
        print("❌ エラーハンドリング機能が有効になっていません")
        return
    
    _global_api.error_handler.show_help(error_category)


def check_common_mistakes() -> List[str]:
    """一般的なミステイクをチェック
    
    Returns:
        List[str]: 発見された問題のリスト
    """
    if not _global_api.error_handler:
        return []
    
    return _global_api.error_handler.check_common_patterns(_global_api.call_history)


def show_quality_summary(code_text: str = "") -> None:
    """現在のセッションの品質サマリーを表示
    
    Args:
        code_text: 分析対象のコードテキスト（オプション）
    """
    _global_api.show_quality_summary(code_text)


def get_session_quality_report(code_text: str = "") -> Optional[Dict[str, Any]]:
    """セッション品質レポートを取得
    
    Args:
        code_text: 分析対象のコードテキスト（オプション）
    
    Returns:
        Dict: 品質レポートデータ
    """
    return _global_api.generate_session_quality_report(code_text)


def get_progress_analytics() -> Dict[str, Any]:
    """進捗分析データを取得
    
    Returns:
        Dict: 進捗分析データ
    """
    return _global_api.get_progress_analytics()


def analyze_code_quality(code_text: str) -> Dict[str, Any]:
    """コード品質を分析
    
    Args:
        code_text: 分析対象のコード
    
    Returns:
        Dict: コード品質分析結果
    """
    from .quality_assurance import analyze_code_quality as qa_analyze
    
    # API呼び出し履歴からAPI使用を抽出
    api_calls = [call["api"] for call in _global_api.call_history]
    
    return qa_analyze(code_text, api_calls)


def show_comprehensive_summary(code_text: str = "") -> None:
    """包括的学習サマリーを表示
    
    Args:
        code_text: 分析対象のコードテキスト（オプション）
    """
    _global_api.show_comprehensive_summary(code_text)


def generate_comprehensive_report(code_text: str = "", 
                                collaborators: List[str] = None,
                                submission_date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    """包括的レポートを生成
    
    Args:
        code_text: 分析対象のコードテキスト（オプション）
        collaborators: 協力者リスト（オプション）
        submission_date: 提出日時（オプション）
    
    Returns:
        Dict: 包括的レポートデータ
    """
    return _global_api.generate_comprehensive_report(code_text, collaborators, submission_date)


def export_sheets_data(code_text: str = "", output_file: str = "") -> Optional[str]:
    """Google Sheets用データをエクスポート
    
    Args:
        code_text: 分析対象のコードテキスト（オプション）
        output_file: 出力ファイルパス（オプション、未指定時はJSON文字列を返す）
    
    Returns:
        str: ファイルパスまたはJSON文字列
    """
    return _global_api.export_for_sheets(code_text, output_file)


def analyze_code_complexity(code_text: str) -> Dict[str, Any]:
    """コード複雑度を分析
    
    Args:
        code_text: 分析対象のコード
    
    Returns:
        Dict: 複雑度分析結果
    """
    from .progress_analytics import analyze_code_complexity as ac_analyze
    return ac_analyze(code_text)


def request_hint() -> Optional[str]:
    """ヒントを要求
    
    Returns:
        str: ヒントメッセージ
    """
    return _global_api.request_hint()


def show_learning_feedback() -> None:
    """学習フィードバックを表示"""
    _global_api.show_learning_feedback()


def toggle_auto_hints(enabled: bool) -> None:
    """自動ヒントの有効/無効を切り替え
    
    Args:
        enabled: True で有効、False で無効
    """
    _global_api.toggle_auto_hints(enabled)


def get_educational_feedback() -> List[Dict[str, Any]]:
    """教育フィードバックを取得
    
    Returns:
        List[Dict]: フィードバックメッセージのリスト
    """
    return _global_api.get_educational_feedback()


def detect_learning_patterns() -> List[str]:
    """学習パターンを検出
    
    Returns:
        List[str]: 検出されたパターンのリスト
    """
    from .educational_feedback import detect_infinite_loop
    
    api_history = _global_api.call_history
    patterns = []
    
    # 無限ループ検出
    loop_info = detect_infinite_loop(api_history)
    if loop_info:
        patterns.append(f"無限ループパターン: {loop_info.get('type', 'unknown')}")
    
    # 連続失敗パターン
    consecutive_failures = _global_api.consecutive_failures
    if consecutive_failures >= 3:
        patterns.append(f"連続失敗: {consecutive_failures}回")
    
    # API多様性チェック
    unique_apis = len(set(entry.get('api', '') for entry in api_history))
    if unique_apis <= 2 and len(api_history) >= 10:
        patterns.append("API使用の多様性不足")
    
    return patterns


def upload_student_data() -> bool:
    """現在の学生データをGoogle Sheetsにアップロード
    
    Returns:
        bool: アップロード成功の可否
    """
    if not _global_api.data_uploader:
        print("⚠️ データアップロード機能が無効です")
        return False
    
    if not _global_api.student_id:
        print("⚠️ 学生IDが設定されていません")
        return False
    
    # セッションデータ構築
    session_data = {
        "stage_id": _global_api.current_stage_id or "",
        "session_duration": 0.0,
        "success_rate": 0.0,
        "failed_attempts": _global_api.consecutive_failures,
        "hint_requests": 0,
        "code_lines": 0,
        "complexity": 0,
        "learning_stage": "beginner"
    }
    
    # 進捗データから詳細情報を取得
    if _global_api.progression_manager:
        progress_data = _global_api.progression_manager.get_progress_data()
        session_data.update({
            "session_duration": progress_data.get("session_duration", 0.0),
            "success_rate": progress_data.get("success_rate", 0.0)
        })
    
    _global_api.data_uploader.queue_student_progress(_global_api.student_id, session_data)
    print("📊 学生データをアップロードキューに追加しました")
    return True


def force_sheets_upload() -> bool:
    """Google Sheetsに強制アップロード
    
    Returns:
        bool: アップロード成功の可否
    """
    if not _global_api.data_uploader:
        print("⚠️ データアップロード機能が無効です")
        return False
    
    return _global_api.data_uploader.force_upload()


def get_sheets_status() -> Dict[str, Any]:
    """Google Sheets統合状態を取得
    
    Returns:
        Dict[str, Any]: 統合状態情報
    """
    if not _global_api.data_uploader:
        return {"enabled": False, "message": "データアップロード機能が無効です"}
    
    return _global_api.data_uploader.get_upload_status()


def show_sheets_status() -> None:
    """Google Sheets統合状態を表示"""
    status = get_sheets_status()
    
    print("\n" + "=" * 50)
    print("📊 Google Sheets統合状態")
    print("=" * 50)
    
    if status.get("enabled", False):
        print("✅ Google Sheets統合: 有効")
        print(f"📝 アップロードキュー: {status.get('queue_size', 0)}件")
        print(f"🔗 接続状態: {status.get('connection_status', 'unknown')}")
        
        last_upload = status.get('last_upload')
        if last_upload:
            print(f"⏰ 最終アップロード: {last_upload}")
        else:
            print("⏰ 最終アップロード: なし")
    else:
        print("⚠️ Google Sheets統合: 無効")
        print("   設定またはライブラリが不足している可能性があります")
        print("   設定ファイル: config/google_sheets.json")
        print("   必要ライブラリ: gspread, oauth2client")


def generate_class_report(class_students: List[str]) -> Optional[Dict[str, Any]]:
    """クラス全体のレポートを生成
    
    Args:
        class_students (List[str]): クラスの学生IDリスト
    
    Returns:
        Optional[Dict[str, Any]]: クラスレポート（失敗時None）
    """
    if not _global_api.data_uploader:
        print("⚠️ データアップロード機能が無効です")
        return None
    
    from .data_uploader import TeacherDashboard
    dashboard = TeacherDashboard(_global_api.data_uploader)
    
    return dashboard.generate_class_summary(class_students)


def show_class_report(class_students: List[str]) -> None:
    """クラス全体のレポートを表示
    
    Args:
        class_students (List[str]): クラスの学生IDリスト
    """
    report = generate_class_report(class_students)
    
    if not report:
        print("❌ クラスレポート生成に失敗しました")
        return
    
    if "error" in report:
        print(f"❌ エラー: {report['error']}")
        return
    
    print("\n" + "=" * 60)
    print("👨‍🏫 クラス全体レポート")
    print("=" * 60)
    
    print(f"📊 総学生数: {report['total_students']}名")
    print(f"✅ アクティブ学生: {report['active_students']}名")
    print(f"📈 平均進捗度: {report['average_progress']:.1%}")
    
    print(f"\n🏆 優秀学生:")
    for student in report.get('top_performers', []):
        print(f"   • {student['student_id']}: {student['score']:.1%} ({student['grade']})")
    
    print(f"\n⚠️ 支援が必要な学生:")
    for student in report.get('students_needing_help', []):
        print(f"   • {student['student_id']}: {student['score']:.1%} (課題{student['issues']}個)")
    
    print(f"\n🔍 共通課題:")
    for issue in report.get('common_issues', []):
        print(f"   • {issue}")


# エクスポート用
__all__ = [
    "APILayer", "APIUsageError", "initialize_api",
    "initialize_stage", "turn_left", "turn_right", "move",
    "attack", "pickup", "see", "can_undo", "undo",
    "is_game_finished", "get_game_result", "get_call_history", "reset_stage",
    "show_current_state", "set_auto_render", "show_legend", "show_action_history",
    "enable_action_tracking", "disable_action_tracking", "reset_action_history",
    "get_action_count", "get_action_history_summary",
    "set_student_id", "show_progress_summary", "get_progress_report", 
    "get_learning_recommendations", "use_hint",
    "end_session", "get_session_summary", "list_session_history", 
    "export_session_data", "log_user_input", "log_debug_info",
    "get_error_feedback", "show_error_help", "check_common_mistakes",
    "show_quality_summary", "get_session_quality_report", "get_progress_analytics", 
    "analyze_code_quality", "show_comprehensive_summary", "generate_comprehensive_report",
    "export_sheets_data", "analyze_code_complexity", "request_hint", "show_learning_feedback",
    "toggle_auto_hints", "get_educational_feedback", "detect_learning_patterns",
    "upload_student_data", "force_sheets_upload", "get_sheets_status", "show_sheets_status",
    "generate_class_report", "show_class_report"
]