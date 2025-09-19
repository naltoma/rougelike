#!/usr/bin/env python3
"""
🆕 v1.2.1: PauseControllerのUnit Tests
テスト対象: 一時停止制御、PAUSE_PENDING状態管理、アクション境界での一時停止
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from engine.pause_controller import PauseController
from engine import ExecutionMode, PauseRequest, PauseControlError


class TestPauseController(unittest.TestCase):
    """PauseControllerのテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.controller = PauseController()
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNone(self.controller.pause_request)
        self.assertFalse(self.controller.pause_pending)
        self.assertIsNone(self.controller.last_pause_time)
    
    def test_request_pause_at_next_action(self):
        """次アクション境界での一時停止要求テスト"""
        # 一時停止要求
        request = self.controller.request_pause_at_next_action("test_user")
        
        # 結果検証
        self.assertIsNotNone(request)
        self.assertEqual(request.requester, "test_user")
        self.assertEqual(request.target_boundary, "next_action")
        self.assertFalse(request.fulfilled)
        self.assertTrue(self.controller.pause_pending)
        self.assertEqual(self.controller.pause_request, request)
    
    def test_request_pause_with_existing_request(self):
        """既存の要求がある場合の一時停止要求テスト"""
        # 最初の要求
        first_request = self.controller.request_pause_at_next_action("user1")
        
        # 2番目の要求（既存を上書き）
        second_request = self.controller.request_pause_at_next_action("user2")
        
        # 結果検証
        self.assertNotEqual(first_request, second_request)
        self.assertEqual(second_request.requester, "user2")
        self.assertTrue(self.controller.pause_pending)
        self.assertEqual(self.controller.pause_request, second_request)
    
    def test_is_pause_pending(self):
        """一時停止要求確認テスト"""
        # 初期状態: 要求なし
        self.assertFalse(self.controller.is_pause_pending())
        
        # 一時停止要求後: 要求あり
        self.controller.request_pause_at_next_action("test_user")
        self.assertTrue(self.controller.is_pause_pending())
        
        # 要求が実行された後: 要求なし
        self.controller.execute_pause_at_boundary()
        self.assertFalse(self.controller.is_pause_pending())
    
    def test_execute_pause_at_boundary(self):
        """境界での一時停止実行テスト"""
        # 一時停止要求を作成
        request = self.controller.request_pause_at_next_action("test_user")
        
        # 境界で一時停止を実行
        result = self.controller.execute_pause_at_boundary()
        
        # 結果検証
        self.assertTrue(result)
        self.assertTrue(request.fulfilled)
        self.assertFalse(self.controller.pause_pending)
        self.assertIsNotNone(self.controller.last_pause_time)
    
    def test_execute_pause_without_request(self):
        """要求なしでの一時停止実行テスト（エラーケース）"""
        result = self.controller.execute_pause_at_boundary()
        
        # 結果検証
        self.assertFalse(result)
        self.assertFalse(self.controller.pause_pending)
        self.assertIsNone(self.controller.last_pause_time)
    
    def test_cancel_pause_request(self):
        """一時停止要求キャンセルテスト"""
        # 一時停止要求を作成
        request = self.controller.request_pause_at_next_action("test_user")
        
        # 要求をキャンセル
        result = self.controller.cancel_pause_request()
        
        # 結果検証
        self.assertTrue(result)
        self.assertTrue(request.fulfilled)
        self.assertFalse(self.controller.pause_pending)
    
    def test_cancel_pause_request_without_request(self):
        """要求なしでのキャンセルテスト"""
        result = self.controller.cancel_pause_request()
        
        # 結果検証
        self.assertFalse(result)
    
    def test_get_pause_status(self):
        """一時停止状態取得テスト"""
        # 初期状態
        status = self.controller.get_pause_status()
        self.assertFalse(status["is_pending"])
        self.assertFalse(status["has_request"])
        self.assertIsNone(status["last_pause_time"])
        
        # 一時停止要求後
        self.controller.request_pause_at_next_action("test_user")
        status = self.controller.get_pause_status()
        self.assertTrue(status["is_pending"])
        self.assertTrue(status["has_request"])
        self.assertEqual(status["requester"], "test_user")
        self.assertEqual(status["target_boundary"], "next_action")
        self.assertFalse(status["fulfilled"])
    
    def test_handle_continuous_mode_pause(self):
        """連続実行モードでの一時停止処理テスト"""
        # 一時停止要求なし: モード変更なし
        result_mode = self.controller.handle_continuous_mode_pause(ExecutionMode.CONTINUOUS)
        self.assertEqual(result_mode, ExecutionMode.CONTINUOUS)
        
        # 一時停止要求あり: PAUSE_PENDINGに変更
        self.controller.request_pause_at_next_action("test_user")
        result_mode = self.controller.handle_continuous_mode_pause(ExecutionMode.CONTINUOUS)
        self.assertEqual(result_mode, ExecutionMode.PAUSE_PENDING)
        
        # 他のモード: 変更なし
        result_mode = self.controller.handle_continuous_mode_pause(ExecutionMode.PAUSED)
        self.assertEqual(result_mode, ExecutionMode.PAUSED)
    
    def test_should_pause_at_boundary(self):
        """境界での一時停止判定テスト"""
        # 境界なし: False
        self.assertFalse(self.controller.should_pause_at_boundary(False))
        
        # 境界あり、要求なし: False
        self.assertFalse(self.controller.should_pause_at_boundary(True))
        
        # 境界あり、要求あり: True
        self.controller.request_pause_at_next_action("test_user")
        self.assertTrue(self.controller.should_pause_at_boundary(True))
    
    def test_get_pause_timing_info(self):
        """一時停止タイミング情報取得テスト"""
        # 要求なし
        timing_info = self.controller.get_pause_timing_info()
        self.assertFalse(timing_info["pending_pause"])
        self.assertEqual(timing_info["target_timing"], "next_action_boundary")
        
        # 要求あり
        self.controller.request_pause_at_next_action("test_user")
        timing_info = self.controller.get_pause_timing_info()
        self.assertTrue(timing_info["pending_pause"])
        self.assertIn("request_age_ms", timing_info)
        self.assertEqual(timing_info["target_boundary"], "next_action")
    
    def test_reset(self):
        """リセット機能テスト"""
        # 状態を変更
        self.controller.request_pause_at_next_action("test_user")
        self.controller.last_pause_time = datetime.now()
        
        # リセット実行
        self.controller.reset()
        
        # 初期状態に戻ることを確認
        self.assertIsNone(self.controller.pause_request)
        self.assertFalse(self.controller.pause_pending)
        self.assertIsNone(self.controller.last_pause_time)
    
    def test_validate_pause_response_time(self):
        """一時停止応答時間検証テスト"""
        # 要求なし: True
        self.assertTrue(self.controller.validate_pause_response_time())
        
        # 要求後すぐ: True
        self.controller.request_pause_at_next_action("test_user")
        self.assertTrue(self.controller.validate_pause_response_time())
        
        # 要求を過去に設定してタイムアウトをシミュレート
        self.controller.pause_request.requested_at = datetime.now() - timedelta(milliseconds=100)
        self.assertFalse(self.controller.validate_pause_response_time(50.0))
    
    def test_get_performance_metrics(self):
        """パフォーマンスメトリクス取得テスト"""
        # 要求なし
        metrics = self.controller.get_performance_metrics()
        self.assertFalse(metrics["has_active_request"])
        self.assertFalse(metrics["pause_pending"])
        
        # 要求あり
        self.controller.request_pause_at_next_action("test_user")
        metrics = self.controller.get_performance_metrics()
        self.assertTrue(metrics["has_active_request"])
        self.assertTrue(metrics["pause_pending"])
        self.assertIn("request_age_ms", metrics)
        self.assertIn("response_time_valid", metrics)
    
    @patch('engine.pause_controller.logger')
    def test_error_handling(self, mock_logger):
        """エラーハンドリングテスト"""
        # モックでエラーを発生させる
        with patch.object(self.controller, '_lock') as mock_lock:
            mock_lock.__enter__.side_effect = Exception("Test error")
            
            # エラーが適切に処理されることを確認
            with self.assertRaises(PauseControlError):
                self.controller.request_pause_at_next_action("test_user")
    
    def test_str_representation(self):
        """文字列表現テスト"""
        # 初期状態
        str_repr = str(self.controller)
        self.assertIn("PauseController", str_repr)
        self.assertIn("status=idle", str_repr)
        self.assertIn("has_request=False", str_repr)
        
        # 要求後
        self.controller.request_pause_at_next_action("test_user")
        str_repr = str(self.controller)
        self.assertIn("status=pending", str_repr)
        self.assertIn("has_request=True", str_repr)
    
    @patch('engine.pause_controller.logger')
    def test_logging_behavior(self, mock_logger):
        """ロギング動作テスト"""
        # 一時停止要求でログ出力を確認
        self.controller.request_pause_at_next_action("test_user")
        self.assertTrue(mock_logger.info.called)
        
        # 一時停止実行でログ出力を確認
        self.controller.execute_pause_at_boundary()
        self.assertTrue(mock_logger.info.called)
    
    def test_nfr_response_time_compliance(self):
        """NFR-001.1: 50ms応答時間要件テスト"""
        start_time = datetime.now()
        
        # 一時停止要求
        self.controller.request_pause_at_next_action("test_user")
        
        response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # 50ms以内での応答を確認
        self.assertLess(response_time_ms, 50.0)
    
    def test_concurrent_access_safety(self):
        """スレッドセーフティテスト（基本）"""
        import threading
        import time
        
        results = []
        
        def make_pause_request(requester_id):
            try:
                request = self.controller.request_pause_at_next_action(f"user_{requester_id}")
                results.append(request.requester)
            except Exception as e:
                results.append(f"error_{requester_id}")
        
        # 複数スレッドで同時に要求
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_pause_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()
        
        # 結果確認（最終的に1つの要求が残る）
        self.assertEqual(len(results), 5)
        self.assertIsNotNone(self.controller.pause_request)


if __name__ == '__main__':
    unittest.main()