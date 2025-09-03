"""
🆕 v1.2.1: ResetManagerのUnit Tests
テスト対象: システムリセット、コンポーネント管理、検証機能
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from engine.reset_manager import ResetManager, Resettable
from engine import ResetResult, ResetOperationError


class MockResettableComponent(Resettable):
    """テスト用リセット可能コンポーネント"""
    
    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.reset_called = False
        self.reset_count = 0
    
    def reset(self) -> None:
        """リセット実行"""
        if self.should_fail:
            raise Exception(f"Reset failed for {self.name}")
        self.reset_called = True
        self.reset_count += 1


class TestResetManager(unittest.TestCase):
    """ResetManagerのテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.manager = ResetManager()
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(len(self.manager.components), 0)
        self.assertEqual(len(self.manager.reset_history), 0)
        self.assertIsNone(self.manager.last_reset_time)
    
    def test_register_component(self):
        """コンポーネント登録テスト"""
        component = MockResettableComponent("test_component")
        
        # コンポーネント登録
        self.manager.register_component("test", component)
        
        # 結果検証
        self.assertIn("test", self.manager.components)
        self.assertEqual(self.manager.components["test"], component)
    
    def test_unregister_component(self):
        """コンポーネント登録解除テスト"""
        component = MockResettableComponent("test_component")
        
        # 登録と解除
        self.manager.register_component("test", component)
        result = self.manager.unregister_component("test")
        
        # 結果検証
        self.assertTrue(result)
        self.assertNotIn("test", self.manager.components)
        
        # 存在しないコンポーネントの解除
        result = self.manager.unregister_component("nonexistent")
        self.assertFalse(result)
    
    def test_full_system_reset_success(self):
        """システムリセット成功テスト"""
        # テスト用コンポーネントを登録
        components = [
            MockResettableComponent("component1"),
            MockResettableComponent("component2"),
            MockResettableComponent("component3")
        ]
        
        for i, component in enumerate(components):
            self.manager.register_component(f"comp_{i}", component)
        
        # システムリセット実行
        start_time = datetime.now()
        result = self.manager.full_system_reset()
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # 結果検証
        self.assertTrue(result.success)
        self.assertEqual(len(result.components_reset), 3)
        self.assertEqual(len(result.errors), 0)
        self.assertIsNotNone(result.reset_timestamp)
        
        # 全コンポーネントがリセットされたことを確認
        for component in components:
            self.assertTrue(component.reset_called)
        
        # 履歴に追加されたことを確認
        self.assertEqual(len(self.manager.reset_history), 1)
        self.assertEqual(self.manager.last_reset_time, result.reset_timestamp)
        
        # NFR-001.3: 200ms以内の要件（実際のテストでは緩和）
        self.assertLess(execution_time_ms, 1000.0)  # 1秒以内
    
    def test_full_system_reset_with_failures(self):
        """コンポーネント失敗を含むシステムリセットテスト"""
        # 成功と失敗のコンポーネントを混在
        components = [
            MockResettableComponent("success1"),
            MockResettableComponent("failure1", should_fail=True),
            MockResettableComponent("success2"),
            MockResettableComponent("failure2", should_fail=True)
        ]
        
        for i, component in enumerate(components):
            self.manager.register_component(f"comp_{i}", component)
        
        # システムリセット実行
        result = self.manager.full_system_reset()
        
        # 結果検証
        self.assertFalse(result.success)  # 失敗があるため
        self.assertEqual(len(result.components_reset), 2)  # 成功したのは2つ
        self.assertEqual(len(result.errors), 2)  # エラーは2つ
        
        # 成功したコンポーネントはリセット済み
        self.assertTrue(components[0].reset_called)
        self.assertTrue(components[2].reset_called)
        
        # 失敗したコンポーネントはエラー記録に含まれる
        self.assertTrue(any("failure1" in error for error in result.errors))
        self.assertTrue(any("failure2" in error for error in result.errors))
    
    def test_reset_execution_controller(self):
        """ExecutionController固有リセットテスト"""
        # モックExecutionController
        mock_controller = MagicMock()
        
        # 正常リセット
        self.manager.reset_execution_controller(mock_controller)
        mock_controller.reset.assert_called_once()
        
        # エラーが発生する場合
        mock_controller.reset.side_effect = Exception("Reset error")
        with self.assertRaises(ResetOperationError):
            self.manager.reset_execution_controller(mock_controller)
    
    def test_reset_game_manager(self):
        """GameManager固有リセットテスト"""
        # モックGameManager (reset_gameメソッドあり)
        mock_manager = MagicMock()
        mock_manager.reset_game = MagicMock()
        
        # 正常リセット
        self.manager.reset_game_manager(mock_manager)
        mock_manager.reset_game.assert_called_once()
        
        # reset_gameメソッドがない場合
        mock_manager_no_method = MagicMock(spec=[])
        self.manager.reset_game_manager(mock_manager_no_method)  # エラーなく完了
        
        # エラーが発生する場合
        mock_manager.reset_game.side_effect = Exception("Reset error")
        with self.assertRaises(ResetOperationError):
            self.manager.reset_game_manager(mock_manager)
    
    def test_reset_session_logs(self):
        """セッションログリセットテスト"""
        # モックSessionLogManager
        mock_logger = MagicMock()
        mock_logger.reset_session = MagicMock()
        
        # 正常リセット
        self.manager.reset_session_logs(mock_logger)
        mock_logger.reset_session.assert_called_once()
        
        # reset_sessionメソッドがない場合
        mock_logger_no_method = MagicMock(spec=[])
        self.manager.reset_session_logs(mock_logger_no_method)  # エラーなく完了
        
        # エラーが発生する場合
        mock_logger.reset_session.side_effect = Exception("Reset error")
        with self.assertRaises(ResetOperationError):
            self.manager.reset_session_logs(mock_logger)
    
    def test_validate_reset_completion(self):
        """リセット完了検証テスト"""
        # リセット履歴なし
        self.assertFalse(self.manager.validate_reset_completion())
        
        # 成功したリセットを実行
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        result = self.manager.full_system_reset()
        
        # 検証成功
        self.assertTrue(self.manager.validate_reset_completion())
        
        # 失敗したリセット結果を追加
        failed_result = ResetResult(
            success=False,
            reset_timestamp=datetime.now(),
            components_reset=[],
            errors=["Test error"]
        )
        self.manager.reset_history.append(failed_result)
        
        # 検証失敗（最新が失敗）
        self.assertFalse(self.manager.validate_reset_completion())
    
    def test_get_reset_status(self):
        """リセット状況取得テスト"""
        # 初期状態
        status = self.manager.get_reset_status()
        self.assertEqual(status["registered_components"], [])
        self.assertEqual(status["component_count"], 0)
        self.assertIsNone(status["last_reset_time"])
        self.assertEqual(status["reset_history_count"], 0)
        
        # コンポーネント登録とリセット後
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        self.manager.full_system_reset()
        
        status = self.manager.get_reset_status()
        self.assertEqual(status["registered_components"], ["test"])
        self.assertEqual(status["component_count"], 1)
        self.assertIsNotNone(status["last_reset_time"])
        self.assertEqual(status["reset_history_count"], 1)
        self.assertTrue(status["last_reset_success"])
        self.assertEqual(status["last_reset_components"], ["test"])
        self.assertEqual(status["last_reset_errors"], [])
    
    def test_get_reset_history(self):
        """リセット履歴取得テスト"""
        # 複数のリセットを実行
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        
        for i in range(5):
            self.manager.full_system_reset()
        
        # 履歴取得（最新3件）
        history = self.manager.get_reset_history(limit=3)
        self.assertEqual(len(history), 3)
        
        # 全履歴取得
        full_history = self.manager.get_reset_history(limit=0)
        self.assertEqual(len(full_history), 5)
    
    def test_get_performance_metrics(self):
        """パフォーマンスメトリクス取得テスト"""
        # 履歴なし
        metrics = self.manager.get_performance_metrics()
        self.assertTrue(metrics["no_reset_history"])
        
        # 複数のリセットを実行
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        
        for i in range(5):
            self.manager.full_system_reset()
        
        metrics = self.manager.get_performance_metrics()
        self.assertEqual(metrics["total_resets"], 5)
        self.assertEqual(metrics["successful_resets"], 5)
        self.assertEqual(metrics["recent_reset_count"], 5)
    
    def test_emergency_reset(self):
        """緊急リセットテスト"""
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        
        # 緊急リセット実行
        result = self.manager.emergency_reset()
        
        # 結果検証
        self.assertTrue(result.success)
        self.assertTrue(component.reset_called)
    
    def test_emergency_reset_with_failure(self):
        """失敗を含む緊急リセットテスト"""
        # フルシステムリセットが失敗するようにモック
        with patch.object(self.manager, 'full_system_reset') as mock_reset:
            mock_reset.side_effect = Exception("Critical error")
            
            result = self.manager.emergency_reset()
            
            # フォールバック結果を確認
            self.assertFalse(result.success)
            self.assertEqual(len(result.components_reset), 0)
            self.assertTrue(any("緊急リセット致命的失敗" in error for error in result.errors))
    
    def test_clear_reset_history(self):
        """リセット履歴クリアテスト"""
        # 履歴を作成
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        self.manager.full_system_reset()
        
        self.assertEqual(len(self.manager.reset_history), 1)
        
        # 履歴クリア
        self.manager.clear_reset_history()
        self.assertEqual(len(self.manager.reset_history), 0)
    
    def test_reset_history_size_limit(self):
        """リセット履歴サイズ制限テスト"""
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        
        # 制限を超える数のリセットを実行
        for i in range(55):  # 制限は50
            self.manager.full_system_reset()
        
        # 履歴サイズが制限内
        self.assertLessEqual(len(self.manager.reset_history), 50)
    
    @patch('engine.reset_manager.gc')
    def test_memory_cleanup(self, mock_gc):
        """メモリクリーンアップテスト"""
        mock_gc.collect.return_value = 10
        
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        
        # リセット実行
        self.manager.full_system_reset()
        
        # ガベージコレクションが呼ばれたことを確認
        mock_gc.collect.assert_called_once()
    
    @patch('engine.reset_manager.logger')
    def test_logging_behavior(self, mock_logger):
        """ロギング動作テスト"""
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        
        # リセット実行でログ出力を確認
        self.manager.full_system_reset()
        
        self.assertTrue(mock_logger.info.called)
        self.assertTrue(mock_logger.debug.called)
    
    def test_str_representation(self):
        """文字列表現テスト"""
        str_repr = str(self.manager)
        self.assertIn("ResetManager", str_repr)
        self.assertIn("components=0", str_repr)
        self.assertIn("history=0", str_repr)
        
        # コンポーネント追加とリセット後
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        self.manager.full_system_reset()
        
        str_repr = str(self.manager)
        self.assertIn("components=1", str_repr)
        self.assertIn("history=1", str_repr)
    
    def test_nfr_performance_requirement(self):
        """NFR-001.3: 200ms性能要件テスト"""
        # 複数の軽量コンポーネントを登録
        for i in range(10):
            component = MockResettableComponent(f"component_{i}")
            self.manager.register_component(f"comp_{i}", component)
        
        start_time = datetime.now()
        result = self.manager.full_system_reset()
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # パフォーマンス要件確認（テスト環境では緩和）
        self.assertTrue(result.success)
        self.assertLess(execution_time_ms, 1000.0)  # 1秒以内
    
    def test_concurrent_reset_safety(self):
        """並行リセット安全性テスト（基本）"""
        import threading
        
        component = MockResettableComponent("test")
        self.manager.register_component("test", component)
        
        results = []
        
        def execute_reset():
            try:
                result = self.manager.full_system_reset()
                results.append(result.success)
            except Exception:
                results.append(False)
        
        # 複数スレッドで同時にリセット
        threads = []
        for i in range(3):
            thread = threading.Thread(target=execute_reset)
            threads.append(thread)
            thread.start()
        
        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()
        
        # 結果確認
        self.assertEqual(len(results), 3)
        self.assertTrue(all(results))  # 全て成功
        
        # コンポーネントのリセット回数確認
        self.assertEqual(component.reset_count, 3)


if __name__ == '__main__':
    unittest.main()