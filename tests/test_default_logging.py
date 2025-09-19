#!/usr/bin/env python3
"""
デフォルトログ生成機能のテスト
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from engine.session_log_manager import SessionLogManager, LogResult


class TestDefaultLogging:
    """デフォルトログ生成機能のテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.manager = SessionLogManager()
    
    def test_enable_default_logging_success(self):
        """デフォルトログ有効化成功のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                # SessionLoggerをモック
                with patch('engine.session_log_manager.SessionLogger') as mock_logger_class:
                    mock_logger = MagicMock()
                    mock_logger.start_session = MagicMock()
                    mock_logger_class.return_value = mock_logger
                    
                    result = self.manager.enable_default_logging("123456A", "stage01")
            
            assert isinstance(result, LogResult)
            assert result.success is True
            assert result.log_path is not None
            assert result.session_id is not None
            assert result.error_message is None
            
            # SessionLoggerが作成されていることを確認
            assert self.manager.session_logger is not None
            assert self.manager.enabled is True
    
    def test_enable_default_logging_default_user(self):
        """デフォルト学生IDの使用テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                with patch('engine.session_log_manager.SessionLogger') as mock_logger_class:
                    mock_logger = MagicMock()
                    mock_logger_class.return_value = mock_logger
                    
                    # 空の学生IDを渡す
                    result = self.manager.enable_default_logging("", "stage01")
            
            # start_sessionが"DEFAULT_USER"で呼ばれていることを確認
            mock_logger.start_session.assert_called_once()
            args, kwargs = mock_logger.start_session.call_args
            assert args[0] == "DEFAULT_USER"  # student_id
    
    def test_enable_default_logging_already_enabled(self):
        """既に有効化されている場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                with patch('engine.session_log_manager.SessionLogger') as mock_logger_class:
                    mock_logger = MagicMock()
                    mock_logger.session_id = "test_session_123"
                    mock_logger_class.return_value = mock_logger
                    
                    # 1回目の有効化
                    self.manager.enable_default_logging("123456A", "stage01")
                    
                    # 2回目の有効化（force_enable=False）
                    result = self.manager.enable_default_logging("123456B", "stage02", force_enable=False)
            
            # 既に有効なので新しいSessionLoggerは作成されない
            assert result.success is True
            assert result.session_id == "test_session_123"
    
    def test_enable_default_logging_force_enable(self):
        """強制有効化のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                with patch('engine.session_log_manager.SessionLogger') as mock_logger_class:
                    mock_logger = MagicMock()
                    mock_logger_class.return_value = mock_logger
                    
                    # 1回目の有効化
                    self.manager.enable_default_logging("123456A", "stage01")
                    
                    # 2回目の有効化（force_enable=True, デフォルト）
                    result = self.manager.enable_default_logging("123456B", "stage02", force_enable=True)
            
            # 強制有効化なので新しいSessionLoggerが作成される
            assert result.success is True
            assert mock_logger_class.call_count == 2  # 2回作成されている
    
    def test_enable_default_logging_error_handling(self):
        """エラー処理のテスト"""
        with patch('config.ROOT_DIR', Path("/invalid/path")):
            with patch('engine.session_log_manager.SessionLogger') as mock_logger_class:
                # SessionLogger作成でエラーが発生
                mock_logger_class.side_effect = Exception("ログ初期化エラー")
                
                result = self.manager.enable_default_logging("123456A", "stage01")
        
        assert result.success is False
        assert result.log_path is None
        assert result.error_message is not None
        assert "セッションログの有効化に失敗しました" in result.error_message
    
    def test_ensure_log_directories(self):
        """ログディレクトリ作成のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                self.manager._ensure_log_directories()
            
            # 必要なディレクトリが作成されていることを確認
            expected_dirs = [
                temp_path / "data",
                temp_path / "data" / "sessions",
                temp_path / "data" / "diagnostics", 
                temp_path / "data" / "exports",
                temp_path / "data" / "backup" / "archived"
            ]
            
            for expected_dir in expected_dirs:
                assert expected_dir.exists()
                assert expected_dir.is_dir()
    
    def test_ensure_log_directories_error(self):
        """ログディレクトリ作成エラーのテスト"""
        with patch('config.ROOT_DIR', Path("/invalid/readonly/path")):
            from engine.session_log_manager import LogFileAccessError
            
            with pytest.raises(LogFileAccessError):
                self.manager._ensure_log_directories()


if __name__ == "__main__":
    pytest.main([__file__])