"""
🆕 v1.2.1: リセット管理システム
ResetManager - 包括的システムリセット、コンポーネント管理、検証機能
"""

import threading
import logging
import gc
from typing import Optional, List, Dict, Any, Protocol
from datetime import datetime

from . import ExecutionMode, ResetResult, ResetOperationError

logger = logging.getLogger(__name__)

class Resettable(Protocol):
    """リセット可能なコンポーネントのプロトコル"""
    def reset(self) -> None:
        """コンポーネントをリセット"""
        pass

class ResetManager:
    """包括的システムリセット管理クラス"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.components: Dict[str, Resettable] = {}
        self.reset_history: List[ResetResult] = []
        self.last_reset_time: Optional[datetime] = None
        
        logger.debug("ResetManager初期化完了")
    
    def register_component(self, name: str, component: Resettable) -> None:
        """リセット対象コンポーネントの登録"""
        with self._lock:
            self.components[name] = component
            logger.debug(f"🔧 リセット対象コンポーネント登録: {name}")
    
    def unregister_component(self, name: str) -> bool:
        """リセット対象コンポーネントの登録解除"""
        with self._lock:
            if name in self.components:
                del self.components[name]
                logger.debug(f"🔧 リセット対象コンポーネント登録解除: {name}")
                return True
            return False
    
    def full_system_reset(self) -> ResetResult:
        """🆕 v1.2.1: 包括的システムリセット"""
        start_time = datetime.now()
        components_reset = []
        errors = []
        
        try:
            with self._lock:
                logger.info("🔄 完全システムリセット開始")
                
                # 各コンポーネントのリセット実行
                for component_name, component in self.components.items():
                    try:
                        logger.debug(f"🔄 {component_name} リセット中...")
                        component.reset()
                        components_reset.append(component_name)
                        logger.debug(f"✅ {component_name} リセット完了")
                    except Exception as e:
                        error_msg = f"{component_name} リセットエラー: {e}"
                        errors.append(error_msg)
                        logger.error(f"❌ {error_msg}")
                
                # メモリクリーンアップ実行
                self._perform_memory_cleanup()
                
                # リセット結果の作成
                end_time = datetime.now()
                execution_time_ms = (end_time - start_time).total_seconds() * 1000
                
                result = ResetResult(
                    success=len(errors) == 0,
                    reset_timestamp=end_time,
                    components_reset=components_reset,
                    errors=errors
                )
                
                # リセット履歴に追加
                self.reset_history.append(result)
                self.last_reset_time = end_time
                
                # 履歴サイズ制限（最新50件まで保持）
                if len(self.reset_history) > 50:
                    self.reset_history = self.reset_history[-50:]
                
                logger.info(f"🔄 システムリセット完了 ({execution_time_ms:.2f}ms)")
                
                # NFR-001.3: 200ms以内の要件チェック
                if execution_time_ms > 200.0:
                    logger.warning(f"⚠️ リセット時間要件違反: {execution_time_ms:.2f}ms > 200ms")
                
                return result
                
        except Exception as e:
            error_msg = f"システムリセット重大エラー: {e}"
            logger.critical(f"🚨 {error_msg}")
            
            return ResetResult(
                success=False,
                reset_timestamp=datetime.now(),
                components_reset=components_reset,
                errors=errors + [error_msg]
            )
    
    def reset_execution_controller(self, execution_controller) -> None:
        """ExecutionController固有のリセット処理"""
        try:
            if execution_controller:
                execution_controller.reset()
                logger.debug("✅ ExecutionController リセット完了")
        except Exception as e:
            logger.error(f"❌ ExecutionController リセットエラー: {e}")
            raise ResetOperationError(f"ExecutionControllerのリセットに失敗: {e}")
    
    def reset_game_manager(self, game_manager) -> None:
        """GameManager固有のリセット処理"""
        try:
            if game_manager and hasattr(game_manager, 'reset_game'):
                game_manager.reset_game()
                logger.debug("✅ GameManager リセット完了")
        except Exception as e:
            logger.error(f"❌ GameManager リセットエラー: {e}")
            raise ResetOperationError(f"GameManagerのリセットに失敗: {e}")
    
    def reset_session_logs(self, session_log_manager) -> None:
        """セッションログのリセット処理"""
        try:
            if session_log_manager and hasattr(session_log_manager, 'reset_session'):
                session_log_manager.reset_session()
                logger.debug("✅ SessionLogManager リセット完了")
        except Exception as e:
            logger.error(f"❌ SessionLogManager リセットエラー: {e}")
            raise ResetOperationError(f"SessionLogManagerのリセットに失敗: {e}")
    
    def _perform_memory_cleanup(self) -> None:
        """メモリクリーンアップ実行"""
        try:
            # Python ガベージコレクションを実行
            collected = gc.collect()
            logger.debug(f"🧹 メモリクリーンアップ: {collected}個のオブジェクトを回収")
        except Exception as e:
            logger.warning(f"⚠️ メモリクリーンアップエラー: {e}")
    
    def validate_reset_completion(self) -> bool:
        """リセット完了の検証"""
        with self._lock:
            if not self.reset_history:
                return False
            
            last_reset = self.reset_history[-1]
            
            # 最新のリセットが成功したかチェック
            if not last_reset.success:
                logger.warning("⚠️ 最新のリセットが失敗しています")
                return False
            
            # 全てのコンポーネントがリセットされたかチェック  
            expected_components = set(self.components.keys())
            reset_components = set(last_reset.components_reset)
            
            if not expected_components.issubset(reset_components):
                missing = expected_components - reset_components
                logger.warning(f"⚠️ リセットされていないコンポーネント: {missing}")
                return False
            
            logger.debug("✅ リセット完了の検証に合格")
            return True
    
    def get_reset_status(self) -> Dict[str, Any]:
        """リセット状況の詳細取得"""
        with self._lock:
            status = {
                "registered_components": list(self.components.keys()),
                "component_count": len(self.components),
                "last_reset_time": self.last_reset_time,
                "reset_history_count": len(self.reset_history)
            }
            
            if self.reset_history:
                last_reset = self.reset_history[-1]
                status.update({
                    "last_reset_success": last_reset.success,
                    "last_reset_components": last_reset.components_reset,
                    "last_reset_errors": last_reset.errors
                })
            
            return status
    
    def get_reset_history(self, limit: int = 10) -> List[ResetResult]:
        """リセット履歴を取得"""
        with self._lock:
            return self.reset_history[-limit:] if limit > 0 else self.reset_history.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """リセット性能メトリクス取得"""
        with self._lock:
            if not self.reset_history:
                return {"no_reset_history": True}
            
            # 最近のリセット性能を分析
            recent_resets = self.reset_history[-10:]
            reset_times = []
            
            for i in range(1, len(recent_resets)):
                if recent_resets[i-1].reset_timestamp and recent_resets[i].reset_timestamp:
                    time_diff = (recent_resets[i].reset_timestamp - recent_resets[i-1].reset_timestamp).total_seconds() * 1000
                    reset_times.append(time_diff)
            
            metrics = {
                "total_resets": len(self.reset_history),
                "successful_resets": sum(1 for r in self.reset_history if r.success),
                "recent_reset_count": len(recent_resets)
            }
            
            if reset_times:
                metrics.update({
                    "avg_reset_time_ms": sum(reset_times) / len(reset_times),
                    "max_reset_time_ms": max(reset_times),
                    "min_reset_time_ms": min(reset_times)
                })
            
            return metrics
    
    def emergency_reset(self) -> ResetResult:
        """緊急リセット（エラー回復用）"""
        logger.warning("🚨 緊急リセット実行中...")
        
        try:
            # 通常のfull_system_reset()を試行
            result = self.full_system_reset()
            
            if result.success:
                logger.info("✅ 緊急リセット成功")
                return result
            else:
                logger.error("❌ 緊急リセット部分的失敗")
                return result
                
        except Exception as e:
            logger.critical(f"🚨 緊急リセット致命的失敗: {e}")
            
            # 最小限のフォールバックリセット
            return ResetResult(
                success=False,
                reset_timestamp=datetime.now(),
                components_reset=[],
                errors=[f"緊急リセット致命的失敗: {e}"]
            )
    
    def clear_reset_history(self) -> None:
        """リセット履歴のクリア"""
        with self._lock:
            self.reset_history.clear()
            logger.debug("🔄 リセット履歴をクリアしました")
    
    def __str__(self) -> str:
        """文字列表現"""
        with self._lock:
            return f"ResetManager(components={len(self.components)}, history={len(self.reset_history)})"