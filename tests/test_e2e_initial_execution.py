#!/usr/bin/env python3
"""
E2Eテスト: 初回確認モード機能の完全動作検証
v1.2.4新機能: 学生初回体験の完全フロー検証とパフォーマンステスト
"""

import pytest
import time
from unittest.mock import Mock, patch
from engine.hyperparameter_manager import HyperParameterManager
from engine.initial_confirmation_flag_manager import InitialConfirmationFlagManager
from engine.stage_description_renderer import StageDescriptionRenderer
from engine.conditional_session_logger import ConditionalSessionLogger
from engine.session_log_manager import SessionLogManager
from engine.stage_loader import StageLoader


class TestE2EInitialExecution:
    """学生初回体験の完全フロー E2Eテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        # 実際のクラスインスタンスを使用（モックなし）
        self.hyperparameter_manager = HyperParameterManager()
        self.confirmation_flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
        self.stage_loader = Mock(spec=StageLoader)  # StageLoaderのみモック
        self.stage_description_renderer = StageDescriptionRenderer(self.stage_loader)
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_session_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_complete_first_time_student_experience(self):
        """学生初回体験の完全フローE2Eテスト（ステージ理解→フラグ変更→実行）"""
        stage_id = "stage01"
        student_id = "123456A"
        
        # === フェーズ1: 学生が初回実行 ===
        print(f"\n=== フェーズ1: 学生初回実行開始 ({stage_id}) ===")
        
        # 初回実行判定
        is_first_execution = self.confirmation_flag_manager.is_first_execution(stage_id, student_id)
        assert is_first_execution is True, "初回実行が正しく検出されていません"
        print("✅ 初回実行を検出")
        
        # 確認モード状態の確認（デフォルト）
        confirmation_mode = self.confirmation_flag_manager.get_confirmation_mode()
        assert confirmation_mode is False, "デフォルトの確認モードが正しく設定されていません"
        print("✅ 確認モード（学習フェーズ）を確認")
        
        # === フェーズ2: ステージ理解プロセス ===
        print("\n=== フェーズ2: ステージ理解プロセス ===")
        
        # ステージデータのモック設定
        mock_stage = self._create_mock_stage(stage_id)
        self.stage_loader.load_stage.return_value = mock_stage
        
        # ステージ説明表示（学生がステージ内容を理解）
        stage_description = self.stage_description_renderer.display_stage_conditions(stage_id, student_id)
        
        # ステージ説明の内容検証
        assert f"ステージ情報: {mock_stage.title}" in stage_description
        assert mock_stage.description in stage_description
        assert "🎯 ボード情報:" in stage_description
        assert "⚡ 制約条件:" in stage_description
        assert "🏆 クリア条件:" in stage_description
        print("✅ ステージ説明が正常に表示されました")
        
        # 表示済みマークの設定（自動実行）
        self.confirmation_flag_manager.mark_stage_intro_displayed(stage_id)
        print("✅ ステージ説明表示済みマークを設定")
        
        # === フェーズ3: セッションログ除外の確認 ===
        print("\n=== フェーズ3: 確認モードでのセッションログ除外 ===")
        
        # 確認モードでのログ除外動作
        should_log_confirmation = self.conditional_session_logger.should_log_session(False)
        assert should_log_confirmation is False, "確認モードでログが除外されていません"
        print("✅ 確認モードでセッションログが除外されています")
        
        # セッション開始ログの除外
        start_log_result = self.conditional_session_logger.conditional_log_start(
            False,  # 確認モード
            stage_id=stage_id,
            student_id=student_id
        )
        assert start_log_result is None, "確認モードでセッション開始ログが除外されていません"
        print("✅ セッション開始ログが除外されました")
        
        # === フェーズ4: 学生がコードを理解し実行モードに切り替え ===
        print("\n=== フェーズ4: 実行モードへの切り替え ===")
        
        # 再実行確認（表示済みなので初回実行ではない）
        is_second_execution = self.confirmation_flag_manager.is_first_execution(stage_id, student_id)
        assert is_second_execution is False, "二回目実行が正しく判定されていません"
        print("✅ 二回目実行を正しく判定")
        
        # 実行モードへの切り替え（学生が手動実行）
        self.confirmation_flag_manager.set_confirmation_mode(True)
        execution_mode = self.confirmation_flag_manager.get_confirmation_mode()
        assert execution_mode is True, "実行モードへの切り替えが正しく動作していません"
        print("✅ 実行モードに切り替え完了")
        
        # === フェーズ5: 実行モードでのセッションログ記録 ===
        print("\n=== フェーズ5: 実行モードでのセッションログ記録 ===")
        
        # 実行モードでのログ記録動作
        should_log_execution = self.conditional_session_logger.should_log_session(True)
        assert should_log_execution is True, "実行モードでログが記録されていません"
        print("✅ 実行モードでセッションログが有効化されています")
        
        # セッション開始ログの記録
        start_log_execution_result = self.conditional_session_logger.conditional_log_start(
            True,  # 実行モード
            stage_id=stage_id,
            student_id=student_id,
            framework_version="v1.2.4"
        )
        assert start_log_execution_result is not None, "実行モードでセッション開始ログが記録されていません"
        assert start_log_execution_result["status"] == "logged"
        print("✅ セッション開始ログが記録されました")
        
        # アクション実行ログの記録（SessionLogManagerにsession_loggerを設定）
        self.session_log_manager.session_logger = Mock()
        for action_num in range(1, 6):  # 5回のアクション
            event_result = self.conditional_session_logger.conditional_log_event(
                True,  # 実行モード
                "move_action",
                {"action_count": action_num, "position": [action_num, 0]}
            )
            assert event_result is not None, f"アクション{action_num}のログが記録されていません"
        print("✅ アクション実行ログが記録されました")
        
        # セッション終了ログの記録
        end_log_result = self.conditional_session_logger.conditional_log_end(
            True,  # 実行モード
            action_count=5,
            completed_successfully=True
        )
        assert end_log_result is not None, "実行モードでセッション終了ログが記録されていません"
        assert end_log_result["status"] == "logged"
        print("✅ セッション終了ログが記録されました")
        
        # === フェーズ6: 最終状態検証 ===
        print("\n=== フェーズ6: 最終状態検証 ===")
        
        # 表示済みステージの確認
        displayed_stages = self.confirmation_flag_manager.get_intro_displayed_stages()
        assert stage_id in displayed_stages, "表示済みステージが記録されていません"
        print(f"✅ 表示済みステージ: {displayed_stages}")
        
        # 現在のモード状態確認
        current_status = self.conditional_session_logger.get_current_mode_status()
        assert current_status["confirmation_mode"] is True
        assert current_status["logging_enabled"] is True
        assert current_status["mode_description"] == "実行モード"
        print(f"✅ 最終モード状態: {current_status['mode_description']}")
        
        print("\n🎉 学生初回体験の完全フローが正常に完了しました！")
    
    def _create_mock_stage(self, stage_id: str):
        """テスト用のモックステージを作成"""
        mock_stage = Mock()
        mock_stage.id = stage_id
        mock_stage.title = "基本移動ステージ"
        mock_stage.description = "基本的な移動操作を学ぶステージです。turn_leftとturn_right、moveを使ってゴールを目指しましょう。"
        mock_stage.board_size = (5, 5)
        mock_stage.player_start = Mock(x=0, y=0)
        mock_stage.goal_position = Mock(x=4, y=4)
        mock_stage.allowed_apis = ["turn_left", "turn_right", "move", "see"]
        mock_stage.constraints = {"max_turns": 20}
        mock_stage.enemies = []
        mock_stage.items = []
        return mock_stage


class TestE2EModeSwitchingWorkflow:
    """モード切替ワークフローのE2Eテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.confirmation_flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_session_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_mode_switching_workflow_e2e(self):
        """モード切替ワークフローのE2Eテスト"""
        stage_id = "stage02"
        student_id = "654321B"
        
        print(f"\n=== モード切替ワークフロー開始 ({stage_id}) ===")
        
        # === ステップ1: 初期状態（確認モード） ===
        assert self.confirmation_flag_manager.get_confirmation_mode() is False
        assert self.conditional_session_logger.should_log_session(False) is False
        print("✅ 初期状態: 確認モード")
        
        # === ステップ2: 確認モード→実行モード切り替え ===
        self.confirmation_flag_manager.set_confirmation_mode(True)
        assert self.confirmation_flag_manager.get_confirmation_mode() is True
        assert self.conditional_session_logger.should_log_session(True) is True
        print("✅ 確認モード → 実行モード")
        
        # === ステップ3: 実行モード→確認モード切り替え ===
        self.confirmation_flag_manager.set_confirmation_mode(False)
        assert self.confirmation_flag_manager.get_confirmation_mode() is False
        assert self.conditional_session_logger.should_log_session(False) is False
        print("✅ 実行モード → 確認モード")
        
        # === ステップ4: 再度実行モードに切り替え ===
        self.confirmation_flag_manager.set_confirmation_mode(True)
        assert self.confirmation_flag_manager.get_confirmation_mode() is True
        assert self.conditional_session_logger.should_log_session(True) is True
        print("✅ 確認モード → 実行モード（再切り替え）")
        
        print("🎉 モード切替ワークフローが正常に完了しました！")


class TestE2ERegressionTest:
    """既存機能への影響がないことを確認する回帰テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.confirmation_flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
    
    def test_hyperparameter_manager_regression(self):
        """HyperParameterManagerの既存機能回帰テスト"""
        print("\n=== HyperParameterManager回帰テスト ===")
        
        # 既存のハイパーパラメータ設定が正常に動作することを確認
        stage_id = "stage01"
        student_id = "123456A"
        logging_enabled = True
        
        self.hyperparameter_manager.set_stage_id(stage_id)
        self.hyperparameter_manager.set_student_id(student_id)
        self.hyperparameter_manager.set_logging_enabled(logging_enabled)
        
        # 既存のgetterメソッドが正常に動作することを確認
        assert self.hyperparameter_manager.get_stage_id() == stage_id
        assert self.hyperparameter_manager.get_student_id() == student_id
        assert self.hyperparameter_manager.is_logging_enabled() == logging_enabled
        
        # v1.2.4新フィールドが追加されてもvalidationが正常に動作することを確認
        validation_result = self.hyperparameter_manager.validate()
        assert validation_result is True
        
        print("✅ HyperParameterManagerの既存機能は正常です")
    
    def test_new_fields_backward_compatibility(self):
        """新フィールドの後方互換性テスト"""
        print("\n=== 新フィールド後方互換性テスト ===")
        
        # 新フィールドがデフォルト値で正しく初期化されることを確認
        assert self.hyperparameter_manager.data.initial_confirmation_mode is False
        assert isinstance(self.hyperparameter_manager.data.stage_intro_displayed, dict)
        assert len(self.hyperparameter_manager.data.stage_intro_displayed) == 0
        
        # 新フィールドが既存の機能に影響しないことを確認
        summary = self.hyperparameter_manager.get_summary()
        assert "stage_id" in summary
        assert "student_id" in summary
        assert "log_enabled" in summary
        
        print("✅ 新フィールドの後方互換性は正常です")


class TestE2EPerformanceValidation:
    """パフォーマンス目標の検証テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.confirmation_flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
        self.stage_loader = Mock(spec=StageLoader)
        self.stage_description_renderer = StageDescriptionRenderer(self.stage_loader)
        self.session_log_manager = Mock(spec=SessionLogManager)
        self.conditional_session_logger = ConditionalSessionLogger(self.session_log_manager)
    
    def test_flag_judgment_performance(self):
        """フラグ判定のパフォーマンステスト（目標: <1ms）"""
        print("\n=== フラグ判定パフォーマンステスト（目標: <1ms） ===")
        
        stage_id = "stage01"
        student_id = "123456A"
        
        # フラグ判定の実行時間を測定
        iterations = 1000  # 1000回実行して平均を取る
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            self.conditional_session_logger.should_log_session(False)
            self.confirmation_flag_manager.get_confirmation_mode()
            self.confirmation_flag_manager.is_first_execution(stage_id, student_id)
        end_time = time.perf_counter()
        
        average_time_ms = ((end_time - start_time) / iterations) * 1000
        
        print(f"フラグ判定平均時間: {average_time_ms:.4f}ms")
        assert average_time_ms < 1.0, f"フラグ判定が目標時間を超過: {average_time_ms:.4f}ms > 1.0ms"
        print("✅ フラグ判定パフォーマンス目標達成")
    
    def test_description_display_performance(self):
        """説明表示のパフォーマンステスト（目標: <50ms）"""
        print("\n=== 説明表示パフォーマンステスト（目標: <50ms） ===")
        
        stage_id = "stage01"
        student_id = "123456A"
        
        # ステージデータのモック設定
        mock_stage = Mock()
        mock_stage.id = stage_id
        mock_stage.title = "パフォーマンステスト用ステージ"
        mock_stage.description = "パフォーマンステスト用の説明" * 50  # 長い説明文
        mock_stage.board_size = (10, 10)
        mock_stage.player_start = Mock(x=0, y=0)
        mock_stage.goal_position = Mock(x=9, y=9)
        mock_stage.allowed_apis = ["turn_left", "turn_right", "move", "see", "attack", "pickup"]
        mock_stage.constraints = {"max_turns": 100}
        mock_stage.enemies = [{"position": [i, i], "type": "normal"} for i in range(5)]
        mock_stage.items = [{"position": [i, i+1], "name": f"item{i}", "type": "weapon"} for i in range(5)]
        
        self.stage_loader.load_stage.return_value = mock_stage
        
        # 説明表示の実行時間を測定
        start_time = time.perf_counter()
        description = self.stage_description_renderer.display_stage_conditions(stage_id, student_id)
        end_time = time.perf_counter()
        
        execution_time_ms = (end_time - start_time) * 1000
        
        print(f"説明表示実行時間: {execution_time_ms:.4f}ms")
        assert execution_time_ms < 50.0, f"説明表示が目標時間を超過: {execution_time_ms:.4f}ms > 50.0ms"
        assert len(description) > 0, "説明表示の内容が空です"
        print("✅ 説明表示パフォーマンス目標達成")
    
    def test_session_log_condition_performance(self):
        """セッションログ条件判定のパフォーマンステスト"""
        print("\n=== セッションログ条件判定パフォーマンステスト ===")
        
        # 大量の条件判定の実行時間を測定
        iterations = 10000
        
        start_time = time.perf_counter()
        for i in range(iterations):
            confirmation_mode = i % 2 == 0  # 交互に切り替え
            self.conditional_session_logger.should_log_session(confirmation_mode)
        end_time = time.perf_counter()
        
        total_time_ms = (end_time - start_time) * 1000
        average_time_ms = total_time_ms / iterations
        
        print(f"条件判定合計時間: {total_time_ms:.4f}ms")
        print(f"条件判定平均時間: {average_time_ms:.6f}ms")
        assert average_time_ms < 0.01, f"条件判定が遅すぎます: {average_time_ms:.6f}ms > 0.01ms"
        print("✅ セッションログ条件判定パフォーマンス良好")


class TestE2ESystemIntegration:
    """システム統合の最終検証テスト"""
    
    @patch('main.hyperparameter_manager')
    @patch('main.confirmation_flag_manager')
    @patch('main.stage_description_renderer')
    @patch('main.conditional_session_logger')
    def test_main_py_integration_simulation(self, mock_conditional_logger, mock_renderer, mock_flag_manager, mock_hpm):
        """main.py統合のシミュレーションテスト"""
        print("\n=== main.py統合シミュレーションテスト ===")
        
        from main import setup_confirmation_mode
        
        # 初回実行・確認モード シナリオ
        mock_flag_manager.is_first_execution.return_value = True
        mock_flag_manager.get_confirmation_mode.return_value = False
        mock_renderer.display_stage_conditions.return_value = "シミュレーション用ステージ説明"
        
        result = setup_confirmation_mode("stage01", "123456A")
        
        # 呼び出し検証
        mock_flag_manager.is_first_execution.assert_called_with("stage01", "123456A")
        mock_flag_manager.get_confirmation_mode.assert_called_once()
        mock_renderer.display_stage_conditions.assert_called_with("stage01", "123456A")
        mock_flag_manager.mark_stage_intro_displayed.assert_called_with("stage01")
        
        assert result is True
        print("✅ main.py統合シミュレーション成功")
    
    def test_all_components_integration_health_check(self):
        """全コンポーネント統合のヘルスチェック"""
        print("\n=== 全コンポーネント統合ヘルスチェック ===")
        
        # すべてのコンポーネントを実際に初期化
        hyperparameter_manager = HyperParameterManager()
        confirmation_flag_manager = InitialConfirmationFlagManager(hyperparameter_manager)
        stage_loader = Mock(spec=StageLoader)
        stage_description_renderer = StageDescriptionRenderer(stage_loader)
        session_log_manager = Mock(spec=SessionLogManager)
        conditional_session_logger = ConditionalSessionLogger(session_log_manager)
        
        # 各コンポーネントの基本機能が正常に動作することを確認
        components_health = {}
        
        try:
            # HyperParameterManager
            hyperparameter_manager.set_stage_id("test")
            components_health["HyperParameterManager"] = "OK"
        except Exception as e:
            components_health["HyperParameterManager"] = f"ERROR: {e}"
        
        try:
            # InitialConfirmationFlagManager
            confirmation_flag_manager.set_confirmation_mode(True)
            confirmation_flag_manager.get_confirmation_mode()
            components_health["InitialConfirmationFlagManager"] = "OK"
        except Exception as e:
            components_health["InitialConfirmationFlagManager"] = f"ERROR: {e}"
        
        try:
            # StageDescriptionRenderer（モック使用）
            mock_stage = Mock()
            mock_stage.id = "test"
            mock_stage.title = "テスト"
            mock_stage.description = "テスト説明"
            mock_stage.board_size = (3, 3)
            mock_stage.player_start = Mock(x=0, y=0)
            mock_stage.goal_position = Mock(x=2, y=2)
            mock_stage.allowed_apis = ["move"]
            mock_stage.constraints = {"max_turns": 10}
            mock_stage.enemies = []
            mock_stage.items = []
            
            stage_loader.load_stage.return_value = mock_stage
            stage_description_renderer.display_stage_conditions("test", "test")
            components_health["StageDescriptionRenderer"] = "OK"
        except Exception as e:
            components_health["StageDescriptionRenderer"] = f"ERROR: {e}"
        
        try:
            # ConditionalSessionLogger
            conditional_session_logger.should_log_session(True)
            components_health["ConditionalSessionLogger"] = "OK"
        except Exception as e:
            components_health["ConditionalSessionLogger"] = f"ERROR: {e}"
        
        # 結果レポート
        print("コンポーネントヘルスチェック結果:")
        all_ok = True
        for component, status in components_health.items():
            status_icon = "✅" if status == "OK" else "❌"
            print(f"  {status_icon} {component}: {status}")
            if status != "OK":
                all_ok = False
        
        assert all_ok, f"一部のコンポーネントでエラーが発生しました: {components_health}"
        print("🎉 全コンポーネント統合ヘルスチェック成功！")