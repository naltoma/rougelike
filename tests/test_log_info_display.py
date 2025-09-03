"""
ログ情報表示機能のテスト
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from engine.session_log_manager import SessionLogManager


class TestLogInfoDisplay:
    """ログ情報表示機能のテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.manager = SessionLogManager()
    
    def test_show_log_info_no_logs(self, capsys):
        """ログファイルが存在しない場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            with patch('config.ROOT_DIR', temp_path):
                self.manager.show_log_info()
            
            captured = capsys.readouterr()
            assert "ログファイルが見つかりませんでした" in captured.out
    
    def test_show_log_info_with_logs(self, capsys):
        """ログファイルが存在する場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            # テスト用ログファイル作成（実際の形式に合わせる: YYYYMMDD_HHMMSS_STUDENT_ID.jsonl）
            log_file = sessions_dir / "20241201_150000_123456A.jsonl"
            log_entries = [
                {"timestamp": "2024-12-01T15:00:00", "session_id": "abcd1234", "event_type": "game_start"},
                {"timestamp": "2024-12-01T15:01:00", "session_id": "abcd1234", "event_type": "game_end"}
            ]
            
            with log_file.open('w', encoding='utf-8') as f:
                for entry in log_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            with patch('config.ROOT_DIR', temp_path):
                self.manager.show_log_info()
            
            captured = capsys.readouterr()
            assert "📊 ログファイル情報" in captured.out
            assert "20241201_150000_123456A.jsonl" in captured.out
            assert "学生ID: 123456A" in captured.out
            assert "セッション: abcd1234" in captured.out
            assert "エントリ数: 2" in captured.out
    
    def test_get_latest_log_path_success(self):
        """最新ログファイル取得成功"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            # 複数のログファイル作成
            old_log = sessions_dir / "123456A_20241201_140000_old123.jsonl"
            new_log = sessions_dir / "123456A_20241201_150000_new456.jsonl"
            
            old_log.touch()
            new_log.touch()
            
            # 新しいファイルのmtimeを後にする
            import time
            time.sleep(0.1)
            new_log.touch()
            
            with patch('config.ROOT_DIR', temp_path):
                result = self.manager.get_latest_log_path()
            
            assert result == new_log
    
    def test_get_latest_log_path_no_logs(self):
        """ログファイルが存在しない場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            with patch('config.ROOT_DIR', temp_path):
                result = self.manager.get_latest_log_path()
            
            assert result is None
    
    def test_extract_student_id_from_filename(self):
        """ファイル名からの学生ID抽出"""
        # 正常なパターン（実際の形式: YYYYMMDD_HHMMSS_STUDENT_ID.jsonl）
        assert self.manager._extract_student_id_from_filename("20241201_150000_123456A.jsonl") == "123456A"
        assert self.manager._extract_student_id_from_filename("20241201_150000_999999Z.jsonl") == "999999Z"
        
        # 不正なパターン
        assert self.manager._extract_student_id_from_filename("invalid_filename.jsonl") == "UNKNOWN"
        assert self.manager._extract_student_id_from_filename("20241201_150000.jsonl") == "UNKNOWN"
    
    def test_extract_session_id_from_file(self):
        """ファイルからのセッションID抽出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "test.jsonl"
            
            # テスト用ファイル作成
            log_entries = [
                {"timestamp": "2024-12-01T15:00:00", "session_id": "abcd1234", "event": "start"},
                {"timestamp": "2024-12-01T15:01:00", "session_id": "abcd1234", "event": "action"}
            ]
            
            with log_file.open('w', encoding='utf-8') as f:
                for entry in log_entries:
                    f.write(json.dumps(entry) + '\n')
            
            session_id = self.manager._extract_session_id_from_file(log_file)
            assert session_id == "abcd1234"
    
    def test_extract_session_id_from_file_no_session_id(self):
        """セッションIDがないファイル"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "test.jsonl"
            
            # セッションIDがないログエントリ
            log_entries = [
                {"timestamp": "2024-12-01T15:00:00", "event": "start"},
                {"timestamp": "2024-12-01T15:01:00", "event": "action"}
            ]
            
            with log_file.open('w', encoding='utf-8') as f:
                for entry in log_entries:
                    f.write(json.dumps(entry) + '\n')
            
            session_id = self.manager._extract_session_id_from_file(log_file)
            assert session_id == "UNKNOWN"
    
    def test_count_log_entries(self):
        """ログエントリ数カウント"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "test.jsonl"
            
            # テスト用ファイル作成
            log_entries = [
                {"timestamp": "2024-12-01T15:00:00", "event": "start"},
                {"timestamp": "2024-12-01T15:01:00", "event": "action"},
                {"timestamp": "2024-12-01T15:02:00", "event": "end"}
            ]
            
            with log_file.open('w', encoding='utf-8') as f:
                for entry in log_entries:
                    f.write(json.dumps(entry) + '\n')
            
            count = self.manager._count_log_entries(log_file)
            assert count == 3
    
    def test_count_log_entries_invalid_file(self):
        """存在しないファイルのエントリ数カウント"""
        non_existent_file = Path("/non/existent/file.jsonl")
        count = self.manager._count_log_entries(non_existent_file)
        assert count == 0
    
    def test_count_log_entries_with_empty_lines(self):
        """空行を含むファイルのエントリ数カウント"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "with_empty_lines.jsonl"
            
            # 空行を含むファイル作成
            with log_file.open('w', encoding='utf-8') as f:
                f.write('{"valid": "entry"}\n')
                f.write('\n')  # 空行
                f.write('{"another": "valid entry"}\n')
                f.write('   \n')  # スペースのみの行
                f.write('{"third": "entry"}\n')
            
            count = self.manager._count_log_entries(log_file)
            assert count == 3  # 空行以外をカウント


if __name__ == "__main__":
    pytest.main([__file__])