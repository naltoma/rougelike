"""
アクション履歴追跡システム
ActionHistoryTracker - 実行順序付きアクション操作の記録と表示
"""

import threading
import logging
from collections import deque
from datetime import datetime
from typing import Optional, Dict, Any, List

from . import ActionHistoryEntry

logger = logging.getLogger(__name__)

class ActionTrackingError(Exception):
    """アクション履歴追跡エラー"""
    pass

class ActionHistoryTracker:
    """アクション履歴追跡クラス"""
    
    def __init__(self, max_history: int = 1000):
        self.history: deque = deque(maxlen=max_history)
        self.action_counter: int = 0
        self._lock = threading.Lock()
        self.enabled = True
        
        logger.debug(f"ActionHistoryTracker初期化完了（最大履歴: {max_history}）")
    
    def track_action(self, action_name: str, execution_result: Optional[Any] = None) -> None:
        """アクション履歴記録"""
        if not self.enabled:
            return
            
        try:
            with self._lock:
                self.action_counter += 1
                entry = ActionHistoryEntry(
                    sequence=self.action_counter,
                    action_name=action_name,
                    timestamp=datetime.now(),
                    execution_result=execution_result
                )
                self.history.append(entry)
                
            # ターミナルに履歴出力（要求仕様3.2の「N: function_name()」形式）
            print(f"{self.action_counter}: {action_name}()")
            
            logger.debug(f"アクション記録: {entry}")
            
        except Exception as e:
            logger.error(f"アクション履歴記録中にエラー: {e}")
            raise ActionTrackingError(f"アクション履歴の記録に失敗しました: {e}")
    
    def display_action_history(self, last_n: Optional[int] = None) -> None:
        """履歴表示（「N: function_name()」形式）"""
        try:
            with self._lock:
                history_to_show = list(self.history)
                
            if not history_to_show:
                print("📋 アクション履歴: なし")
                return
                
            if last_n is not None:
                history_to_show = history_to_show[-last_n:]
                
            print("📋 アクション履歴:")
            for entry in history_to_show:
                timestamp_str = entry.timestamp.strftime("%H:%M:%S")
                print(f"  {entry.sequence}: {entry.action_name}() [{timestamp_str}]")
                
            logger.debug(f"アクション履歴表示完了（{len(history_to_show)}件）")
            
        except Exception as e:
            logger.error(f"アクション履歴表示中にエラー: {e}")
            raise ActionTrackingError(f"アクション履歴の表示に失敗しました: {e}")
    
    def reset_counter(self) -> None:
        """アクション履歴のカウンターリセット"""
        try:
            with self._lock:
                self.action_counter = 0
                self.history.clear()
                
            logger.debug("アクション履歴カウンターリセット完了")
            
        except Exception as e:
            logger.error(f"カウンターリセット中にエラー: {e}")
            raise ActionTrackingError(f"アクション履歴のリセットに失敗しました: {e}")
    
    def get_action_count(self) -> int:
        """実行回数取得"""
        with self._lock:
            return self.action_counter
    
    def get_last_action(self) -> Optional[ActionHistoryEntry]:
        """最新のアクションを取得"""
        with self._lock:
            if self.history:
                return self.history[-1]
            return None
    
    def get_history_summary(self) -> Dict[str, Any]:
        """履歴サマリーの取得"""
        with self._lock:
            action_counts = {}
            for entry in self.history:
                action_name = entry.action_name
                action_counts[action_name] = action_counts.get(action_name, 0) + 1
                
            return {
                "total_actions": self.action_counter,
                "unique_actions": len(action_counts),
                "action_breakdown": action_counts,
                "history_size": len(self.history),
                "last_action": str(self.get_last_action()) if self.history else None
            }
    
    def enable_tracking(self) -> None:
        """履歴追跡を有効化"""
        self.enabled = True
        logger.debug("アクション履歴追跡を有効化")
    
    def disable_tracking(self) -> None:
        """履歴追跡を無効化"""
        self.enabled = False
        logger.debug("アクション履歴追跡を無効化")
    
    def is_tracking_enabled(self) -> bool:
        """履歴追跡の有効性確認"""
        return self.enabled
    
    def export_history(self) -> List[Dict[str, Any]]:
        """履歴をエクスポート（JSON形式）"""
        try:
            with self._lock:
                exported_data = []
                for entry in self.history:
                    exported_data.append({
                        "sequence": entry.sequence,
                        "action_name": entry.action_name,
                        "timestamp": entry.timestamp.isoformat(),
                        "execution_result": str(entry.execution_result) if entry.execution_result else None
                    })
                    
            logger.debug(f"履歴エクスポート完了（{len(exported_data)}件）")
            return exported_data
            
        except Exception as e:
            logger.error(f"履歴エクスポート中にエラー: {e}")
            raise ActionTrackingError(f"履歴のエクスポートに失敗しました: {e}")