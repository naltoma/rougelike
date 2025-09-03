"""
🆕 v1.2.1: アクション境界検出システム
ActionBoundaryDetector - APIコール境界の精密検出とアクション完了管理
"""

import threading
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from . import ActionBoundary, ExecutionMode

logger = logging.getLogger(__name__)

class ActionBoundaryDetector:
    """アクション境界検出管理クラス"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.current_boundary: Optional[ActionBoundary] = None
        self.boundary_history: List[ActionBoundary] = []
        self.sequence_counter = 0
        self.active_actions: Dict[str, datetime] = {}
        
        logger.debug("ActionBoundaryDetector初期化完了")
    
    def mark_action_start(self, action_name: str) -> ActionBoundary:
        """APIアクション開始時の境界マーキング"""
        with self._lock:
            self.sequence_counter += 1
            now = datetime.now()
            
            # 新しいアクション境界を作成
            boundary = ActionBoundary(
                boundary_type="api_call",
                action_name=action_name,
                timestamp=now,
                sequence_number=self.sequence_counter
            )
            
            # 境界情報を更新
            self.current_boundary = boundary
            self.active_actions[action_name] = now
            
            logger.debug(f"🔍 アクション開始境界: {action_name} (#{self.sequence_counter})")
            return boundary
    
    def mark_action_complete(self, action_name: str) -> bool:
        """APIアクション完了時の境界マーキング"""
        with self._lock:
            if action_name not in self.active_actions:
                logger.warning(f"⚠️ 未開始のアクション完了: {action_name}")
                return False
            
            # アクション完了処理
            del self.active_actions[action_name]
            
            if self.current_boundary and self.current_boundary.action_name == action_name:
                # 境界履歴に追加
                self.boundary_history.append(self.current_boundary)
                
                # 履歴サイズ制限（最新100件まで保持）
                if len(self.boundary_history) > 100:
                    self.boundary_history = self.boundary_history[-100:]
                
                self.current_boundary = None
                logger.debug(f"✅ アクション完了境界: {action_name}")
                return True
            
            return False
    
    def is_action_boundary(self) -> bool:
        """現在がアクション境界かどうかを判定"""
        with self._lock:
            # アクティブなアクションがない場合は境界
            return len(self.active_actions) == 0
    
    def get_current_boundary(self) -> Optional[ActionBoundary]:
        """現在のアクション境界情報を取得"""
        with self._lock:
            return self.current_boundary
    
    def get_next_boundary_info(self) -> Dict[str, Any]:
        """次のアクション境界に関する情報を取得"""
        with self._lock:
            return {
                "has_active_actions": len(self.active_actions) > 0,
                "active_action_names": list(self.active_actions.keys()),
                "next_sequence_number": self.sequence_counter + 1,
                "current_boundary": self.current_boundary
            }
    
    def get_boundary_history(self, limit: int = 10) -> List[ActionBoundary]:
        """アクション境界履歴を取得"""
        with self._lock:
            return self.boundary_history[-limit:] if limit > 0 else self.boundary_history.copy()
    
    def clear_history(self) -> None:
        """境界履歴をクリア"""
        with self._lock:
            self.boundary_history.clear()
            logger.debug("🔄 アクション境界履歴をクリアしました")
    
    def reset(self) -> None:
        """ActionBoundaryDetectorの完全リセット"""
        with self._lock:
            self.current_boundary = None
            self.boundary_history.clear()
            self.sequence_counter = 0
            self.active_actions.clear()
            
        logger.debug("🔄 ActionBoundaryDetectorをリセットしました")
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        with self._lock:
            return {
                "total_actions": len(self.boundary_history),
                "active_actions_count": len(self.active_actions),
                "sequence_counter": self.sequence_counter,
                "has_current_boundary": self.current_boundary is not None
            }
    
    def detect_api_calls(self, execution_mode: ExecutionMode) -> bool:
        """実行モードに基づいたAPIコール検出"""
        if execution_mode == ExecutionMode.STEPPING:
            # ステップモードでは厳密な境界検出
            return self.is_action_boundary()
        elif execution_mode == ExecutionMode.CONTINUOUS:
            # 連続実行モードでは境界検出を緩和
            return True
        elif execution_mode == ExecutionMode.PAUSE_PENDING:
            # 一時停止待機モードでは境界で停止
            return self.is_action_boundary()
        else:
            # その他のモードでは常に境界として扱う
            return True
    
    def __str__(self) -> str:
        """文字列表現"""
        with self._lock:
            return f"ActionBoundaryDetector(seq={self.sequence_counter}, active={len(self.active_actions)}, history={len(self.boundary_history)})"