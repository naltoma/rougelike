#!/usr/bin/env python3
"""
🆕 v1.2.1: StateTransitionManagerのUnit Tests
テスト対象: 状態遷移管理、妥当性検証、ロールバック機能
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from engine.state_transition_manager import StateTransitionManager, TransitionResult
from engine import ExecutionMode, StateTransitionError


class TestStateTransitionManager(unittest.TestCase):
    """StateTransitionManagerのテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.manager = StateTransitionManager()
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.manager.current_state, ExecutionMode.PAUSED)
        self.assertIsNone(self.manager.previous_state)
        self.assertEqual(len(self.manager.transition_history), 0)
        self.assertIsNotNone(self.manager.transition_matrix)
    
    def test_transition_matrix_structure(self):
        """遷移マトリックス構造テスト"""
        matrix = self.manager.transition_matrix
        
        # 全ExecutionModeが定義されている
        for mode in ExecutionMode:
            self.assertIn(mode, matrix)
        
        # PAUSED状態から可能な遷移を確認
        paused_transitions = matrix[ExecutionMode.PAUSED]
        expected_transitions = [
            ExecutionMode.STEPPING,
            ExecutionMode.CONTINUOUS,
            ExecutionMode.RESET,
            ExecutionMode.COMPLETED,
            ExecutionMode.ERROR
        ]
        for expected in expected_transitions:
            self.assertIn(expected, paused_transitions)
    
    def test_valid_transition(self):
        """有効な状態遷移テスト"""
        # PAUSED → STEPPING (有効)
        result = self.manager.transition_to(ExecutionMode.STEPPING, "user_step_request")
        
        # 結果検証
        self.assertTrue(result.success)
        self.assertEqual(result.from_state, ExecutionMode.PAUSED)
        self.assertEqual(result.to_state, ExecutionMode.STEPPING)
        self.assertEqual(self.manager.current_state, ExecutionMode.STEPPING)
        self.assertEqual(self.manager.previous_state, ExecutionMode.PAUSED)
        self.assertEqual(len(self.manager.transition_history), 1)
    
    def test_invalid_transition(self):
        """無効な状態遷移テスト"""
        # PAUSED → STEP_EXECUTING (無効)
        result = self.manager.transition_to(ExecutionMode.STEP_EXECUTING, "invalid_request")
        
        # 結果検証
        self.assertFalse(result.success)
        self.assertEqual(result.from_state, ExecutionMode.PAUSED)
        self.assertEqual(result.to_state, ExecutionMode.STEP_EXECUTING)
        self.assertIsNotNone(result.error_message)
        self.assertEqual(self.manager.current_state, ExecutionMode.PAUSED)  # 変更されない
        self.assertEqual(len(self.manager.transition_history), 1)  # 失敗も記録
    
    def test_same_state_transition(self):
        """同じ状態への遷移テスト"""
        # PAUSED → PAUSED (有効)
        result = self.manager.transition_to(ExecutionMode.PAUSED, "same_state")
        
        # 結果検証
        self.assertTrue(result.success)
        self.assertEqual(result.from_state, ExecutionMode.PAUSED)
        self.assertEqual(result.to_state, ExecutionMode.PAUSED)
    
    def test_validate_transition_external(self):
        """外部用遷移妥当性検証テスト"""
        # 有効な遷移
        self.assertTrue(self.manager.validate_transition(ExecutionMode.PAUSED, ExecutionMode.STEPPING))
        
        # 無効な遷移
        self.assertFalse(self.manager.validate_transition(ExecutionMode.PAUSED, ExecutionMode.STEP_EXECUTING))
        
        # 同じ状態
        self.assertTrue(self.manager.validate_transition(ExecutionMode.PAUSED, ExecutionMode.PAUSED))
    
    def test_rollback_transition(self):
        """状態遷移ロールバックテスト"""
        # 状態遷移を実行
        self.manager.transition_to(ExecutionMode.STEPPING, "user_request")
        
        # ロールバック実行
        result = self.manager.rollback_transition()
        
        # 結果検証
        self.assertTrue(result)
        self.assertEqual(self.manager.current_state, ExecutionMode.PAUSED)
        self.assertIsNone(self.manager.previous_state)
        self.assertEqual(len(self.manager.transition_history), 2)  # 元の遷移 + ロールバック
    
    def test_rollback_without_previous_state(self):
        """前状態なしでのロールバックテスト（エラーケース）"""
        result = self.manager.rollback_transition()
        
        # 結果検証
        self.assertFalse(result)
        self.assertEqual(self.manager.current_state, ExecutionMode.PAUSED)
    
    def test_rollback_invalid_transition(self):
        """無効なロールバック遷移テスト"""
        # 連続した遷移でロールバック不可能な状態を作成
        self.manager.transition_to(ExecutionMode.CONTINUOUS, "start_continuous")
        self.manager.transition_to(ExecutionMode.COMPLETED, "complete_execution")
        
        # COMPLETEDからCONTINUOUSへのロールバックは無効
        with patch.object(self.manager, '_validate_transition', return_value=False):
            result = self.manager.rollback_transition()
            self.assertFalse(result)
    
    def test_get_current_state(self):
        """現在状態取得テスト"""
        self.assertEqual(self.manager.get_current_state(), ExecutionMode.PAUSED)
        
        # 状態変更後
        self.manager.transition_to(ExecutionMode.STEPPING, "test")
        self.assertEqual(self.manager.get_current_state(), ExecutionMode.STEPPING)
    
    def test_get_transition_history(self):
        """遷移履歴取得テスト"""
        # 複数の遷移を実行
        transitions = [
            (ExecutionMode.STEPPING, "step1"),
            (ExecutionMode.PAUSED, "pause1"),
            (ExecutionMode.CONTINUOUS, "continuous1")
        ]
        
        for state, reason in transitions:
            self.manager.transition_to(state, reason)
        
        # 履歴取得（最新2件）
        history = self.manager.get_transition_history(limit=2)
        self.assertEqual(len(history), 2)
        
        # 最新の履歴が先頭
        self.assertEqual(history[0].to_state, ExecutionMode.CONTINUOUS)
        self.assertEqual(history[1].to_state, ExecutionMode.PAUSED)
    
    def test_get_allowed_transitions(self):
        """許可済み遷移取得テスト"""
        # 現在状態から許可された遷移
        allowed = self.manager.get_allowed_transitions()
        expected = self.manager.transition_matrix[ExecutionMode.PAUSED]
        self.assertEqual(set(allowed), set(expected))
        
        # 指定状態から許可された遷移
        allowed_from_stepping = self.manager.get_allowed_transitions(ExecutionMode.STEPPING)
        expected_from_stepping = self.manager.transition_matrix[ExecutionMode.STEPPING]
        self.assertEqual(set(allowed_from_stepping), set(expected_from_stepping))
    
    def test_get_transition_statistics(self):
        """遷移統計情報取得テスト"""
        # 初期統計
        stats = self.manager.get_transition_statistics()
        self.assertEqual(stats["current_state"], ExecutionMode.PAUSED.value)
        self.assertIsNone(stats["previous_state"])
        self.assertEqual(stats["total_transitions"], 0)
        self.assertEqual(stats["successful_transitions"], 0)
        self.assertEqual(stats["success_rate"], 1.0)
        
        # いくつかの遷移を実行
        self.manager.transition_to(ExecutionMode.STEPPING, "valid")
        self.manager.transition_to(ExecutionMode.STEP_EXECUTING, "invalid")  # 失敗
        
        stats = self.manager.get_transition_statistics()
        self.assertEqual(stats["total_transitions"], 2)
        self.assertEqual(stats["successful_transitions"], 1)
        self.assertEqual(stats["success_rate"], 0.5)
    
    def test_reset(self):
        """リセット機能テスト"""
        # 状態を変更
        self.manager.transition_to(ExecutionMode.STEPPING, "test")
        
        # リセット実行
        self.manager.reset()
        
        # 初期状態に戻ることを確認
        self.assertEqual(self.manager.current_state, ExecutionMode.PAUSED)
        self.assertIsNone(self.manager.previous_state)
        self.assertEqual(len(self.manager.transition_history), 0)
    
    def test_clear_history(self):
        """履歴クリアテスト"""
        # 履歴を作成
        self.manager.transition_to(ExecutionMode.STEPPING, "test")
        self.assertEqual(len(self.manager.transition_history), 1)
        
        # 履歴クリア
        self.manager.clear_history()
        self.assertEqual(len(self.manager.transition_history), 0)
        
        # 現在状態は保持
        self.assertEqual(self.manager.current_state, ExecutionMode.STEPPING)
    
    def test_validate_state_consistency(self):
        """状態整合性検証テスト"""
        # 正常状態
        self.assertTrue(self.manager.validate_state_consistency())
        
        # 無効な現在状態をシミュレート
        self.manager.current_state = "invalid_state"
        self.assertFalse(self.manager.validate_state_consistency())
        
        # 復元
        self.manager.current_state = ExecutionMode.PAUSED
        self.assertTrue(self.manager.validate_state_consistency())
        
        # 無効な前状態をシミュレート
        self.manager.previous_state = "invalid_previous"
        self.assertFalse(self.manager.validate_state_consistency())
    
    def test_transition_history_size_limit(self):
        """遷移履歴サイズ制限テスト"""
        # 制限を超える遷移を実行
        for i in range(105):  # 制限は100
            target_state = ExecutionMode.STEPPING if i % 2 == 0 else ExecutionMode.PAUSED
            self.manager.transition_to(target_state, f"transition_{i}")
        
        # 履歴サイズが制限内
        self.assertLessEqual(len(self.manager.transition_history), 100)
    
    def test_str_representation(self):
        """文字列表現テスト"""
        str_repr = str(self.manager)
        self.assertIn("StateTransitionManager", str_repr)
        self.assertIn("current=paused", str_repr)
        self.assertIn("transitions=0", str_repr)
        
        # 遷移後
        self.manager.transition_to(ExecutionMode.STEPPING, "test")
        str_repr = str(self.manager)
        self.assertIn("current=stepping", str_repr)
        self.assertIn("transitions=1", str_repr)
    
    @patch('engine.state_transition_manager.logger')
    def test_error_handling(self, mock_logger):
        """エラーハンドリングテスト"""
        # モックでエラーを発生させる
        with patch.object(self.manager, '_lock') as mock_lock:
            mock_lock.__enter__.side_effect = Exception("Test error")
            
            # エラーが適切に処理されることを確認
            with self.assertRaises(StateTransitionError):
                self.manager.transition_to(ExecutionMode.STEPPING, "test")
    
    @patch('engine.state_transition_manager.logger')
    def test_logging_behavior(self, mock_logger):
        """ロギング動作テスト"""
        # 有効な遷移でログ出力を確認
        self.manager.transition_to(ExecutionMode.STEPPING, "test")
        self.assertTrue(mock_logger.debug.called)
        
        # 無効な遷移でエラーログ出力を確認
        self.manager.transition_to(ExecutionMode.STEP_EXECUTING, "invalid")
        self.assertTrue(mock_logger.error.called)
    
    def test_complex_transition_sequence(self):
        """複雑な遷移シーケンステスト"""
        # 実際の使用パターンをシミュレート
        transitions = [
            (ExecutionMode.STEPPING, "user_step"),
            (ExecutionMode.STEP_EXECUTING, "execute_step"),  # 無効
            (ExecutionMode.PAUSED, "step_complete"),
            (ExecutionMode.CONTINUOUS, "user_continuous"),
            (ExecutionMode.PAUSE_PENDING, "user_pause_request"),
            (ExecutionMode.PAUSED, "pause_executed"),
            (ExecutionMode.RESET, "user_reset"),
            (ExecutionMode.ERROR, "reset_error"),  # 無効
            (ExecutionMode.PAUSED, "recovery")
        ]
        
        success_count = 0
        for target_state, reason in transitions:
            result = self.manager.transition_to(target_state, reason)
            if result.success:
                success_count += 1
        
        # 最終状態確認
        self.assertEqual(self.manager.current_state, ExecutionMode.PAUSED)
        self.assertEqual(len(self.manager.transition_history), len(transitions))
        
        # 成功率確認
        stats = self.manager.get_transition_statistics()
        expected_success_rate = success_count / len(transitions)
        self.assertEqual(stats["success_rate"], expected_success_rate)
    
    def test_concurrent_transition_safety(self):
        """並行遷移安全性テスト（基本）"""
        import threading
        
        results = []
        
        def make_transition(target_state, reason):
            try:
                result = self.manager.transition_to(target_state, reason)
                results.append(result.success)
            except Exception:
                results.append(False)
        
        # 複数スレッドで同時に遷移
        threads = []
        for i in range(5):
            target = ExecutionMode.STEPPING if i % 2 == 0 else ExecutionMode.CONTINUOUS
            thread = threading.Thread(target=make_transition, args=(target, f"thread_{i}"))
            threads.append(thread)
            thread.start()
        
        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()
        
        # 結果確認
        self.assertEqual(len(results), 5)
        self.assertTrue(any(results))  # 少なくとも1つは成功


if __name__ == '__main__':
    unittest.main()