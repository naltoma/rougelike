"""
🆕 v1.2.1: 一時停止制御システム
PauseController - 次アクション境界での一時停止制御とPAUSE_PENDING状態管理
"""

import threading
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from . import ExecutionMode, PauseRequest, PauseControlError

logger = logging.getLogger(__name__)

class PauseController:
    """一時停止制御管理クラス"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.pause_request: Optional[PauseRequest] = None
        self.pause_pending = False
        self.last_pause_time: Optional[datetime] = None
        
        logger.debug("PauseController初期化完了")
    
    def request_pause_at_next_action(self, requester: str = "user") -> PauseRequest:
        """次のアクション境界での一時停止要求"""
        try:
            with self._lock:
                now = datetime.now()
                
                # 既存の一時停止要求をキャンセル
                if self.pause_request and not self.pause_request.fulfilled:
                    logger.debug("🔄 既存の一時停止要求をキャンセル")
                
                # 新しい一時停止要求を作成
                self.pause_request = PauseRequest(
                    requested_at=now,
                    requester=requester,
                    target_boundary="next_action",
                    fulfilled=False
                )
                
                self.pause_pending = True
                
                logger.info(f"⏸️ 次アクション境界での一時停止要求: {requester}")
                return self.pause_request
                
        except Exception as e:
            logger.error(f"❌ 一時停止要求エラー: {e}")
            raise PauseControlError(f"一時停止要求に失敗しました: {e}")
    
    def is_pause_pending(self) -> bool:
        """一時停止要求の確認"""
        with self._lock:
            return self.pause_pending and self.pause_request is not None and not self.pause_request.fulfilled
    
    def execute_pause_at_boundary(self) -> bool:
        """アクション境界での一時停止実行"""
        try:
            with self._lock:
                if not self.is_pause_pending():
                    return False
                
                # 一時停止要求を実行
                if self.pause_request:
                    self.pause_request.fulfilled = True
                
                self.pause_pending = False
                self.last_pause_time = datetime.now()
                
                logger.info("⏸️ アクション境界で一時停止を実行")
                return True
                
        except Exception as e:
            logger.error(f"❌ 一時停止実行エラー: {e}")
            raise PauseControlError(f"一時停止の実行に失敗しました: {e}")
    
    def cancel_pause_request(self) -> bool:
        """一時停止要求のキャンセル"""
        try:
            with self._lock:
                if self.pause_request and not self.pause_request.fulfilled:
                    self.pause_request.fulfilled = True
                    self.pause_pending = False
                    logger.debug("🚫 一時停止要求をキャンセルしました")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ 一時停止キャンセルエラー: {e}")
            raise PauseControlError(f"一時停止のキャンセルに失敗しました: {e}")
    
    def get_pause_status(self) -> Dict[str, Any]:
        """一時停止状態の詳細取得"""
        with self._lock:
            status = {
                "is_pending": self.pause_pending,
                "has_request": self.pause_request is not None,
                "last_pause_time": self.last_pause_time
            }
            
            if self.pause_request:
                status.update({
                    "requester": self.pause_request.requester,
                    "requested_at": self.pause_request.requested_at,
                    "target_boundary": self.pause_request.target_boundary,
                    "fulfilled": self.pause_request.fulfilled
                })
            
            return status
    
    def handle_continuous_mode_pause(self, execution_mode: ExecutionMode) -> ExecutionMode:
        """連続実行モードでの一時停止処理"""
        if execution_mode == ExecutionMode.CONTINUOUS and self.is_pause_pending():
            logger.info("⏸️ 連続実行中の一時停止要求検出 - PAUSE_PENDING mode に移行")
            return ExecutionMode.PAUSE_PENDING
        return execution_mode
    
    def should_pause_at_boundary(self, has_boundary: bool) -> bool:
        """アクション境界で一時停止すべきかの判定"""
        with self._lock:
            return self.pause_pending and has_boundary
    
    def get_pause_timing_info(self) -> Dict[str, Any]:
        """一時停止タイミング情報の取得"""
        with self._lock:
            timing_info = {
                "pending_pause": self.pause_pending,
                "target_timing": "next_action_boundary"
            }
            
            if self.pause_request:
                timing_info.update({
                    "request_age_ms": (datetime.now() - self.pause_request.requested_at).total_seconds() * 1000,
                    "target_boundary": self.pause_request.target_boundary
                })
            
            return timing_info
    
    def reset(self) -> None:
        """PauseControllerの完全リセット"""
        with self._lock:
            self.pause_request = None
            self.pause_pending = False
            self.last_pause_time = None
            
        logger.debug("🔄 PauseControllerをリセットしました")
    
    def validate_pause_response_time(self, max_response_ms: float = 50.0) -> bool:
        """一時停止応答時間の検証（NFR-001.1: 50ms以内）"""
        with self._lock:
            if not self.pause_request:
                return True
            
            response_time_ms = (datetime.now() - self.pause_request.requested_at).total_seconds() * 1000
            is_valid = response_time_ms <= max_response_ms
            
            if not is_valid:
                logger.warning(f"⚠️ 一時停止応答時間違反: {response_time_ms:.2f}ms > {max_response_ms}ms")
            
            return is_valid
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクス取得"""
        with self._lock:
            metrics = {
                "has_active_request": self.pause_request is not None,
                "pause_pending": self.pause_pending
            }
            
            if self.pause_request:
                age_ms = (datetime.now() - self.pause_request.requested_at).total_seconds() * 1000
                metrics.update({
                    "request_age_ms": age_ms,
                    "response_time_valid": age_ms <= 50.0
                })
            
            return metrics
    
    def __str__(self) -> str:
        """文字列表現"""
        with self._lock:
            status = "pending" if self.pause_pending else "idle"
            return f"PauseController(status={status}, has_request={self.pause_request is not None})"