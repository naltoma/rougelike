"""
HyperParameterManagerの単体テスト
v1.2.4新機能: 初回確認モード関連フィールドのテストを含む
"""

import pytest
from engine.hyperparameter_manager import HyperParametersData, HyperParameterManager, HyperParameterError


class TestHyperParametersData:
    """HyperParametersDataクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        data = HyperParametersData()
        assert data.stage_id == "stage01"
        assert data.student_id is None
        assert data.log_enabled is True
        
        # v1.2.4新機能: 初回確認モード関連フィールドのデフォルト値
        assert data.initial_confirmation_mode is False  # デフォルトは確認モード
        assert isinstance(data.stage_intro_displayed, dict)
        assert len(data.stage_intro_displayed) == 0
    
    def test_v124_new_fields_validation(self):
        """v1.2.4新フィールドのバリデーションテスト"""
        # 正常なケース
        data = HyperParametersData(
            initial_confirmation_mode=True,
            stage_intro_displayed={"stage01": True, "stage02": False}
        )
        assert data.initial_confirmation_mode is True
        assert data.stage_intro_displayed == {"stage01": True, "stage02": False}
    
    def test_v124_invalid_confirmation_mode_type(self):
        """初回確認モードフラグの型エラーテスト"""
        with pytest.raises(ValueError, match="initial_confirmation_modeはbool型である必要があります"):
            HyperParametersData(initial_confirmation_mode="invalid")
    
    def test_v124_invalid_stage_intro_displayed_type(self):
        """stage_intro_displayedの型エラーテスト"""
        with pytest.raises(ValueError, match="stage_intro_displayedはdict型である必要があります"):
            HyperParametersData(stage_intro_displayed="invalid")
    
    def test_existing_validation_still_works(self):
        """既存のバリデーション機能が正常に動作することを確認"""
        # 空のステージIDのテスト
        with pytest.raises(ValueError, match="ステージIDは必須です"):
            HyperParametersData(stage_id="")
        
        # 空文字の学生IDのテスト
        with pytest.raises(ValueError, match="学生IDが空文字です"):
            HyperParametersData(student_id="")


class TestHyperParameterManager:
    """HyperParameterManagerクラスの基本動作テスト"""
    
    def test_initialization(self):
        """初期化テスト"""
        manager = HyperParameterManager()
        assert isinstance(manager.data, HyperParametersData)
        
        # v1.2.4新機能: 初期化時のデフォルト値確認
        assert manager.data.initial_confirmation_mode is False
        assert isinstance(manager.data.stage_intro_displayed, dict)
    
    def test_validate_success(self):
        """バリデーション成功テスト"""
        manager = HyperParameterManager()
        manager.data.student_id = "123456A"
        
        # バリデーションが成功することを確認
        result = manager.validate()
        assert result is True
    
    def test_validate_missing_student_id(self):
        """学生ID未設定エラーのテスト"""
        manager = HyperParameterManager()
        # student_idがNoneのままではバリデーションが失敗する
        
        with pytest.raises(HyperParameterError, match="学生IDが設定されていません"):
            manager.validate()