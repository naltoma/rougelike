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
        
        # step実行カウンター（連続API呼び出し防止用）
        self.current_step_actions_allowed = 0
        
        # step実行許可トークン（スレッドセーフ）
        self.step_execution_token = threading.Event()
        
        # step実行中フラグ（無限ループ検出無効化用）
        self.is_step_execution_active = False
        
        # 初期状態は一時停止
        self.pause_event.clear()
        self.step_event.clear()
        self.stop_requested.clear()
        self.current_step_actions_allowed = 0
        self.step_execution_token.clear()
        
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
                    # Reset後は新しいsolve()実行を許可
                    if not hasattr(self, '_solve_thread_started'):
                        logger.info("🔄 Reset後のStep実行: 新しいsolve()を開始します")
                        self.state.mode = ExecutionMode.STEPPING  # COMPLETED→STEPPINGに遷移
                        self.state.is_running = False  # solve()スレッド開始前
                    else:
                        return StepResult(
                            success=False,
                            action_executed="already_completed",
                            new_state=ExecutionMode.COMPLETED,
                            execution_time_ms=0.0,
                            actions_executed=0
                        )
                
                # 🔧 連続実行中はSTEPPINGに変更しない
                if self.state.mode != ExecutionMode.CONTINUOUS:
                    # PAUSED状態からSTEPPINGに遷移する場合、古いフラグを必ずリセット
                    if self.state.mode == ExecutionMode.PAUSED:
                        self.single_step_requested = False
                        logger.debug("🔍 PAUSED→STEPPING遷移: 古いフラグリセット")
                    self.state.mode = ExecutionMode.STEPPING
                
                # ステップフラグをセット - solve()実行を1アクション分許可
                self.single_step_requested = True
                
                # 新しいstep要求時は1アクション分許可
                self.current_step_actions_allowed = 1
                
                # step実行トークンをセット（1アクションのみ許可）
                self.step_execution_token.set()
                
                # step実行中フラグをセット
                self.is_step_execution_active = True
                
                self.state.step_count += 1
                
                # ステップ実行許可（solve()の次の1アクションを実行させる）
                self.step_event.set()
                
                # solve()実行中でない場合は、solve()実行を開始する必要がある
                if not self.state.is_running:
                    self.state.is_running = True
                    logger.info("🚀 solve()実行を開始（ステップモード）")
                
                # solve()スレッドが開始されていない場合は、強制的にフラグを削除してGUIループで開始させる
                if hasattr(self, '_solve_thread_started'):
                    logger.debug("🔍 solve()スレッド既存確認済み")
                else:
                    logger.info("🚀 solve()スレッド開始準備完了")
                
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
                # Reset後は新しいsolve()実行を許可
                if not hasattr(self, '_solve_thread_started'):
                    logger.info("🔄 Reset後のContinue実行: 新しいsolve()を開始します")
                    self.state.mode = ExecutionMode.CONTINUOUS  # COMPLETED→CONTINUOUSに遷移
                    self.state.is_running = False  # solve()スレッド開始前
                else:
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
            
            # solve()スレッドが開始されていない場合の準備
            if hasattr(self, '_solve_thread_started'):
                logger.debug("🔍 solve()スレッド既存確認済み（連続実行）")
            else:
                logger.info("🚀 solve()スレッド開始準備完了（連続実行）")
            
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
                # 一時停止では停止要求は設定しない（メインループ継続のため）
                logger.info("⏸️ 実行を即座に一時停止しました")
    
    def stop_execution(self) -> None:
        """実行停止"""
        with self._lock:
            self.stop_requested.set()
            self.state.is_running = False
            
        logger.info("⏹️ 実行停止がリクエストされました")
    
    def wait_for_action(self) -> None:
        """アクション待機処理"""
        # 停止要求の優先チェック
        if self.stop_requested.is_set():
            logger.debug("🔍 停止要求検出 - solve()スレッド終了")
            import threading
            current_thread = threading.current_thread()
            if current_thread is not threading.main_thread():
                # バックグラウンドスレッドの場合は例外を発生させて終了
                logger.info(f"🔄 solve()スレッド {current_thread.name} を停止要求により終了")
                raise RuntimeError("solve() execution stopped by reset")
            else:
                logger.info("🔍 停止要求をメインスレッドで検出 - 処理継続")
            return
            
        current_mode = self.state.mode
        
        # ログ出力でデバッグ
        import threading
        thread_name = threading.current_thread().name
        logger.info(f"🔍 wait_for_action呼び出し: mode={current_mode}, step_req={self.single_step_requested}, pause_req={self.pause_requested}, thread={thread_name}")
        
        if current_mode == ExecutionMode.STEPPING:
            # ステップモードではトークンベース制御
            if self.step_execution_token.is_set():
                # トークンを即座にクリア（1回限りの使用）
                with self._lock:
                    self.step_execution_token.clear()
                    self.current_step_actions_allowed -= 1
                    # アクション数が0になったらPAUSEDに遷移（フラグはAPI完了後にクリア）
                    if self.current_step_actions_allowed <= 0:
                        self.state.mode = ExecutionMode.PAUSED
                        self.single_step_requested = False
                        # is_step_execution_activeはAPI実行完了後にクリアする
                logger.info(f"🔍 ステップモード: トークン使用→1APIコール許可 (actions_allowed={self.current_step_actions_allowed})")
                return  # APIコール実行を許可
            else:
                # トークンがない場合は待機（solve()スレッドを継続）
                logger.debug("🔍 ステップモード: トークンなし→待機開始")
                while not self.step_execution_token.is_set() and self.state.mode == ExecutionMode.STEPPING:
                    time.sleep(0.001)  # CPU負荷軽減（1ms間隔）
                    # 停止要求チェック
                    if self.stop_requested.is_set():
                        logger.debug("🔍 ステップモード待機中: 停止要求検出")
                        break
                    # モード変更チェック
                    if self.state.mode != ExecutionMode.STEPPING:
                        break
                logger.debug("🔍 ステップモード: 待機終了")
                # 待機後、再帰的にwait_for_action()を呼び出して再チェック
                self.wait_for_action()
                return
        elif current_mode == ExecutionMode.CONTINUOUS:
            self._handle_continuous_mode()
        elif current_mode == ExecutionMode.PAUSED:
            # PAUSED状態では長時間待機（solve()スレッドを継続）
            logger.info(f"🔍 PAUSED状態: 実行再開待機中 (thread={thread_name})")
            while self.state.mode == ExecutionMode.PAUSED and not self.step_execution_token.is_set():
                time.sleep(0.01)  # 10ms間隔でチェック（応答性向上）
                # 停止要求チェック
                if self.stop_requested.is_set():
                    logger.debug("🔍 PAUSED状態待機中: 停止要求検出")
                    break
                # モード変更チェック（Resume等）
                if self.state.mode != ExecutionMode.PAUSED:
                    break
                # step実行トークンがセットされたらループを抜ける
                if self.step_execution_token.is_set():
                    break
            # 待機後、再帰的にwait_for_action()を呼び出して再チェック
            self.wait_for_action()
            return
        elif self.stop_requested.is_set():
            self._handle_stop_request()
        else:
            # その他の状態では短時間待機（停止要求チェック付き）
            logger.debug(f"wait_for_action: 状態 {current_mode} で待機中")
            start_wait = time.time()
            while time.time() - start_wait < 0.01:
                if self.stop_requested.is_set():
                    logger.debug("🔍 その他状態での停止要求検出")
                    break
                time.sleep(0.001)
    
    def _handle_stepping_mode(self) -> None:
        """ステップモード処理（ネストループ対応版）"""
        # single_step_requestedフラグがセットされている場合のみ実行を許可
        if self.single_step_requested:
            logger.debug("🔍 ステップモード: 1アクション実行を許可")
            # フラグはAPI実行完了後にクリアする（ここではクリアしない）
            return  # APIアクションの実行を許可
        else:
            # フラグがセットされていない場合は待機
            # ネストループの場合、内側のループが完了するまでこの状態が続く
            logger.debug("🔍 ステップモード: 次のステップ要求を待機中")
            while not self.single_step_requested and self.state.mode == ExecutionMode.STEPPING:
                time.sleep(0.001)  # CPU負荷軽減（1ms間隔）
                # 停止要求チェック
                if self.stop_requested.is_set():
                    break
                # プログラム終了チェック
                if self.state.mode != ExecutionMode.STEPPING:
                    break
            return
    
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
        # ただし、バックグラウンドスレッドからは呼び出さない（メインスレッドエラー回避）
        import threading
        if threading.current_thread() is threading.main_thread():
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
    
    def _terminate_solve_threads(self) -> None:
        """solve()スレッドを完全に停止してリセット"""
        import threading
        import time
        
        # 現在のスレッド一覧を取得
        active_threads = threading.enumerate()
        solve_threads = [t for t in active_threads if t.name.startswith('Thread-') and t != threading.main_thread()]
        
        logger.info(f"🔄 アクティブなsolve()スレッド数: {len(solve_threads)}")
        
        # まず停止要求を設定（実行中のsolve()に停止シグナルを送信）
        self.stop_requested.set()
        
        # solve()スレッドが停止するまで少し待機
        max_wait_time = 1.0  # 1秒まで待機
        start_wait = time.time()
        
        while solve_threads and (time.time() - start_wait < max_wait_time):
            # 生きているsolve()スレッドの確認
            alive_threads = [t for t in solve_threads if t.is_alive()]
            if not alive_threads:
                break
            
            logger.info(f"🔄 solve()スレッド停止待機中: {len(alive_threads)}個のスレッドが実行中")
            time.sleep(0.1)  # 100ms待機
            
            # スレッドリストを更新
            active_threads = threading.enumerate()
            solve_threads = [t for t in active_threads if t.name.startswith('Thread-') and t != threading.main_thread()]
        
        # 最終確認
        final_threads = [t for t in solve_threads if t.is_alive()]
        if final_threads:
            logger.warning(f"⚠️ {len(final_threads)}個のsolve()スレッドが停止しませんでした")
            for thread in final_threads:
                logger.warning(f"⚠️ 未停止スレッド: {thread.name}, alive={thread.is_alive()}")
            
            # 強制的に継続処理（デーモンスレッドなのでプロセス終了時に自動終了される）
            logger.warning("⚠️ デーモンスレッドとして継続実行されますが、新しいsolve()実行は可能です")
        else:
            logger.info("✅ 全てのsolve()スレッドが停止しました")
        
        # solve()スレッド状態フラグは呼び出し元でリセットされる（重複削除を避ける）
        # if hasattr(self, '_solve_thread_started'):
        #     delattr(self, '_solve_thread_started')
        #     logger.info("🔄 _solve_thread_started フラグを削除")
            
        # APIの実行状態もリセット
        from engine.api import _global_api
        if _global_api and hasattr(_global_api, 'call_history'):
            _global_api.call_history.clear()
            logger.info("🔄 API呼び出し履歴をクリア")
            
        # action_trackerもリセット（API実行カウンターをリセット）
        if _global_api and hasattr(_global_api, 'action_tracker') and _global_api.action_tracker:
            _global_api.action_tracker.reset_counter()
            logger.info("🔄 ActionTrackerもリセット")
            
        # reset完了後に停止要求をクリア（新しいsolve()実行のため）
        self.stop_requested.clear()
        logger.info("🔄 スレッド終了処理完了、新しいsolve()実行準備完了")
        
        logger.info("🔄 solve()スレッド状態をリセットしました")

    def full_system_reset(self):
        """完全システムリセット"""
        logger.info("🔄 完全システムリセットを開始します")
        start_time = datetime.now()
        
        try:
            with self._lock:
                # Speed設定を保持
                current_sleep_interval = self.state.sleep_interval if self.state else 1.0
                
                # solve()スレッドの停止要求を先に設定
                self.stop_requested.set()
                
                # ExecutionController状態リセット（Speed設定除く）
                self.state = ExecutionState()
                self.state.sleep_interval = current_sleep_interval  # Speed設定を復元
                self.state.mode = ExecutionMode.PAUSED  # 明示的にPAUSED状態にリセット
                self.state.is_running = False  # 実行停止状態をクリア
                self.single_step_requested = False
                self.pause_requested = False
                self.pause_event.clear()
                self.step_event.clear()
                self.current_step_actions_allowed = 0
                self.step_execution_token.clear()
                self.is_step_execution_active = False
                
                logger.info(f"🔄 ExecutionState リセット完了: mode={self.state.mode}, running={self.state.is_running}")
                
                # 少し待ってから停止要求をクリア（solve()スレッドが停止するまで）
                import time
                time.sleep(0.1)
                
                # solve()スレッド完全停止とリセット
                self._terminate_solve_threads()
                
                # solve()完了状態をリセット（重要：新しいsolve()実行を可能にする）
                if hasattr(self, '_solve_thread_started'):
                    delattr(self, '_solve_thread_started')
                    logger.info("🔄 _solve_thread_started フラグを強制削除（再実行許可）")
                
                logger.info(f"🔄 Speed設定を保持: sleep_interval={current_sleep_interval}秒")
            
            # GameManagerリセット
            try:
                from engine.api import _global_api
                if _global_api and hasattr(_global_api, 'game_manager') and _global_api.game_manager:
                    _global_api.game_manager.reset_game()
                    logger.info("✅ GameManager.reset_game() 実行完了")
                    
                    # Reset後の状態確認
                    current_state = _global_api.game_manager.get_current_state()
                    if current_state is None:
                        logger.warning("⚠️ Reset後: current_state が None")
                    else:
                        state_type = type(current_state).__name__
                        logger.info(f"🔍 Reset後の状態: {state_type}")
                        if hasattr(current_state, 'player'):
                            logger.info(f"🔍 Reset後のプレイヤー: HP={current_state.player.hp}")
                        else:
                            logger.error(f"🚨 Reset後: current_state に player 属性がありません")
                    
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
    
    def mark_step_api_complete(self) -> None:
        """単一ステップのAPI実行完了マーク"""
        with self._lock:
            logger.info(f"🔍 mark_step_api_complete呼び出し: current_flag={self.is_step_execution_active}")
            if self.is_step_execution_active:
                self.is_step_execution_active = False
                logger.info("🔍 step API実行完了: フラグクリア完了")
            else:
                logger.info("🔍 step API実行完了: フラグ既にFalse")
    
    def mark_solve_complete(self) -> None:
        """solve()完了マーク"""
        with self._lock:
            self.state.mode = ExecutionMode.COMPLETED
            self.state.is_running = False
            self.is_step_execution_active = False
            
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