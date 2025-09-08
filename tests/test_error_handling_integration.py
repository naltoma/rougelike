"""
🚀 v1.2.5: Error Handling Integration Test Suite
7段階速度制御エラーハンドリング統合テストスイート
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
from engine.speed_control_error_handler import SpeedControlErrorHandler, SpeedControlErrorManager
from engine.enhanced_7stage_speed_errors import (
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


class TestErrorHandlingIntegration(unittest.TestCase):
    """エラーハンドリング統合テスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
        self.error_handler = SpeedControlErrorHandler(
            speed_manager=self.speed_manager,
            ultra_controller=self.ultra_controller
        )
        
        # エラー追跡をリセット
        _global_error_tracker.error_counts.clear()
        _global_error_tracker.recent_errors.clear()
    
    def test_complete_error_recovery_workflow(self):
        """完全なエラー復旧ワークフローテスト"""
        # シナリオ1: 無効な速度倍率 → 自動復旧
        invalid_speed_error = InvalidSpeedMultiplierError(15, [1, 2, 3, 4, 5, 10, 50])
        
        result = self.error_handler.handle_error(invalid_speed_error, "test_scenario_1")
        
        self.assertTrue(result['handled'])
        self.assertTrue(result.get('recovery_applied', False))
        self.assertIn(result.get('new_speed_multiplier'), [1, 2, 3, 4, 5, 10, 50])
        
        # シナリオ2: 超高速エラー → 降格処理
        ultra_speed_error = UltraHighSpeedError(50, "システム負荷過多")
        
        result = self.error_handler.handle_error(ultra_speed_error, "test_scenario_2")
        
        self.assertTrue(result['handled'])
        self.assertTrue(result.get('recovery_applied', False))
        self.assertLessEqual(result.get('new_speed_multiplier', 50), 10)
        
        # シナリオ3: 精度エラー → 安全速度への変更
        precision_error = HighPrecisionTimingError(2.0, 12.0, 5.0, 50)  # 12ms偏差 > 5ms許容
        
        result = self.error_handler.handle_error(precision_error, "test_scenario_3")
        
        self.assertTrue(result['handled'])
        if result.get('recovery_applied', False):
            self.assertLessEqual(result.get('new_speed_multiplier', 50), 5)
    
    def test_error_cascading_prevention(self):
        """エラーカスケード防止テスト"""
        # 連続的なエラー発生をシミュレート
        errors = [
            InvalidSpeedMultiplierError(15),
            UltraHighSpeedError(50, "負荷過多"),
            HighPrecisionTimingError(4.0, 8.0, 5.0, 50),
            RealTimeSpeedChangeError(50, 5, "システム負荷"),
            ExecutionSyncError("timing", "0.02", "0.05")
        ]
        
        results = []
        for i, error in enumerate(errors):
            result = self.error_handler.handle_error(error, f"cascade_test_{i}")
            results.append(result)
            time.sleep(0.1)  # 短い間隔でエラー発生
        
        # 全てのエラーが処理されることを確認
        handled_count = sum(1 for r in results if r['handled'])
        self.assertEqual(handled_count, len(errors), "一部のエラーが未処理")
        
        # 連続エラーカウントが正しく記録されることを確認
        self.assertEqual(self.error_handler.consecutive_error_count, len(errors))
    
    def test_error_cooldown_mechanism_effectiveness(self):
        """エラークールダウン機構の効果テスト"""
        # 初期設定: 短いクールダウン期間
        self.error_handler.error_cooldown_seconds = 1
        
        error = InvalidSpeedMultiplierError(15)
        
        # 初回エラー処理
        result1 = self.error_handler.handle_error(error, "cooldown_test_1")
        self.assertTrue(result1['handled'])
        
        # クールダウン中のエラー処理（即座に実行）
        result2 = self.error_handler.handle_error(error, "cooldown_test_2")
        
        # クールダウン期間後のエラー処理
        time.sleep(1.2)  # クールダウン期間終了を待機
        result3 = self.error_handler.handle_error(error, "cooldown_test_3")
        self.assertTrue(result3['handled'])
    
    def test_automatic_recovery_with_real_components(self):
        """実コンポーネントでの自動復旧テスト"""
        # 実際の速度管理コンポーネントを使用してテスト
        
        # テスト1: 無効速度からの自動復旧
        initial_speed = self.speed_manager.current_speed_multiplier
        
        try:
            self.speed_manager.set_speed_multiplier(99)  # 無効速度
            self.fail("無効速度が設定されてしまった")
        except InvalidSpeedMultiplierError as e:
            result = handle_speed_control_error(e, self.speed_manager)
            
            self.assertTrue(result['recovery_applied'])
            recovered_speed = result['new_speed_multiplier']
            self.assertIn(recovered_speed, [1, 2, 3, 4, 5, 10, 50])
            self.assertEqual(self.speed_manager.current_speed_multiplier, recovered_speed)
        
        # テスト2: 超高速からの段階的降格
        self.speed_manager.set_speed_multiplier(50)
        
        ultra_error = UltraHighSpeedError(50, "高負荷による性能低下")
        result = handle_speed_control_error(ultra_error, self.speed_manager)
        
        if result['recovery_applied']:
            self.assertLessEqual(self.speed_manager.current_speed_multiplier, 10)
    
    def test_error_notification_system(self):
        """エラー通知システムテスト"""
        notification_received = []
        
        def test_notification_callback(notification_data):
            notification_received.append(notification_data)
        
        self.error_handler.add_notification_callback(test_notification_callback)
        
        # 複数種類のエラーで通知をテスト
        test_errors = [
            InvalidSpeedMultiplierError(25),
            UltraHighSpeedError(10, "軽微な負荷"),
            HighPrecisionTimingError(5.0, 7.0, 5.0, 10)
        ]
        
        for error in test_errors:
            self.error_handler.handle_error(error, "notification_test")
        
        # 通知が正しく送信されることを確認
        self.assertEqual(len(notification_received), len(test_errors))
        
        for i, notification in enumerate(notification_received):
            self.assertIn('error', notification)
            self.assertIn('recovery_result', notification)
            self.assertIn('timestamp', notification)
            self.assertEqual(notification['error'].__class__.__name__, 
                           test_errors[i].__class__.__name__)
    
    def test_error_statistics_tracking(self):
        """エラー統計追跡テスト"""
        # 初期統計をクリア
        _global_error_tracker.error_counts.clear()
        _global_error_tracker.recent_errors.clear()
        
        # 様々なエラーを発生させる
        error_types = [
            InvalidSpeedMultiplierError(15),
            InvalidSpeedMultiplierError(99),  # 同じタイプ
            UltraHighSpeedError(50, "負荷1"),
            HighPrecisionTimingError(2.0, 8.0, 5.0, 50),
            UltraHighSpeedError(10, "負荷2"),  # 同じタイプ
            SpeedDegradationError(50, 10, "連続失敗", 5)
        ]
        
        for error in error_types:
            self.error_handler.handle_error(error, "statistics_test")
        
        # 統計を取得して検証
        stats = self.error_handler.get_error_statistics()
        
        self.assertIn('global_statistics', stats)
        self.assertIn('handler_statistics', stats)
        
        global_stats = stats['global_statistics']
        self.assertEqual(global_stats['total_errors'], len(error_types))
        
        # エラータイプ別カウントの検証
        error_counts = global_stats['error_types']
        self.assertEqual(error_counts['InvalidSpeedMultiplierError'], 2)
        self.assertEqual(error_counts['UltraHighSpeedError'], 2)
        self.assertEqual(error_counts['HighPrecisionTimingError'], 1)
        self.assertEqual(error_counts['SpeedDegradationError'], 1)
    
    def test_error_recovery_under_concurrent_operations(self):
        """同時操作下でのエラー復旧テスト"""
        results = []
        
        def error_generation_worker(worker_id):
            """エラー生成ワーカー"""
            worker_errors = [
                InvalidSpeedMultiplierError(10 + worker_id),
                UltraHighSpeedError(50, f"Worker{worker_id}負荷"),
                HighPrecisionTimingError(2.0, 6.0, 5.0, 50)
            ]
            
            for error in worker_errors:
                try:
                    result = self.error_handler.handle_error(
                        error, f"concurrent_worker_{worker_id}"
                    )
                    results.append(('success', worker_id, result))
                except Exception as e:
                    results.append(('error', worker_id, str(e)))
        
        # 複数のワーカーを並行実行
        workers = []
        for i in range(3):
            worker = threading.Thread(target=error_generation_worker, args=(i,))
            workers.append(worker)
            worker.start()
        
        # 全ワーカー完了を待機
        for worker in workers:
            worker.join()
        
        # 結果検証
        successful_results = [r for r in results if r[0] == 'success']
        error_results = [r for r in results if r[0] == 'error']
        
        self.assertGreaterEqual(len(successful_results), 6, "同時操作でのエラー処理成功数不足")
        self.assertLessEqual(len(error_results), 3, "同時操作でのエラー処理失敗数過多")
        
        print(f"\n同時エラー処理結果:")
        print(f"  成功: {len(successful_results)}件")
        print(f"  失敗: {len(error_results)}件")


class TestSpeedControlErrorManager(unittest.TestCase):
    """速度制御エラーマネージャーテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.error_manager = SpeedControlErrorManager()
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
    
    def test_multiple_error_handler_management(self):
        """複数エラーハンドラー管理テスト"""
        # 複数の名前付きハンドラーを作成
        handler1 = self.error_manager.create_error_handler(
            "primary", 
            speed_manager=self.speed_manager,
            ultra_controller=self.ultra_controller
        )
        
        handler2 = self.error_manager.create_error_handler(
            "secondary",
            speed_manager=self.speed_manager
        )
        
        # ハンドラーが正しく管理されることを確認
        self.assertIsNotNone(self.error_manager.get_handler("primary"))
        self.assertIsNotNone(self.error_manager.get_handler("secondary"))
        self.assertIsNone(self.error_manager.get_handler("nonexistent"))
        
        # 各ハンドラーが独立して動作することを確認
        error1 = InvalidSpeedMultiplierError(15)
        error2 = UltraHighSpeedError(50, "負荷過多")
        
        result1 = handler1.handle_error(error1, "primary_test")
        result2 = handler2.handle_error(error2, "secondary_test")
        
        self.assertTrue(result1['handled'])
        self.assertTrue(result2['handled'])
    
    def test_global_error_handler_functionality(self):
        """グローバルエラーハンドラー機能テスト"""
        global_handler = SpeedControlErrorHandler(
            speed_manager=self.speed_manager,
            ultra_controller=self.ultra_controller
        )
        
        self.error_manager.set_global_handler(global_handler)
        
        # グローバルハンドラーが正しく設定されることを確認
        self.assertIsNotNone(self.error_manager.global_error_handler)
        self.assertEqual(self.error_manager.global_error_handler, global_handler)
    
    def test_integrated_statistics_collection(self):
        """統合統計収集テスト"""
        # 複数のハンドラーでエラーを処理
        handler1 = self.error_manager.create_error_handler("stats_test_1")
        handler2 = self.error_manager.create_error_handler("stats_test_2")
        
        # 各ハンドラーでエラーを処理
        errors1 = [InvalidSpeedMultiplierError(15), UltraHighSpeedError(50, "負荷")]
        errors2 = [HighPrecisionTimingError(2.0, 8.0, 5.0, 50)]
        
        for error in errors1:
            handler1.handle_error(error, "handler1_test")
        
        for error in errors2:
            handler2.handle_error(error, "handler2_test")
        
        # 統合統計を取得
        integrated_stats = self.error_manager.get_global_statistics()
        
        self.assertIn('handlers', integrated_stats)
        self.assertIn('global_error_tracker', integrated_stats)
        
        # 各ハンドラーの統計が含まれることを確認
        handler_stats = integrated_stats['handlers']
        self.assertIn('stats_test_1', handler_stats)
        self.assertIn('stats_test_2', handler_stats)


class TestErrorRecoveryScenarios(unittest.TestCase):
    """エラー復旧シナリオテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
        self.error_handler = SpeedControlErrorHandler(
            speed_manager=self.speed_manager,
            ultra_controller=self.ultra_controller
        )
    
    def test_progressive_speed_degradation_scenario(self):
        """段階的速度劣化シナリオテスト"""
        # x50 → 精度失敗 → x10 → 精度失敗 → x5 → 安定
        
        self.speed_manager.set_speed_multiplier(50)
        
        # 1回目の精度失敗（x50 → x10への降格）
        precision_error_1 = HighPrecisionTimingError(2.0, 12.0, 5.0, 50)  # 重大な精度失敗
        result_1 = self.error_handler.handle_error(precision_error_1, "degradation_1")
        
        if result_1.get('recovery_applied'):
            new_speed_1 = result_1.get('new_speed_multiplier')
            self.assertLessEqual(new_speed_1, 10)
            self.speed_manager.set_speed_multiplier(new_speed_1)  # 状態を更新
        
        # 2回目の精度失敗（x10 → x5への降格）
        precision_error_2 = HighPrecisionTimingError(10.0, 18.0, 10.0, 10)  # 10ms許容値超過
        result_2 = self.error_handler.handle_error(precision_error_2, "degradation_2")
        
        if result_2.get('recovery_applied'):
            new_speed_2 = result_2.get('new_speed_multiplier')
            self.assertLessEqual(new_speed_2, 5)
        
        # 最終的に安全な速度に到達することを確認
        final_speed = self.speed_manager.current_speed_multiplier
        self.assertLessEqual(final_speed, 5, "段階的劣化が適切に実行されなかった")
    
    def test_emergency_fallback_scenario(self):
        """緊急フォールバックシナリオテスト"""
        # システム負荷過多によりx50からx1への緊急降格
        
        self.speed_manager.set_speed_multiplier(50)
        
        # 緊急事態のシミュレート（連続的な重大エラー）
        critical_errors = [
            UltraHighSpeedError(50, "システムメモリ不足"),
            HighPrecisionTimingError(2.0, 25.0, 5.0, 50),  # 5倍の偏差
            ExecutionSyncError("ultra_controller", "active", "failed")
        ]
        
        for error in critical_errors:
            result = self.error_handler.handle_error(error, "emergency_scenario")
            
            # エラー処理により速度が下がることを期待
            current_speed = self.speed_manager.current_speed_multiplier
            if result.get('recovery_applied'):
                self.assertLessEqual(current_speed, 50)
        
        # 最終的に安全速度（x5以下）に到達することを確認
        final_speed = self.speed_manager.current_speed_multiplier
        self.assertLessEqual(final_speed, 5, "緊急フォールバックが不十分")
    
    def test_recovery_history_tracking(self):
        """復旧履歴追跡テスト"""
        # 複数の復旧処理を実行
        recovery_scenarios = [
            InvalidSpeedMultiplierError(15),
            UltraHighSpeedError(50, "負荷問題"),
            HighPrecisionTimingError(4.0, 9.0, 5.0, 50)
        ]
        
        for error in recovery_scenarios:
            self.error_handler.handle_error(error, "history_test")
        
        # 復旧履歴が正しく記録されることを確認
        stats = self.error_handler.get_error_statistics()
        recovery_history = stats['recovery_history']
        
        self.assertGreaterEqual(len(recovery_history), 1, "復旧履歴が記録されていない")
        
        # 各復旧記録に必要な情報が含まれることを確認
        for recovery in recovery_history:
            self.assertIn('error_type', recovery)
            self.assertIn('timestamp', recovery)
            self.assertIn('recovery_action', recovery)
            self.assertIn('success', recovery)


if __name__ == '__main__':
    # テストスイート実行
    unittest.main(verbosity=2)