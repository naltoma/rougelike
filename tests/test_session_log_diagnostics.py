#!/usr/bin/env python3
"""
SessionLogManager診断機能のテスト
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from engine.session_log_manager import SessionLogManager, DiagnosticReport
from engine.session_logging import SessionLogger


class TestSessionLogManagerDiagnostics:
    """SessionLogManager診断機能のテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.manager = SessionLogManager()
    
    def test_diagnose_logging_system_no_logger(self):
        """SessionLoggerが初期化されていない場合の診断"""
        with patch.object(self.manager, '_check_log_directories', return_value=True):
            with patch.object(self.manager, '_verify_permissions', return_value=True):
                report = self.manager.diagnose_logging_system()
        
        assert isinstance(report, DiagnosticReport)
        assert not report.session_logger_enabled
        assert report.log_directory_exists
        assert report.permissions_valid
        assert report.has_issues()
        assert "SessionLoggerが初期化されていません" in report.issues
        assert "enable_default_logging()を呼び出してください" in report.recommendations
    
    def test_diagnose_logging_system_healthy(self):
        """正常なシステムの診断"""
        # Mock SessionLoggerを設定
        mock_session_logger = MagicMock(spec=SessionLogger)
        mock_session_logger.log_event = MagicMock()
        self.manager.session_logger = mock_session_logger
        
        with patch.object(self.manager, '_check_log_directories', return_value=True):
            with patch.object(self.manager, '_verify_permissions', return_value=True):
                report = self.manager.diagnose_logging_system()
        
        assert report.session_logger_enabled
        assert report.log_directory_exists
        assert report.permissions_valid
        assert not report.has_issues()
        assert len(report.issues) == 0
        assert len(report.recommendations) == 0
    
    def test_diagnose_logging_system_multiple_issues(self):
        """複数の問題がある場合の診断"""
        with patch.object(self.manager, '_check_log_directories', return_value=False):
            with patch.object(self.manager, '_verify_permissions', return_value=False):
                report = self.manager.diagnose_logging_system()
        
        assert not report.session_logger_enabled
        assert not report.log_directory_exists
        assert not report.permissions_valid
        assert report.has_issues()
        assert len(report.issues) >= 3  # SessionLogger、ディレクトリ、権限の3つの問題
        assert len(report.recommendations) >= 3
    
    def test_check_log_directories_exists(self):
        """ログディレクトリが存在する場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            data_dir = temp_path / "data" / "sessions"
            data_dir.mkdir(parents=True)
            
            with patch('config.ROOT_DIR', temp_path):
                result = self.manager._check_log_directories()
            
            assert result is True
    
    def test_check_log_directories_not_exists(self):
        """ログディレクトリが存在しない場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                result = self.manager._check_log_directories()
            
            assert result is False
    
    def test_check_session_logger_status_no_logger(self):
        """SessionLoggerが存在しない場合"""
        result = self.manager._check_session_logger_status()
        assert result is False
    
    def test_check_session_logger_status_valid_logger(self):
        """有効なSessionLoggerの場合"""
        mock_session_logger = MagicMock(spec=SessionLogger)
        mock_session_logger.log_event = MagicMock()
        self.manager.session_logger = mock_session_logger
        
        result = self.manager._check_session_logger_status()
        assert result is True
    
    def test_verify_permissions_success(self):
        """書き込み権限が有効な場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            data_dir = temp_path / "data" / "sessions"
            data_dir.mkdir(parents=True)
            
            with patch('config.ROOT_DIR', temp_path):
                result = self.manager._verify_permissions()
            
            assert result is True
    
    def test_verify_permissions_creates_directory(self):
        """権限確認時にディレクトリが作成される場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                result = self.manager._verify_permissions()
            
            assert result is True
            assert (temp_path / "data" / "sessions").exists()
    
    def test_diagnostic_report_format(self):
        """診断レポートのフォーマットテスト"""
        report = DiagnosticReport(
            timestamp=datetime.now(),
            session_logger_enabled=False,
            log_directory_exists=True,
            permissions_valid=False,
            issues=["テスト問題1", "テスト問題2"],
            recommendations=["テスト推奨1", "テスト推奨2"]
        )
        
        formatted = report.format_report()
        
        assert "🔍 システム診断レポート" in formatted
        assert "SessionLogger有効: ❌" in formatted
        assert "ログディレクトリ: ✅" in formatted
        assert "書き込み権限: ❌" in formatted
        assert "⚠️  検出された問題:" in formatted
        assert "💡 推奨事項:" in formatted
        assert "テスト問題1" in formatted
        assert "テスト推奨1" in formatted


if __name__ == "__main__":
    pytest.main([__file__])