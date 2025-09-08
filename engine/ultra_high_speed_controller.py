"""
🚀 v1.2.5: Ultra High Speed Controller
超高速実行（x10, x50）専用の制御システム
高精度タイミング制御と安定性監視機能を提供
"""

import time
import logging
import statistics
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class HighPrecisionTimingData:
    """高精度タイミングデータ"""
    target_interval: float
    actual_intervals: List[float] = field(default_factory=list)
    precision_deviation_ms: List[float] = field(default_factory=list)
    stability_coefficient: float = 0.0
    measurement_count: int = 0
    
    def add_measurement(self, actual_interval: float):
        """測定値追加"""
        self.actual_intervals.append(actual_interval)
        deviation_ms = abs(actual_interval - self.target_interval) * 1000
        self.precision_deviation_ms.append(deviation_ms)
        self.measurement_count += 1
        
        # 最新100件に制限
        if len(self.actual_intervals) > 100:
            self.actual_intervals = self.actual_intervals[-100:]
            self.precision_deviation_ms = self.precision_deviation_ms[-100:]
        
        # 安定性係数更新
        if len(self.actual_intervals) >= 5:
            self.stability_coefficient = statistics.stdev(self.actual_intervals)


class UltraHighSpeedController:
    """超高速制御専用コンポーネント"""
    
    def __init__(self, speed_control_manager):
        """
        初期化
        
        Args:
            speed_control_manager: Enhanced7StageSpeedControlManagerインスタンス
        """
        self.speed_control_manager = speed_control_manager
        
        # 高精度タイミング管理
        self.timing_data: Optional[HighPrecisionTimingData] = None
        self.ultra_high_speed_active = False
        self.current_target_interval = 0.0
        self.current_tolerance_ms = 0.0
        
        # 性能監視
        self.performance_degradation_detected = False
        self.consecutive_precision_failures = 0
        self.max_consecutive_failures = 5
        
        # 精度統計
        self.precision_stats = {
            'total_measurements': 0,
            'precision_failures': 0,
            'auto_degradations': 0,
            'avg_deviation_ms': 0.0
        }
        
        logger.info("✅ UltraHighSpeedController 初期化完了")
    
    def enable_ultra_high_speed_mode(self, target_interval: float) -> bool:
        """
        超高速モード有効化
        
        Args:
            target_interval: 目標間隔（x10=0.1s, x50=0.02s）
            
        Returns:
            bool: 有効化成功フラグ
        """
        try:
            multiplier = self._interval_to_multiplier(target_interval)
            if multiplier not in [10, 50]:
                logger.error(f"❌ 超高速モード対象外の間隔: {target_interval}s")
                return False
            
            # 精度許容値設定
            tolerance_ms = 10.0 if multiplier == 10 else 5.0
            
            # 高精度タイマー設定
            self.setup_precision_timer(target_interval, tolerance_ms)
            
            # 超高速モード状態更新
            self.ultra_high_speed_active = True
            self.current_target_interval = target_interval
            self.current_tolerance_ms = tolerance_ms
            
            # 性能監視リセット
            self.consecutive_precision_failures = 0
            self.performance_degradation_detected = False
            
            logger.info(f"🏃‍♂️ 超高速モード有効化: {target_interval}s間隔 (±{tolerance_ms}ms)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 超高速モード有効化エラー: {e}")
            return False
    
    def setup_precision_timer(self, interval: float, tolerance_ms: float) -> None:
        """
        高精度タイマー設定
        
        Args:
            interval: 目標間隔
            tolerance_ms: 精度許容値（ミリ秒）
        """
        self.timing_data = HighPrecisionTimingData(target_interval=interval)
        self.current_tolerance_ms = tolerance_ms
        logger.debug(f"🎯 高精度タイマー設定: {interval}s ±{tolerance_ms}ms")
    
    def ultra_precise_sleep(self, target_interval: float, tolerance_ms: float) -> float:
        """
        超高精度スリープ実装
        
        Args:
            target_interval: 目標間隔
            tolerance_ms: 精度許容値
            
        Returns:
            float: 実際の経過時間
        """
        start_time = time.perf_counter()
        target_end = start_time + target_interval
        tolerance_sec = tolerance_ms / 1000.0
        
        try:
            # Phase 1: 粗いスリープフェーズ（95%まで）
            rough_end = target_end - (target_interval * 0.05)
            current_time = time.perf_counter()
            
            while current_time < rough_end:
                remaining = rough_end - current_time
                if remaining > 0.001:  # 1ms以上残っていれば粗いスリープ
                    time.sleep(min(remaining * 0.8, 0.001))
                current_time = time.perf_counter()
            
            # Phase 2: 精密スピンロックフェーズ（残り5%）
            while time.perf_counter() < target_end - tolerance_sec:
                pass  # CPU集約的な高精度待機
            
            # Phase 3: 最終調整フェーズ
            while time.perf_counter() < target_end:
                pass
            
            actual_elapsed = time.perf_counter() - start_time
            
            # 測定データ記録
            if self.timing_data:
                self.timing_data.add_measurement(actual_elapsed)
            
            # 精度チェック
            deviation_ms = abs(actual_elapsed - target_interval) * 1000
            self._update_precision_stats(deviation_ms, tolerance_ms)
            
            return actual_elapsed
            
        except Exception as e:
            logger.error(f"❌ 超高精度スリープエラー: {e}")
            return time.sleep(target_interval) or target_interval
    
    def monitor_ultra_speed_stability(self) -> Dict:
        """
        超高速安定性監視
        
        Returns:
            Dict: 安定性監視結果
        """
        if not self.timing_data or not self.ultra_high_speed_active:
            return {'status': 'inactive', 'stability': 'unknown'}
        
        measurements = len(self.timing_data.actual_intervals)
        if measurements < 5:
            return {'status': 'insufficient_data', 'measurements': measurements}
        
        # 統計計算
        intervals = self.timing_data.actual_intervals[-20:]  # 最新20件
        deviations = self.timing_data.precision_deviation_ms[-20:]
        
        avg_deviation = statistics.mean(deviations)
        max_deviation = max(deviations)
        stability_score = 1.0 - (self.timing_data.stability_coefficient / self.current_target_interval)
        
        # 安定性判定
        is_stable = (avg_deviation <= self.current_tolerance_ms and 
                    max_deviation <= self.current_tolerance_ms * 1.5 and
                    stability_score > 0.8)
        
        result = {
            'status': 'stable' if is_stable else 'unstable',
            'measurements': measurements,
            'avg_deviation_ms': avg_deviation,
            'max_deviation_ms': max_deviation,
            'stability_score': stability_score,
            'target_interval': self.current_target_interval,
            'tolerance_ms': self.current_tolerance_ms,
            'consecutive_failures': self.consecutive_precision_failures
        }
        
        # 不安定検出時の処理
        if not is_stable:
            self._handle_instability(result)
        
        return result
    
    def handle_ultra_speed_degradation(self) -> bool:
        """
        超高速性能低下時の自動対処
        
        Returns:
            bool: 対処成功フラグ
        """
        if not self.performance_degradation_detected:
            return True
        
        try:
            current_multiplier = self.speed_control_manager.get_current_speed_multiplier()
            
            # 降格戦略
            if current_multiplier == 50:
                # x50 → x10に降格
                success = self.speed_control_manager.set_speed_multiplier(10)
                if success:
                    logger.warning("⬇️ 性能低下により x50 → x10 に自動降格しました")
                    self.precision_stats['auto_degradations'] += 1
                    return True
            elif current_multiplier == 10:
                # x10 → x5に降格
                success = self.speed_control_manager.set_speed_multiplier(5)
                if success:
                    logger.warning("⬇️ 性能低下により x10 → x5 に自動降格しました")
                    self.precision_stats['auto_degradations'] += 1
                    # 超高速モード無効化
                    self.ultra_high_speed_active = False
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 性能低下対処エラー: {e}")
            return False
    
    def monitor_precision_deviation(self) -> float:
        """
        精度偏差監視
        
        Returns:
            float: 平均偏差（ミリ秒）
        """
        if not self.timing_data or not self.timing_data.precision_deviation_ms:
            return 0.0
        
        recent_deviations = self.timing_data.precision_deviation_ms[-10:]  # 最新10件
        return statistics.mean(recent_deviations)
    
    def get_ultra_speed_performance_stats(self) -> Dict:
        """超高速性能統計取得"""
        return {
            'precision_stats': self.precision_stats.copy(),
            'timing_data': {
                'measurements': len(self.timing_data.actual_intervals) if self.timing_data else 0,
                'avg_deviation': self.monitor_precision_deviation(),
                'stability_coefficient': self.timing_data.stability_coefficient if self.timing_data else 0.0
            },
            'ultra_speed_active': self.ultra_high_speed_active,
            'performance_degradation': self.performance_degradation_detected
        }
    
    def reset_ultra_speed_controller(self) -> None:
        """超高速コントローラーリセット"""
        self.timing_data = None
        self.ultra_high_speed_active = False
        self.performance_degradation_detected = False
        self.consecutive_precision_failures = 0
        
        # 統計リセット
        self.precision_stats = {
            'total_measurements': 0,
            'precision_failures': 0,
            'auto_degradations': 0,
            'avg_deviation_ms': 0.0
        }
        
        logger.info("🔄 UltraHighSpeedController リセット完了")
    
    def _interval_to_multiplier(self, interval: float) -> int:
        """間隔から倍率推定"""
        # 近似マッチング
        if abs(interval - 0.02) < 0.005:
            return 50
        elif abs(interval - 0.1) < 0.02:
            return 10
        elif abs(interval - 0.2) < 0.05:
            return 5
        else:
            return 1
    
    def _update_precision_stats(self, deviation_ms: float, tolerance_ms: float) -> None:
        """精度統計更新"""
        self.precision_stats['total_measurements'] += 1
        
        if deviation_ms > tolerance_ms:
            self.precision_stats['precision_failures'] += 1
            self.consecutive_precision_failures += 1
            
            # 連続失敗チェック
            if self.consecutive_precision_failures >= self.max_consecutive_failures:
                self.performance_degradation_detected = True
                logger.warning(f"⚠️ 精度低下検出: 連続{self.consecutive_precision_failures}回失敗")
        else:
            self.consecutive_precision_failures = 0
        
        # 平均偏差更新
        total = self.precision_stats['total_measurements']
        current_avg = self.precision_stats['avg_deviation_ms']
        self.precision_stats['avg_deviation_ms'] = (current_avg * (total - 1) + deviation_ms) / total
        
        # Speed Control Managerに測定値通知
        if hasattr(self.speed_control_manager, 'record_precision_measurement'):
            self.speed_control_manager.record_precision_measurement(
                deviation_ms / 1000 + self.current_target_interval,  # actual_interval
                self.current_target_interval  # target_interval
            )
    
    def _handle_instability(self, stability_result: Dict) -> None:
        """不安定状態処理"""
        logger.warning(f"⚠️ 超高速実行不安定: avg_dev={stability_result['avg_deviation_ms']:.2f}ms, "
                      f"max_dev={stability_result['max_deviation_ms']:.2f}ms")
        
        # 不安定状態での自動降格判定
        if stability_result['avg_deviation_ms'] > self.current_tolerance_ms * 2:
            self.performance_degradation_detected = True