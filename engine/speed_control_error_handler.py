"""
🚀 v1.2.5: Speed Control Error Handler
7段階速度制御エラーハンドラー
自動復旧機能とユーザー向け通知システムを提供
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta

from .enhanced_7stage_speed_errors import (
    Enhanced7StageSpeedControlError,
    InvalidSpeedMultiplierError,
    UltraHighSpeedError,
    HighPrecisionTimingError,
    RealTimeSpeedChangeError,
    ExecutionSyncError,
    SpeedDegradationError,
    handle_speed_control_error,
    _global_error_tracker
)

logger = logging.getLogger(__name__)


class SpeedControlErrorHandler:
    """
    7段階速度制御エラーハンドラー
    
    エラーの検出、分類、自動復旧、ユーザー通知を統合管理
    """
    
    def __init__(self, speed_manager=None, ultra_controller=None, 
                 execution_controller=None, gui_renderer=None):
        """
        初期化
        
        Args:
            speed_manager: Enhanced7StageSpeedControlManager
            ultra_controller: UltraHighSpeedController
            execution_controller: ExecutionController
            gui_renderer: GuiRenderer（ユーザー通知用）
        """
        self.speed_manager = speed_manager
        self.ultra_controller = ultra_controller
        self.execution_controller = execution_controller
        self.gui_renderer = gui_renderer
        
        # エラー処理設定
        self.auto_recovery_enabled = True
        self.user_notification_enabled = True
        self.max_consecutive_errors = 5
        self.error_cooldown_seconds = 30
        
        # エラー状態管理
        self.consecutive_error_count = 0
        self.last_error_time = None
        self.recent_error_types = []
        self.recovery_history = []
        
        # 通知コールバック
        self.notification_callbacks = []
        
        logger.info("✅ SpeedControlErrorHandler 初期化完了")
    
    def handle_error(self, error: Exception, context: str = "unknown") -> Dict[str, Any]:
        """
        エラー処理メイン関数
        
        Args:
            error: 発生したエラー
            context: エラー発生コンテキスト
            
        Returns:
            dict: 処理結果
        """
        try:
            # 7段階速度制御エラーかどうか判定
            if not isinstance(error, Enhanced7StageSpeedControlError):
                # 一般的なエラーを7段階速度制御エラーに変換を試行
                converted_error = self._try_convert_to_speed_error(error, context)
                if not converted_error:
                    return self._handle_non_speed_error(error, context)
                error = converted_error
            
            # エラー統計記録
            _global_error_tracker.record_error(error)
            
            # 連続エラー管理
            self._update_consecutive_error_count(error)
            
            # クールダウンチェック
            if self._is_in_error_cooldown():
                logger.info("エラークールダウン中、処理をスキップ")
                return {'handled': False, 'reason': 'cooldown'}
            
            # 自動復旧処理
            recovery_result = self._attempt_automatic_recovery(error)
            
            # ユーザー通知
            self._notify_user(error, recovery_result)
            
            # 処理結果返却
            result = {
                'handled': True,
                'error_type': error.__class__.__name__,
                'recovery_applied': recovery_result.get('recovery_applied', False),
                'new_speed': recovery_result.get('new_speed_multiplier'),
                'user_notified': self.user_notification_enabled,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"エラー処理完了: {error.__class__.__name__} in {context}")
            return result
            
        except Exception as handler_error:
            logger.error(f"エラーハンドラー内でエラー発生: {handler_error}")
            return {'handled': False, 'error': str(handler_error)}
    
    def _try_convert_to_speed_error(self, error: Exception, context: str) -> Optional[Enhanced7StageSpeedControlError]:
        """一般エラーを7段階速度制御エラーに変換を試行"""
        error_msg = str(error)
        
        # ValueError with speed multiplier
        if isinstance(error, ValueError) and ("speed" in error_msg.lower() or "multiplier" in error_msg.lower()):
            return InvalidSpeedMultiplierError(0, [1, 2, 3, 4, 5, 10, 50])
        
        # TimeoutError or performance issues
        if isinstance(error, (TimeoutError, OSError)):
            return UltraHighSpeedError(50, f"システム性能問題: {error_msg}")
        
        # RuntimeError in execution
        if isinstance(error, RuntimeError) and "execution" in error_msg.lower():
            return ExecutionSyncError("execution_flow", "normal", "error")
        
        return None
    
    def _handle_non_speed_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """7段階速度制御以外のエラー処理"""
        logger.info(f"非速度制御エラーをスキップ: {error.__class__.__name__} in {context}")
        return {'handled': False, 'reason': 'not_speed_control_error'}
    
    def _update_consecutive_error_count(self, error: Enhanced7StageSpeedControlError):
        """連続エラーカウント更新"""
        now = datetime.now()
        
        # 前回エラーから十分時間が経過した場合はリセット
        if (self.last_error_time and 
            now - self.last_error_time > timedelta(minutes=5)):
            self.consecutive_error_count = 0
            self.recent_error_types = []
        
        self.consecutive_error_count += 1
        self.last_error_time = now
        self.recent_error_types.append(error.__class__.__name__)
        
        # 最新10件に制限
        if len(self.recent_error_types) > 10:
            self.recent_error_types = self.recent_error_types[-10:]
        
        # 連続エラー警告
        if self.consecutive_error_count >= self.max_consecutive_errors:
            logger.warning(f"連続エラー警告: {self.consecutive_error_count}回連続")
    
    def _is_in_error_cooldown(self) -> bool:
        """エラークールダウン中かチェック"""
        if not self.last_error_time:
            return False
        
        cooldown_end = self.last_error_time + timedelta(seconds=self.error_cooldown_seconds)
        return datetime.now() < cooldown_end
    
    def _attempt_automatic_recovery(self, error: Enhanced7StageSpeedControlError) -> Dict[str, Any]:
        """自動復旧処理"""
        if not self.auto_recovery_enabled:
            return {'recovery_applied': False, 'reason': 'auto_recovery_disabled'}
        
        # 連続エラー多すぎる場合は復旧を停止
        if self.consecutive_error_count > self.max_consecutive_errors:
            logger.warning("連続エラー過多により自動復旧を停止")
            return {'recovery_applied': False, 'reason': 'too_many_errors'}
        
        # 標準エラー復旧処理
        recovery_result = handle_speed_control_error(error, self.speed_manager)
        
        # 復旧履歴記録
        if recovery_result.get('recovery_applied'):
            self.recovery_history.append({
                'error_type': error.__class__.__name__,
                'timestamp': datetime.now(),
                'recovery_action': f"speed changed to x{recovery_result.get('new_speed_multiplier', 'unknown')}",
                'success': True
            })
            
            # ExecutionControllerと同期
            if self.execution_controller and recovery_result.get('new_speed_multiplier'):
                try:
                    self.execution_controller.sync_speed_with_state_7stage()
                except Exception as sync_error:
                    logger.error(f"ExecutionController同期エラー: {sync_error}")
        
        # 復旧履歴を最新20件に制限
        if len(self.recovery_history) > 20:
            self.recovery_history = self.recovery_history[-20:]
        
        return recovery_result
    
    def _notify_user(self, error: Enhanced7StageSpeedControlError, recovery_result: Dict[str, Any]):
        """ユーザー通知"""
        if not self.user_notification_enabled:
            return
        
        try:
            # GUI通知（レンダラー経由）
            if self.gui_renderer:
                self._notify_via_gui(error, recovery_result)
            
            # コールバック通知
            self._notify_via_callbacks(error, recovery_result)
            
            # コンソール通知
            self._notify_via_console(error, recovery_result)
            
        except Exception as notification_error:
            logger.error(f"ユーザー通知エラー: {notification_error}")
    
    def _notify_via_gui(self, error: Enhanced7StageSpeedControlError, recovery_result: Dict[str, Any]):
        """GUI経由の通知"""
        if hasattr(self.gui_renderer, 'show_speed_error_notification'):
            message = error.get_user_friendly_message()
            if recovery_result.get('recovery_applied'):
                message += f"\n\n✅ 自動復旧: x{recovery_result.get('new_speed_multiplier')}に変更しました"
            
            self.gui_renderer.show_speed_error_notification(message)
    
    def _notify_via_callbacks(self, error: Enhanced7StageSpeedControlError, recovery_result: Dict[str, Any]):
        """コールバック経由の通知"""
        for callback in self.notification_callbacks:
            try:
                callback({
                    'error': error,
                    'recovery_result': recovery_result,
                    'timestamp': datetime.now()
                })
            except Exception as callback_error:
                logger.error(f"通知コールバックエラー: {callback_error}")
    
    def _notify_via_console(self, error: Enhanced7StageSpeedControlError, recovery_result: Dict[str, Any]):
        """コンソール経由の通知"""
        print(f"\n{error.get_user_friendly_message()}")
        
        if recovery_result.get('recovery_applied'):
            new_speed = recovery_result.get('new_speed_multiplier')
            print(f"✅ 自動復旧完了: 速度をx{new_speed}に変更しました")
        
        print()  # 空行
    
    def add_notification_callback(self, callback: Callable):
        """通知コールバック追加"""
        self.notification_callbacks.append(callback)
        logger.debug("通知コールバック追加")
    
    def enable_auto_recovery(self, enabled: bool = True):
        """自動復旧有効/無効設定"""
        self.auto_recovery_enabled = enabled
        logger.info(f"自動復旧: {'有効' if enabled else '無効'}")
    
    def enable_user_notification(self, enabled: bool = True):
        """ユーザー通知有効/無効設定"""
        self.user_notification_enabled = enabled
        logger.info(f"ユーザー通知: {'有効' if enabled else '無効'}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計取得"""
        global_stats = _global_error_tracker.get_error_statistics()
        
        handler_stats = {
            'consecutive_errors': self.consecutive_error_count,
            'recent_error_types': self.recent_error_types,
            'recovery_count': len(self.recovery_history),
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None,
            'auto_recovery_enabled': self.auto_recovery_enabled,
            'user_notification_enabled': self.user_notification_enabled
        }
        
        return {
            'global_statistics': global_stats,
            'handler_statistics': handler_stats,
            'recovery_history': self.recovery_history[-10:]  # 最新10件
        }
    
    def reset_error_state(self):
        """エラー状態リセット"""
        self.consecutive_error_count = 0
        self.last_error_time = None
        self.recent_error_types = []
        logger.info("エラー状態リセット完了")
    
    def create_test_errors(self) -> List[Enhanced7StageSpeedControlError]:
        """テスト用エラー作成（開発・テスト用）"""
        test_errors = [
            InvalidSpeedMultiplierError(15),
            UltraHighSpeedError(50, "高負荷による精度低下"),
            HighPrecisionTimingError(20.0, 8.2, 5.0, 50),
            RealTimeSpeedChangeError(50, 10, "システム負荷過多"),
            ExecutionSyncError("sleep_interval", "0.02", "0.05"),
            SpeedDegradationError(50, 5, "連続精度失敗", 8)
        ]
        return test_errors


# デコレーター関数

def handle_speed_control_errors(error_handler: SpeedControlErrorHandler):
    """
    7段階速度制御エラーハンドリングデコレーター
    
    Usage:
        @handle_speed_control_errors(my_error_handler)
        def some_speed_control_function():
            # 速度制御処理
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = f"{func.__name__}()"
                error_handler.handle_error(e, context)
                raise  # 必要に応じて再発生
        return wrapper
    return decorator


# 上位レベル管理クラス

class SpeedControlErrorManager:
    """7段階速度制御エラー管理の上位クラス"""
    
    def __init__(self):
        self.handlers = {}
        self.global_error_handler = None
        
    def create_error_handler(self, name: str, **kwargs) -> SpeedControlErrorHandler:
        """名前付きエラーハンドラー作成"""
        handler = SpeedControlErrorHandler(**kwargs)
        self.handlers[name] = handler
        logger.info(f"エラーハンドラー作成: {name}")
        return handler
    
    def get_handler(self, name: str) -> Optional[SpeedControlErrorHandler]:
        """名前付きエラーハンドラー取得"""
        return self.handlers.get(name)
    
    def set_global_handler(self, handler: SpeedControlErrorHandler):
        """グローバルエラーハンドラー設定"""
        self.global_error_handler = handler
        logger.info("グローバルエラーハンドラー設定完了")
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """全ハンドラーの統合統計"""
        all_stats = {}
        for name, handler in self.handlers.items():
            all_stats[name] = handler.get_error_statistics()
        
        return {
            'handlers': all_stats,
            'global_error_tracker': _global_error_tracker.get_error_statistics()
        }


# グローバルエラーマネージャー
_global_error_manager = SpeedControlErrorManager()