#!/usr/bin/env python3
"""
Webhook Uploader テストスイート
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import uuid

from engine.webhook_uploader import (
    WebhookUploader, WebhookConfigManager, WebhookUploadError,
    create_sample_webhook_config
)
from engine.session_data_models import StudentLogEntry, LogLevel


class TestWebhookConfigManager:
    """WebhookConfigManager単体テスト"""
    
    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリ"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config_manager(self, temp_dir):
        """テスト用WebhookConfigManager"""
        config_file = temp_dir / "test_webhook_config.json"
        return WebhookConfigManager(str(config_file))
    
    def test_config_manager_initialization(self, config_manager):
        """WebhookConfigManager初期化テスト"""
        assert config_manager.get_webhook_url() is None
        assert config_manager.get_student_id() is None
        assert not config_manager.is_configured()
    
    def test_webhook_url_validation(self, config_manager):
        """Webhook URL検証テスト"""
        # 有効なURL
        valid_urls = [
            "https://script.google.com/macros/s/ABC123/exec",
            "https://script.googleusercontent.com/macros/s/XYZ789/exec"
        ]
        
        for url in valid_urls:
            config_manager.set_webhook_url(url)
            assert config_manager.get_webhook_url() == url
        
        # 無効なURL
        invalid_urls = [
            "https://example.com/webhook",
            "not_a_url",
            "",
            None
        ]
        
        for url in invalid_urls:
            with pytest.raises(WebhookUploadError):
                config_manager.set_webhook_url(url)
    
    def test_student_id_validation(self, config_manager):
        """学生ID検証テスト"""
        # 有効な学生ID
        valid_ids = ["123456A", "999999Z", "000000B"]
        
        for student_id in valid_ids:
            config_manager.set_student_id(student_id)
            assert config_manager.get_student_id() == student_id
        
        # 無効な学生ID
        invalid_ids = [
            "12345A",      # 桁数不足
            "1234567A",    # 桁数過多
            "123456a",     # 小文字
            "123456AB",    # 文字過多
            "ABCDEFG",     # 数字なし
            ""
        ]
        
        for student_id in invalid_ids:
            with pytest.raises(WebhookUploadError):
                config_manager.set_student_id(student_id)
    
    def test_config_persistence(self, config_manager):
        """設定の永続化テスト"""
        webhook_url = "https://script.google.com/macros/s/TEST123/exec"
        student_id = "123456A"
        
        # 設定保存
        config_manager.set_webhook_url(webhook_url)
        config_manager.set_student_id(student_id)
        
        # 新しいインスタンスで読み込み
        new_config = WebhookConfigManager(config_manager.config_file)
        
        assert new_config.get_webhook_url() == webhook_url
        assert new_config.get_student_id() == student_id
        assert new_config.is_configured()


class TestWebhookUploader:
    """WebhookUploader単体テスト"""
    
    @pytest.fixture
    def mock_config_manager(self):
        """モック設定マネージャー"""
        config = Mock()
        config.get_webhook_url.return_value = "https://script.google.com/macros/s/TEST/exec"
        config.get_student_id.return_value = "123456A"
        config.is_configured.return_value = True
        return config
    
    @pytest.fixture
    def uploader(self, mock_config_manager):
        """テスト用WebhookUploader"""
        return WebhookUploader(mock_config_manager)
    
    @pytest.fixture
    def sample_log_entries(self):
        """サンプルログエントリ"""
        entries = []
        session_id = str(uuid.uuid4())
        
        for i in range(5):
            entry = StudentLogEntry(
                student_id="123456A",
                session_id=session_id,
                stage="stage01",
                timestamp=datetime.now(),
                level=i + 1,
                hp=100 - i * 10,
                max_hp=100,
                position=(i, 0),
                score=i * 50,
                action_type="move",
                log_level=LogLevel.INFO
            )
            entries.append(entry)
        
        return entries
    
    def test_uploader_initialization(self, uploader):
        """WebhookUploader初期化テスト"""
        assert uploader.config_manager is not None
        stats = uploader.get_statistics()
        assert stats['total_uploads'] == 0
        assert stats['successful_uploads'] == 0
        assert stats['failed_uploads'] == 0
    
    def test_convert_entry_to_webhook_data(self, uploader, sample_log_entries):
        """ログエントリのWebhookデータ変換テスト"""
        entry = sample_log_entries[0]
        webhook_data = uploader._convert_entry_to_webhook_data(entry, "123456A")
        
        assert webhook_data['student_id'] == "123456A"
        assert webhook_data['session_id'] == entry.session_id
        assert webhook_data['stage'] == "stage01"
        assert webhook_data['level'] == 1
        assert webhook_data['hp'] == 100
        assert webhook_data['position_x'] == 0
        assert webhook_data['position_y'] == 0
        assert webhook_data['action_type'] == "move"
        assert webhook_data['log_level'] == "INFO"
    
    @patch('requests.post')
    def test_upload_session_logs_success(self, mock_post, uploader, sample_log_entries):
        """セッションログアップロード成功テスト"""
        # モックレスポンス設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = uploader.upload_session_logs(sample_log_entries)
        
        assert result['success'] is True
        assert result['uploaded_count'] == 5
        assert result['failed_count'] == 0
        assert result['total_count'] == 5
        assert mock_post.call_count == 5
    
    @patch('requests.post')
    def test_upload_session_logs_partial_failure(self, mock_post, uploader, sample_log_entries):
        """セッションログアップロード部分失敗テスト"""
        # 3回目の呼び出しで失敗させる
        mock_responses = [Mock(status_code=200) for _ in range(5)]
        mock_responses[2].status_code = 500  # 3回目を失敗に
        mock_post.side_effect = mock_responses
        
        result = uploader.upload_session_logs(sample_log_entries)
        
        assert result['success'] is False
        assert result['uploaded_count'] == 4
        assert result['failed_count'] == 1
        assert result['total_count'] == 5
        assert 'error' in result
    
    def test_upload_empty_entries(self, uploader):
        """空のエントリリストのアップロードテスト"""
        result = uploader.upload_session_logs([])
        
        assert result['success'] is False
        assert result['uploaded_count'] == 0
        assert result['failed_count'] == 0
        assert 'error' in result
    
    def test_upload_without_configuration(self):
        """未設定状態でのアップロードテスト"""
        mock_config = Mock()
        mock_config.is_configured.return_value = False
        
        uploader = WebhookUploader(mock_config)
        
        with pytest.raises(WebhookUploadError):
            uploader.upload_session_logs([Mock()])
    
    @patch('requests.post')
    def test_webhook_connection_test_success(self, mock_post, uploader):
        """Webhook接続テスト成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        success, message = uploader.test_webhook_connection()
        
        assert success is True
        assert "成功" in message
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_webhook_connection_test_failure(self, mock_post, uploader):
        """Webhook接続テスト失敗"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        success, message = uploader.test_webhook_connection()
        
        assert success is False
        assert "失敗" in message
    
    def test_statistics_tracking(self, uploader):
        """統計追跡テスト"""
        # 初期状態
        stats = uploader.get_statistics()
        assert stats['total_uploads'] == 0
        
        # 統計リセット
        uploader.reset_statistics()
        stats = uploader.get_statistics()
        assert stats['successful_uploads'] == 0


class TestWebhookIntegration:
    """Webhook統合テスト"""
    
    def test_sample_config_creation(self):
        """サンプル設定ファイル作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 元のディレクトリを変更
            original_cwd = Path.cwd()
            try:
                import os
                os.chdir(temp_path)
                
                config_path = create_sample_webhook_config()
                assert Path(config_path).exists()
                
                # 設定内容確認
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                assert 'webhook_url' in config
                assert 'student_id' in config
                assert 'description' in config
                assert 'created_at' in config
                
            finally:
                os.chdir(original_cwd)
    
    def test_end_to_end_configuration_flow(self):
        """エンドツーエンド設定フローテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "webhook_config.json"
            
            # 設定マネージャー作成
            config_manager = WebhookConfigManager(str(config_file))
            
            # 初期状態確認
            assert not config_manager.is_configured()
            
            # Webhook URL設定
            webhook_url = "https://script.google.com/macros/s/TEST123/exec"
            config_manager.set_webhook_url(webhook_url)
            
            # 学生ID設定
            student_id = "123456A"
            config_manager.set_student_id(student_id)
            
            # 設定完了確認
            assert config_manager.is_configured()
            
            # アップローダー作成
            uploader = WebhookUploader(config_manager)
            
            # 設定が正しく連携されているか確認
            assert config_manager.get_webhook_url() == webhook_url
            assert config_manager.get_student_id() == student_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])