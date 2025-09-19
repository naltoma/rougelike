#!/usr/bin/env python3
"""
🆕 v1.2.1: ActionBoundaryDetectorのUnit Tests
テスト対象: アクション境界検出機能、シーケンス管理、実行モード対応
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from engine.action_boundary_detector import ActionBoundaryDetector
from engine import ExecutionMode, ActionBoundary


class TestActionBoundaryDetector(unittest.TestCase):
    """ActionBoundaryDetectorのテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.detector = ActionBoundaryDetector()
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.detector.action_sequence, 0)
        self.assertEqual(self.detector.pending_actions, 0)
        self.assertFalse(self.detector.in_action_execution)
        self.assertIsNone(self.detector.current_action_start_time)
        self.assertEqual(len(self.detector.boundary_history), 0)
    
    def test_mark_action_start(self):
        """アクション開始マーク機能テスト"""
        # アクション開始をマーク
        result = self.detector.mark_action_start("test_action")
        
        # 結果検証
        self.assertTrue(result)
        self.assertEqual(self.detector.action_sequence, 1)
        self.assertEqual(self.detector.pending_actions, 1)
        self.assertTrue(self.detector.in_action_execution)
        self.assertIsNotNone(self.detector.current_action_start_time)
        self.assertEqual(self.detector.current_action_name, "test_action")
    
    def test_mark_action_complete(self):
        """アクション完了マーク機能テスト"""
        # 事前準備: アクション開始
        self.detector.mark_action_start("test_action")
        
        # アクション完了をマーク  
        result = self.detector.mark_action_complete("test_action")
        
        # 結果検証
        self.assertTrue(result)
        self.assertEqual(self.detector.pending_actions, 0)
        self.assertFalse(self.detector.in_action_execution)
        self.assertIsNone(self.detector.current_action_start_time)
        self.assertEqual(len(self.detector.boundary_history), 1)
        
        # 境界履歴の確認
        boundary = self.detector.boundary_history[0]
        self.assertEqual(boundary.action_name, "test_action")
        self.assertEqual(boundary.sequence_number, 1)
        self.assertTrue(boundary.success)
    
    def test_mark_action_complete_without_start(self):
        """開始マークなしでの完了マークテスト（エラーケース）"""
        result = self.detector.mark_action_complete("test_action")
        
        # 結果検証
        self.assertFalse(result)
        self.assertEqual(self.detector.pending_actions, 0)
        self.assertFalse(self.detector.in_action_execution)
    
    def test_detect_boundary_step_mode(self):
        """ステップモードでの境界検出テスト"""
        # ステップモードで境界検出
        boundary = self.detector.detect_boundary(ExecutionMode.STEPPING)
        
        # 結果検証
        self.assertIsNotNone(boundary)
        self.assertEqual(boundary.boundary_type, "step_ready")
        self.assertEqual(boundary.execution_mode, ExecutionMode.STEPPING)
        self.assertTrue(boundary.allows_step_execution)
    
    def test_detect_boundary_continuous_mode_with_pending_action(self):
        """連続モード・保留アクションありでの境界検出テスト"""
        # アクションを開始状態にする
        self.detector.mark_action_start("test_action")
        
        # 連続モードで境界検出
        boundary = self.detector.detect_boundary(ExecutionMode.CONTINUOUS)
        
        # 結果検証
        self.assertIsNotNone(boundary)
        self.assertEqual(boundary.boundary_type, "action_in_progress")
        self.assertFalse(boundary.allows_step_execution)
        self.assertTrue(boundary.has_pending_actions)
    
    def test_detect_boundary_continuous_mode_no_pending_action(self):
        """連続モード・保留アクションなしでの境界検出テスト"""
        # 連続モードで境界検出
        boundary = self.detector.detect_boundary(ExecutionMode.CONTINUOUS)
        
        # 結果検証
        self.assertIsNotNone(boundary)
        self.assertEqual(boundary.boundary_type, "continuous_ready")
        self.assertTrue(boundary.allows_step_execution)
        self.assertFalse(boundary.has_pending_actions)
    
    def test_should_allow_step_execution(self):
        """ステップ実行許可判定テスト"""
        # 初期状態: 許可
        self.assertTrue(self.detector.should_allow_step_execution())
        
        # アクション実行中: 不許可
        self.detector.mark_action_start("test_action")
        self.assertFalse(self.detector.should_allow_step_execution())
        
        # アクション完了: 許可
        self.detector.mark_action_complete("test_action")
        self.assertTrue(self.detector.should_allow_step_execution())
    
    def test_get_action_status(self):
        """アクション状態取得テスト"""
        # 初期状態
        status = self.detector.get_action_status()
        self.assertEqual(status["sequence_number"], 0)
        self.assertEqual(status["pending_actions"], 0)
        self.assertFalse(status["in_execution"])
        self.assertIsNone(status["current_action"])
        
        # アクション実行中
        self.detector.mark_action_start("test_action")
        status = self.detector.get_action_status()
        self.assertEqual(status["sequence_number"], 1)
        self.assertEqual(status["pending_actions"], 1)
        self.assertTrue(status["in_execution"])
        self.assertEqual(status["current_action"], "test_action")
    
    def test_get_boundary_history(self):
        """境界履歴取得テスト"""
        # 複数のアクションを実行
        for i in range(3):
            action_name = f"action_{i}"
            self.detector.mark_action_start(action_name)
            self.detector.mark_action_complete(action_name)
        
        # 履歴取得
        history = self.detector.get_boundary_history(limit=2)
        self.assertEqual(len(history), 2)
        
        # 最新の履歴が先頭に来ることを確認
        self.assertEqual(history[0].action_name, "action_2")
        self.assertEqual(history[1].action_name, "action_1")
    
    def test_clear_boundary_history(self):
        """境界履歴クリアテスト"""
        # 履歴を作成
        self.detector.mark_action_start("test_action")
        self.detector.mark_action_complete("test_action")
        
        # 履歴クリア
        self.detector.clear_boundary_history()
        self.assertEqual(len(self.detector.boundary_history), 0)
    
    def test_reset(self):
        """リセット機能テスト"""
        # 状態を変更
        self.detector.mark_action_start("test_action")
        
        # リセット実行
        self.detector.reset()
        
        # 初期状態に戻ることを確認
        self.assertEqual(self.detector.action_sequence, 0)
        self.assertEqual(self.detector.pending_actions, 0)
        self.assertFalse(self.detector.in_action_execution)
        self.assertIsNone(self.detector.current_action_start_time)
        self.assertEqual(len(self.detector.boundary_history), 0)
    
    def test_sequence_number_increment(self):
        """シーケンス番号増加テスト"""
        # 複数アクションでシーケンス番号の増加を確認
        for i in range(5):
            self.detector.mark_action_start(f"action_{i}")
            self.assertEqual(self.detector.action_sequence, i + 1)
            self.detector.mark_action_complete(f"action_{i}")
    
    def test_boundary_history_size_limit(self):
        """境界履歴サイズ制限テスト"""
        # 制限を超える数の履歴を作成
        for i in range(55):  # 制限は50
            self.detector.mark_action_start(f"action_{i}")
            self.detector.mark_action_complete(f"action_{i}")
        
        # 履歴サイズが制限内であることを確認
        self.assertLessEqual(len(self.detector.boundary_history), 50)
        
        # 最新の履歴が保持されていることを確認
        history = self.detector.get_boundary_history(limit=1)
        self.assertEqual(history[0].action_name, "action_54")
    
    @patch('engine.action_boundary_detector.logger')
    def test_logging_behavior(self, mock_logger):
        """ロギング動作テスト"""
        # アクション開始・完了でログ出力を確認
        self.detector.mark_action_start("test_action")
        self.detector.mark_action_complete("test_action")
        
        # ログ呼び出しを確認
        self.assertTrue(mock_logger.debug.called)
    
    def test_performance_validation(self):
        """パフォーマンス検証テスト"""
        start_time = datetime.now()
        
        # 大量のアクション処理
        for i in range(100):
            self.detector.mark_action_start(f"action_{i}")
            self.detector.mark_action_complete(f"action_{i}")
        
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # 100アクションが100ms以内で処理されることを確認
        self.assertLess(execution_time_ms, 100.0)


if __name__ == '__main__':
    unittest.main()