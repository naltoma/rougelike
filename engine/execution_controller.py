"""
🆕 v1.2.1: シンプル版 ExecutionController
複雑なコンポーネント統合ではなく、直接的なボタン制御を実装
"""

import threading
import time
import logging
from typing import Optional
from datetime import datetime

from . import ExecutionMode, ExecutionState, StepResult

logger = logging.getLogger(__name__)


class ExecutionController:
    """シンプル版実行制御管理クラス"""
    
    def __init__(self, game_api=None):
        self.game_api = game_api
        self.state = ExecutionState()
        self.pause_event = threading.Event()
        self.step_event = threading.Event()
        self.stop_requested = threading.Event()
        self._lock = threading.Lock()
        
        # シンプルな制御フラグ
        self.single_step_requested = False
        self.pause_requested = False
        
        # 初期状態は一時停止
        self.pause_event.clear()
        self.step_event.clear()
        self.stop_requested.clear()
        
        logger.debug("ExecutionController (シンプル版) 初期化完了")
    
    def pause_before_solve(self) -> None:
        """solve()実行直前で自動的に停止"""
        with self._lock:
            self.state.mode = ExecutionMode.PAUSED
            self.state.is_running = False
            self.pause_event.clear()
            self.step_event.clear()
            self.stop_requested.clear()
            
            # リセット後の初期化
            self.single_step_requested = False
            self.pause_requested = False
            
        logger.info("🔄 solve()実行前で一時停止しました")
    
    def step_execution(self) -> StepResult:
        """単一ステップ実行"""
        start_time = datetime.now()
        
        try:
            with self._lock:
                if self.state.mode == ExecutionMode.COMPLETED:
                    return StepResult(
                        success=False,
                        action_executed="already_completed",
                        new_state=ExecutionMode.COMPLETED,
                        execution_time_ms=0.0,
                        actions_executed=0
                    )
                
                # ステップフラグをセット - solve()実行を1アクション分許可
                self.single_step_requested = True
                
                # 🔧 連続実行中はSTEPPINGに変更しない
                if self.state.mode != ExecutionMode.CONTINUOUS:
                    self.state.mode = ExecutionMode.STEPPING
                
                self.state.step_count += 1
                
                # ステップ実行許可（solve()の次の1アクションを実行させる）
                self.step_event.set()
                
                # solve()実行中でない場合は、solve()実行を開始する必要がある
                if not self.state.is_running:
                    self.state.is_running = True
                    logger.info("🚀 solve()実行を開始（ステップモード）")
                
            logger.info(f"✅ ステップ実行要求 #{self.state.step_count}")
            
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return StepResult(
                success=True,
                action_executed="step_requested", 
                new_state=ExecutionMode.STEPPING,
                execution_time_ms=execution_time_ms,
                actions_executed=1
            )
            
        except Exception as e:
            logger.error(f"❌ ステップ実行エラー: {e}")
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return StepResult(
                success=False,
                action_executed="error",
                new_state=ExecutionMode.ERROR,
                execution_time_ms=execution_time_ms,
                actions_executed=0,
                error_message=str(e)
            )
    
    def continuous_execution(self, sleep_interval: float = None) -> None:
        """連続実行開始"""
        with self._lock:
            if self.state.mode == ExecutionMode.COMPLETED:
                logger.info("✅ solve()の実行が既に完了しています")
                return
                
            self.state.mode = ExecutionMode.CONTINUOUS
            
            # sleep_intervalが指定されていない場合は現在の値を保持
            if sleep_interval is not None:
                self.state.sleep_interval = sleep_interval
            # 現在のsleep_intervalが未設定の場合のみデフォルト値を使用
            elif not hasattr(self.state, 'sleep_interval') or self.state.sleep_interval is None:
                self.state.sleep_interval = 1.0
                
            self.state.is_running = True
            self.pause_event.set()
            self.pause_requested = False
            
            # 初回ステップ実行要求を送信
            self.single_step_requested = True
            
        logger.info(f"🚀 まとめて実行開始（速度: {self.state.sleep_interval}秒間隔）")
    
    def update_sleep_interval_realtime(self, new_interval: float) -> None:
        """🚀 v1.2.5: リアルタイムsleep間隔更新"""
        with self._lock:
            old_interval = self.state.sleep_interval
            self.state.sleep_interval = new_interval
            logger.info(f"⚡ ExecutionController sleep_interval更新: {old_interval}→{new_interval}秒")
    
    def pause_execution(self) -> None:
        """実行を一時停止"""
        with self._lock:
            current_mode = self.state.mode
            
            if current_mode == ExecutionMode.CONTINUOUS:
                # 連続実行中の一時停止要求 - 即座に状態変更
                self.pause_requested = False  # フラグをリセット（処理完了）
                self.state.mode = ExecutionMode.PAUSED
                self.state.is_running = False
                self.pause_event.clear()
                logger.info("⏸️ 連続実行を次のアクション境界で一時停止しました")
            else:
                # 即座に一時停止
                self.state.mode = ExecutionMode.PAUSED
                self.state.is_running = False
                self.pause_event.clear()
                self.stop_requested.set()
                logger.info("⏸️ 実行を即座に一時停止しました")
    
    def stop_execution(self) -> None:
        """実行停止"""
        with self._lock:
            self.stop_requested.set()
            self.state.is_running = False
            
        logger.info("⏹️ 実行停止がリクエストされました")
    
    def wait_for_action(self) -> None:
        """アクション待機処理"""
        current_mode = self.state.mode
        
        # ログ出力でデバッグ
        logger.debug(f"wait_for_action呼び出し: mode={current_mode}, step_req={self.single_step_requested}, pause_req={self.pause_requested}")
        
        if current_mode == ExecutionMode.STEPPING:
            self._handle_stepping_mode()
        elif current_mode == ExecutionMode.CONTINUOUS:
            self._handle_continuous_mode()
        elif self.stop_requested.is_set():
            self._handle_stop_request()
        else:
            # その他の状態（PAUSED等）では待機
            logger.debug(f"wait_for_action: 状態 {current_mode} で待機中")
            time.sleep(0.01)
    
    def _handle_stepping_mode(self) -> None:
        """ステップモード処理（ハードコーディング方式対応）"""
        # 🚫 GUIループでのハードコーディング制御のため、wait_for_action()は何もしない
        logger.debug("🔍 ステップモード: GUIループでハードコーディング実行中")
        return  # 即座に戻る
    
    def _handle_continuous_mode(self) -> None:
        """連続実行モード処理（v1.2.5: 7段階速度対応）"""
        if self.pause_requested or self.stop_requested.is_set():
            # 一時停止要求の処理
            with self._lock:
                self.state.mode = ExecutionMode.PAUSED
                self.state.is_running = False
                self.pause_event.clear()
                self.stop_requested.clear()
                self.pause_requested = False
                
            logger.info("⏸️ アクション境界で一時停止しました")
            return
        
        # v1.2.5: 7段階速度対応の高精度スリープ
        sleep_time = max(self.state.sleep_interval, 0.001)  # 最小1ms（x50対応）
        
        # 超高速モード（x10, x50）の高精度制御
        if hasattr(self, '_ultra_high_speed_controller') and self._ultra_high_speed_controller:
            if sleep_time <= 0.05:  # x10以上の場合
                # 高精度スリープを使用
                tolerance_ms = 1.0 if sleep_time <= 0.001 else 5.0
                try:
                    self._ultra_high_speed_controller.ultra_precise_sleep(sleep_time, tolerance_ms)
                except Exception as e:
                    logger.warning(f"⚠️ 高精度スリープ失敗、標準スリープを使用: {e}")
                    time.sleep(sleep_time)
            else:
                time.sleep(sleep_time)
        else:
            time.sleep(sleep_time)
        
        # GUI応答性確保のため、定期的にpygameイベントをチェック
        import pygame
        try:
            pygame.event.pump()  # イベントキューを処理
        except:
            pass  # pygame初期化前はスキップ
    
    def _handle_stop_request(self) -> None:
        """停止要求処理"""
        with self._lock:
            self.state.mode = ExecutionMode.PAUSED
            self.state.is_running = False
            self.stop_requested.clear()
            
        logger.info("⏹️ 停止要求により一時停止しました")
    
    def full_system_reset(self):
        """完全システムリセット"""
        logger.info("🔄 完全システムリセットを開始します")
        start_time = datetime.now()
        
        try:
            with self._lock:
                # ExecutionController状態リセット
                self.state = ExecutionState()
                self.single_step_requested = False
                self.pause_requested = False
                self.pause_event.clear()
                self.step_event.clear()
                self.stop_requested.clear()
            
            # GameManagerリセット
            try:
                from engine.api import _global_api
                if _global_api and hasattr(_global_api, 'game_manager') and _global_api.game_manager:
                    _global_api.game_manager.reset_game()
                    logger.info("✅ GameManager.reset_game() 実行完了")
                    
                    # ActionHistoryTrackerリセット
                    if hasattr(_global_api, 'action_tracker') and _global_api.action_tracker:
                        _global_api.action_tracker.reset_counter()
                        logger.info("✅ ActionHistoryTracker.reset_counter() 実行完了")
                    
                    # レンダラー強制更新
                    if hasattr(_global_api, 'renderer') and _global_api.renderer:
                        # 画面を強制更新
                        if hasattr(_global_api.renderer, 'force_update'):
                            _global_api.renderer.force_update()
                        elif hasattr(_global_api.renderer, 'render_frame'):
                            # 現在の状態で再描画
                            current_state = _global_api.game_manager.get_current_state()
                            _global_api.renderer.render_frame(current_state)
                            _global_api.renderer.update_display()
                        logger.info("✅ GUI画面更新完了")
                        
            except Exception as e:
                logger.warning(f"⚠️ GameManager/Renderer リセット中にエラー: {e}")
            
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # 簡単なリセット結果を返す
            from . import ResetResult
            result = ResetResult(
                success=True,
                reset_timestamp=datetime.now(),
                components_reset=['execution_controller', 'game_manager', 'renderer'],
                errors=[]
            )
            
            logger.info("✅ 完全システムリセット成功")
            return result
            
        except Exception as e:
            logger.error(f"❌ システムリセットエラー: {e}")
            
            from . import ResetResult
            return ResetResult(
                success=False,
                reset_timestamp=datetime.now(),
                components_reset=[],
                errors=[str(e)]
            )
    
    def is_execution_complete(self) -> bool:
        """実行完了確認"""
        return self.state.mode == ExecutionMode.COMPLETED
    
    def mark_solve_complete(self) -> None:
        """solve()完了マーク"""
        with self._lock:
            self.state.mode = ExecutionMode.COMPLETED
            self.state.is_running = False
            
        logger.info("🏁 solve()の実行が完了しました")
    
    def get_detailed_state(self):
        """詳細状態取得"""
        return self.state
    
    # v1.2.5: 7段階速度制御統合メソッド
    def setup_7stage_speed_control(self, speed_control_manager, ultra_controller):
        """
        7段階速度制御システム統合
        
        Args:
            speed_control_manager: Enhanced7StageSpeedControlManager
            ultra_controller: UltraHighSpeedController
        """
        self._7stage_speed_manager = speed_control_manager
        self._ultra_high_speed_controller = ultra_controller
        logger.info("✅ 7段階速度制御システム統合完了")
    
    def update_sleep_interval_realtime(self, new_interval: float) -> bool:
        """
        実行中のスリープ間隔リアルタイム更新
        
        Args:
            new_interval: 新しいスリープ間隔
            
        Returns:
            bool: 更新成功フラグ
        """
        try:
            with self._lock:
                old_interval = self.state.sleep_interval
                self.state.sleep_interval = new_interval
                
            logger.info(f"⚡ スリープ間隔リアルタイム更新: {old_interval}s → {new_interval}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ スリープ間隔更新エラー: {e}")
            return False
    
    def get_7stage_speed_metrics_for_logging(self) -> dict:
        """
        セッションログ用7段階速度メトリクス取得
        
        Returns:
            dict: 速度メトリクス
        """
        if hasattr(self, '_7stage_speed_manager') and self._7stage_speed_manager:
            try:
                metrics = self._7stage_speed_manager.get_7stage_speed_metrics()
                return {
                    'current_speed_multiplier': self._7stage_speed_manager.get_current_speed_multiplier(),
                    'speed_changes_count': len(metrics.speed_changes),
                    'max_speed_used': metrics.max_speed_used,
                    'average_speed': metrics.average_speed_multiplier,
                    'realtime_changes': metrics.realtime_changes_count,
                    'ultra_speed_usage': metrics.ultra_high_speed_usage
                }
            except Exception as e:
                logger.error(f"❌ 7段階速度メトリクス取得エラー: {e}")
                return {}
        
        return {
            'current_speed_multiplier': 1,
            'speed_changes_count': 0,
            'max_speed_used': 1,
            'average_speed': 1.0,
            'realtime_changes': 0,
            'ultra_speed_usage': {}
        }
    
    def sync_speed_with_state_7stage(self) -> None:
        """ExecutionStateと7段階速度設定の同期"""
        if hasattr(self, '_7stage_speed_manager') and self._7stage_speed_manager:
            try:
                config = self._7stage_speed_manager.get_speed_configuration()
                self.state.sleep_interval = config.sleep_interval
                logger.debug(f"🔄 速度同期: x{config.current_multiplier} ({config.sleep_interval}s)")
            except Exception as e:
                logger.error(f"❌ 速度同期エラー: {e}")
    
    def handle_ultra_high_speed_execution(self, interval: float) -> bool:
        """
        超高速実行専用処理
        
        Args:
            interval: 実行間隔
            
        Returns:
            bool: 処理成功フラグ
        """
        if not hasattr(self, '_ultra_high_speed_controller') or not self._ultra_high_speed_controller:
            return False
            
        try:
            # 超高速モード有効化
            if interval <= 0.1:  # x10以上の場合
                success = self._ultra_high_speed_controller.enable_ultra_high_speed_mode(interval)
                if success:
                    logger.info(f"🏃‍♂️ 超高速実行モード開始: {interval}s")
                return success
            else:
                # 超高速モード無効化
                if self._ultra_high_speed_controller.ultra_high_speed_active:
                    self._ultra_high_speed_controller.ultra_high_speed_active = False
                    logger.info("🚶‍♂️ 標準速度モードに切替")
                return True
                
        except Exception as e:
            logger.error(f"❌ 超高速実行処理エラー: {e}")
            return False
    
    def get_ultra_speed_stability_info(self) -> dict:
        """超高速実行安定性情報取得"""
        if hasattr(self, '_ultra_high_speed_controller') and self._ultra_high_speed_controller:
            return self._ultra_high_speed_controller.monitor_ultra_speed_stability()
        return {'status': 'not_available'}
    
    # 互換性のための追加メソッド
    def pause_at_next_action_boundary(self):
        """次アクション境界での一時停止要求（互換性）"""
        self.pause_execution()
        return {"requester": "user"}
    
    def reset_system(self):
        """システムリセット（互換性）"""
        return self.full_system_reset()