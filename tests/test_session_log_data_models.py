"""
セッションログデータモデルのテスト
"""

import pytest
from pathlib import Path
from datetime import datetime

from engine.session_log_manager import (
    LogResult, DiagnosticReport, LogFileInfo, LogConfig, ValidationResult,
    LoggingSystemError, LogFileAccessError, LogValidationError, ConfigurationError
)
from engine.session_logging import LogLevel


class TestLogResult:
    """LogResultデータモデルのテスト"""
    
    def test_success_result(self):
        """成功ケースのテスト"""
        result = LogResult(
            success=True,
            log_path=Path("/test/log.jsonl"),
            error_message=None,
            session_id="test_session_123"
        )
        
        assert result.success is True
        assert result.log_path == Path("/test/log.jsonl")
        assert result.error_message is None
        assert result.session_id == "test_session_123"
    
    def test_failure_result(self):
        """失敗ケースのテスト"""
        result = LogResult(
            success=False,
            log_path=None,
            error_message="ログファイルの作成に失敗しました",
            session_id=None
        )
        
        assert result.success is False
        assert result.log_path is None
        assert result.error_message == "ログファイルの作成に失敗しました"
        assert result.session_id is None


class TestDiagnosticReport:
    """DiagnosticReportデータモデルのテスト"""
    
    def test_healthy_system(self):
        """正常システムのテスト"""
        report = DiagnosticReport(
            timestamp=datetime.now(),
            session_logger_enabled=True,
            log_directory_exists=True,
            permissions_valid=True,
            issues=[],
            recommendations=[]
        )
        
        assert not report.has_issues()
        formatted = report.format_report()
        assert "✅ システムは正常です" in formatted
        assert "SessionLogger有効: ✅" in formatted
    
    def test_problematic_system(self):
        """問題のあるシステムのテスト"""
        report = DiagnosticReport(
            timestamp=datetime.now(),
            session_logger_enabled=False,
            log_directory_exists=False,
            permissions_valid=False,
            issues=[
                "ログディレクトリが存在しません",
                "書き込み権限がありません"
            ],
            recommendations=[
                "ログディレクトリを作成してください",
                "書き込み権限を設定してください"
            ]
        )
        
        assert report.has_issues()
        formatted = report.format_report()
        assert "⚠️  検出された問題:" in formatted
        assert "💡 推奨事項:" in formatted
        assert "ログディレクトリが存在しません" in formatted


class TestLogFileInfo:
    """LogFileInfoデータモデルのテスト"""
    
    def test_log_file_info_creation(self):
        """ログファイル情報の作成テスト"""
        now = datetime.now()
        info = LogFileInfo(
            file_path=Path("/data/sessions/20250903_123456_123456A.jsonl"),
            student_id="123456A",
            session_id="session_123",
            created_at=now,
            file_size=1024,
            entry_count=50,
            last_modified=now
        )
        
        assert info.file_path.name == "20250903_123456_123456A.jsonl"
        assert info.student_id == "123456A"
        assert info.session_id == "session_123"
        assert info.file_size == 1024
        assert info.entry_count == 50


class TestLogConfig:
    """LogConfigデータモデルのテスト"""
    
    def test_default_config(self):
        """デフォルト設定のテスト"""
        config = LogConfig(
            log_level=LogLevel.INFO,
            output_directory=Path("/data/sessions"),
            file_rotation=True,
            max_file_size=10 * 1024 * 1024,  # 10MB
            google_sheets_sync=False,
            retention_days=30
        )
        
        assert config.log_level == LogLevel.INFO
        assert config.output_directory == Path("/data/sessions")
        assert config.file_rotation is True
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.google_sheets_sync is False
        assert config.retention_days == 30


class TestValidationResult:
    """ValidationResultデータモデルのテスト"""
    
    def test_valid_log(self):
        """有効なログのテスト"""
        result = ValidationResult(
            is_valid=True,
            total_entries=100,
            corrupted_entries=[],
            missing_fields=[],
            recommendations=[]
        )
        
        assert result.is_valid is True
        assert result.total_entries == 100
        assert len(result.corrupted_entries) == 0
        assert len(result.missing_fields) == 0
    
    def test_invalid_log(self):
        """無効なログのテスト"""
        result = ValidationResult(
            is_valid=False,
            total_entries=100,
            corrupted_entries=[15, 23, 67],
            missing_fields=["timestamp", "session_id"],
            recommendations=[
                "破損したエントリを修復してください",
                "不足フィールドを補完してください"
            ]
        )
        
        assert result.is_valid is False
        assert result.total_entries == 100
        assert result.corrupted_entries == [15, 23, 67]
        assert "timestamp" in result.missing_fields
        assert "session_id" in result.missing_fields
        assert len(result.recommendations) == 2


class TestErrorHandling:
    """エラーハンドリングクラスのテスト"""
    
    def test_logging_system_error_inheritance(self):
        """エラークラス継承のテスト"""
        # LogFileAccessErrorがLoggingSystemErrorを継承していることを確認
        access_error = LogFileAccessError("ファイルアクセスエラー")
        assert isinstance(access_error, LoggingSystemError)
        
        # LogValidationErrorがLoggingSystemErrorを継承していることを確認
        validation_error = LogValidationError("検証エラー")
        assert isinstance(validation_error, LoggingSystemError)
        
        # ConfigurationErrorがLoggingSystemErrorを継承していることを確認
        config_error = ConfigurationError("設定エラー")
        assert isinstance(config_error, LoggingSystemError)
    
    def test_log_file_access_error(self):
        """LogFileAccessErrorのテスト"""
        file_path = Path("/test/log.jsonl")
        error = LogFileAccessError("ファイルにアクセスできません", file_path)
        
        assert str(error) == "ファイルにアクセスできません"
        assert error.file_path == file_path
        
        suggestions = error.suggest_recovery()
        assert len(suggestions) >= 2
        assert any("パーミッション" in s for s in suggestions)
        assert any(str(file_path) in s for s in suggestions)
    
    def test_log_validation_error(self):
        """LogValidationErrorのテスト"""
        corrupted_entries = [10, 15, 20]
        error = LogValidationError("ログの整合性に問題があります", corrupted_entries)
        
        assert str(error) == "ログの整合性に問題があります"
        assert error.corrupted_entries == corrupted_entries
        
        suggestions = error.suggest_recovery()
        assert len(suggestions) >= 2
        assert any("バックアップ" in s for s in suggestions)
        assert any("10, 15, 20" in s for s in suggestions)
    
    def test_configuration_error(self):
        """ConfigurationErrorのテスト"""
        error = ConfigurationError("無効な設定です", "STUDENT_ID")
        
        assert str(error) == "無効な設定です"
        assert error.config_key == "STUDENT_ID"
        
        suggestions = error.suggest_recovery()
        assert len(suggestions) >= 3
        assert any("config.py" in s for s in suggestions)
        assert any("STUDENT_ID" in s for s in suggestions)


if __name__ == "__main__":
    pytest.main([__file__])