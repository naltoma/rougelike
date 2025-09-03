"""
ログ設定管理システムのテスト
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from engine.session_log_manager import SessionLogManager, LogConfig


class TestLogConfigManagement:
    """ログ設定管理システムのテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.manager = SessionLogManager()
    
    def test_get_default_config(self):
        """デフォルト設定取得"""
        config = self.manager._get_default_config()
        
        assert isinstance(config, LogConfig)
        assert config.logging_level == 'INFO'
        assert config.max_file_size_mb == 10
        assert config.max_log_files == 100
        assert config.google_sheets_enabled is False
        assert config.backup_enabled is True
        assert config.auto_cleanup_enabled is True
    
    def test_configure_logging_success(self):
        """ログ設定適用成功"""
        config = LogConfig(
            logging_level='DEBUG',
            max_file_size_mb=20,
            max_log_files=50,
            google_sheets_enabled=True,
            google_sheets_url='https://example.com/sheets',
            backup_enabled=True,
            auto_cleanup_enabled=False
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                success = self.manager.configure_logging(config)
            
            assert success is True
            assert self.manager._max_file_size == 20 * 1024 * 1024
            assert self.manager._max_log_files == 50
            assert self.manager._google_sheets_enabled is True
    
    def test_configure_logging_with_env_vars(self):
        """環境変数を使用した設定適用"""
        config = LogConfig()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            env_vars = {
                'LOGGING_LEVEL': 'ERROR',
                'MAX_LOG_FILE_SIZE': '5',
                'MAX_LOG_FILES': '25'
            }
            
            with patch('config.ROOT_DIR', temp_path):
                with patch.dict(os.environ, env_vars):
                    success = self.manager.configure_logging(config)
            
            assert success is True
            assert self.manager._max_file_size == 5 * 1024 * 1024
            assert self.manager._max_log_files == 25
    
    def test_save_and_load_config(self):
        """設定の保存と読み込み"""
        original_config = LogConfig(
            logging_level='WARNING',
            max_file_size_mb=15,
            max_log_files=75,
            google_sheets_enabled=True,
            google_sheets_url='https://test.example.com',
            backup_enabled=False,
            auto_cleanup_enabled=True
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                # 設定を保存
                self.manager._save_config_to_file(original_config)
                
                # 設定を読み込み
                loaded_config = self.manager.load_config_from_file()
            
            assert loaded_config.logging_level == 'WARNING'
            assert loaded_config.max_file_size_mb == 15
            assert loaded_config.max_log_files == 75
            assert loaded_config.google_sheets_enabled is True
            assert loaded_config.google_sheets_url == 'https://test.example.com'
            assert loaded_config.backup_enabled is False
            assert loaded_config.auto_cleanup_enabled is True
    
    def test_load_config_no_file(self):
        """設定ファイルが存在しない場合"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                config = self.manager.load_config_from_file()
            
            # デフォルト設定が返される
            assert config.logging_level == 'INFO'
            assert config.max_file_size_mb == 10
            assert config.max_log_files == 100
    
    def test_reset_to_default_config(self):
        """デフォルト設定へのリセット"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                success = self.manager.reset_to_default_config()
            
            assert success is True
            assert self.manager._max_file_size == 10 * 1024 * 1024
            assert self.manager._max_log_files == 100
    
    def test_show_current_config(self, capsys):
        """現在の設定表示"""
        config = LogConfig(
            logging_level='DEBUG',
            max_file_size_mb=25,
            max_log_files=150,
            google_sheets_enabled=True,
            google_sheets_url='https://config-test.example.com',
            backup_enabled=True,
            auto_cleanup_enabled=True
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                # 設定を保存
                self.manager._save_config_to_file(config)
                # 設定を表示
                self.manager.show_current_config()
            
            captured = capsys.readouterr()
            assert "⚙️  現在のログ設定" in captured.out
            assert "ログレベル: DEBUG" in captured.out
            assert "最大ファイルサイズ: 25 MB" in captured.out
            assert "最大ログファイル数: 150" in captured.out
            assert "Google Sheets連携: 有効" in captured.out
            assert "https://config-test.example.com" in captured.out
    
    def test_apply_log_rotation_no_files(self):
        """ログローテーション（ファイルなし）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('config.ROOT_DIR', temp_path):
                success = self.manager.apply_log_rotation()
            
            assert success is True
    
    def test_apply_log_rotation_with_files(self):
        """ログローテーション（ファイルあり）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            # 小さなファイルを作成（ローテーション対象外）
            small_file = sessions_dir / "20241201_100000_TEST001.jsonl"
            small_file.write_text("small file content")
            
            with patch('config.ROOT_DIR', temp_path):
                success = self.manager.apply_log_rotation()
            
            assert success is True
            assert small_file.exists()  # 小さなファイルはそのまま
    
    def test_rotate_large_file(self):
        """大きなファイルのローテーション"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            # 大きなファイルをシミュレート
            large_file = sessions_dir / "20241201_100000_LARGE.jsonl"
            large_file.write_text("large file content" * 1000)
            
            with patch('config.ROOT_DIR', temp_path):
                self.manager._rotate_large_file(large_file)
            
            # 元ファイルが移動されている
            assert not large_file.exists()
            
            # バックアップディレクトリにファイルが存在
            backup_dir = temp_path / "data" / "backup"
            backup_files = list(backup_dir.glob("*_backup_*.jsonl"))
            assert len(backup_files) == 1
    
    def test_cleanup_old_files(self):
        """古いファイルのクリーンアップ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sessions_dir = temp_path / "data" / "sessions"
            sessions_dir.mkdir(parents=True)
            
            # 複数のログファイルを作成
            files = []
            for i in range(5):
                log_file = sessions_dir / f"20241201_10{i:02d}00_TEST{i:03d}.jsonl"
                log_file.write_text(f"content {i}")
                files.append(log_file)
                # ファイル作成時刻を微調整
                import time
                time.sleep(0.01)
            
            # 最大ファイル数を3に設定
            self.manager._max_log_files = 3
            
            with patch('config.ROOT_DIR', temp_path):
                self.manager._cleanup_old_files(files)
            
            # 古いファイルがアーカイブされている
            archived_dir = temp_path / "data" / "backup" / "archived"
            archived_files = list(archived_dir.glob("*.jsonl"))
            assert len(archived_files) == 2  # 古い2ファイルがアーカイブ
    
    def test_config_error_handling(self):
        """設定エラー処理"""
        config = LogConfig()
        
        # 不正なパスでエラーを発生させる（設定ファイル保存エラーでも処理は継続される）
        with patch('config.ROOT_DIR', Path("/invalid/readonly/path")):
            success = self.manager.configure_logging(config)
        
        # 設定適用は成功するが、ファイル保存でエラーログが出力される
        assert success is True


if __name__ == "__main__":
    pytest.main([__file__])