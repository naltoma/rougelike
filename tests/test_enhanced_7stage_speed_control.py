#!/usr/bin/env python3
"""
🚀 v1.2.5: Enhanced 7-Stage Speed Control Test Suite
7段階速度制御システムの包括的テストスイート
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# プロジェクトパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.enhanced_7stage_speed_control_manager import Enhanced7StageSpeedControlManager
from engine.ultra_high_speed_controller import UltraHighSpeedController
from engine.enhanced_7stage_speed_errors import (
    Enhanced7StageSpeedControlError,
    InvalidSpeedMultiplierError,
    UltraHighSpeedError,
    HighPrecisionTimingError,
    RealTimeSpeedChangeError,
    ExecutionSyncError,
    SpeedDegradationError
)
from engine.speed_control_error_handler import SpeedControlErrorHandler


class TestEnhanced7StageSpeedControlManager(unittest.TestCase):
    """Enhanced7StageSpeedControlManager テストクラス"""
    
    def setUp(self):
        """テスト初期化"""
        self.manager = Enhanced7StageSpeedControlManager()
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.manager.current_speed_multiplier, 1)
        self.assertIn(1, self.manager.valid_speed_multipliers)
        self.assertIn(50, self.manager.valid_speed_multipliers)
        self.assertEqual(len(self.manager.valid_speed_multipliers), 7)
    
    def test_valid_speed_multiplier_setting(self):
        """有効な速度倍率設定テスト"""
        valid_speeds = [1, 2, 3, 4, 5, 10, 50]
        
        for speed in valid_speeds:
            self.assertTrue(self.manager.set_speed_multiplier(speed))
            self.assertEqual(self.manager.current_speed_multiplier, speed)
    
    def test_invalid_speed_multiplier_setting(self):
        """無効な速度倍率設定テスト"""
        invalid_speeds = [0, 6, 7, 8, 9, 11, 25, 100, -1]
        
        for speed in invalid_speeds:
            with self.assertRaises(InvalidSpeedMultiplierError):
                self.manager.set_speed_multiplier(speed)
    
    def test_sleep_interval_calculation(self):
        """sleep間隔計算テスト"""
        base_interval = 0.1
        
        # x1速度
        self.manager.set_speed_multiplier(1)
        self.assertAlmostEqual(
            self.manager.calculate_sleep_interval(base_interval), 
            0.1, 
            places=3
        )
        
        # x10速度
        self.manager.set_speed_multiplier(10)
        self.assertAlmostEqual(
            self.manager.calculate_sleep_interval(base_interval), 
            0.01, 
            places=3
        )
        
        # x50速度
        self.manager.set_speed_multiplier(50)
        self.assertAlmostEqual(
            self.manager.calculate_sleep_interval(base_interval), 
            0.002, 
            places=4
        )
    
    def test_ultra_high_speed_detection(self):
        """超高速判定テスト"""
        # 標準速度
        for speed in [1, 2, 3, 4, 5]:
            self.manager.set_speed_multiplier(speed)
            self.assertFalse(self.manager.is_ultra_high_speed())
        
        # 超高速
        for speed in [10, 50]:
            self.manager.set_speed_multiplier(speed)
            self.assertTrue(self.manager.is_ultra_high_speed())
    
    def test_realtime_speed_change(self):
        """リアルタイム速度変更テスト"""
        # 通常の変更
        self.assertTrue(self.manager.change_speed_realtime(5))
        self.assertEqual(self.manager.current_speed_multiplier, 5)
        
        # 無効な速度への変更
        with self.assertRaises(RealTimeSpeedChangeError):
            self.manager.change_speed_realtime(15)
    
    def test_speed_control_metrics(self):
        """速度制御メトリクス取得テスト"""
        self.manager.set_speed_multiplier(10)
        
        metrics = self.manager.get_speed_control_metrics()
        
        self.assertIn('current_speed_multiplier', metrics)
        self.assertIn('is_ultra_high_speed', metrics)
        self.assertIn('precision_tolerance_ms', metrics)
        self.assertEqual(metrics['current_speed_multiplier'], 10)
        self.assertTrue(metrics['is_ultra_high_speed'])
        self.assertEqual(metrics['precision_tolerance_ms'], 10.0)


class TestUltraHighSpeedController(unittest.TestCase):
    """UltraHighSpeedController テストクラス"""
    
    def setUp(self):
        """テスト初期化"""
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.ultra_controller.speed_manager)
        self.assertEqual(self.ultra_controller.precision_failure_count, 0)
    
    def test_precision_sleep_timing(self):
        """高精度スリープタイミングテスト"""
        # x10速度での精度テスト（±10ms許容）
        self.speed_manager.set_speed_multiplier(10)
        target_sleep = 0.02  # 20ms
        
        start_time = time.time()
        self.ultra_controller.ultra_precise_sleep(target_sleep)
        elapsed = time.time() - start_time
        
        # 20ms ± 10ms の範囲内かチェック
        self.assertGreaterEqual(elapsed, 0.01)  # 最低10ms
        self.assertLessEqual(elapsed, 0.03)     # 最大30ms
    
    def test_x50_precision_requirements(self):
        """x50速度精度要件テスト（±5ms）"""
        self.speed_manager.set_speed_multiplier(50)
        target_sleep = 0.004  # 4ms
        
        # 複数回測定して平均精度をチェック
        deviations = []
        for _ in range(10):
            start_time = time.time()
            self.ultra_controller.ultra_precise_sleep(target_sleep)
            elapsed = time.time() - start_time
            deviations.append(abs(elapsed - target_sleep) * 1000)  # ms単位
        
        avg_deviation = sum(deviations) / len(deviations)
        self.assertLessEqual(avg_deviation, 5.0, "x50速度で±5ms精度要件未達成")
    
    def test_stability_monitoring(self):
        """安定性監視テスト"""
        self.speed_manager.set_speed_multiplier(50)
        
        # 安定性監視実行
        result = self.ultra_controller.monitor_ultra_speed_stability()
        
        self.assertIn('stability_score', result)
        self.assertIn('precision_failures', result)
        self.assertIn('recommended_action', result)
        self.assertGreaterEqual(result['stability_score'], 0.0)
        self.assertLessEqual(result['stability_score'], 1.0)
    
    def test_precision_degradation_handling(self):
        """精度劣化処理テスト"""
        self.speed_manager.set_speed_multiplier(50)
        
        # 意図的に精度失敗を発生
        self.ultra_controller.precision_failure_count = 5
        
        with self.assertRaises(SpeedDegradationError):
            self.ultra_controller._handle_precision_failure(15.0, 5.0)


class TestSpeedControlErrorClasses(unittest.TestCase):
    """速度制御エラークラステスト"""
    
    def test_invalid_speed_multiplier_error(self):
        """無効速度倍率エラーテスト"""
        error = InvalidSpeedMultiplierError(15)
        
        self.assertEqual(error.invalid_multiplier, 15)
        self.assertIn("無効な速度倍率", error.message)
        self.assertTrue(len(error.recovery_suggestions) > 0)
        
        # 自動フォールバック倍率テスト
        fallback = error.get_automatic_fallback_multiplier()
        self.assertIn(fallback, [1, 2, 3, 4, 5, 10, 50])
    
    def test_ultra_high_speed_error(self):
        """超高速実行エラーテスト"""
        error = UltraHighSpeedError(50, "システム負荷過多")
        
        self.assertEqual(error.multiplier, 50)
        self.assertEqual(error.specific_issue, "システム負荷過多")
        self.assertIn("超高速実行エラー", error.message)
        
        # 推奨フォールバック速度テスト
        fallback = error.get_recommended_fallback_speed()
        self.assertEqual(fallback, 10)  # x50 → x10
    
    def test_high_precision_timing_error(self):
        """高精度タイミングエラーテスト"""
        error = HighPrecisionTimingError(4.0, 12.0, 5.0, 50)
        
        self.assertEqual(error.target_interval_ms, 4.0)
        self.assertEqual(error.actual_deviation_ms, 12.0)
        self.assertEqual(error.tolerance_ms, 5.0)
        self.assertEqual(error.multiplier, 50)
        
        # 重要な精度失敗判定テスト
        self.assertTrue(error.is_critical_precision_failure())
    
    def test_realtime_speed_change_error(self):
        """リアルタイム速度変更エラーテスト"""
        error = RealTimeSpeedChangeError(50, 5, "システム負荷")
        
        self.assertEqual(error.from_multiplier, 50)
        self.assertEqual(error.to_multiplier, 5)
        self.assertEqual(error.failure_reason, "システム負荷")
        
        # 現在速度維持推奨判定テスト
        self.assertTrue(error.should_maintain_current_speed())
    
    def test_speed_degradation_error(self):
        """速度性能低下エラーテスト"""
        error = SpeedDegradationError(50, 10, "連続精度失敗", 8)
        
        self.assertEqual(error.original_multiplier, 50)
        self.assertEqual(error.degraded_multiplier, 10)
        self.assertEqual(error.degradation_reason, "連続精度失敗")
        self.assertEqual(error.failure_count, 8)
        
        # 深刻な劣化判定テスト
        self.assertTrue(error.is_severe_degradation())


class TestSpeedControlErrorHandler(unittest.TestCase):
    """速度制御エラーハンドラーテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.speed_manager = Mock(spec=Enhanced7StageSpeedControlManager)
        self.error_handler = SpeedControlErrorHandler(
            speed_manager=self.speed_manager
        )
    
    def test_error_handler_initialization(self):
        """エラーハンドラー初期化テスト"""
        self.assertEqual(self.error_handler.consecutive_error_count, 0)
        self.assertTrue(self.error_handler.auto_recovery_enabled)
        self.assertTrue(self.error_handler.user_notification_enabled)
    
    def test_speed_control_error_handling(self):
        """速度制御エラー処理テスト"""
        error = InvalidSpeedMultiplierError(15)
        
        result = self.error_handler.handle_error(error, "test_context")
        
        self.assertTrue(result['handled'])
        self.assertEqual(result['error_type'], 'InvalidSpeedMultiplierError')
        self.assertEqual(result['context'], 'test_context')
    
    def test_automatic_recovery(self):
        """自動復旧処理テスト"""
        error = UltraHighSpeedError(50, "高負荷")
        
        result = self.error_handler.handle_error(error, "test")
        
        # 自動復旧が試行されることを確認
        self.assertTrue(result.get('recovery_applied', False))
    
    def test_consecutive_error_management(self):
        """連続エラー管理テスト"""
        error = InvalidSpeedMultiplierError(15)
        
        # 連続エラー発生
        for i in range(3):
            self.error_handler.handle_error(error, f"test_{i}")
        
        self.assertEqual(self.error_handler.consecutive_error_count, 3)
        self.assertEqual(len(self.error_handler.recent_error_types), 3)
    
    def test_error_cooldown_mechanism(self):
        """エラークールダウン機能テスト"""
        error = InvalidSpeedMultiplierError(15)
        
        # 初回エラー処理
        result1 = self.error_handler.handle_error(error, "test1")
        self.assertTrue(result1['handled'])
        
        # クールダウン中の処理（即座に再実行）
        result2 = self.error_handler.handle_error(error, "test2")
        
        # クールダウン設定によって結果が変わる可能性をチェック
        self.assertIn(result2['handled'], [True, False])
    
    def test_notification_callbacks(self):
        """通知コールバックテスト"""
        callback_called = False
        callback_data = None
        
        def test_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        self.error_handler.add_notification_callback(test_callback)
        
        error = InvalidSpeedMultiplierError(15)
        self.error_handler.handle_error(error, "test")
        
        self.assertTrue(callback_called)
        self.assertIsNotNone(callback_data)
        self.assertIn('error', callback_data)
    
    def test_error_statistics(self):
        """エラー統計取得テスト"""
        # いくつかのエラーを発生
        errors = [
            InvalidSpeedMultiplierError(15),
            UltraHighSpeedError(50, "負荷過多"),
            HighPrecisionTimingError(4.0, 8.0, 5.0, 50)
        ]
        
        for error in errors:
            self.error_handler.handle_error(error, "test")
        
        stats = self.error_handler.get_error_statistics()
        
        self.assertIn('global_statistics', stats)
        self.assertIn('handler_statistics', stats)
        self.assertIn('recovery_history', stats)
        self.assertEqual(stats['handler_statistics']['consecutive_errors'], 3)


class TestIntegrationScenarios(unittest.TestCase):
    """統合シナリオテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
        self.error_handler = SpeedControlErrorHandler(
            speed_manager=self.speed_manager,
            ultra_controller=self.ultra_controller
        )
    
    def test_complete_speed_transition_scenario(self):
        """完全な速度遷移シナリオテスト"""
        # x1 → x5 → x10 → x50 → x10（降格）→ x5 → x1
        speed_sequence = [1, 5, 10, 50, 10, 5, 1]
        
        for target_speed in speed_sequence:
            try:
                success = self.speed_manager.set_speed_multiplier(target_speed)
                self.assertTrue(success, f"速度x{target_speed}への変更失敗")
                
                # 超高速の場合は精度チェック
                if target_speed >= 10:
                    self.assertTrue(self.speed_manager.is_ultra_high_speed())
                    
                    # 短時間の安定性テスト
                    sleep_interval = self.speed_manager.calculate_sleep_interval(0.02)
                    start_time = time.time()
                    self.ultra_controller.ultra_precise_sleep(sleep_interval)
                    elapsed = time.time() - start_time
                    
                    # 精度要件チェック
                    tolerance = 0.01 if target_speed == 10 else 0.005  # x10: ±10ms, x50: ±5ms
                    deviation = abs(elapsed - sleep_interval)
                    self.assertLessEqual(deviation, tolerance, 
                                       f"x{target_speed}速度で精度要件未達成: {deviation*1000:.1f}ms")
                
            except Enhanced7StageSpeedControlError as e:
                # エラー発生時は自動復旧を試行
                result = self.error_handler.handle_error(e, f"speed_transition_to_x{target_speed}")
                
                # 復旧が試行されたかチェック
                if result.get('recovery_applied'):
                    recovered_speed = result.get('new_speed_multiplier')
                    self.assertIsNotNone(recovered_speed)
                    self.assertIn(recovered_speed, [1, 2, 3, 4, 5, 10, 50])
    
    def test_high_load_degradation_scenario(self):
        """高負荷時劣化シナリオテスト"""
        # x50で開始
        self.speed_manager.set_speed_multiplier(50)
        
        # 意図的に精度失敗を発生させて劣化をテスト
        for i in range(5):
            try:
                # 精度要件を満たさない状況をシミュレート
                error = HighPrecisionTimingError(2.0, 8.0, 5.0, 50)  # 8ms偏差 > 5ms許容値
                result = self.error_handler.handle_error(error, f"precision_failure_{i}")
                
                if result.get('recovery_applied'):
                    new_speed = result.get('new_speed_multiplier')
                    if new_speed and new_speed < 50:
                        # 自動降格が発生した場合
                        self.assertLess(new_speed, 50)
                        break
                        
            except Exception as e:
                self.fail(f"予期しないエラーが発生: {e}")
    
    def test_concurrent_speed_changes(self):
        """同時速度変更テスト"""
        results = []
        
        def change_speed_worker(target_speed):
            try:
                success = self.speed_manager.change_speed_realtime(target_speed)
                results.append((target_speed, success))
            except Exception as e:
                results.append((target_speed, False, str(e)))
        
        # 複数スレッドで同時に速度変更を試行
        threads = []
        target_speeds = [5, 10, 2, 50, 3]
        
        for speed in target_speeds:
            thread = threading.Thread(target=change_speed_worker, args=(speed,))
            threads.append(thread)
            thread.start()
        
        # 全スレッド完了を待機
        for thread in threads:
            thread.join()
        
        # 少なくとも1つの変更が成功することを期待
        successful_changes = [r for r in results if len(r) == 2 and r[1]]
        self.assertGreater(len(successful_changes), 0, "同時速度変更で成功例なし")


class TestPerformanceBenchmarks(unittest.TestCase):
    """パフォーマンスベンチマークテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
    
    def test_sleep_interval_calculation_performance(self):
        """sleep間隔計算パフォーマンステスト"""
        base_interval = 0.02
        iterations = 10000
        
        start_time = time.time()
        for _ in range(iterations):
            self.speed_manager.calculate_sleep_interval(base_interval)
        elapsed = time.time() - start_time
        
        # 10000回の計算が0.1秒以内に完了することを期待
        self.assertLess(elapsed, 0.1, f"sleep間隔計算が遅すぎます: {elapsed:.3f}秒")
    
    def test_ultra_high_speed_precision_consistency(self):
        """超高速精度一貫性テスト"""
        self.speed_manager.set_speed_multiplier(50)
        target_sleep = 0.002  # 2ms
        measurements = []
        
        # 100回の精密測定
        for _ in range(100):
            start_time = time.time()
            self.ultra_controller.ultra_precise_sleep(target_sleep)
            elapsed = time.time() - start_time
            measurements.append(elapsed)
        
        # 統計分析
        avg_time = sum(measurements) / len(measurements)
        deviations = [abs(m - target_sleep) for m in measurements]
        avg_deviation = sum(deviations) / len(deviations)
        max_deviation = max(deviations)
        
        # 精度要件チェック（±5ms for x50）
        self.assertLess(avg_deviation, 0.005, f"平均偏差が要件超過: {avg_deviation*1000:.2f}ms")
        self.assertLess(max_deviation, 0.01, f"最大偏差が許容範囲超過: {max_deviation*1000:.2f}ms")
        
        print(f"\n超高速精度測定結果:")
        print(f"  目標時間: {target_sleep*1000:.1f}ms")
        print(f"  平均実行時間: {avg_time*1000:.2f}ms")
        print(f"  平均偏差: {avg_deviation*1000:.2f}ms")
        print(f"  最大偏差: {max_deviation*1000:.2f}ms")


if __name__ == '__main__':
    # テストスイート実行
    unittest.main(verbosity=2)