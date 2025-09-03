"""
実行制御システム
ExecutionController - solve()関数の実行制御とステップ実行管理
"""

import threading
import time
import logging
from typing import Optional, Callable, Any, Dict, List
from datetime import datetime

from . import ExecutionMode, ExecutionState, StepResult, ExecutionStateDetail, StepExecutionError
from .action_boundary_detector import ActionBoundaryDetector
from .pause_controller import PauseController
from .state_transition_manager import StateTransitionManager, TransitionResult
from .reset_manager import ResetManager

logger = logging.getLogger(__name__)

def with_error_handling(operation_name: str):
    """🆕 v1.2.1: エラーハンドリングデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.debug(f"✅ {operation_name} 成功")
                return result
            except StepExecutionError as e:
                logger.error(f"❌ {operation_name} ステップ実行エラー: {e}")
                display_educational_error(operation_name, str(e), "step_execution")
                return None
            except Exception as e:
                logger.critical(f"🚨 {operation_name} 予期しないエラー: {e}")
                # システムを安全な状態に復旧
                if hasattr(args[0], '_safe_state_recovery'):
                    args[0]._safe_state_recovery()
                display_educational_error(operation_name, "システムエラーが発生しました", "system_error")
                return None
        return wrapper
    return decorator

def display_educational_error(operation: str, message: str, error_type: str = "general") -> None:
    """🆕 v1.2.1: 教育的エラーメッセージ表示"""
    educational_messages = {
        "step_execution": "💡 ステップ実行で問題が発生しました。Resetボタンを押して初期状態に戻してください。",
        "pause_control": "💡 一時停止で問題が発生しました。Continueボタンで実行を再開するか、Resetで初期化してください。",
        "system_error": "💡 システムエラーが発生しました。Resetボタンで初期状態に戻すことをお勧めします。",
        "general": "💡 操作に問題が発生しました。Resetボタンで初期状態に戻してください。"
    }
    
    print(f"❌ エラー: {operation} - {message}")
    print(educational_messages.get(error_type, educational_messages["general"]))

class ExecutionControlError(Exception):
    """実行制御関連のエラー"""
    pass

class ExecutionController:
    """実行制御管理クラス"""
    
    def __init__(self, game_api=None):
        self.game_api = game_api
        self.state = ExecutionState()
        self.pause_event = threading.Event()
        self.step_event = threading.Event()
        self.stop_requested = threading.Event()
        self._lock = threading.Lock()
        self.action_callback: Optional[Callable[[str], Any]] = None
        
        # 🆕 v1.2.1: 単一アクション制御用フラグ
        self.pending_action = False
        self.action_completed = False
        self.action_start_time: Optional[datetime] = None
        
        # 🆕 v1.2.1: 新規コンポーネント統合
        self.action_boundary_detector = ActionBoundaryDetector()
        self.pause_controller = PauseController()
        self.state_transition_manager = StateTransitionManager()
        self.reset_manager = ResetManager()
        
        # ResetManagerにコンポーネントを登録
        self.reset_manager.register_component("action_boundary_detector", self.action_boundary_detector)
        self.reset_manager.register_component("pause_controller", self.pause_controller)
        self.reset_manager.register_component("state_transition_manager", self.state_transition_manager)
        self.reset_manager.register_component("execution_controller", self)
        
        # GameAPI関連のリセット処理も追加
        if hasattr(self.game_api, 'reset_game'):
            self.reset_manager.register_component("game_api", self.game_api)
        
        # 初期状態は一時停止
        self.pause_event.clear()
        self.step_event.clear()
        self.stop_requested.clear()
        
        logger.debug("ExecutionController初期化完了（v1.2.1統合版）")
    
    def pause_before_solve(self) -> None:
        """solve()実行直前で自動的に停止"""
        with self._lock:
            self.state.mode = ExecutionMode.PAUSED
            self.state.is_running = False
            self.pause_event.clear()
            
        logger.info("🔄 solve()実行前で一時停止しました")
        logger.info("💡 GUI上のボタンまたはキーボードショートカット（F1=Step、F2=Run、F3=Stop）で実行制御してください")
        
        # 一時停止状態にセットするのみ（GUIループに制御を戻す）
        # _wait_for_user_actionは呼び出さない
    
    @with_error_handling("ステップ実行")
    def step_execution(self) -> StepResult:
        """🆕 v1.2.1: 単一ステップ実行（厳密な1アクション制御）"""
        start_time = datetime.now()
        
        with self._lock:
            if self.state.mode == ExecutionMode.COMPLETED:
                logger.info("✅ solve()の実行が既に完了しています")
                return StepResult(
                    success=False,
                    action_executed="none",
                    new_state=ExecutionMode.COMPLETED,
                    execution_time_ms=0.0
                )
            
            # 🆕 v1.2.1: StateTransitionManagerによる安全な状態遷移
            transition_result = self.state_transition_manager.transition_to(
                ExecutionMode.STEPPING, 
                "user_step_request"
            )
            
            if not transition_result.success:
                logger.error(f"❌ ステップ実行状態遷移失敗: {transition_result.error_message}")
                raise StepExecutionError(f"状態遷移失敗: {transition_result.error_message}")
                
            # ステップ実行開始
            self.state.mode = ExecutionMode.STEPPING
            self.state.step_count += 1
            self.state.current_action = "step_pending"
            self.state.last_transition = start_time
            
            # 🆕 v1.2.1: ActionBoundaryDetectorでアクション境界をマーク
            boundary = self.action_boundary_detector.mark_action_start("step_execution")
            
            # 実際のステップ実行を開始
            try:
                # GameAPIが利用可能かチェック
                if self.game_api is None:
                    logger.warning("⚠️ GameAPIが設定されていません - モックアクション実行")
                    # モックアクション実行
                    time.sleep(0.05)  # 50ms待機してアクション実行をシミュレート
                    action_executed = True
                else:
                    # ステップ実行フラグをセット
                    self.step_event.set()
                    self.pending_action = True
                    self.state.current_action = "step_executing"
                    
                    # 実行許可をセット（solve()ループが1つのアクションを実行する）
                    # これにより、solve()実行中のwait_for_actionが1つのアクションを許可する
                    
                    # 短時間待機してアクションが完了するまで待つ
                    wait_start = datetime.now()
                    max_wait_ms = 200.0  # 最大200ms待機に短縮
                    
                    while self.pending_action and (datetime.now() - wait_start).total_seconds() * 1000 < max_wait_ms:
                        time.sleep(0.01)  # 10ms間隔でチェック
                    
                    # アクションが実行されたかどうかを確認
                    action_executed = not self.pending_action
                    
                    # タイムアウトした場合は強制的にアクション完了として扱う
                    if not action_executed:
                        logger.warning(f"⚠️ ステップ実行タイムアウト - 強制完了")
                        self.pending_action = False
                        action_executed = True
                
                # アクション境界を完了としてマーク
                self.action_boundary_detector.mark_action_complete("step_execution")
                
                # 状態をPAUSEDに戻す
                pause_transition = self.state_transition_manager.transition_to(
                    ExecutionMode.PAUSED, 
                    "step_complete"
                )
                
                if pause_transition.success:
                    self.state.mode = ExecutionMode.PAUSED
                    self.state.current_action = None
                
            except Exception as e:
                logger.error(f"❌ ステップ実行エラー: {e}")
                # エラー状態に遷移
                self.state_transition_manager.transition_to(ExecutionMode.ERROR, "step_error")
                self.state.mode = ExecutionMode.ERROR
                
                execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                return StepResult(
                    success=False,
                    action_executed="error",
                    new_state=ExecutionMode.ERROR,
                    execution_time_ms=execution_time_ms,
                    error_message=str(e)
                )
            
        logger.debug(f"🔍 ステップ実行 #{self.state.step_count} 完了")
        
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        actions_count = 1 if action_executed else 0
        
        return StepResult(
            success=action_executed,
            action_executed="step_completed" if action_executed else "step_timeout",
            new_state=ExecutionMode.PAUSED,
            execution_time_ms=execution_time_ms,
            actions_executed=actions_count
        )
    
    def continuous_execution(self, sleep_interval: float = 1.0) -> None:
        """まとめて実行（sleep_intervalに基づく連続実行制御）"""
        with self._lock:
            if self.state.mode == ExecutionMode.COMPLETED:
                logger.info("✅ solve()の実行が既に完了しています")
                return
                
            self.state.mode = ExecutionMode.CONTINUOUS
            self.state.sleep_interval = sleep_interval
            self.state.is_running = True
            self.pause_event.set()
            
        logger.info(f"🚀 まとめて実行開始（速度: {sleep_interval}秒間隔）")
    
    @with_error_handling("一時停止実行")
    def pause_execution(self) -> None:
        """🆕 v1.2.1: 実行を一時停止（PauseController統合）"""
        with self._lock:
            current_mode = self.state.mode
            
            # 🆕 v1.2.1: PauseControllerで次アクション境界一時停止要求
            if current_mode == ExecutionMode.CONTINUOUS:
                pause_request = self.pause_controller.request_pause_at_next_action("user")
                # StateTransitionManagerで状態遷移
                transition_result = self.state_transition_manager.transition_to(
                    ExecutionMode.PAUSE_PENDING,
                    "user_pause_request"
                )
                
                if transition_result.success:
                    self.state.mode = ExecutionMode.PAUSE_PENDING
                    self.state.pause_pending = True
                    self.state.last_transition = datetime.now()
                    logger.info("⏸️ 次のアクション境界での一時停止を要求しました")
                else:
                    logger.error(f"❌ PAUSE_PENDING遷移失敗: {transition_result.error_message}")
            
            elif current_mode == ExecutionMode.PAUSED:
                # 既に一時停止状態の場合は何もしない
                logger.info("⏸️ 既に一時停止状態です")
            
            else:
                # その他の状態では即座に一時停止
                pause_request = self.pause_controller.request_pause_at_next_action("user")
                transition_result = self.state_transition_manager.transition_to(
                    ExecutionMode.PAUSED,
                    "immediate_pause"
                )
                
                if transition_result.success:
                    self.state.mode = ExecutionMode.PAUSED
                    self.state.is_running = False
                    self.state.current_action = None
                    self.state.last_transition = datetime.now()
                    self.pause_event.clear()
                    self.stop_requested.set()
                    logger.info("⏸️ 実行を即座に一時停止しました")
                else:
                    # フォールバック：即座の一時停止
                    self._immediate_pause()
    
    def _immediate_pause(self) -> None:
        """即座の一時停止（内部用）"""
        transition_result = self.state_transition_manager.transition_to(
            ExecutionMode.PAUSED,
            "immediate_pause"
        )
        
        if transition_result.success:
            self.state.mode = ExecutionMode.PAUSED
            self.state.is_running = False
            self.state.current_action = None
            self.state.last_transition = datetime.now()
            self.pause_event.clear()
            self.stop_requested.set()
            logger.info("⏸️ 実行を即座に一時停止しました")
    
    def stop_execution(self) -> None:
        """実行停止（次のアクション操作実行後に一時停止）"""
        with self._lock:
            if self.state.mode == ExecutionMode.COMPLETED:
                logger.info("✅ solve()の実行が既に完了しています")
                return
                
            # 停止リクエストを設定
            self.stop_requested.set()
            self.state.is_running = False
            
        logger.info("⏹️ 実行停止がリクエストされました（次のアクション後に停止）")
    
    def is_execution_complete(self) -> bool:
        """実行完了確認"""
        return self.state.mode == ExecutionMode.COMPLETED
    
    def set_animation_speed(self, speed_level: int) -> None:
        """アニメーション速度設定（1-5の段階）"""
        speed_map = {
            1: 1.0,      # 1倍速（1秒）
            2: 0.5,      # 2倍速（0.5秒）  
            3: 0.25,     # 4倍速（0.25秒）
            4: 0.125,    # 8倍速（0.125秒）
            5: 0.0625    # 16倍速（0.0625秒）
        }
        
        if speed_level not in speed_map:
            raise ExecutionControlError(f"無効な速度レベル: {speed_level}. 1-5の範囲で指定してください")
        
        with self._lock:
            self.state.sleep_interval = speed_map[speed_level]
            
        logger.debug(f"⚡ 実行速度設定: {speed_level}レベル ({speed_map[speed_level]}秒)")
    
    def get_speed_options(self) -> dict:
        """速度選択肢の取得"""
        return {
            "1倍速 (1.0s)": 1,
            "2倍速 (0.5s)": 2, 
            "4倍速 (0.25s)": 3,
            "8倍速 (0.125s)": 4,
            "16倍速 (0.0625s)": 5
        }
    
    def wait_for_action(self) -> None:
        """🆕 v1.2.1: 改善されたアクション待機（無限ループ回避）"""
        try:
            if self.state.mode == ExecutionMode.STEPPING:
                self._handle_stepping_mode()
            elif self.state.mode == ExecutionMode.CONTINUOUS:
                self._handle_continuous_mode()
            elif self.state.mode == ExecutionMode.PAUSE_PENDING:
                self._handle_pause_pending_mode()
        except Exception as e:
            logger.error(f"❌ wait_for_action エラー: {e}")
            self._safe_state_recovery()
    
    def _handle_stepping_mode(self) -> None:
        """ステップモードでの待機処理"""
        with self._lock:
            if self.pending_action:
                # 1つのアクション実行を許可
                self.pending_action = False
                self.state.current_action = "executing"
                logger.debug("🔍 単一アクション実行許可")
                return
            else:
                # アクション完了後はPAUSEDに遷移して無限ループ待機
                self.state.mode = ExecutionMode.PAUSED
                self.state.current_action = None
                self.state.last_transition = datetime.now()
                self.action_completed = True
                self.step_event.clear()
                
                # ステップ実行完了を通知
                logger.info("⏸️ ステップ実行完了 - 次のStepボタンクリックを待機中")
                
                # 無限ループ待機（GUIイベント処理を継続）
                while self.state.mode == ExecutionMode.PAUSED and not self.step_event.is_set():
                    time.sleep(0.01)  # 10ms間隔でチェック
        logger.debug("🔍 ステップ実行完了 - PAUSED mode に移行")
        
        # 🆕 v1.2.1: 30秒タイムアウト付き待機（無限ループ回避）
        self._wait_for_user_input_with_timeout()
    
    def _handle_continuous_mode(self) -> None:
        """連続実行モードでの処理"""
        if self.stop_requested.is_set():
            logger.info("⏹️ 停止リクエスト検出 - 即座に一時停止")
            with self._lock:
                self.state.mode = ExecutionMode.PAUSED
                self.state.is_running = False
                self.state.current_action = None
                self.state.last_transition = datetime.now()
                self.stop_requested.clear()
            print("⏸️ 連続実行が一時停止されました")
            return
        else:
            # アニメーション用sleep（CPU使用率最適化：0.05秒）
            sleep_time = max(self.state.sleep_interval, 0.05)
            
            # 連続実行中のGUI更新を強制実行
            self._force_gui_update_during_continuous()
            
            time.sleep(sleep_time)
    
    def _handle_pause_pending_mode(self) -> None:
        """一時停止待機モードでの処理"""
        # PauseControllerが境界での一時停止実行を判定
        if self.pause_controller.should_pause_at_boundary(has_boundary=True):
            logger.info("⏸️ 一時停止待機 - アクション境界で停止実行")
            
            # 一時停止を実行
            pause_executed = self.pause_controller.execute_pause_at_boundary()
            
            if pause_executed:
                with self._lock:
                    # StateTransitionManagerで安全な遷移
                    transition_result = self.state_transition_manager.transition_to(
                        ExecutionMode.PAUSED,
                        "pause_boundary_executed"
                    )
                    
                    if transition_result.success:
                        self.state.mode = ExecutionMode.PAUSED
                        self.state.is_running = False
                        self.state.current_action = None
                        self.state.last_transition = datetime.now()
                        self.state.pause_pending = False
                        self.stop_requested.set()  # 実行停止フラグをセット
                        self.pause_event.clear()  # pause_eventをクリア
                        
                logger.info("⏸️ アクション境界で一時停止しました")
                print("⏸️ アクション境界で一時停止しました")
                
                # 一時停止後は通常の待機ループに戻る
                return
            else:
                logger.warning("⚠️ 一時停止実行に失敗しました")
        else:
            # 境界でない場合は継続
            time.sleep(0.01)  # 短時間待機
    
    def _wait_for_user_input_with_timeout(self) -> None:
        """🆕 v1.2.1: タイムアウト付きユーザー入力待機"""
        timeout_seconds = 30.0
        start_time = time.time()
        
        while self.state.mode == ExecutionMode.PAUSED:
            # タイムアウトチェック
            if time.time() - start_time > timeout_seconds:
                logger.warning("⚠️ ステップ実行待機タイムアウト - デッドロック防止のため継続")
                break
                
            # step_eventが設定されるまで短時間待機
            if self.step_event.wait(timeout=0.1):
                break
                
            # 停止要求または連続実行モードがあれば終了
            if self.state.mode == ExecutionMode.CONTINUOUS or self.stop_requested.is_set():
                return
    
    def _safe_state_recovery(self) -> None:
        """エラー発生時の安全な状態復旧"""
        with self._lock:
            self.state.mode = ExecutionMode.PAUSED
            self.state.is_running = False
            self.state.current_action = None
            self.state.error_state = "recovered_from_error"
            self.state.last_transition = datetime.now()
            self.pending_action = False
            self.action_completed = True
        logger.info("🔄 エラー回復: 安全なPAUSED状態に復帰")
    
    def _wait_for_gui_or_console(self) -> None:
        """GUI/コンソール環境判別待機処理"""
        try:
            import pygame
            if pygame.get_init():
                # GUI環境：短時間待機でメインループに制御を返す
                self._wait_for_gui_main_loop()
            else:
                # コンソール環境：従来の待機処理
                self._wait_for_user_action()
        except ImportError:
            # pygameなし：コンソール待機
            self._wait_for_user_action()
    
    def _wait_for_gui_main_loop(self) -> None:
        """GUI環境での軽量待機処理（メインループ協調）"""
        print("⏸️ 一時停止中 - 次のアクションを待機中")
        print("💡 GUI操作: Stepボタン または スペースキーで次へ")
        
        # ステップモードでは真のユーザー操作まで待機
        while True:
            # step_eventが既にセットされている場合はすぐに抜ける
            if self.step_event.is_set():
                break
                
            # 100msごとにチェック
            if self.step_event.wait(timeout=0.1):
                break
                
            # 停止要求または連続実行モードがあれば終了
            if self.state.mode == ExecutionMode.CONTINUOUS or self.stop_requested.is_set():
                return
                
            # ステップモードでは継続待機（タイムアウトを削除）
            # ユーザーが明示的にStepボタンを押すかキー操作するまで無限待機
            
    def _force_gui_update_during_continuous(self) -> None:
        """連続実行中の強制GUI更新
        
        Continueボタン使用時にステップごとのGUI描画を確保します。
        """
        try:
            # APIレイヤーからrendererにアクセス
            from . import api
            if hasattr(api, '_global_api') and api._global_api and api._global_api.renderer:
                renderer = api._global_api.renderer
                game_manager = api._global_api.game_manager
                
                if renderer and game_manager:
                    # 現在の状態を取得してレンダリング実行
                    game_state = game_manager.get_current_state()
                    renderer.render_frame(game_state)
                    renderer.update_display()
                    
        except Exception as e:
            # GUI更新エラーは無視（連続実行を継続）
            pass
    
    def mark_solve_complete(self) -> None:
        """solve()実行完了の標記"""
        with self._lock:
            self.state.mode = ExecutionMode.COMPLETED
            self.state.is_running = False
            
        logger.info("🏁 solve()の実行が完了しました")
        print("✅ solve()関数の実行が完了しました")
        print("📊 実行完了 - 結果を確認してください")
        print("💡 Exitボタンまたは×ボタンで終了してください")
        
        # 実行完了後はGUIイベント待機のみ（一時停止処理をスキップ）
        # _wait_for_user_action()を呼ばずにGUI制御をメインループに委ねる
    
    def set_action_callback(self, callback: Callable[[str], Any]) -> None:
        """アクション実行時のコールバック設定"""
        self.action_callback = callback
    
    def get_execution_state(self) -> ExecutionState:
        """現在の実行状態取得"""
        return self.state
    
    def get_detailed_state(self) -> ExecutionStateDetail:
        """🆕 v1.2.1: 詳細な実行状態の取得"""
        with self._lock:
            return ExecutionStateDetail(
                mode=self.state.mode,
                step_count=self.state.step_count,
                is_running=self.state.is_running,
                current_action=self.state.current_action,
                pause_pending=self.state.pause_pending,
                last_transition=self.state.last_transition,
                error_state=self.state.error_state
            )
    
    def is_action_boundary(self) -> bool:
        """🆕 v1.2.1: アクション境界の検出"""
        with self._lock:
            return self.action_completed or self.state.mode in [ExecutionMode.PAUSED, ExecutionMode.PAUSE_PENDING]
    
    def _wait_for_user_action(self) -> None:
        """ユーザーアクション待機"""
        logger.debug("ユーザーアクション待機中...")
        print("⏸️ 一時停止中 - 次のアクションを待機中")
        print("   ステップ実行: スペースキー または ステップボタン")
        print("   連続実行: Enterキー または 連続実行ボタン")
        print("   停止: Escキー または 停止ボタン")
        
        # キーボード入力とGUIイベントを監視
        try:
            import pygame
            self._wait_for_pygame_input()
        except ImportError:
            # pygameが無い場合は簡易的な入力待機
            self._wait_for_console_input()
    
    def _wait_for_pygame_input(self) -> None:
        """pygame環境での入力待機"""
        import pygame
        import time
        
        # pygameが初期化されているかチェック
        if not pygame.get_init():
            self._wait_for_console_input()
            return
            
        print("💡 GUI操作: Stepボタン または スペースキーで次へ")
        
        # 安全な待機制限を追加（最大30秒）
        start_time = time.time()
        max_wait_time = 30.0
        
        # step_eventが設定されるまで待機（レンダラーがイベント処理してフラグ設定）
        # イベント競合を避けるため、ExecutionControllerはイベント処理しない
        while not self.step_event.wait(timeout=0.1):
            # 安全制限チェック
            if time.time() - start_time > max_wait_time:
                logger.warning("⚠️ 待機タイムアウト - デッドロック防止のため継続")
                break
                
            # 停止要求または連続実行モードがあれば終了
            if self.state.mode == ExecutionMode.CONTINUOUS or self.stop_requested.is_set():
                return
    
    def _wait_for_console_input(self) -> None:
        """コンソール環境での入力待機"""
        print("キーを入力してください: [Space]ステップ実行 [Enter]連続実行 [q]停止")
        
        while True:
            try:
                import sys, tty, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    key = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    
                if key == ' ':
                    print("\n🔍 ステップ実行を開始")
                    break
                elif key == '\r':
                    print("\n▶️ 連続実行を開始")
                    self.continuous_execution()
                    break
                elif key == 'q':
                    print("\n⏹️ 実行を停止")
                    self.stop_execution()
                    break
                    
            except (ImportError, OSError):
                # Windows環境やttyが使えない場合のフォールバック
                user_input = input("入力してください [s]ステップ/[c]連続/[q]停止: ").lower()
                if user_input == 's' or user_input == '':
                    print("🔍 ステップ実行を開始")
                    break
                elif user_input == 'c':
                    print("▶️ 連続実行を開始")
                    self.continuous_execution()
                    break
                elif user_input == 'q':
                    print("⏹️ 実行を停止")
                    self.stop_execution()
                    break
    
    def reset(self) -> None:
        """🆕 v1.2.1: 実行制御状態のリセット（拡張フィールド対応）"""
        with self._lock:
            self.state = ExecutionState()
            self.pause_event.clear()
            self.step_event.clear() 
            self.stop_requested.clear()
            
            # 🆕 v1.2.1: 新規フラグのリセット
            self.pending_action = False
            self.action_completed = False
            self.action_start_time = None
            
        logger.debug("実行制御状態をリセットしました（v1.2.1対応）")
    
    # 🆕 v1.2.1: 新規統合メソッド
    
    @with_error_handling("完全システムリセット")
    def full_system_reset(self):
        """🆕 v1.2.1: ResetManagerによる完全システムリセット"""
        logger.info("🔄 完全システムリセットを開始します")
        
        # GameManagerがある場合は追加でリセット
        try:
            from engine.api import _global_api
            
            # _global_apiが初期化されているかチェック
            if _global_api is None:
                logger.warning("⚠️ _global_api が初期化されていません")
            else:
                if hasattr(_global_api, 'game_manager') and _global_api.game_manager:
                    logger.debug("🔄 GameManager も含めてリセット")
                    
                    # GameManagerのリセットを実行
                    if hasattr(_global_api.game_manager, 'reset_game'):
                        _global_api.game_manager.reset_game()
                        logger.info("✅ GameManager.reset_game() 実行完了")
                    
                    # Rendererもリセット
                    if hasattr(_global_api, 'renderer') and _global_api.renderer:
                        if hasattr(_global_api.renderer, 'reset'):
                            _global_api.renderer.reset()
                            logger.info("✅ Renderer.reset() 実行完了")
                else:
                    logger.warning("⚠️ GameManager が _global_api に設定されていません")
                
        except ImportError:
            logger.warning("⚠️ engine.api のインポートに失敗しました")
        except Exception as e:
            logger.warning(f"⚠️ GameManager リセット中にエラー: {e}")
        
        reset_result = self.reset_manager.full_system_reset()
        
        if reset_result.success:
            logger.info("✅ 完全システムリセット成功")
        else:
            logger.error(f"❌ 完全システムリセット部分的失敗: {reset_result.errors}")
            
        return reset_result
    
    def request_pause_at_boundary(self) -> bool:
        """🆕 v1.2.1: 次アクション境界での一時停止要求（外部用）"""
        if self.state.mode == ExecutionMode.CONTINUOUS:
            self.pause_controller.request_pause_at_next_action("api")
            return True
        return False
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """🆕 v1.2.1: 包括的ステータス情報取得"""
        with self._lock:
            return {
                "execution_state": self.get_detailed_state().__dict__,
                "boundary_detector": self.action_boundary_detector.get_statistics(),
                "pause_controller": self.pause_controller.get_pause_status(),
                "state_manager": self.state_transition_manager.get_transition_statistics(),
                "reset_manager": self.reset_manager.get_reset_status(),
                "performance_metrics": {
                    "pause_response": self.pause_controller.get_performance_metrics(),
                    "reset_performance": self.reset_manager.get_performance_metrics()
                }
            }
    
    def validate_system_consistency(self) -> bool:
        """🆕 v1.2.1: システム整合性検証"""
        try:
            # 各コンポーネントの整合性をチェック
            state_valid = self.state_transition_manager.validate_state_consistency()
            boundary_valid = self.action_boundary_detector.is_action_boundary()
            reset_valid = self.reset_manager.validate_reset_completion() if self.reset_manager.reset_history else True
            
            overall_valid = state_valid and reset_valid
            
            if not overall_valid:
                logger.warning("⚠️ システム整合性検証に問題があります")
            
            return overall_valid
            
        except Exception as e:
            logger.error(f"❌ システム整合性検証エラー: {e}")
            return False