"""
InitialConfirmationFlagManagerの単体テスト
v1.2.4新機能: 初回確認モードフラグ管理システムのテスト
"""

import pytest
from engine.hyperparameter_manager import HyperParameterManager
from engine.initial_confirmation_flag_manager import InitialConfirmationFlagManager


class TestInitialConfirmationFlagManager:
    """InitialConfirmationFlagManagerクラスのテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
    
    def test_initialization(self):
        """初期化テスト"""
        assert isinstance(self.flag_manager.hyperparameter_manager, HyperParameterManager)
        
        # デフォルト値の確認
        assert self.flag_manager.get_confirmation_mode() is False  # デフォルトは確認モード
    
    def test_default_confirmation_mode(self):
        """デフォルト値がFalse（確認モード）であることを検証"""
        confirmation_mode = self.flag_manager.get_confirmation_mode()
        assert confirmation_mode is False, "デフォルトは確認モードである必要があります"
    
    def test_set_confirmation_mode_valid_values(self):
        """フラグ設定機能の正常ケーステスト"""
        # False（確認モード）に設定
        self.flag_manager.set_confirmation_mode(False)
        assert self.flag_manager.get_confirmation_mode() is False
        
        # True（実行モード）に設定
        self.flag_manager.set_confirmation_mode(True)
        assert self.flag_manager.get_confirmation_mode() is True
        
        # 再度False（確認モード）に設定
        self.flag_manager.set_confirmation_mode(False)
        assert self.flag_manager.get_confirmation_mode() is False
    
    def test_flag_transition_false_to_true_to_false(self):
        """フラグ遷移機能（False→True→False）の単体テスト"""
        # 初期状態: False（確認モード）
        assert self.flag_manager.get_confirmation_mode() is False
        
        # False→True（確認モード→実行モード）
        self.flag_manager.set_confirmation_mode(True)
        assert self.flag_manager.get_confirmation_mode() is True
        
        # True→False（実行モード→確認モード）
        self.flag_manager.set_confirmation_mode(False)
        assert self.flag_manager.get_confirmation_mode() is False
    
    def test_set_confirmation_mode_invalid_type(self):
        """フラグ設定時の型エラーテスト"""
        with pytest.raises(ValueError, match="confirmation_modeはbool型である必要があります"):
            self.flag_manager.set_confirmation_mode("invalid")
        
        with pytest.raises(ValueError, match="confirmation_modeはbool型である必要があります"):
            self.flag_manager.set_confirmation_mode(1)
        
        with pytest.raises(ValueError, match="confirmation_modeはbool型である必要があります"):
            self.flag_manager.set_confirmation_mode(None)
    
    def test_hyperparameter_manager_integration(self):
        """HyperParameterManagerとの統合が正しく動作することを検証"""
        # フラグマネージャー経由での設定
        self.flag_manager.set_confirmation_mode(True)
        
        # ハイパーパラメータマネージャーから直接確認
        assert self.hyperparameter_manager.data.initial_confirmation_mode is True
        
        # ハイパーパラメータマネージャー経由での直接設定
        self.hyperparameter_manager.data.initial_confirmation_mode = False
        
        # フラグマネージャー経由で確認
        assert self.flag_manager.get_confirmation_mode() is False
    
    def test_flag_state_immediate_reflection(self):
        """フラグ状態の即座反映機能をテストで確認"""
        # 設定直後の反映確認
        self.flag_manager.set_confirmation_mode(True)
        assert self.flag_manager.get_confirmation_mode() is True, "設定は即座に反映される必要があります"
        
        self.flag_manager.set_confirmation_mode(False)
        assert self.flag_manager.get_confirmation_mode() is False, "設定は即座に反映される必要があります"


class TestFirstExecutionDetection:
    """初回実行判定機能のテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
    
    def test_is_first_execution_with_new_stage(self):
        """新しいステージの初回実行判定テスト"""
        # 新しいステージは初回実行とみなされる
        assert self.flag_manager.is_first_execution("stage01") is True
        assert self.flag_manager.is_first_execution("stage02") is True
    
    def test_is_first_execution_with_displayed_stage(self):
        """表示済みステージの再実行判定テスト"""
        # ステージを表示済みとしてマーク
        self.flag_manager.mark_stage_intro_displayed("stage01")
        
        # 表示済みステージは再実行とみなされる
        assert self.flag_manager.is_first_execution("stage01") is False
        
        # 他のステージは依然として初回実行
        assert self.flag_manager.is_first_execution("stage02") is True
    
    def test_is_first_execution_invalid_stage_id(self):
        """無効なステージIDでのエラーテスト"""
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.flag_manager.is_first_execution("")
        
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.flag_manager.is_first_execution(None)
    
    def test_mark_stage_intro_displayed(self):
        """ステージ説明表示済みマーク機能のテスト"""
        # 初期状態では初回実行
        assert self.flag_manager.is_first_execution("stage01") is True
        
        # 表示済みマークを設定
        self.flag_manager.mark_stage_intro_displayed("stage01")
        
        # 表示済みマーク後は再実行
        assert self.flag_manager.is_first_execution("stage01") is False
    
    def test_mark_stage_intro_displayed_invalid_stage_id(self):
        """無効なステージIDでのマーク設定エラーテスト"""
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.flag_manager.mark_stage_intro_displayed("")
        
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.flag_manager.mark_stage_intro_displayed(None)
    
    def test_multiple_stages_tracking(self):
        """複数ステージの追跡テスト"""
        # stage01を表示済みマーク
        self.flag_manager.mark_stage_intro_displayed("stage01")
        
        # stage01は再実行、stage02は初回実行
        assert self.flag_manager.is_first_execution("stage01") is False
        assert self.flag_manager.is_first_execution("stage02") is True
        
        # stage02も表示済みマーク
        self.flag_manager.mark_stage_intro_displayed("stage02")
        
        # 両方とも再実行
        assert self.flag_manager.is_first_execution("stage01") is False
        assert self.flag_manager.is_first_execution("stage02") is False


class TestStageIntroHistory:
    """ステージ説明表示履歴管理のテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.hyperparameter_manager = HyperParameterManager()
        self.flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
    
    def test_get_intro_displayed_stages_empty(self):
        """表示済みステージ一覧取得（空の場合）"""
        displayed_stages = self.flag_manager.get_intro_displayed_stages()
        assert displayed_stages == []
    
    def test_get_intro_displayed_stages_with_stages(self):
        """表示済みステージ一覧取得（ステージありの場合）"""
        # 複数ステージを表示済みマーク
        self.flag_manager.mark_stage_intro_displayed("stage01")
        self.flag_manager.mark_stage_intro_displayed("stage03")
        
        displayed_stages = self.flag_manager.get_intro_displayed_stages()
        assert set(displayed_stages) == {"stage01", "stage03"}
    
    def test_reset_stage_intro_history(self):
        """ステージ説明表示履歴のリセット機能テスト"""
        # 複数ステージを表示済みマーク
        self.flag_manager.mark_stage_intro_displayed("stage01")
        self.flag_manager.mark_stage_intro_displayed("stage02")
        
        # リセット前の確認
        assert len(self.flag_manager.get_intro_displayed_stages()) == 2
        assert self.flag_manager.is_first_execution("stage01") is False
        
        # 履歴リセット
        self.flag_manager.reset_stage_intro_history()
        
        # リセット後の確認
        assert len(self.flag_manager.get_intro_displayed_stages()) == 0
        assert self.flag_manager.is_first_execution("stage01") is True
        assert self.flag_manager.is_first_execution("stage02") is True
    
    def test_stage_intro_history_persistence(self):
        """ステージ説明表示履歴の永続性テスト"""
        # ステージをマーク
        self.flag_manager.mark_stage_intro_displayed("stage01")
        
        # 別のフラグマネージャーインスタンスで同じデータを参照
        another_flag_manager = InitialConfirmationFlagManager(self.hyperparameter_manager)
        
        # 履歴が共有されていることを確認
        assert another_flag_manager.is_first_execution("stage01") is False
        assert "stage01" in another_flag_manager.get_intro_displayed_stages()