"""
🚀 v1.2.5: Enhanced 7-Stage Speed Control Manager
7段階速度制御の中核となるマネージャークラス
x1, x2, x3, x4, x5, x10, x50の包括的速度制御を提供
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# 7段階速度倍率とスリープ間隔のマッピング
ENHANCED_7STAGE_SPEED_MAPPING = {
    1: 2.0,     # x1 (2秒) - 学習モード（ゆっくり）
    2: 1.0,     # x2 (1秒) - 標準速度
    3: 0.5,     # x3 (0.5秒) - 2倍速相当
    4: 0.25,    # x4 (0.25秒) - 4倍速
    5: 0.1,     # x5 (0.1秒) - 10倍速
    10: 0.05,   # x10 (0.05秒) - 20倍速（超高速）
    50: 0.001   # x50 (0.001秒) - 1000倍速（最高速度・視認不可）
}

# 超高速モード判定
ULTRA_HIGH_SPEED_MULTIPLIERS = [10, 50]

# 超高速精度許容値（ミリ秒）
ULTRA_HIGH_SPEED_PRECISION_TOLERANCE = {
    10: 5.0,   # x10: ±5ms
    50: 1.0    # x50: ±1ms（1ms間隔のため高精度）
}


@dataclass
class UltraHighSpeedConfiguration:
    """超高速設定管理"""
    current_multiplier: int = 2  # デフォルトをx2に統一
    sleep_interval: float = 1.0
    is_ultra_high_speed: bool = False
    precision_tolerance_ms: float = 5.0
    last_changed: datetime = field(default_factory=datetime.now)
    is_realtime_change: bool = False
    
    def __post_init__(self):
        """バリデーション"""
        valid_multipliers = [1, 2, 3, 4, 5, 10, 50]
        if self.current_multiplier not in valid_multipliers:
            raise ValueError(f"速度倍率は{valid_multipliers}のいずれかである必要があります")
        if self.sleep_interval < 0.01:
            raise ValueError("スリープ間隔は0.01秒以上である必要があります")
        self.is_ultra_high_speed = self.current_multiplier in ULTRA_HIGH_SPEED_MULTIPLIERS


@dataclass  
class Enhanced7StageSpeedMetrics:
    """7段階速度メトリクス"""
    session_id: str
    speed_changes: List[Tuple[datetime, int]] = field(default_factory=list)
    total_execution_time_by_speed: Dict[int, float] = field(default_factory=dict)
    ultra_high_speed_usage: Dict[int, float] = field(default_factory=dict)
    average_speed_multiplier: float = 1.0
    max_speed_used: int = 1
    ultra_speed_precision_stats: Dict[str, float] = field(default_factory=dict)
    realtime_changes_count: int = 0


class Enhanced7StageSpeedControlManager:
    """7段階速度制御管理クラス"""
    
    def __init__(self, execution_controller):
        """
        初期化
        
        Args:
            execution_controller: ExecutionControllerインスタンス
        """
        self.execution_controller = execution_controller
        self.config = UltraHighSpeedConfiguration()
        
        # 速度変更履歴とメトリクス
        self.speed_change_history: List[Tuple[datetime, int, float]] = []
        self.current_speed_start_time: Optional[datetime] = None
        
        # 精度監視用
        self.precision_measurements: List[float] = []
        self.precision_monitoring_enabled = False
        
        logger.info("✅ Enhanced7StageSpeedControlManager 初期化完了")
    
    def set_speed_multiplier(self, multiplier: int) -> bool:
        """
        速度倍率設定
        
        Args:
            multiplier: 速度倍率 (1, 2, 3, 4, 5, 10, 50)
            
        Returns:
            bool: 設定成功フラグ
        """
        try:
            # バリデーション
            if not self.validate_speed_multiplier(multiplier):
                logger.error(f"❌ 無効な速度倍率: {multiplier}")
                return False
            
            # 前の設定の実行時間記録
            self._record_speed_usage_time()
            
            # 新しい設定適用
            old_multiplier = self.config.current_multiplier
            sleep_interval = self.calculate_sleep_interval(multiplier)
            
            self.config.current_multiplier = multiplier
            self.config.sleep_interval = sleep_interval
            self.config.is_ultra_high_speed = self.is_ultra_high_speed(multiplier)
            self.config.last_changed = datetime.now()
            self.config.is_realtime_change = self.execution_controller.state.is_running
            
            # 超高速モードの精度許容値設定
            if self.config.is_ultra_high_speed:
                self.config.precision_tolerance_ms = ULTRA_HIGH_SPEED_PRECISION_TOLERANCE[multiplier]
                self.precision_monitoring_enabled = True
                logger.info(f"🏃‍♂️ 超高速モード有効化: x{multiplier} (±{self.config.precision_tolerance_ms}ms)")
            else:
                self.precision_monitoring_enabled = False
                logger.info(f"🚶‍♂️ 標準速度モード: x{multiplier}")
            
            # 履歴記録
            self.speed_change_history.append((datetime.now(), old_multiplier, multiplier))
            
            # ExecutionControllerに反映（リアルタイム変更対応）
            if hasattr(self.execution_controller, 'update_sleep_interval_realtime'):
                self.execution_controller.update_sleep_interval_realtime(sleep_interval)
            else:
                # 従来の方法
                self.execution_controller.state.sleep_interval = sleep_interval
            
            # 実行時間測定開始
            self.current_speed_start_time = datetime.now()
            
            logger.info(f"✅ 速度倍率変更: x{old_multiplier} → x{multiplier} ({sleep_interval}秒間隔)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 速度倍率設定エラー: {e}")
            return False
    
    def get_current_speed_multiplier(self) -> int:
        """現在の速度倍率取得"""
        return self.config.current_multiplier
    
    def calculate_sleep_interval(self, multiplier: int) -> float:
        """
        倍率から実際のスリープ時間算出
        
        Args:
            multiplier: 速度倍率
            
        Returns:
            float: スリープ間隔（秒）
        """
        if multiplier not in ENHANCED_7STAGE_SPEED_MAPPING:
            logger.warning(f"⚠️ 未定義の倍率、デフォルト使用: {multiplier}")
            return 1.0
        
        return ENHANCED_7STAGE_SPEED_MAPPING[multiplier]
    
    def is_ultra_high_speed(self, multiplier: int) -> bool:
        """
        超高速モード判定
        
        Args:
            multiplier: 速度倍率
            
        Returns:
            bool: 超高速モードフラグ
        """
        return multiplier in ULTRA_HIGH_SPEED_MULTIPLIERS
    
    def apply_speed_change_realtime(self, multiplier: int) -> bool:
        """
        実行中のリアルタイム速度変更
        
        Args:
            multiplier: 新しい速度倍率
            
        Returns:
            bool: 変更成功フラグ
        """
        if not self.execution_controller.state.is_running:
            logger.info("ℹ️ 実行中ではないため、通常設定を適用")
            return self.set_speed_multiplier(multiplier)
        
        try:
            # リアルタイム変更フラグを設定
            old_config = self.config
            success = self.set_speed_multiplier(multiplier)
            
            if success:
                # リアルタイム変更統計更新
                self._record_realtime_change()
                logger.info(f"⚡ リアルタイム速度変更成功: x{old_config.current_multiplier} → x{multiplier}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ リアルタイム速度変更エラー: {e}")
            return False
    
    def reset_to_default_speed(self) -> None:
        """デフォルト速度（x1）にリセット"""
        logger.info("🔄 速度をデフォルト（x1）にリセット")
        self.set_speed_multiplier(1)
    
    def validate_speed_multiplier(self, multiplier: int) -> bool:
        """
        速度倍率の妥当性検証
        
        Args:
            multiplier: 検証する速度倍率
            
        Returns:
            bool: 妥当性フラグ
        """
        valid_multipliers = list(ENHANCED_7STAGE_SPEED_MAPPING.keys())
        is_valid = multiplier in valid_multipliers
        
        if not is_valid:
            logger.error(f"❌ 無効な速度倍率: {multiplier}, 有効値: {valid_multipliers}")
        
        return is_valid
    
    def get_speed_configuration(self) -> UltraHighSpeedConfiguration:
        """現在の速度設定取得"""
        return self.config
    
    def get_7stage_speed_metrics(self) -> Enhanced7StageSpeedMetrics:
        """7段階速度メトリクス取得"""
        # 現在の実行時間記録
        self._record_speed_usage_time()
        
        # 統計計算
        total_changes = len(self.speed_change_history)
        if total_changes > 0:
            speed_values = [change[2] for change in self.speed_change_history]  # 新しい速度値
            max_speed = max(speed_values) if speed_values else 1
            avg_speed = sum(speed_values) / len(speed_values) if speed_values else 1.0
        else:
            max_speed = self.config.current_multiplier
            avg_speed = float(self.config.current_multiplier)
        
        # 超高速使用統計
        ultra_usage = {}
        for multiplier in ULTRA_HIGH_SPEED_MULTIPLIERS:
            # TODO: 実際の使用時間を計算（現在は仮実装）
            ultra_usage[multiplier] = 0.0
        
        # 精度統計
        precision_stats = {}
        if self.precision_measurements:
            precision_stats = {
                'avg_deviation_ms': sum(self.precision_measurements) / len(self.precision_measurements),
                'max_deviation_ms': max(self.precision_measurements),
                'measurements_count': len(self.precision_measurements)
            }
        
        return Enhanced7StageSpeedMetrics(
            session_id=f"session_{int(datetime.now().timestamp())}",
            speed_changes=[(change[0], change[2]) for change in self.speed_change_history],
            total_execution_time_by_speed={},  # TODO: 実装
            ultra_high_speed_usage=ultra_usage,
            average_speed_multiplier=avg_speed,
            max_speed_used=max_speed,
            ultra_speed_precision_stats=precision_stats,
            realtime_changes_count=sum(1 for change in self.speed_change_history 
                                     if self._is_realtime_change(change[0]))
        )
    
    def record_precision_measurement(self, actual_interval: float, target_interval: float) -> None:
        """
        精度測定記録
        
        Args:
            actual_interval: 実際の間隔
            target_interval: 目標間隔
        """
        if not self.precision_monitoring_enabled:
            return
        
        deviation_ms = abs(actual_interval - target_interval) * 1000
        self.precision_measurements.append(deviation_ms)
        
        # 測定値を最新100件に制限
        if len(self.precision_measurements) > 100:
            self.precision_measurements = self.precision_measurements[-100:]
        
        # 精度要件チェック
        tolerance = self.config.precision_tolerance_ms
        if deviation_ms > tolerance:
            logger.warning(f"⚠️ 精度要件未達成: {deviation_ms:.1f}ms > {tolerance}ms (x{self.config.current_multiplier})")
    
    def _record_speed_usage_time(self) -> None:
        """現在の速度での使用時間を記録"""
        if self.current_speed_start_time:
            usage_time = (datetime.now() - self.current_speed_start_time).total_seconds()
            # TODO: 速度別使用時間統計に追加
            logger.debug(f"Speed x{self.config.current_multiplier} usage: {usage_time:.2f}s")
    
    def _record_realtime_change(self) -> None:
        """リアルタイム変更統計更新"""
        # TODO: リアルタイム変更統計の詳細実装
        pass
    
    def _is_realtime_change(self, change_time: datetime) -> bool:
        """変更がリアルタイム変更かどうか判定"""
        # TODO: 実行状態との照合による判定実装
        return False
    
    def get_all_valid_multipliers(self) -> List[int]:
        """有効な速度倍率一覧取得"""
        return sorted(list(ENHANCED_7STAGE_SPEED_MAPPING.keys()))
    
    def get_speed_interval_mapping(self) -> Dict[int, float]:
        """速度倍率-間隔マッピング取得"""
        return ENHANCED_7STAGE_SPEED_MAPPING.copy()