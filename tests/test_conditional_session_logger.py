"""
ConditionalSessionLoggerの単体テスト
v1.2.4新機能: セッションログ条件制御システムのテスト
"""

import pytest
from unittest.mock import Mock, patch
from engine.session_log_manager import SessionLogManager
from engine.conditional_session_logger import ConditionalSessionLogger


class TestConditionalSessionLogger:
    """ConditionalSessionLoggerクラスの基本動作テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_initialization(self):
        """初期化テスト"""
        assert isinstance(self.conditional_logger.session_log_manager, Mock)
        assert self.conditional_logger._confirmation_mode is False
    
    def test_should_log_session_confirmation_mode_false(self):
        """確認モード(False)時にログを生成しないことを検証"""
        confirmation_mode = False
        result = self.conditional_logger.should_log_session(confirmation_mode)
        
        assert result is False
        assert self.conditional_logger._confirmation_mode is False
    
    def test_should_log_session_execution_mode_true(self):
        """実行モード(True)時に通常通りログを生成することを検証"""
        confirmation_mode = True
        result = self.conditional_logger.should_log_session(confirmation_mode)
        
        assert result is True
        assert self.conditional_logger._confirmation_mode is True
    
    def test_should_log_session_mode_caching(self):
        """モード状態の内部キャッシュが正しく更新されることを確認"""
        # 確認モードに設定
        self.conditional_logger.should_log_session(False)
        assert self.conditional_logger._confirmation_mode is False
        
        # 実行モードに設定
        self.conditional_logger.should_log_session(True)
        assert self.conditional_logger._confirmation_mode is True


class TestConditionalLoggingExclusion:
    """ログ除外機能のテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_conditional_log_start_confirmation_mode_exclusion(self):
        """確認モード時のセッション開始ログ除外テスト"""
        confirmation_mode = False
        
        result = self.conditional_logger.conditional_log_start(
            confirmation_mode, 
            stage_id="stage01",
            student_id="123456A"
        )
        
        # 確認モード時はログを除外（Noneを返す）
        assert result is None
        
        # SessionLogManagerのlog_session_startが呼ばれないことを確認
        self.session_log_manager.log_session_start.assert_not_called()
    
    def test_conditional_log_start_execution_mode_logging(self):
        """実行モード時のセッション開始ログ生成テスト"""
        confirmation_mode = True
        
        result = self.conditional_logger.conditional_log_start(
            confirmation_mode, 
            stage_id="stage01",
            student_id="123456A"
        )
        
        # 実行モード時はログを生成
        assert result is not None
        assert result["status"] == "logged"
        assert result["mode"] == "execution"
        
        # SessionLogManagerのlog_session_startが呼ばれることを確認
        self.session_log_manager.log_session_start.assert_called_once()
        
        # 呼び出し引数の確認
        call_args = self.session_log_manager.log_session_start.call_args[0][0]
        assert call_args["mode"] == "execution"
        assert call_args["confirmation_disabled"] is True
        assert call_args["stage_id"] == "stage01"
        assert call_args["student_id"] == "123456A"
    
    def test_conditional_log_end_confirmation_mode_exclusion(self):
        """確認モード時のセッション終了ログ除外テスト"""
        confirmation_mode = False
        
        result = self.conditional_logger.conditional_log_end(
            confirmation_mode,
            action_count=10,
            completed_successfully=True
        )
        
        # 確認モード時はログを除外（Noneを返す）
        assert result is None
        
        # SessionLogManagerのlog_session_completeが呼ばれないことを確認
        self.session_log_manager.log_session_complete.assert_not_called()
    
    def test_conditional_log_end_execution_mode_logging(self):
        """実行モード時のセッション終了ログ生成テスト"""
        confirmation_mode = True
        
        result = self.conditional_logger.conditional_log_end(
            confirmation_mode,
            action_count=15,
            completed_successfully=False
        )
        
        # 実行モード時はログを生成
        assert result is not None
        assert result["status"] == "logged"
        assert result["mode"] == "execution"
        
        # SessionLogManagerのlog_session_completeが呼ばれることを確認
        self.session_log_manager.log_session_complete.assert_called_once()
        
        # 呼び出し引数の確認
        call_args = self.session_log_manager.log_session_complete.call_args[0][0]
        assert call_args["mode"] == "execution"
        assert call_args["confirmation_disabled"] is True
        assert call_args["action_count"] == 15
        assert call_args["completed_successfully"] is False


class TestActionCountExclusion:
    """action_count等の学習データ記録除外機能のテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.session_log_manager.session_logger = Mock()
        self.conditional_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_conditional_log_event_confirmation_mode_exclusion(self):
        """確認モード時のイベントログ（action_count含む）除外テスト"""
        confirmation_mode = False
        
        result = self.conditional_logger.conditional_log_event(
            confirmation_mode,
            "move_action",
            {"action_count": 5, "position": [1, 1]}
        )
        
        # 確認モード時はイベントログを除外（Noneを返す）
        assert result is None
        
        # SessionLoggerのlog_eventが呼ばれないことを確認
        self.session_log_manager.session_logger.log_event.assert_not_called()
    
    def test_conditional_log_event_execution_mode_logging(self):
        """実行モード時のイベントログ（action_count含む）記録テスト"""
        confirmation_mode = True
        
        result = self.conditional_logger.conditional_log_event(
            confirmation_mode,
            "move_action",
            {"action_count": 8, "position": [2, 3]}
        )
        
        # 実行モード時はイベントログを記録
        assert result is not None
        assert result["status"] == "logged"
        assert result["event_type"] == "move_action"
        
        # SessionLoggerのlog_eventが呼ばれることを確認
        self.session_log_manager.session_logger.log_event.assert_called_once_with(
            "move_action",
            {
                "action_count": 8,
                "position": [2, 3],
                "mode": "execution",
                "confirmation_disabled": True
            }
        )
    
    def test_conditional_log_event_no_session_logger(self):
        """SessionLoggerが初期化されていない場合のテスト"""
        self.session_log_manager.session_logger = None
        confirmation_mode = True
        
        result = self.conditional_logger.conditional_log_event(
            confirmation_mode,
            "test_event",
            {"data": "test"}
        )
        
        # SessionLoggerが存在しない場合はNoneを返す
        assert result is None


class TestSessionLogManagerIntegration:
    """SessionLogManagerとの統合動作テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_get_session_log_manager(self):
        """SessionLogManagerインスタンスの取得テスト"""
        manager = self.conditional_logger.get_session_log_manager()
        assert manager is self.session_log_manager
    
    def test_is_logging_active_confirmation_mode(self):
        """確認モード時のログ有効性確認テスト"""
        # 確認モードに設定
        self.conditional_logger.should_log_session(False)
        
        assert self.conditional_logger.is_logging_active() is False
    
    def test_is_logging_active_execution_mode(self):
        """実行モード時のログ有効性確認テスト"""
        # 実行モードに設定
        self.conditional_logger.should_log_session(True)
        
        assert self.conditional_logger.is_logging_active() is True
    
    def test_get_current_mode_status_confirmation(self):
        """確認モード時のステータス取得テスト"""
        self.conditional_logger.should_log_session(False)
        
        status = self.conditional_logger.get_current_mode_status()
        
        assert status["confirmation_mode"] is False
        assert status["logging_enabled"] is False
        assert status["mode_description"] == "確認モード"
        assert status["log_behavior"] == "除外"
    
    def test_get_current_mode_status_execution(self):
        """実行モード時のステータス取得テスト"""
        self.conditional_logger.should_log_session(True)
        
        status = self.conditional_logger.get_current_mode_status()
        
        assert status["confirmation_mode"] is True
        assert status["logging_enabled"] is True
        assert status["mode_description"] == "実行モード"
        assert status["log_behavior"] == "生成"


class TestDebugAndSimulation:
    """デバッグ・シミュレーション機能のテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_enable_debug_logging_success(self):
        """デバッグログ強制有効化の成功ケーステスト"""
        # SessionLogManagerのモック設定
        from engine.session_log_manager import LogResult
        mock_result = LogResult(
            success=True,
            log_path="/path/to/log.json",
            error_message=None,
            session_id="debug123"
        )
        self.session_log_manager.enable_default_logging.return_value = mock_result
        
        result = self.conditional_logger.enable_debug_logging("stage01", "DEBUG_USER")
        
        assert result is True
        self.session_log_manager.enable_default_logging.assert_called_once_with(
            student_id="DEBUG_USER",
            stage_id="stage01",
            force_enable=True
        )
    
    def test_enable_debug_logging_failure(self):
        """デバッグログ強制有効化の失敗ケーステスト"""
        # SessionLogManagerのモック設定（失敗）
        from engine.session_log_manager import LogResult
        mock_result = LogResult(
            success=False,
            log_path=None,
            error_message="テストエラー",
            session_id=None
        )
        self.session_log_manager.enable_default_logging.return_value = mock_result
        
        result = self.conditional_logger.enable_debug_logging("stage01", "DEBUG_USER")
        
        assert result is False
    
    def test_simulate_execution_mode_logging(self):
        """実行モードログ動作シミュレーションテスト"""
        result = self.conditional_logger.simulate_execution_mode_logging("stage01", "TEST_USER")
        
        assert result["simulation_mode"] == "execution"
        assert result["would_generate_logs"] is True
        
        predicted = result["predicted_behavior"]
        assert predicted["session_would_start"] is True
        assert predicted["events_would_be_recorded"] is True
        assert predicted["action_count_would_be_tracked"] is True
        assert predicted["session_would_complete"] is True
        assert "data/sessions/stage01/" in predicted["file_would_be_created"]
    
    def test_get_log_exclusion_summary_confirmation_mode(self):
        """確認モード時のログ除外サマリーテスト"""
        # SessionLogManager の状態をモック
        self.session_log_manager.session_logger = Mock()
        self.session_log_manager.is_logging_enabled.return_value = True
        
        # 確認モードに設定
        self.conditional_logger.should_log_session(False)
        
        summary = self.conditional_logger.get_log_exclusion_summary()
        
        assert summary["confirmation_mode"] is False
        assert summary["logging_will_be_excluded"] is True
        assert summary["session_logger_initialized"] is True
        assert "確認モードのため" in summary["exclusion_reason"]
        assert "実行モードに切り替える" in summary["recommendation"]
    
    def test_get_log_exclusion_summary_execution_mode(self):
        """実行モード時のログ除外サマリーテスト"""
        # SessionLogManager の状態をモック
        self.session_log_manager.session_logger = Mock()
        self.session_log_manager.is_logging_enabled.return_value = True
        
        # 実行モードに設定
        self.conditional_logger.should_log_session(True)
        
        summary = self.conditional_logger.get_log_exclusion_summary()
        
        assert summary["confirmation_mode"] is True
        assert summary["logging_will_be_excluded"] is False
        assert summary["session_logger_initialized"] is True
        assert summary["exclusion_reason"] is None
        assert "現在実行モード" in summary["recommendation"]


class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_conditional_log_start_exception_handling(self):
        """セッション開始ログでの例外処理テスト"""
        # SessionLogManagerでエラーが発生する設定
        self.session_log_manager.log_session_start.side_effect = Exception("テストエラー")
        
        result = self.conditional_logger.conditional_log_start(
            True,
            stage_id="stage01",
            student_id="123456A"
        )
        
        # 例外が発生してもNoneを返す
        assert result is None
    
    def test_conditional_log_end_exception_handling(self):
        """セッション終了ログでの例外処理テスト"""
        # SessionLogManagerでエラーが発生する設定
        self.session_log_manager.log_session_complete.side_effect = Exception("テストエラー")
        
        result = self.conditional_logger.conditional_log_end(
            True,
            action_count=10,
            completed_successfully=True
        )
        
        # 例外が発生してもNoneを返す
        assert result is None
    
    def test_conditional_log_event_exception_handling(self):
        """イベントログでの例外処理テスト"""
        # SessionLoggerでエラーが発生する設定
        self.session_log_manager.session_logger = Mock()
        self.session_log_manager.session_logger.log_event.side_effect = Exception("テストエラー")
        
        result = self.conditional_logger.conditional_log_event(
            True,
            "test_event",
            {"data": "test"}
        )
        
        # 例外が発生してもNoneを返す
        assert result is None
    
    def test_get_log_exclusion_summary_exception_handling(self):
        """ログ除外サマリーでの例外処理テスト"""
        # get_current_mode_statusで例外が発生する設定
        with patch.object(self.conditional_logger, 'get_current_mode_status', side_effect=Exception("テストエラー")):
            summary = self.conditional_logger.get_log_exclusion_summary()
            
            assert summary["logging_will_be_excluded"] is True
            assert "エラーのため状態確認不可" in summary["exclusion_reason"]
            assert "システム管理者にお問い合わせください" in summary["recommendation"]