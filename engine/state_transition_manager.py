"""
🆕 v1.2.1: 状態遷移管理システム
StateTransitionManager - 安全な状態遷移、妥当性検証、ロールバック機能
"""

import threading
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from . import ExecutionMode, StateTransitionError

logger = logging.getLogger(__name__)

@dataclass
class TransitionRecord:
    """状態遷移記録"""
    from_state: ExecutionMode
    to_state: ExecutionMode
    transition_time: datetime
    reason: str
    success: bool
    rollback_state: Optional[ExecutionMode] = None

class StateTransitionManager:
    """状態遷移管理クラス"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.current_state = ExecutionMode.PAUSED
        self.previous_state: Optional[ExecutionMode] = None
        self.transition_history: List[TransitionRecord] = []
        self.transition_matrix = self._build_transition_matrix()
        
        logger.debug("StateTransitionManager初期化完了")
    
    def _build_transition_matrix(self) -> Dict[ExecutionMode, List[ExecutionMode]]:
        """状態遷移妥当性マトリックスを構築"""
        return {
            ExecutionMode.PAUSED: [
                ExecutionMode.STEPPING,
                ExecutionMode.CONTINUOUS, 
                ExecutionMode.PAUSE_PENDING,
                ExecutionMode.RESET,
                ExecutionMode.COMPLETED,
                ExecutionMode.ERROR
            ],
            ExecutionMode.STEPPING: [
                ExecutionMode.STEP_EXECUTING,
                ExecutionMode.PAUSED,
                ExecutionMode.CONTINUOUS,
                ExecutionMode.RESET,
                ExecutionMode.ERROR
            ],
            ExecutionMode.STEP_EXECUTING: [
                ExecutionMode.PAUSED,
                ExecutionMode.STEPPING,
                ExecutionMode.RESET,
                ExecutionMode.ERROR
            ],
            ExecutionMode.CONTINUOUS: [
                ExecutionMode.PAUSE_PENDING,
                ExecutionMode.PAUSED,
                ExecutionMode.COMPLETED,
                ExecutionMode.RESET,
                ExecutionMode.ERROR
            ],
            ExecutionMode.PAUSE_PENDING: [
                ExecutionMode.PAUSED,
                ExecutionMode.RESET,
                ExecutionMode.ERROR
            ],
            ExecutionMode.COMPLETED: [
                ExecutionMode.RESET,
                ExecutionMode.PAUSED,
                ExecutionMode.ERROR
            ],
            ExecutionMode.RESET: [
                ExecutionMode.PAUSED,
                ExecutionMode.ERROR
            ],
            ExecutionMode.ERROR: [
                ExecutionMode.PAUSED,
                ExecutionMode.RESET
            ]
        }
    
    def transition_to(self, target_state: ExecutionMode, reason: str = "") -> 'TransitionResult':
        """安全な状態遷移"""
        try:
            with self._lock:
                from_state = self.current_state
                
                # 状態遷移の妥当性を検証
                if not self._validate_transition(from_state, target_state):
                    error_msg = f"無効な状態遷移: {from_state.value} → {target_state.value}"
                    logger.error(f"❌ {error_msg}")
                    
                    # 失敗記録を追加
                    self._record_transition(from_state, target_state, reason, success=False)
                    
                    return TransitionResult(
                        success=False,
                        from_state=from_state,
                        to_state=target_state,
                        error_message=error_msg
                    )
                
                # 状態遷移を実行
                self.previous_state = from_state
                self.current_state = target_state
                
                # 成功記録を追加
                self._record_transition(from_state, target_state, reason, success=True)
                
                logger.debug(f"✅ 状態遷移成功: {from_state.value} → {target_state.value} ({reason})")
                
                return TransitionResult(
                    success=True,
                    from_state=from_state,
                    to_state=target_state,
                    transition_time=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"❌ 状態遷移例外: {e}")
            raise StateTransitionError(f"状態遷移に失敗しました: {e}")
    
    def validate_transition(self, from_state: ExecutionMode, to_state: ExecutionMode) -> bool:
        """状態遷移の妥当性検証（外部用）"""
        return self._validate_transition(from_state, to_state)
    
    def _validate_transition(self, from_state: ExecutionMode, to_state: ExecutionMode) -> bool:
        """状態遷移の妥当性検証（内部用）"""
        if from_state == to_state:
            return True  # 同じ状態への遷移は常に有効
        
        allowed_states = self.transition_matrix.get(from_state, [])
        return to_state in allowed_states
    
    def rollback_transition(self) -> bool:
        """状態遷移のロールバック"""
        try:
            with self._lock:
                if self.previous_state is None:
                    logger.warning("⚠️ ロールバック対象の前の状態が存在しません")
                    return False
                
                rollback_target = self.previous_state
                current_state = self.current_state
                
                # ロールバック用の遷移妥当性確認
                if not self._validate_transition(current_state, rollback_target):
                    logger.error(f"❌ ロールバック不可: {current_state.value} → {rollback_target.value}")
                    return False
                
                # ロールバック実行
                self.current_state = rollback_target
                self.previous_state = None
                
                # ロールバック記録を追加
                self._record_transition(
                    current_state, 
                    rollback_target, 
                    "rollback", 
                    success=True
                )
                
                logger.info(f"🔄 状態ロールバック成功: {current_state.value} → {rollback_target.value}")
                return True
                
        except Exception as e:
            logger.error(f"❌ ロールバックエラー: {e}")
            raise StateTransitionError(f"状態ロールバックに失敗しました: {e}")
    
    def get_current_state(self) -> ExecutionMode:
        """現在の状態を取得"""
        with self._lock:
            return self.current_state
    
    def get_transition_history(self, limit: int = 20) -> List[TransitionRecord]:
        """状態遷移履歴を取得"""
        with self._lock:
            return self.transition_history[-limit:] if limit > 0 else self.transition_history.copy()
    
    def _record_transition(self, from_state: ExecutionMode, to_state: ExecutionMode, 
                          reason: str, success: bool) -> None:
        """状態遷移記録を追加"""
        record = TransitionRecord(
            from_state=from_state,
            to_state=to_state,
            transition_time=datetime.now(),
            reason=reason,
            success=success
        )
        
        self.transition_history.append(record)
        
        # 履歴サイズ制限（最新100件まで保持）
        if len(self.transition_history) > 100:
            self.transition_history = self.transition_history[-100:]
    
    def get_allowed_transitions(self, from_state: Optional[ExecutionMode] = None) -> List[ExecutionMode]:
        """指定状態から遷移可能な状態リストを取得"""
        with self._lock:
            state = from_state or self.current_state
            return self.transition_matrix.get(state, []).copy()
    
    def get_transition_statistics(self) -> Dict[str, Any]:
        """遷移統計情報を取得"""
        with self._lock:
            total_transitions = len(self.transition_history)
            successful_transitions = sum(1 for r in self.transition_history if r.success)
            
            return {
                "current_state": self.current_state.value,
                "previous_state": self.previous_state.value if self.previous_state else None,
                "total_transitions": total_transitions,
                "successful_transitions": successful_transitions,
                "success_rate": successful_transitions / total_transitions if total_transitions > 0 else 1.0,
                "history_size": len(self.transition_history)
            }
    
    def reset(self) -> None:
        """StateTransitionManagerの完全リセット"""
        with self._lock:
            self.current_state = ExecutionMode.PAUSED
            self.previous_state = None
            self.transition_history.clear()
            
        logger.debug("🔄 StateTransitionManagerをリセットしました")
    
    def clear_history(self) -> None:
        """遷移履歴のクリア"""
        with self._lock:
            self.transition_history.clear()
            logger.debug("🔄 状態遷移履歴をクリアしました")
    
    def validate_state_consistency(self) -> bool:
        """状態の整合性を検証"""
        with self._lock:
            # 現在の状態が有効なExecutionModeかチェック
            if not isinstance(self.current_state, ExecutionMode):
                logger.error("❌ 現在の状態が無効です")
                return False
            
            # 前の状態がある場合は妥当性をチェック
            if self.previous_state and not isinstance(self.previous_state, ExecutionMode):
                logger.error("❌ 前の状態が無効です")
                return False
            
            return True
    
    def __str__(self) -> str:
        """文字列表現"""
        with self._lock:
            return f"StateTransitionManager(current={self.current_state.value}, transitions={len(self.transition_history)})"

@dataclass
class TransitionResult:
    """状態遷移結果"""
    success: bool
    from_state: ExecutionMode
    to_state: ExecutionMode
    transition_time: Optional[datetime] = None
    error_message: Optional[str] = None