#!/usr/bin/env python3
"""
Google認証ライブラリセットアップテスト
Modern Google Auth library import validation
"""

import pytest
from unittest.mock import patch, MagicMock


def test_google_auth_libraries_import():
    """新しいGoogle認証ライブラリのimport動作確認"""
    try:
        import google.auth
        import google_auth_oauthlib.flow
        import google.auth.transport.requests
        import gspread
        
        # バージョン確認
        assert hasattr(google.auth, '__version__') or hasattr(google.auth, 'version')
        assert hasattr(gspread, '__version__')
        
        print(f"✅ gspread version: {gspread.__version__}")
        
    except ImportError as e:
        pytest.fail(f"Google認証ライブラリのimportに失敗: {e}")


def test_oauth_credentials_directory_exists():
    """OAuth認証情報ディレクトリの存在確認"""
    from pathlib import Path
    
    credentials_dir = Path('.oauth_credentials')
    assert credentials_dir.exists(), ".oauth_credentials ディレクトリが存在しません"
    assert credentials_dir.is_dir(), ".oauth_credentials はディレクトリである必要があります"


def test_deprecated_oauth2client_removal():
    """非推奨oauth2clientライブラリの非使用確認"""
    try:
        import oauth2client
        pytest.fail("oauth2clientライブラリが依然として利用可能です。削除してください。")
    except ImportError:
        # 期待される動作: oauth2clientは利用不可であるべき
        pass


@patch('google_auth_oauthlib.flow.InstalledAppFlow')
def test_oauth_flow_initialization(mock_flow):
    """OAuth2フロー初期化テスト（モック使用）"""
    mock_flow_instance = MagicMock()
    mock_flow.from_client_config.return_value = mock_flow_instance
    
    # OAuth2スコープ定義
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    # クライアント設定（ダミー）
    client_config = {
        "web": {
            "client_id": "dummy_client_id",
            "client_secret": "dummy_client_secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    
    # フロー作成テスト
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_config(client_config, scopes)
    
    # モックが呼ばれたことを確認
    mock_flow.from_client_config.assert_called_once_with(client_config, scopes)


def test_tenacity_retry_import():
    """リトライライブラリのimport確認"""
    try:
        from tenacity import retry, stop_after_attempt, wait_exponential
        
        # デコレータが正常に動作するかテスト
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=5)
        )
        def test_retry_function():
            return "success"
        
        result = test_retry_function()
        assert result == "success"
        
    except ImportError as e:
        pytest.fail(f"tenacityライブラリのimportに失敗: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])