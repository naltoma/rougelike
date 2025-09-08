"""
🚀 v1.2.5: Enhanced 7-Stage Speed Control Error Classes
7段階速度制御専用エラークラス体系
教育的エラーメッセージと適切な自動復旧機能を提供
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class Enhanced7StageSpeedControlError(Exception):
    """
    7段階速度制御関連エラー基底クラス
    
    全ての7段階速度制御関連エラーの基底となるクラス。
    教育的エラーメッセージと復旧提案機能を提供。
    """
    
    def __init__(self, message: str, error_code: str = None, recovery_suggestions: List[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.recovery_suggestions = recovery_suggestions or []
        self.timestamp = datetime.now()
        
        # ログ記録
        logger.error(f"7段階速度制御エラー [{self.error_code}]: {message}")
    
    def get_user_friendly_message(self) -> str:
        """ユーザー向け分かりやすいエラーメッセージ"""
        base_message = f"❌ 速度制御エラー: {self.message}"
        
        if self.recovery_suggestions:
            suggestions = "\n".join([f"  💡 {suggestion}" for suggestion in self.recovery_suggestions])
            return f"{base_message}\n\n解決方法:\n{suggestions}"
        
        return base_message
    
    def to_dict(self) -> Dict[str, Any]:
        """エラー情報を辞書形式で取得"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'recovery_suggestions': self.recovery_suggestions
        }


class InvalidSpeedMultiplierError(Enhanced7StageSpeedControlError):
    """
    無効な速度倍率エラー
    
    7段階速度制御で無効な倍率（1,2,3,4,5,10,50以外）が指定された場合のエラー
    """
    
    def __init__(self, invalid_multiplier: int, valid_multipliers: List[int] = None):
        valid_multipliers = valid_multipliers or [1, 2, 3, 4, 5, 10, 50]
        
        message = f"無効な速度倍率: x{invalid_multiplier}"
        recovery_suggestions = [
            f"有効な速度倍率を使用してください: {valid_multipliers}",
            "デフォルト速度（x1）から開始することをお勧めします",
            "段階的に速度を上げて動作を確認してください"
        ]
        
        super().__init__(message, "INVALID_SPEED_MULTIPLIER", recovery_suggestions)
        self.invalid_multiplier = invalid_multiplier
        self.valid_multipliers = valid_multipliers
    
    def get_automatic_fallback_multiplier(self) -> int:
        """自動フォールバック倍率取得"""
        # 最も近い有効な倍率を選択
        valid_list = sorted(self.valid_multipliers)
        
        if self.invalid_multiplier < min(valid_list):
            return min(valid_list)  # x1
        elif self.invalid_multiplier > max(valid_list):
            return 5  # 超高速ではなく標準範囲の最高速度
        else:
            # 最も近い値を検索
            closest = min(valid_list, key=lambda x: abs(x - self.invalid_multiplier))
            return closest


class UltraHighSpeedError(Enhanced7StageSpeedControlError):
    """
    超高速実行エラー
    
    x10, x50での超高速実行時に発生する問題のエラー
    """
    
    def __init__(self, multiplier: int, specific_issue: str, performance_data: Dict = None):
        message = f"超高速実行エラー (x{multiplier}): {specific_issue}"
        
        recovery_suggestions = [
            "より安全な速度（x5以下）に変更してください",
            "システムリソースの使用状況を確認してください",
            "他のアプリケーションを終了してパフォーマンスを向上させてください"
        ]
        
        if multiplier == 50:
            recovery_suggestions.insert(0, "x10速度に降格して試してみてください")
        
        super().__init__(message, "ULTRA_HIGH_SPEED_ERROR", recovery_suggestions)
        self.multiplier = multiplier
        self.specific_issue = specific_issue
        self.performance_data = performance_data or {}
    
    def get_recommended_fallback_speed(self) -> int:
        """推奨フォールバック速度取得"""
        if self.multiplier == 50:
            return 10  # x50 → x10
        elif self.multiplier == 10:
            return 5   # x10 → x5
        else:
            return 1   # その他は安全速度


class HighPrecisionTimingError(Enhanced7StageSpeedControlError):
    """
    高精度タイミングエラー
    
    超高速実行時の精度要件（±5ms for x50, ±10ms for x10）未達成エラー
    """
    
    def __init__(self, target_interval_ms: float, actual_deviation_ms: float, 
                 tolerance_ms: float, multiplier: int):
        message = f"タイミング精度エラー: 偏差{actual_deviation_ms:.1f}ms > 許容値{tolerance_ms:.1f}ms"
        
        recovery_suggestions = [
            f"現在のx{multiplier}速度から安全な速度に変更してください",
            "バックグラウンドプロセスを減らしてシステム負荷を下げてください",
            "精度が重要でない場合は標準速度（x1-x5）を使用してください"
        ]
        
        super().__init__(message, "HIGH_PRECISION_TIMING_ERROR", recovery_suggestions)
        self.target_interval_ms = target_interval_ms
        self.actual_deviation_ms = actual_deviation_ms
        self.tolerance_ms = tolerance_ms
        self.multiplier = multiplier
    
    def is_critical_precision_failure(self) -> bool:
        """重要な精度失敗かどうか判定"""
        return self.actual_deviation_ms > self.tolerance_ms * 2.0


class RealTimeSpeedChangeError(Enhanced7StageSpeedControlError):
    """
    リアルタイム速度変更エラー
    
    実行中の動的な速度変更で発生するエラー
    """
    
    def __init__(self, from_multiplier: int, to_multiplier: int, failure_reason: str):
        message = f"リアルタイム速度変更失敗: x{from_multiplier} → x{to_multiplier} ({failure_reason})"
        
        recovery_suggestions = [
            "実行を一時停止してから速度を変更してください",
            "現在の速度のまま継続することをお勧めします",
            "段階的な速度変更（一度に1-2段階）を試してください"
        ]
        
        super().__init__(message, "REALTIME_SPEED_CHANGE_ERROR", recovery_suggestions)
        self.from_multiplier = from_multiplier
        self.to_multiplier = to_multiplier
        self.failure_reason = failure_reason
    
    def should_maintain_current_speed(self) -> bool:
        """現在速度維持を推奨するか"""
        # 超高速から標準速度への変更失敗は重要
        return self.from_multiplier in [10, 50] and self.to_multiplier <= 5


class ExecutionSyncError(Enhanced7StageSpeedControlError):
    """
    実行同期エラー
    
    ExecutionControllerとの同期で発生する問題
    """
    
    def __init__(self, sync_component: str, expected_state: str, actual_state: str):
        message = f"実行同期エラー: {sync_component} 期待値'{expected_state}' != 実際'{actual_state}'"
        
        recovery_suggestions = [
            "システムリセットを実行してください",
            "実行を停止してから再開してください",
            "問題が続く場合は標準速度（x1）で実行してください"
        ]
        
        super().__init__(message, "EXECUTION_SYNC_ERROR", recovery_suggestions)
        self.sync_component = sync_component
        self.expected_state = expected_state
        self.actual_state = actual_state


class SpeedDegradationError(Enhanced7StageSpeedControlError):
    """
    速度性能低下エラー
    
    連続した精度失敗や性能問題による自動降格エラー
    """
    
    def __init__(self, original_multiplier: int, degraded_multiplier: int, 
                 degradation_reason: str, failure_count: int):
        message = f"性能低下による自動降格: x{original_multiplier} → x{degraded_multiplier} (理由: {degradation_reason})"
        
        recovery_suggestions = [
            f"現在の安全速度（x{degraded_multiplier}）での継続をお勧めします",
            "システム負荷を下げてからより高い速度を試してください",
            "一度実行を停止してシステムを安定させてください"
        ]
        
        super().__init__(message, "SPEED_DEGRADATION_ERROR", recovery_suggestions)
        self.original_multiplier = original_multiplier
        self.degraded_multiplier = degraded_multiplier
        self.degradation_reason = degradation_reason
        self.failure_count = failure_count
    
    def is_severe_degradation(self) -> bool:
        """深刻な性能低下かどうか判定"""
        speed_drop = self.original_multiplier - self.degraded_multiplier
        return speed_drop >= 5 or self.failure_count >= 10


# エラー復旧ユーティリティ関数

def handle_speed_control_error(error: Enhanced7StageSpeedControlError, 
                              speed_manager=None) -> Dict[str, Any]:
    """
    7段階速度制御エラーの統一的な処理
    
    Args:
        error: 発生したエラー
        speed_manager: Enhanced7StageSpeedControlManager（復旧処理用）
        
    Returns:
        dict: 復旧処理結果
    """
    result = {
        'error_handled': True,
        'recovery_applied': False,
        'new_speed_multiplier': None,
        'user_message': error.get_user_friendly_message()
    }
    
    try:
        # エラータイプ別自動復旧処理
        if isinstance(error, InvalidSpeedMultiplierError):
            if speed_manager:
                fallback_speed = error.get_automatic_fallback_multiplier()
                speed_manager.set_speed_multiplier(fallback_speed)
                result['recovery_applied'] = True
                result['new_speed_multiplier'] = fallback_speed
                logger.info(f"自動復旧: 無効速度をx{fallback_speed}に修正")
        
        elif isinstance(error, UltraHighSpeedError):
            if speed_manager:
                fallback_speed = error.get_recommended_fallback_speed()
                speed_manager.set_speed_multiplier(fallback_speed)
                result['recovery_applied'] = True
                result['new_speed_multiplier'] = fallback_speed
                logger.info(f"自動復旧: 超高速エラーをx{fallback_speed}に降格")
        
        elif isinstance(error, HighPrecisionTimingError):
            if speed_manager and error.is_critical_precision_failure():
                # 重大な精度失敗の場合は安全速度に降格
                safe_speed = 5 if error.multiplier >= 10 else 1
                speed_manager.set_speed_multiplier(safe_speed)
                result['recovery_applied'] = True
                result['new_speed_multiplier'] = safe_speed
                logger.info(f"自動復旧: 精度失敗をx{safe_speed}に降格")
        
        elif isinstance(error, RealTimeSpeedChangeError):
            if error.should_maintain_current_speed():
                logger.info("自動復旧: 現在速度を維持")
                result['recovery_applied'] = True
        
        elif isinstance(error, ExecutionSyncError):
            logger.warning("実行同期エラー: システムリセットが必要な可能性があります")
        
        elif isinstance(error, SpeedDegradationError):
            # 既に自動降格済みなので、状態を記録
            result['recovery_applied'] = True
            result['new_speed_multiplier'] = error.degraded_multiplier
            
            if error.is_severe_degradation():
                logger.warning("深刻な性能低下が検出されました")
    
    except Exception as recovery_error:
        logger.error(f"エラー復旧処理中に問題発生: {recovery_error}")
        result['error_handled'] = False
    
    return result


def log_speed_control_error_metrics(error: Enhanced7StageSpeedControlError) -> None:
    """エラーメトリクスのログ記録"""
    metrics = {
        'error_type': error.__class__.__name__,
        'error_code': error.error_code,
        'timestamp': error.timestamp.isoformat(),
        'has_recovery_suggestions': len(error.recovery_suggestions) > 0
    }
    
    # エラータイプ別の詳細メトリクス
    if isinstance(error, HighPrecisionTimingError):
        metrics.update({
            'target_interval_ms': error.target_interval_ms,
            'deviation_ms': error.actual_deviation_ms,
            'tolerance_exceeded_ratio': error.actual_deviation_ms / error.tolerance_ms
        })
    elif isinstance(error, SpeedDegradationError):
        metrics.update({
            'speed_drop': error.original_multiplier - error.degraded_multiplier,
            'failure_count': error.failure_count
        })
    
    logger.info(f"速度制御エラーメトリクス: {metrics}")


# エラー発生統計管理

class SpeedControlErrorTracker:
    """速度制御エラー発生統計管理"""
    
    def __init__(self):
        self.error_counts = {}
        self.recent_errors = []
        self.max_recent_errors = 50
    
    def record_error(self, error: Enhanced7StageSpeedControlError):
        """エラー記録"""
        error_type = error.__class__.__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        self.recent_errors.append({
            'error_type': error_type,
            'timestamp': error.timestamp,
            'message': error.message
        })
        
        # 最新50件に制限
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors = self.recent_errors[-self.max_recent_errors:]
        
        # メトリクス記録
        log_speed_control_error_metrics(error)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計取得"""
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_errors': total_errors,
            'error_types': dict(self.error_counts),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None,
            'recent_errors_count': len(self.recent_errors),
            'error_rate_trend': self._calculate_error_rate_trend()
        }
    
    def _calculate_error_rate_trend(self) -> str:
        """エラー率トレンド計算"""
        if len(self.recent_errors) < 10:
            return "insufficient_data"
        
        # 最新10件と前の10件を比較
        recent_10 = self.recent_errors[-10:]
        previous_10 = self.recent_errors[-20:-10] if len(self.recent_errors) >= 20 else []
        
        if not previous_10:
            return "stable"
        
        recent_time = (recent_10[-1]['timestamp'] - recent_10[0]['timestamp']).total_seconds()
        previous_time = (previous_10[-1]['timestamp'] - previous_10[0]['timestamp']).total_seconds()
        
        if recent_time > 0 and previous_time > 0:
            recent_rate = len(recent_10) / recent_time
            previous_rate = len(previous_10) / previous_time
            
            if recent_rate > previous_rate * 1.5:
                return "increasing"
            elif recent_rate < previous_rate * 0.5:
                return "decreasing"
        
        return "stable"


# グローバルエラートラッカー
_global_error_tracker = SpeedControlErrorTracker()