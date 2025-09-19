#!/usr/bin/env python3
"""
GoogleAuthManager テストスイート
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

from engine.google_auth_manager import GoogleAuthManager, GoogleAuthError


class TestGoogleAuthManager:
    """GoogleAuthManager単体テスト"""
    
    @pytest.fixture
    def temp_credentials_dir(self):
        """一時認証情報ディレクトリ"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def auth_manager(self, temp_credentials_dir):
        """テスト用GoogleAuthManagerインスタンス"""
        return GoogleAuthManager(credentials_dir=temp_credentials_dir)
    
    @pytest.fixture
    def mock_credentials(self):
        """モック認証情報"""
        credentials = MagicMock()
        credentials.token = "mock_token"
        credentials.refresh_token = "mock_refresh_token"
        credentials.token_uri = "https://oauth2.googleapis.com/token"
        credentials.client_id = "mock_client_id"
        credentials.client_secret = "mock_client_secret"
        credentials.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials.expiry = datetime.now() + timedelta(hours=1)
        credentials.expired = False
        return credentials
    
    def test_auth_manager_initialization(self, auth_manager):
        """GoogleAuthManager初期化テスト"""
        assert auth_manager.credentials_dir.exists()
        assert auth_manager.SCOPES == [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]
        assert auth_manager._credentials is None
        assert auth_manager._client is None
    
    def test_save_and_load_credentials(self, auth_manager, mock_credentials):
        """認証情報保存・読み込みテスト"""
        # 保存テスト
        auth_manager.save_credentials(mock_credentials)
        assert auth_manager.credentials_file.exists()
        
        # 読み込みテスト
        loaded_credentials = auth_manager.load_credentials()
        assert loaded_credentials is not None
        assert loaded_credentials.token == mock_credentials.token
        assert loaded_credentials.refresh_token == mock_credentials.refresh_token
        assert loaded_credentials.client_id == mock_credentials.client_id
    
    def test_clear_credentials(self, auth_manager, mock_credentials):
        """認証情報削除テスト"""
        # まず認証情報を保存
        auth_manager.save_credentials(mock_credentials)
        assert auth_manager.credentials_file.exists()
        
        # 削除実行
        auth_manager.clear_credentials()
        assert not auth_manager.credentials_file.exists()
        assert auth_manager._credentials is None
        assert auth_manager._client is None
    
    def test_auth_status(self, auth_manager):
        """認証状態取得テスト"""
        status = auth_manager.get_auth_status()
        
        assert 'authenticated' in status
        assert 'credentials_file_exists' in status
        assert 'client_config_exists' in status
        assert 'scopes' in status
        assert status['scopes'] == auth_manager.SCOPES
    
    @patch('engine.google_auth_manager.InstalledAppFlow')
    def test_setup_client_config(self, mock_flow, auth_manager):
        """クライアント設定セットアップテスト"""
        client_id = "test_client_id"
        client_secret = "test_client_secret"
        
        auth_manager.setup_client_config(client_id, client_secret)
        
        # ファイルが作成されたことを確認
        assert auth_manager.client_config_file.exists()
        
        # ファイル内容確認
        with open(auth_manager.client_config_file, 'r') as f:
            config = json.load(f)
        
        assert config['installed']['client_id'] == client_id
        assert config['installed']['client_secret'] == client_secret
    
    @patch('engine.google_auth_manager.gspread.authorize')
    def test_get_authenticated_client(self, mock_authorize, auth_manager, mock_credentials):
        """認証済みクライアント取得テスト"""
        # 認証情報をセットアップ
        auth_manager._credentials = mock_credentials
        
        # モッククライアント
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        
        # クライアント取得
        client = auth_manager.get_authenticated_client()
        
        assert client == mock_client
        mock_authorize.assert_called_once_with(mock_credentials)
    
    def test_get_authenticated_client_without_auth_raises_error(self, auth_manager):
        """認証なしでクライアント取得を試みた場合のエラーテスト"""
        with pytest.raises(GoogleAuthError):
            auth_manager.get_authenticated_client()
    
    @patch('engine.google_auth_manager.Request')
    def test_refresh_credentials_success(self, mock_request, auth_manager, mock_credentials):
        """認証情報リフレッシュ成功テスト"""
        auth_manager._credentials = mock_credentials
        
        # リフレッシュ実行
        result = auth_manager.refresh_credentials()
        
        assert result is True
        mock_credentials.refresh.assert_called_once()
    
    def test_refresh_credentials_without_refresh_token(self, auth_manager):
        """リフレッシュトークンなしでのリフレッシュテスト"""
        mock_credentials = MagicMock()
        mock_credentials.refresh_token = None
        auth_manager._credentials = mock_credentials
        
        result = auth_manager.refresh_credentials()
        assert result is False
    
    @patch('engine.google_auth_manager.InstalledAppFlow')
    def test_initiate_oauth_flow_without_config_file(self, mock_flow, auth_manager):
        """設定ファイルなしでのOAuth2フローテスト"""
        # client_config.jsonが存在しない状態
        with pytest.raises(GoogleAuthError) as excinfo:
            auth_manager.initiate_oauth_flow()
        
        assert "クライアント設定ファイルが見つかりません" in str(excinfo.value)
    
    @patch('engine.google_auth_manager.InstalledAppFlow')
    def test_initiate_oauth_flow_success(self, mock_flow, auth_manager, mock_credentials):
        """OAuth2フロー成功テスト"""
        # クライアント設定ファイルを作成
        auth_manager.setup_client_config("test_id", "test_secret")
        
        # モックフローのセットアップ
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_credentials
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        # OAuth2フロー実行
        result = auth_manager.initiate_oauth_flow()
        
        assert result == mock_credentials
        mock_flow.from_client_secrets_file.assert_called_once()
        mock_flow_instance.run_local_server.assert_called_once()
    
    def test_student_id_validation_format(self):
        """学生ID形式バリデーション（将来の機能テスト）"""
        # 正しい形式
        valid_ids = ["123456A", "987654B", "111111Z"]
        # 不正な形式  
        invalid_ids = ["12345A", "1234567A", "123456a", "123456AB", "ABCDEFG"]
        
        import re
        student_id_pattern = r'^\\d{6}[A-Z]$'
        
        for valid_id in valid_ids:
            assert re.match(student_id_pattern, valid_id), f"有効なIDが無効と判定: {valid_id}"
        
        for invalid_id in invalid_ids:
            assert not re.match(student_id_pattern, invalid_id), f"無効なIDが有効と判定: {invalid_id}"


class TestGoogleAuthManagerIntegration:
    """GoogleAuthManager統合テスト"""
    
    @pytest.fixture
    def temp_credentials_dir(self):
        """一時認証情報ディレクトリ"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_auth_flow_simulation(self, temp_credentials_dir):
        """完全な認証フローシミュレーション"""
        auth_manager = GoogleAuthManager(credentials_dir=temp_credentials_dir)
        
        # 初期状態確認
        assert not auth_manager.credentials_file.exists()
        status = auth_manager.get_auth_status()
        assert not status['authenticated']
        assert not status['credentials_file_exists']
        
        # クライアント設定作成
        auth_manager.setup_client_config("test_client", "test_secret")
        assert auth_manager.client_config_file.exists()
        
        status = auth_manager.get_auth_status()
        assert status['client_config_exists']


def test_create_sample_client_config():
    """サンプルクライアント設定作成テスト"""
    from engine.google_auth_manager import create_sample_client_config
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_sample_client_config(temp_dir)
        assert Path(config_path).exists()
        
        # 設定内容確認
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert 'installed' in config
        assert 'client_id' in config['installed']
        assert 'client_secret' in config['installed']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])