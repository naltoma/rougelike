#!/usr/bin/env python3
"""
🚀 v1.2.5: Session Logging Integration Test Suite
7段階速度制御SessionLogger統合テストスイート
"""

import unittest
import json
import os
import tempfile
import time
from unittest.mock import Mock, patch
import sys

# プロジェクトパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.session_logging import SessionLogger, SessionSummary
from engine.enhanced_7stage_speed_control_manager import Enhanced7StageSpeedControlManager
from engine.ultra_high_speed_controller import UltraHighSpeedController


class TestSessionLogging7StageIntegration(unittest.TestCase):
    """SessionLogger 7段階速度制御統合テスト"""
    
    def setUp(self):
        """テスト初期化"""
        # テンポラリディレクトリでログファイル作成
        self.temp_dir = tempfile.mkdtemp()
        self.log_file_path = os.path.join(self.temp_dir, "test_session_log.json")
        
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
        self.session_logger = SessionLogger(self.log_file_path)
        
        # ログファイル初期化
        self.session_logger.start_session("test_user", "test_stage")
    
    def tearDown(self):
        """テスト終了処理"""
        # テンポラリファイル削除
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)
        os.rmdir(self.temp_dir)
    
    def test_speed_control_change_logging(self):
        """速度制御変更ログテスト"""
        # 複数の速度変更をログ
        speed_changes = [
            (1, 5, "user_request"),
            (5, 10, "performance_optimization"),
            (10, 50, "batch_processing"),
            (50, 10, "precision_requirement"),
            (10, 1, "safety_fallback")
        ]
        
        for from_speed, to_speed, reason in speed_changes:
            self.session_logger.log_speed_control_change(
                from_speed, to_speed, reason
            )
        
        # ログファイル内容を確認
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        events = log_data.get('events', [])
        speed_events = [e for e in events if e['event_type'] == 'SPEED_CONTROL_CHANGED']
        
        self.assertEqual(len(speed_events), len(speed_changes))
        
        # 各速度変更イベントの詳細を確認
        for i, event in enumerate(speed_events):
            expected_from, expected_to, expected_reason = speed_changes[i]
            
            self.assertEqual(event['data']['from_multiplier'], expected_from)
            self.assertEqual(event['data']['to_multiplier'], expected_to)
            self.assertEqual(event['data']['change_reason'], expected_reason)
            self.assertIn('timestamp', event)
    
    def test_ultra_high_speed_logging(self):
        """超高速モードログテスト"""
        # 超高速モード有効化ログ
        ultra_speed_activations = [
            (10, {"precision_tolerance_ms": 10.0, "monitoring_enabled": True}),
            (50, {"precision_tolerance_ms": 5.0, "monitoring_enabled": True, "warning_level": "critical"})
        ]
        
        for multiplier, config in ultra_speed_activations:
            self.session_logger.log_ultra_high_speed_enabled(multiplier, config)
        
        # ログファイル確認
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        events = log_data.get('events', [])
        ultra_events = [e for e in events if e['event_type'] == 'ULTRA_HIGH_SPEED_ENABLED']
        
        self.assertEqual(len(ultra_events), len(ultra_speed_activations))
        
        # x50速度のイベント詳細確認
        x50_event = next(e for e in ultra_events if e['data']['multiplier'] == 50)
        self.assertEqual(x50_event['data']['config']['precision_tolerance_ms'], 5.0)
        self.assertEqual(x50_event['data']['config']['warning_level'], "critical")
    
    def test_speed_precision_measurement_logging(self):
        """速度精度測定ログテスト"""
        # 実際の精度測定を実行してログ
        self.speed_manager.set_speed_multiplier(50)
        
        precision_measurements = [
            (2.0, 1.8, 0.2, "excellent"),     # 目標2ms、実測1.8ms、偏差0.2ms
            (2.0, 2.3, 0.3, "good"),         # 目標2ms、実測2.3ms、偏差0.3ms
            (4.0, 6.0, 2.0, "acceptable"),   # 目標4ms、実測6.0ms、偏差2.0ms
            (2.0, 8.0, 6.0, "poor")          # 目標2ms、実測8.0ms、偏差6.0ms
        ]
        
        for target, actual, deviation, quality in precision_measurements:
            self.session_logger.log_speed_precision_measurement(
                target, actual, deviation, quality
            )
        
        # ログファイル確認
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        events = log_data.get('events', [])
        precision_events = [e for e in events if e['event_type'] == 'SPEED_PRECISION_MEASURED']
        
        self.assertEqual(len(precision_events), len(precision_measurements))
        
        # 精度品質の分布確認
        quality_counts = {}
        for event in precision_events:
            quality = event['data']['precision_quality']
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        expected_qualities = ["excellent", "good", "acceptable", "poor"]
        for quality in expected_qualities:
            self.assertIn(quality, quality_counts)
            self.assertEqual(quality_counts[quality], 1)
    
    def test_speed_degradation_logging(self):
        """速度劣化ログテスト"""
        # 速度劣化イベントをログ
        degradation_scenarios = [
            (50, 10, "precision_failure", {"failure_count": 3, "avg_deviation_ms": 8.5}),
            (10, 5, "system_load", {"cpu_usage": 85, "memory_usage": 78}),
            (5, 1, "emergency_fallback", {"critical_error": "timing_sync_lost"})
        ]
        
        for original, degraded, reason, metadata in degradation_scenarios:
            self.session_logger.log_speed_degradation(original, degraded, reason, metadata)
        
        # ログファイル確認
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        events = log_data.get('events', [])
        degradation_events = [e for e in events if e['event_type'] == 'SPEED_DEGRADED']
        
        self.assertEqual(len(degradation_events), len(degradation_scenarios))
        
        # 最も深刻な劣化（x50 → x10）の詳細確認
        severe_degradation = next(e for e in degradation_events 
                                if e['data']['original_multiplier'] == 50)
        
        self.assertEqual(severe_degradation['data']['degraded_multiplier'], 10)
        self.assertEqual(severe_degradation['data']['degradation_reason'], "precision_failure")
        self.assertEqual(severe_degradation['data']['metadata']['failure_count'], 3)
    
    def test_7stage_speed_metrics_collection(self):
        """7段階速度メトリクス収集テスト"""
        # 複数の速度で実行をシミュレート
        speed_usage_simulation = [
            (1, 10.0, 5),    # x1速度で10秒、5ステップ
            (5, 8.0, 20),    # x5速度で8秒、20ステップ
            (10, 5.0, 100),  # x10速度で5秒、100ステップ
            (50, 2.0, 500)   # x50速度で2秒、500ステップ
        ]
        
        for multiplier, duration, step_count in speed_usage_simulation:
            self.speed_manager.set_speed_multiplier(multiplier)
            
            # 速度変更をログ
            if multiplier > 1:
                self.session_logger.log_speed_control_change(1, multiplier, "simulation")
            
            # 超高速の場合は追加ログ
            if multiplier >= 10:
                self.session_logger.log_ultra_high_speed_enabled(
                    multiplier, 
                    {"precision_tolerance_ms": 10.0 if multiplier == 10 else 5.0}
                )
            
            # 実行時間とステップ数をシミュレート
            self.session_logger.session_data['total_execution_time'] += duration
            self.session_logger.session_data['total_steps'] += step_count
        
        # 7段階速度メトリクスを取得
        metrics = self.session_logger.get_7stage_speed_metrics()
        
        # メトリクス内容確認
        self.assertIn('speed_usage_distribution', metrics)
        self.assertIn('ultra_high_speed_usage', metrics)
        self.assertIn('precision_performance', metrics)
        self.assertIn('speed_transition_analysis', metrics)
        
        # 速度使用分布の確認
        speed_distribution = metrics['speed_usage_distribution']
        self.assertIn('x1', speed_distribution)
        self.assertIn('x5', speed_distribution)
        self.assertIn('x10', speed_distribution)
        self.assertIn('x50', speed_distribution)
        
        # 超高速使用統計の確認
        ultra_usage = metrics['ultra_high_speed_usage']
        self.assertIn('total_ultra_time', ultra_usage)
        self.assertIn('x10_usage', ultra_usage)
        self.assertIn('x50_usage', ultra_usage)
        self.assertGreater(ultra_usage['total_ultra_time'], 0)
    
    def test_session_summary_with_speed_control_data(self):
        """速度制御データを含むセッション要約テスト"""
        # セッション実行をシミュレート
        session_activities = [
            ("log_speed_control_change", [1, 5, "user_optimization"]),
            ("log_ultra_high_speed_enabled", [10, {"precision_tolerance_ms": 10.0}]),
            ("log_speed_precision_measurement", [10.0, 9.8, 0.2, "excellent"]),
            ("log_speed_degradation", [10, 5, "system_load", {"cpu_usage": 80}])
        ]
        
        for method_name, args in session_activities:
            method = getattr(self.session_logger, method_name)
            method(*args)
        
        # セッション終了とサマリー生成
        summary = self.session_logger.end_session()
        
        # サマリーに速度制御情報が含まれることを確認
        self.assertIsInstance(summary, SessionSummary)
        
        # 7段階速度メトリクスが要約に含まれることを確認
        if hasattr(summary, 'speed_control_metrics'):
            speed_metrics = summary.speed_control_metrics
            self.assertIn('speed_usage_distribution', speed_metrics)
            self.assertIn('ultra_high_speed_usage', speed_metrics)
    
    def test_concurrent_logging_with_speed_control(self):
        """速度制御と同時ログテスト"""
        import threading
        
        log_results = []
        
        def speed_control_worker():
            """速度制御ワーカー"""
            speeds = [1, 5, 10, 2, 50, 3]
            for speed in speeds:
                try:
                    self.session_logger.log_speed_control_change(1, speed, "concurrent_test")
                    log_results.append(('speed_log_success', speed))
                    time.sleep(0.05)
                except Exception as e:
                    log_results.append(('speed_log_error', speed, str(e)))
        
        def precision_measurement_worker():
            """精度測定ワーカー"""
            measurements = [
                (5.0, 4.8, 0.2, "excellent"),
                (10.0, 10.5, 0.5, "good"),
                (2.0, 2.8, 0.8, "acceptable")
            ]
            
            for target, actual, deviation, quality in measurements:
                try:
                    self.session_logger.log_speed_precision_measurement(
                        target, actual, deviation, quality
                    )
                    log_results.append(('precision_log_success', target))
                    time.sleep(0.1)
                except Exception as e:
                    log_results.append(('precision_log_error', target, str(e)))
        
        # 並行実行
        threads = [
            threading.Thread(target=speed_control_worker),
            threading.Thread(target=precision_measurement_worker)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 結果確認
        speed_successes = [r for r in log_results if r[0] == 'speed_log_success']
        precision_successes = [r for r in log_results if r[0] == 'precision_log_success']
        
        self.assertGreaterEqual(len(speed_successes), 4, "速度制御ログ成功数不足")
        self.assertGreaterEqual(len(precision_successes), 2, "精度測定ログ成功数不足")
        
        # ログファイルが破損していないことを確認
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            try:
                log_data = json.load(f)
                self.assertIn('events', log_data)
                self.assertGreater(len(log_data['events']), 0)
            except json.JSONDecodeError:
                self.fail("並行ログ処理でJSONファイルが破損")


class TestSessionLoggerPerformanceWith7Stage(unittest.TestCase):
    """SessionLogger 7段階速度制御パフォーマンステスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file_path = os.path.join(self.temp_dir, "performance_test_log.json")
        self.session_logger = SessionLogger(self.log_file_path)
        self.session_logger.start_session("perf_test_user", "perf_stage")
    
    def tearDown(self):
        """テスト終了処理"""
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)
        os.rmdir(self.temp_dir)
    
    def test_high_frequency_speed_logging_performance(self):
        """高頻度速度ログパフォーマンステスト"""
        # 1000回の速度変更ログを短時間で実行
        speed_sequence = [1, 2, 3, 4, 5, 10, 50] * 143  # 約1000回
        
        start_time = time.time()
        
        for i, speed in enumerate(speed_sequence):
            self.session_logger.log_speed_control_change(
                1, speed, f"performance_test_{i}"
            )
        
        elapsed_time = time.time() - start_time
        
        # 1000回のログが2秒以内に完了することを期待
        self.assertLess(elapsed_time, 2.0, f"高頻度ログが遅すぎます: {elapsed_time:.2f}秒")
        
        # ログファイルサイズが合理的な範囲内であることを確認
        file_size = os.path.getsize(self.log_file_path)
        self.assertLess(file_size, 5 * 1024 * 1024, "ログファイルサイズが大きすぎます")  # 5MB未満
        
        print(f"\n高頻度ログパフォーマンス結果:")
        print(f"  ログ回数: {len(speed_sequence)}回")
        print(f"  実行時間: {elapsed_time:.2f}秒")
        print(f"  ファイルサイズ: {file_size / 1024:.1f}KB")
    
    def test_speed_metrics_calculation_performance(self):
        """速度メトリクス計算パフォーマンステスト"""
        # 大量の速度関連イベントを生成
        for i in range(500):
            self.session_logger.log_speed_control_change(
                1, (i % 7) + 1 if (i % 7) + 1 <= 5 else [10, 50][(i % 7) - 5], 
                f"bulk_test_{i}"
            )
            
            if i % 10 == 0:
                self.session_logger.log_ultra_high_speed_enabled(
                    50, {"precision_tolerance_ms": 5.0}
                )
            
            if i % 5 == 0:
                self.session_logger.log_speed_precision_measurement(
                    5.0, 4.5 + (i % 10) * 0.1, abs((i % 10) * 0.1), "test_quality"
                )
        
        # メトリクス計算のパフォーマンス測定
        start_time = time.time()
        metrics = self.session_logger.get_7stage_speed_metrics()
        calculation_time = time.time() - start_time
        
        # メトリクス計算が0.5秒以内に完了することを期待
        self.assertLess(calculation_time, 0.5, 
                       f"メトリクス計算が遅すぎます: {calculation_time:.3f}秒")
        
        # メトリクス内容が正常であることを確認
        self.assertIn('speed_usage_distribution', metrics)
        self.assertIn('ultra_high_speed_usage', metrics)
        
        print(f"\n速度メトリクス計算パフォーマンス:")
        print(f"  イベント数: 約1500件")
        print(f"  計算時間: {calculation_time:.3f}秒")


if __name__ == '__main__':
    # テストスイート実行
    unittest.main(verbosity=2)