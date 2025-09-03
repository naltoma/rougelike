"""
ログバリデーション機能のテスト
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

from engine.session_log_manager import SessionLogManager, ValidationResult


class TestLogValidation:
    """ログバリデーション機能のテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.manager = SessionLogManager()
    
    def test_validate_log_integrity_valid_file(self):
        """正常なログファイルの検証"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "valid_log.jsonl"
            
            # 正常なログエントリを作成
            valid_entries = [
                {"timestamp": "2024-12-01T15:00:00", "event_type": "game_start", "data": {"level": 1}},
                {"timestamp": "2024-12-01T15:01:00", "event_type": "player_move", "data": {"x": 1, "y": 2}},
                {"timestamp": "2024-12-01T15:02:00", "event_type": "game_end", "data": {"score": 100}}
            ]
            
            with log_file.open('w', encoding='utf-8') as f:
                for entry in valid_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            result = self.manager.validate_log_integrity(log_file)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            assert result.total_entries == 3
            assert result.valid_entries == 3
            assert len(result.corrupted_entries) == 0
            assert len(result.missing_fields) == 0
            assert len(result.error_details) == 0
    
    def test_validate_log_integrity_corrupted_file(self):
        """破損したログファイルの検証"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "corrupted_log.jsonl"
            
            # 破損したログファイルを作成
            with log_file.open('w', encoding='utf-8') as f:
                f.write('{"timestamp": "2024-12-01T15:00:00", "event_type": "game_start"}\n')  # 正常
                f.write('invalid json line\n')  # 破損
                f.write('{"timestamp": "2024-12-01T15:01:00"}\n')  # event_type不足
                f.write('{"event_type": "game_end"}\n')  # timestamp不足
                f.write('["not", "an", "object"]\n')  # JSONオブジェクトでない
            
            result = self.manager.validate_log_integrity(log_file)
            
            assert result.is_valid is False
            assert result.total_entries == 5
            assert result.valid_entries == 1  # 最初の1行のみ有効
            assert len(result.corrupted_entries) == 2  # JSON解析エラーとオブジェクトでない行
            assert len(result.missing_fields) == 2  # event_type, timestamp不足
            assert len(result.error_details) > 0
    
    def test_validate_log_integrity_empty_file(self):
        """空ファイルの検証"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "empty_log.jsonl"
            log_file.touch()
            
            result = self.manager.validate_log_integrity(log_file)
            
            assert result.is_valid is False
            assert result.total_entries == 0
            assert result.valid_entries == 0
    
    def test_validate_log_integrity_no_file(self):
        """ファイルが存在しない場合の検証"""
        non_existent_file = Path("/non/existent/file.jsonl")
        
        result = self.manager.validate_log_integrity(non_existent_file)
        
        assert result.is_valid is False
        assert result.total_entries == 0
        assert result.valid_entries == 0
        assert "検証対象のログファイルが存在しません" in result.error_details
    
    def test_validate_log_integrity_latest_file(self):
        """最新ファイルの自動検証"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            # 最新ログファイルを作成
            log_file = sessions_dir / "20241201_150000_TEST001.jsonl"
            with log_file.open('w', encoding='utf-8') as f:
                f.write('{"timestamp": "2024-12-01T15:00:00", "event_type": "test"}\n')
            
            with patch('config.ROOT_DIR', temp_path):
                result = self.manager.validate_log_integrity()  # file_pathなし
            
            assert result.is_valid is True
            assert result.total_entries == 1
            assert result.valid_entries == 1
    
    def test_repair_log_file_success(self):
        """ログファイル修復成功"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "corrupted_log.jsonl"
            
            # 修復可能な破損ファイルを作成
            with log_file.open('w', encoding='utf-8') as f:
                f.write('{"timestamp": "2024-12-01T15:00:00", "event_type": "game_start"}\n')  # 正常
                f.write('{"event_type": "player_move"}\n')  # timestamp不足（修復可能）
                f.write('{"timestamp": "2024-12-01T15:01:00"}\n')  # event_type不足（修復可能）
                f.write('invalid json\n')  # 修復不可能
            
            with patch('config.ROOT_DIR', temp_path):
                success = self.manager.repair_log_file(log_file, backup=True)
            
            assert success is True
            
            # 修復後のファイルを検証
            result = self.manager.validate_log_integrity(log_file)
            assert result.is_valid is True
            assert result.valid_entries == 3  # 修復可能な3エントリ
            
            # バックアップファイルの存在確認
            backup_dir = temp_path / "data" / "backup"
            backup_files = list(backup_dir.glob("*_before_repair_*.jsonl"))
            assert len(backup_files) == 1
    
    def test_repair_log_file_no_backup(self):
        """バックアップなしでのログファイル修復"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "corrupted_log.jsonl"
            
            with log_file.open('w', encoding='utf-8') as f:
                f.write('{"event_type": "test"}\n')  # timestamp不足
            
            with patch('config.ROOT_DIR', temp_path):
                success = self.manager.repair_log_file(log_file, backup=False)
            
            assert success is True
            
            # バックアップファイルが作成されていないことを確認
            backup_dir = temp_path / "data" / "backup"
            if backup_dir.exists():
                backup_files = list(backup_dir.glob("*_before_repair_*.jsonl"))
                assert len(backup_files) == 0
    
    def test_repair_log_file_not_exists(self):
        """存在しないファイルの修復"""
        non_existent_file = Path("/non/existent/file.jsonl")
        
        success = self.manager.repair_log_file(non_existent_file)
        
        assert success is False
    
    def test_show_validation_report_valid(self, capsys):
        """正常ファイルの検証レポート表示"""
        result = ValidationResult(
            is_valid=True,
            total_entries=5,
            valid_entries=5,
            corrupted_entries=[],
            missing_fields=[],
            error_details=[]
        )
        
        self.manager.show_validation_report(result)
        
        captured = capsys.readouterr()
        assert "🔍 ログファイル整合性検証レポート" in captured.out
        assert "✅ ログファイルは正常です" in captured.out
        assert "総エントリ数: 5" in captured.out
        assert "有効エントリ数: 5" in captured.out
    
    def test_show_validation_report_invalid(self, capsys):
        """問題ありファイルの検証レポート表示"""
        result = ValidationResult(
            is_valid=False,
            total_entries=10,
            valid_entries=7,
            corrupted_entries=[2, 5, 8],
            missing_fields=["timestamp", "event_type"],
            error_details=["行2: JSON解析エラー", "行5: 必須フィールド不足", "行8: JSONオブジェクトではありません"]
        )
        
        self.manager.show_validation_report(result)
        
        captured = capsys.readouterr()
        assert "⚠️  ログファイルに問題が検出されました" in captured.out
        assert "総エントリ数: 10" in captured.out
        assert "有効エントリ数: 7" in captured.out
        assert "破損エントリ数: 3" in captured.out
        assert "不足フィールド数: 2" in captured.out
        assert "破損エントリ (行番号): 2, 5, 8" in captured.out
        assert "不足フィールド: timestamp, event_type" in captured.out
        assert "詳細エラー情報:" in captured.out
    
    def test_validation_result_get_recovery_suggestions(self):
        """ValidationResultの修復推奨事項"""
        result = ValidationResult(
            is_valid=False,
            total_entries=10,
            valid_entries=5,
            corrupted_entries=[1, 3, 5],
            missing_fields=["timestamp"],
            error_details=["test error"]
        )
        
        suggestions = result.get_recovery_suggestions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "ログファイルのバックアップを確認してください" in suggestions
        assert "破損したエントリをスキップして続行できます" in suggestions
        assert any("破損したエントリ: 行" in s for s in suggestions)
    
    def test_validation_with_missing_fields_only(self):
        """必須フィールド不足のみの検証"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "missing_fields.jsonl"
            
            # 必須フィールドが不足したエントリ
            with log_file.open('w', encoding='utf-8') as f:
                f.write('{"timestamp": "2024-12-01T15:00:00"}\n')  # event_type不足
                f.write('{"event_type": "test"}\n')  # timestamp不足
                f.write('{"data": "some_data"}\n')  # 両方不足
            
            result = self.manager.validate_log_integrity(log_file)
            
            assert result.is_valid is False
            assert result.total_entries == 3
            assert result.valid_entries == 0
            assert len(result.corrupted_entries) == 0  # JSON解析は正常
            assert len(result.missing_fields) == 4  # event_type, timestamp, event_type, timestamp


if __name__ == "__main__":
    pytest.main([__file__])