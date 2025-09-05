"""
初回確認モード機能の統合テスト
v1.2.4新機能: 確認モード→実行モードの完全フロー統合テスト
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from engine.hyperparameter_manager import HyperParameterManager
from engine.initial_confirmation_flag_manager import InitialConfirmationFlagManager
from engine.stage_description_renderer import StageDescriptionRenderer
from engine.conditional_session_logger import ConditionalSessionLogger
from engine.session_log_manager import SessionLogManager
from engine.stage_loader import StageLoader


class TestInitialExecutionBehaviorIntegration:
    """初回確認モード機能の統合テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.confirmation_flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
        self.stage_loader = Mock(spec=StageLoader)
        self.stage_description_renderer = StageDescriptionRenderer(self.stage_loader)
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_session_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_confirmation_to_execution_mode_complete_flow(self):
        """確認モード→実行モードの完全フロー統合テスト"""
        stage_id = "stage01"
        student_id = "123456A"
        
        # 初期状態：確認モード（デフォルト）
        assert self.confirmation_flag_manager.get_confirmation_mode() is False
        
        # 1. 初回実行判定
        is_first_time = self.confirmation_flag_manager.is_first_execution(stage_id, student_id)
        assert is_first_time is True
        
        # 2. 確認モードでのセッションログ除外確認
        should_log = self.conditional_session_logger.should_log_session(False)
        assert should_log is False
        
        # 3. ステージ説明表示（モック）
        mock_stage = Mock()
        mock_stage.id = stage_id
        mock_stage.title = "テストステージ"
        mock_stage.description = "テスト用の説明"
        mock_stage.board_size = (5, 5)
        mock_stage.player_start = Mock(x=0, y=0)
        mock_stage.goal_position = Mock(x=4, y=4)
        mock_stage.allowed_apis = ["move", "turn_left", "turn_right"]
        mock_stage.constraints = {"max_turns": 20}
        mock_stage.enemies = []
        mock_stage.items = []
        
        self.stage_loader.load_stage.return_value = mock_stage
        
        description = self.stage_description_renderer.display_stage_conditions(stage_id, student_id)
        assert "テストステージ" in description
        assert "テスト用の説明" in description
        
        # 4. ステージ表示済みマークの設定
        self.confirmation_flag_manager.mark_stage_intro_displayed(stage_id)
        
        # 5. 次回実行時は初回実行でないことを確認
        is_first_time_second = self.confirmation_flag_manager.is_first_execution(stage_id, student_id)
        assert is_first_time_second is False
        
        # 6. 実行モードへの切り替え
        self.confirmation_flag_manager.set_confirmation_mode(True)
        assert self.confirmation_flag_manager.get_confirmation_mode() is True
        
        # 7. 実行モードでのセッションログ記録確認
        should_log_execution = self.conditional_session_logger.should_log_session(True)
        assert should_log_execution is True
        
        # 8. セッション開始ログの記録
        log_start_result = self.conditional_session_logger.conditional_log_start(
            True,
            stage_id=stage_id,
            student_id=student_id
        )
        assert log_start_result is not None
        assert log_start_result["status"] == "logged"
        
        # 9. セッション終了ログの記録
        log_end_result = self.conditional_session_logger.conditional_log_end(
            True,
            action_count=10,
            completed_successfully=True
        )
        assert log_end_result is not None
        assert log_end_result["status"] == "logged"


class TestMainPyFlowIntegration:
    """main.py実行フローの統合テスト"""
    
    @patch('main.confirmation_flag_manager')
    @patch('main.stage_description_renderer')
    @patch('main.conditional_session_logger')
    def test_setup_confirmation_mode_first_time_confirmation(self, mock_conditional_logger, mock_renderer, mock_flag_manager):
        """初回実行・確認モード時のsetup_confirmation_mode統合テスト"""
        from main import setup_confirmation_mode
        
        # モック設定
        mock_flag_manager.is_first_execution.return_value = True
        mock_flag_manager.get_confirmation_mode.return_value = False
        mock_renderer.display_stage_conditions.return_value = "テストステージ説明"
        
        # 関数実行
        result = setup_confirmation_mode("stage01", "123456A")
        
        # 検証
        assert result is True  # 確認モード表示完了
        mock_flag_manager.is_first_execution.assert_called_once_with("stage01", "123456A")
        mock_flag_manager.get_confirmation_mode.assert_called_once()
        mock_renderer.display_stage_conditions.assert_called_once_with("stage01", "123456A")
        mock_flag_manager.mark_stage_intro_displayed.assert_called_once_with("stage01")
    
    @patch('main.confirmation_flag_manager')
    @patch('main.stage_description_renderer')
    @patch('main.conditional_session_logger')
    def test_setup_confirmation_mode_execution_mode(self, mock_conditional_logger, mock_renderer, mock_flag_manager):
        """実行モード時のsetup_confirmation_mode統合テスト"""
        from main import setup_confirmation_mode
        
        # モック設定（実行モード）
        mock_flag_manager.is_first_execution.return_value = False
        mock_flag_manager.get_confirmation_mode.return_value = True
        
        # 関数実行
        result = setup_confirmation_mode("stage01", "123456A")
        
        # 検証
        assert result is False  # 確認モードスキップ
        mock_flag_manager.is_first_execution.assert_called_once_with("stage01", "123456A")
        mock_flag_manager.get_confirmation_mode.assert_called_once()
        # 実行モードでは説明表示やマークは呼ばれない
        mock_renderer.display_stage_conditions.assert_not_called()
        mock_flag_manager.mark_stage_intro_displayed.assert_not_called()
    
    @patch('main.confirmation_flag_manager')
    @patch('main.stage_description_renderer')
    def test_setup_confirmation_mode_error_handling(self, mock_renderer, mock_flag_manager):
        """setup_confirmation_modeのエラーハンドリング統合テスト"""
        from main import setup_confirmation_mode
        
        # モック設定（エラー発生）
        mock_flag_manager.is_first_execution.side_effect = Exception("テストエラー")
        
        # 関数実行
        result = setup_confirmation_mode("stage01", "123456A")
        
        # 検証（エラー時はFalseを返す）
        assert result is False


class TestSessionLogExclusionIntegration:
    """セッションログ除外機能の統合テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_session_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_session_log_generation_and_exclusion_integration(self):
        """セッションログ生成・除外の統合動作テスト"""
        stage_id = "stage01"
        student_id = "123456A"
        
        # 確認モード：ログ除外
        confirmation_mode = False
        
        # セッション開始ログ除外の確認
        start_result = self.conditional_session_logger.conditional_log_start(
            confirmation_mode,
            stage_id=stage_id,
            student_id=student_id
        )
        assert start_result is None
        self.session_log_manager.log_session_start.assert_not_called()
        
        # イベントログ除外の確認
        event_result = self.conditional_session_logger.conditional_log_event(
            confirmation_mode,
            "move_action",
            {"action_count": 5}
        )
        assert event_result is None
        
        # セッション終了ログ除外の確認
        end_result = self.conditional_session_logger.conditional_log_end(
            confirmation_mode,
            action_count=10,
            completed_successfully=True
        )
        assert end_result is None
        self.session_log_manager.log_session_complete.assert_not_called()
        
        # 実行モードに切り替え
        execution_mode = True
        
        # セッション開始ログ生成の確認
        start_result_exec = self.conditional_session_logger.conditional_log_start(
            execution_mode,
            stage_id=stage_id,
            student_id=student_id
        )
        assert start_result_exec is not None
        assert start_result_exec["status"] == "logged"
        self.session_log_manager.log_session_start.assert_called_once()
        
        # セッション終了ログ生成の確認
        end_result_exec = self.conditional_session_logger.conditional_log_end(
            execution_mode,
            action_count=15,
            completed_successfully=False
        )
        assert end_result_exec is not None
        assert end_result_exec["status"] == "logged"
        self.session_log_manager.log_session_complete.assert_called_once()


class TestErrorHandlingIntegration:
    """エラーハンドリングとフォールバック機能の統合テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.confirmation_flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
        self.stage_loader = Mock(spec=StageLoader)
        self.stage_description_renderer = StageDescriptionRenderer(self.stage_loader)
    
    def test_stage_description_fallback_integration(self):
        """ステージ説明フォールバック機能の統合テスト"""
        stage_id = "nonexistent_stage"
        student_id = "123456A"
        
        # ステージローダーでFileNotFoundErrorが発生する設定
        self.stage_loader.load_stage.side_effect = FileNotFoundError("ステージファイルが見つかりません")
        
        # フォールバック表示の動作確認
        description = self.stage_description_renderer.display_stage_conditions(stage_id, student_id)
        
        # フォールバック表示の内容確認
        assert "ステージ説明を読み込めませんでした" in description
        assert "一般的な情報:" in description
        assert "基本的な目標:" in description
        assert "学習のヒント:" in description
    
    def test_confirmation_flag_manager_error_recovery(self):
        """ConfirmationFlagManagerのエラー回復統合テスト"""
        stage_id = "stage01"
        
        # 無効なステージIDでのエラーテスト
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.confirmation_flag_manager.is_first_execution("")
        
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.confirmation_flag_manager.mark_stage_intro_displayed("")
        
        # 無効な確認モード設定でのエラーテスト
        with pytest.raises(ValueError, match="confirmation_modeはbool型である必要があります"):
            self.confirmation_flag_manager.set_confirmation_mode("invalid")
    
    def test_conditional_session_logger_graceful_degradation(self):
        """ConditionalSessionLoggerのグレースフルデグラデーション統合テスト"""
        # SessionLogManagerが初期化されていない場合
        session_log_manager = Mock(spec=SessionLogManager)
        session_log_manager.session_logger = None
        conditional_logger = ConditionalSessionLogger(session_log_manager)
        
        # イベントログ記録時の適切な処理
        result = conditional_logger.conditional_log_event(
            True,  # 実行モード
            "test_event",
            {"data": "test"}
        )
        
        # SessionLoggerが存在しない場合はNoneを返す
        assert result is None
    
    def test_integration_with_exception_handling(self):
        """例外処理との統合テスト"""
        session_log_manager = Mock(spec=SessionLogManager)
        session_log_manager.log_session_start.side_effect = Exception("テストエラー")
        conditional_logger = ConditionalSessionLogger(session_log_manager)
        
        # エラーが発生してもNoneを返し、例外は発生させない
        result = conditional_logger.conditional_log_start(
            True,  # 実行モード
            stage_id="stage01",
            student_id="123456A"
        )
        
        assert result is None  # エラー時はNoneを返す


class TestCompleteWorkflowIntegration:
    """完全ワークフローの統合テスト"""
    
    def test_student_complete_learning_workflow(self):
        """学生の完全学習ワークフロー統合テスト"""
        # 初期化
        hyperparameter_manager = HyperParameterManager()
        confirmation_flag_manager = InitialConfirmationFlagManager(hyperparameter_manager)
        stage_loader = Mock(spec=StageLoader)
        stage_description_renderer = StageDescriptionRenderer(stage_loader)
        session_log_manager = Mock(spec=SessionLogManager)
        conditional_session_logger = ConditionalSessionLogger(session_log_manager)
        
        stage_id = "stage01"
        student_id = "123456A"
        
        # ステップ1: 初回実行（確認モード）
        assert confirmation_flag_manager.is_first_execution(stage_id, student_id) is True
        assert confirmation_flag_manager.get_confirmation_mode() is False
        
        # ステップ2: ステージ説明表示
        mock_stage = Mock()
        mock_stage.id = stage_id
        mock_stage.title = "基本移動ステージ"
        mock_stage.description = "基本的な移動を学ぶステージ"
        mock_stage.board_size = (5, 5)
        mock_stage.player_start = Mock(x=0, y=0)
        mock_stage.goal_position = Mock(x=4, y=4)
        mock_stage.allowed_apis = ["move", "turn_left", "turn_right"]
        mock_stage.constraints = {"max_turns": 20}
        mock_stage.enemies = []
        mock_stage.items = []
        
        stage_loader.load_stage.return_value = mock_stage
        description = stage_description_renderer.display_stage_conditions(stage_id, student_id)
        
        # ステップ3: 説明表示済みマーク
        confirmation_flag_manager.mark_stage_intro_displayed(stage_id)
        
        # ステップ4: 確認モードでのセッションログ除外
        # SessionLogManagerの状態をモック
        session_log_manager.session_logger = Mock()
        session_log_manager.is_logging_enabled.return_value = False
        
        # should_log_sessionを使って確認モードでのログ除外を確認
        should_log = conditional_session_logger.should_log_session(False)
        assert should_log is False
        
        # ステップ5: 実行モードへの切り替え（学生がコードを理解後）
        confirmation_flag_manager.set_confirmation_mode(True)
        
        # ステップ6: 実行モードでの再実行
        assert confirmation_flag_manager.is_first_execution(stage_id, student_id) is False
        assert confirmation_flag_manager.get_confirmation_mode() is True
        
        # ステップ7: 実行モードでのセッションログ記録
        log_start_result = conditional_session_logger.conditional_log_start(
            True,
            stage_id=stage_id,
            student_id=student_id
        )
        assert log_start_result is not None
        
        # ステップ8: 学習データ記録（action_count等）
        event_result = conditional_session_logger.conditional_log_event(
            True,
            "move_action",
            {"action_count": 8}
        )
        assert event_result is not None
        
        # ステップ9: セッション完了
        log_end_result = conditional_session_logger.conditional_log_end(
            True,
            action_count=10,
            completed_successfully=True
        )
        assert log_end_result is not None
        
        # 全プロセスの完了確認
        current_status = conditional_session_logger.get_current_mode_status()
        assert current_status["confirmation_mode"] is True
        assert current_status["logging_enabled"] is True
        assert current_status["mode_description"] == "実行モード"