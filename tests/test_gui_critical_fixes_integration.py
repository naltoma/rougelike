#!/usr/bin/env python3
"""
🆕 v1.2.1: GUI Critical Fixes 統合テスト
テスト対象: Step/Pause/Resetボタン機能、ExecutionController統合、全システム連携
"""

import unittest
import threading
import time
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock

from engine.execution_controller import ExecutionController
from engine.action_boundary_detector import ActionBoundaryDetector
from engine.pause_controller import PauseController
from engine.state_transition_manager import StateTransitionManager
from engine.reset_manager import ResetManager
from engine import ExecutionMode, StepResult, ResetResult


class MockGameAPI:
    """テスト用ゲームAPI"""
    
    def __init__(self):
        self.move_calls = 0
        self.get_calls = 0
        self.is_complete_value = False
    
    def move_player(self, direction):
        """プレイヤー移動（モック）"""
        self.move_calls += 1
        return f"Moved {direction}"
    
    def get_current_position(self):
        """現在位置取得（モック）"""
        self.get_calls += 1
        return (self.get_calls, self.get_calls)
    
    def is_complete(self):
        """完了判定（モック）"""
        return self.is_complete_value


class TestGUICriticalFixesIntegration(unittest.TestCase):
    """GUI Critical Fixes統合テストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.mock_api = MockGameAPI()
        self.execution_controller = ExecutionController(self.mock_api)
    
    def test_component_initialization_integration(self):
        """コンポーネント初期化統合テスト"""
        # 全コンポーネントが正しく初期化されているか確認
        self.assertIsInstance(self.execution_controller.action_boundary_detector, ActionBoundaryDetector)
        self.assertIsInstance(self.execution_controller.pause_controller, PauseController)
        self.assertIsInstance(self.execution_controller.state_transition_manager, StateTransitionManager)
        self.assertIsInstance(self.execution_controller.reset_manager, ResetManager)
        
        # 初期状態確認
        self.assertEqual(self.execution_controller.state.mode, ExecutionMode.PAUSED)
    
    def test_step_button_functionality_fix(self):
        """Stepボタン機能修正テスト（Critical Fix #1）"""
        # 初期状態確認
        self.assertEqual(self.execution_controller.state.mode, ExecutionMode.PAUSED)
        
        # 1回目のステップ実行
        step_result1 = self.execution_controller.step_execution()
        
        # 結果検証
        self.assertIsNotNone(step_result1)
        self.assertTrue(step_result1.success)
        self.assertEqual(step_result1.actions_executed, 1)
        self.assertEqual(self.mock_api.move_calls, 1)  # 1回だけAPI呼び出し
        
        # 状態が適切に遷移したか確認
        self.assertIn(self.execution_controller.state.mode, [ExecutionMode.PAUSED, ExecutionMode.STEPPING])
        
        # 2回目のステップ実行（無限ループにならないか確認）
        step_result2 = self.execution_controller.step_execution()
        
        # 2回目も正常動作することを確認
        self.assertIsNotNone(step_result2)
        self.assertTrue(step_result2.success)
        self.assertEqual(step_result2.actions_executed, 1)
        self.assertEqual(self.mock_api.move_calls, 2)  # 合計2回のAPI呼び出し
    
    def test_pause_button_functionality_fix(self):
        """Pauseボタン機能修正テスト（Critical Fix #2）"""
        # 連続実行を開始
        execution_thread = threading.Thread(
            target=self.execution_controller.continuous_execution
        )
        execution_thread.daemon = True
        execution_thread.start()
        
        # 短時間待機してから一時停止要求
        time.sleep(0.05)  # 50ms待機
        pause_result = self.execution_controller.pause_at_next_action_boundary()
        
        # 一時停止要求が正常に処理されたか確認
        self.assertIsNotNone(pause_result)
        self.assertEqual(pause_result.requester, "user")
        
        # PAUSE_PENDING状態に遷移することを確認
        time.sleep(0.1)  # 100ms待機
        current_mode = self.execution_controller.state.mode
        self.assertIn(current_mode, [ExecutionMode.PAUSE_PENDING, ExecutionMode.PAUSED])
        
        # スレッドクリーンアップ
        self.execution_controller.stop_execution()
        execution_thread.join(timeout=1.0)
    
    def test_reset_button_functionality_fix(self):
        """Resetボタン機能修正テスト（Critical Fix #3）"""
        # 初期状態変更（いくつかのアクションを実行）
        self.execution_controller.step_execution()
        self.execution_controller.step_execution()
        
        initial_calls = self.mock_api.move_calls
        self.assertGreater(initial_calls, 0)
        
        # リセット実行
        start_time = datetime.now()
        reset_result = self.execution_controller.reset_system()
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # リセット結果検証
        self.assertIsNotNone(reset_result)
        self.assertTrue(reset_result.success)
        self.assertIn("execution_controller", reset_result.components_reset)
        self.assertEqual(len(reset_result.errors), 0)
        
        # NFR-001.3: 200ms以内の要件（テスト環境では緩和）
        self.assertLess(execution_time_ms, 1000.0)  # 1秒以内
        
        # 状態がリセットされたか確認
        self.assertEqual(self.execution_controller.state.mode, ExecutionMode.PAUSED)
        
        # 新しいステップが正常動作するか確認
        step_result = self.execution_controller.step_execution()
        self.assertTrue(step_result.success)
    
    def test_action_boundary_detection_integration(self):
        """アクション境界検出統合テスト"""
        # ステップ実行前の境界検出
        boundary_before = self.execution_controller.action_boundary_detector.detect_boundary(
            ExecutionMode.STEPPING
        )
        self.assertIsNotNone(boundary_before)
        self.assertTrue(boundary_before.allows_step_execution)
        
        # ステップ実行
        self.execution_controller.step_execution()
        
        # 実行後の状態確認
        action_status = self.execution_controller.action_boundary_detector.get_action_status()
        self.assertEqual(action_status["sequence_number"], 1)
        self.assertFalse(action_status["in_execution"])
    
    def test_state_transition_validation_integration(self):
        """状態遷移検証統合テスト"""
        state_manager = self.execution_controller.state_transition_manager
        
        # 有効な遷移シーケンス
        valid_transitions = [
            (ExecutionMode.STEPPING, "step_request"),
            (ExecutionMode.PAUSED, "step_complete"), 
            (ExecutionMode.CONTINUOUS, "continuous_request"),
            (ExecutionMode.PAUSE_PENDING, "pause_request"),
            (ExecutionMode.PAUSED, "pause_complete")
        ]
        
        for target_state, reason in valid_transitions:
            result = state_manager.transition_to(target_state, reason)
            self.assertTrue(result.success, f"Failed transition to {target_state.value}")
        
        # 統計確認
        stats = state_manager.get_transition_statistics()
        self.assertEqual(stats["total_transitions"], len(valid_transitions))
        self.assertEqual(stats["successful_transitions"], len(valid_transitions))
        self.assertEqual(stats["success_rate"], 1.0)
    
    def test_pause_controller_integration_with_boundaries(self):
        """PauseController境界統合テスト"""
        pause_controller = self.execution_controller.pause_controller
        boundary_detector = self.execution_controller.action_boundary_detector
        
        # 一時停止要求
        pause_controller.request_pause_at_next_action("test_integration")
        
        # 境界での一時停止判定
        boundary = boundary_detector.detect_boundary(ExecutionMode.CONTINUOUS)
        should_pause = pause_controller.should_pause_at_boundary(True)
        
        self.assertTrue(should_pause)
        self.assertIsNotNone(boundary)
    
    def test_reset_manager_component_registration(self):
        """ResetManagerコンポーネント登録統合テスト"""
        reset_manager = self.execution_controller.reset_manager
        
        # ExecutionControllerが自身を登録したか確認
        status = reset_manager.get_reset_status()
        self.assertIn("execution_controller", status["registered_components"])
        
        # 個別コンポーネントのリセットテスト
        reset_manager.reset_execution_controller(self.execution_controller)
        
        # 状態がリセットされたか確認
        self.assertEqual(self.execution_controller.state.mode, ExecutionMode.PAUSED)
    
    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        # APIエラーをシミュレート
        original_move = self.mock_api.move_player
        self.mock_api.move_player = Mock(side_effect=Exception("API Error"))
        
        # ステップ実行でのエラーハンドリング
        step_result = self.execution_controller.step_execution()
        
        # エラーが適切に処理されたか確認
        self.assertIsNotNone(step_result)
        self.assertFalse(step_result.success)
        self.assertIsNotNone(step_result.error_message)
        
        # 状態がERRORモードに遷移したか確認
        self.assertEqual(self.execution_controller.state.mode, ExecutionMode.ERROR)
        
        # APIを復元
        self.mock_api.move_player = original_move
        
        # リセットでエラー状態から回復
        reset_result = self.execution_controller.reset_system()
        self.assertTrue(reset_result.success)
        self.assertEqual(self.execution_controller.state.mode, ExecutionMode.PAUSED)
    
    def test_nfr_performance_requirements_integration(self):
        """NFR性能要件統合テスト"""
        # NFR-001.1: 50ms ボタン応答時間
        start_time = datetime.now()
        pause_request = self.execution_controller.pause_at_next_action_boundary()
        response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        self.assertLess(response_time_ms, 100.0)  # テスト環境では100ms以内
        self.assertIsNotNone(pause_request)
        
        # NFR-001.2: 100ms ステップ実行時間
        start_time = datetime.now()
        step_result = self.execution_controller.step_execution()
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        self.assertLess(execution_time_ms, 200.0)  # テスト環境では200ms以内
        self.assertTrue(step_result.success)
        
        # NFR-001.3: 200ms リセット時間
        start_time = datetime.now()
        reset_result = self.execution_controller.reset_system()
        reset_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        self.assertLess(reset_time_ms, 500.0)  # テスト環境では500ms以内
        self.assertTrue(reset_result.success)
    
    def test_thread_safety_integration(self):
        """スレッドセーフティ統合テスト"""
        results = []
        
        def step_execution_worker():
            try:
                result = self.execution_controller.step_execution()
                results.append(("step", result.success if result else False))
            except Exception as e:
                results.append(("step_error", str(e)))
        
        def pause_request_worker():
            try:
                request = self.execution_controller.pause_at_next_action_boundary()
                results.append(("pause", request is not None))
            except Exception as e:
                results.append(("pause_error", str(e)))
        
        def reset_worker():
            try:
                result = self.execution_controller.reset_system()
                results.append(("reset", result.success if result else False))
            except Exception as e:
                results.append(("reset_error", str(e)))
        
        # 複数スレッドで同時実行
        threads = [
            threading.Thread(target=step_execution_worker),
            threading.Thread(target=pause_request_worker),
            threading.Thread(target=reset_worker)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=2.0)
        
        # 結果確認
        self.assertEqual(len(results), 3)
        
        # 少なくとも1つは成功することを確認
        success_operations = [result for op, result in results if result is True]
        self.assertGreater(len(success_operations), 0)
    
    def test_complex_workflow_integration(self):
        """複雑ワークフロー統合テスト"""
        # 実際のGUIユーザー操作をシミュレート
        
        # 1. 初期状態確認
        self.assertEqual(self.execution_controller.state.mode, ExecutionMode.PAUSED)
        
        # 2. ステップ実行 x3
        for i in range(3):
            step_result = self.execution_controller.step_execution()
            self.assertTrue(step_result.success, f"Step {i+1} failed")
        
        # 3. 連続実行開始
        execution_thread = threading.Thread(
            target=self.execution_controller.continuous_execution
        )
        execution_thread.daemon = True
        execution_thread.start()
        
        # 4. 短時間後に一時停止要求
        time.sleep(0.1)
        pause_request = self.execution_controller.pause_at_next_action_boundary()
        self.assertIsNotNone(pause_request)
        
        # 5. 一時停止完了を待機
        time.sleep(0.2)
        
        # 6. リセット実行
        reset_result = self.execution_controller.reset_system()
        self.assertTrue(reset_result.success)
        
        # 7. リセット後の動作確認
        step_result = self.execution_controller.step_execution()
        self.assertTrue(step_result.success)
        
        # クリーンアップ
        self.execution_controller.stop_execution()
        execution_thread.join(timeout=1.0)
    
    def test_logging_integration(self):
        """ログ統合テスト"""
        with patch('engine.execution_controller.logger') as mock_logger:
            # 各種操作を実行してログが出力されることを確認
            self.execution_controller.step_execution()
            self.execution_controller.pause_at_next_action_boundary()
            self.execution_controller.reset_system()
            
            # ログ呼び出しを確認
            self.assertTrue(mock_logger.debug.called)
            self.assertTrue(mock_logger.info.called)
    
    def test_educational_error_messages_integration(self):
        """教育的エラーメッセージ統合テスト"""
        # APIエラーをシミュレート
        self.mock_api.move_player = Mock(side_effect=Exception("Test API Error"))
        
        # ステップ実行でエラー発生
        step_result = self.execution_controller.step_execution()
        
        # 教育的エラーメッセージが含まれているか確認
        self.assertFalse(step_result.success)
        self.assertIn("API", step_result.error_message)
        
        # エラー詳細に学習者向けの説明が含まれているか
        error_detail = self.execution_controller.get_execution_state_detail()
        self.assertIsNotNone(error_detail.last_error)
    
    def tearDown(self):
        """テストクリーンアップ"""
        try:
            # ExecutionControllerを安全に停止
            self.execution_controller.stop_execution()
            
            # 短時間待機してスレッドを整理
            time.sleep(0.1)
        except Exception:
            pass  # クリーンアップエラーは無視


if __name__ == '__main__':
    # テスト実行時の設定
    unittest.main(verbosity=2)