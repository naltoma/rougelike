"""
Google共有フォルダ設定管理システム
Shared Folder Configuration Management System for v1.2.3

このモジュールは、教員が設定するGoogle共有フォルダの管理を行います。
"""

import os
import re
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import urlparse


class SharedFolderConfigError(Exception):
    """共有フォルダ設定関連エラー"""
    pass


class SharedFolderConfigManager:
    """Google共有フォルダ設定管理システム"""
    
    # Google Drive URL パターン
    DRIVE_FOLDER_PATTERNS = [
        r'https://drive\\.google\\.com/drive/folders/([a-zA-Z0-9_-]+)',
        r'https://drive\\.google\\.com/drive/u/\\d+/folders/([a-zA-Z0-9_-]+)',
        r'https://drive\\.google\\.com/open\\?id=([a-zA-Z0-9_-]+)'
    ]
    
    def __init__(self, config_module_name: str = "config"):
        """
        SharedFolderConfigManagerの初期化
        
        Args:
            config_module_name: 設定モジュール名
        """
        self.config_module_name = config_module_name
        self.logger = logging.getLogger(__name__)
        
        # 設定読み込み
        self._config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        try:
            # config.pyからの設定読み込み
            config_data = {}
            
            # 環境変数から設定読み込み
            config_data.update(self._load_from_environment())
            
            # config.pyファイルからの設定読み込み（存在する場合）
            config_data.update(self._load_from_config_file())
            
            return config_data
            
        except Exception as e:
            self.logger.error(f"設定読み込みエラー: {e}")
            return {}
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """環境変数からの設定読み込み"""
        config = {}
        
        # Google Sheets関連環境変数
        if 'GOOGLE_SHEETS_SHARED_FOLDER_URL' in os.environ:
            config['google_sheets_shared_folder_url'] = os.environ['GOOGLE_SHEETS_SHARED_FOLDER_URL']
        
        if 'GOOGLE_SHEETS_CLIENT_ID' in os.environ:
            config['google_sheets_client_id'] = os.environ['GOOGLE_SHEETS_CLIENT_ID']
        
        if 'GOOGLE_SHEETS_CLIENT_SECRET' in os.environ:
            config['google_sheets_client_secret'] = os.environ['GOOGLE_SHEETS_CLIENT_SECRET']
        
        return config
    
    def _load_from_config_file(self) -> Dict[str, Any]:
        """config.pyファイルからの設定読み込み"""
        config = {}
        
        try:
            # config.pyをインポート
            import importlib
            config_module = importlib.import_module(self.config_module_name)
            
            # Google Sheets設定項目を取得
            if hasattr(config_module, 'GOOGLE_SHEETS_SHARED_FOLDER_URL'):
                config['google_sheets_shared_folder_url'] = config_module.GOOGLE_SHEETS_SHARED_FOLDER_URL
            
            if hasattr(config_module, 'GOOGLE_SHEETS_CLIENT_ID'):
                config['google_sheets_client_id'] = config_module.GOOGLE_SHEETS_CLIENT_ID
                
            if hasattr(config_module, 'GOOGLE_SHEETS_CLIENT_SECRET'):
                config['google_sheets_client_secret'] = config_module.GOOGLE_SHEETS_CLIENT_SECRET
            
            self.logger.info(f"設定ファイル {self.config_module_name}.py から設定を読み込みました")
            
        except ImportError:
            self.logger.info(f"設定ファイル {self.config_module_name}.py が見つかりません")
        except Exception as e:
            self.logger.warning(f"設定ファイル読み込み中にエラー: {e}")
        
        return config
    
    def get_shared_folder_url(self) -> Optional[str]:
        """
        Google共有フォルダURL取得
        
        Returns:
            共有フォルダURL、設定されていない場合はNone
        """
        return self._config_data.get('google_sheets_shared_folder_url')
    
    def set_shared_folder_url(self, folder_url: str) -> None:
        """
        Google共有フォルダURL設定
        
        Args:
            folder_url: 共有フォルダURL
            
        Raises:
            SharedFolderConfigError: 無効なURLの場合
        """
        if not self.validate_folder_url(folder_url):
            raise SharedFolderConfigError(f"無効なGoogle DriveフォルダURLです: {folder_url}")
        
        self._config_data['google_sheets_shared_folder_url'] = folder_url
        self.logger.info(f"共有フォルダURLを設定しました: {folder_url}")
    
    def validate_folder_url(self, folder_url: str) -> bool:
        """
        共有フォルダURL検証
        
        Args:
            folder_url: 検証するURL
            
        Returns:
            True: 有効, False: 無効
        """
        if not folder_url or not isinstance(folder_url, str):
            return False
        
        # Google DriveフォルダURLパターンマッチング
        for pattern in self.DRIVE_FOLDER_PATTERNS:
            if re.match(pattern, folder_url):
                return True
        
        return False
    
    def extract_folder_id(self, folder_url: str) -> Optional[str]:
        """
        フォルダURLからフォルダID抽出
        
        Args:
            folder_url: Google DriveフォルダURL
            
        Returns:
            フォルダID、抽出できない場合はNone
        """
        for pattern in self.DRIVE_FOLDER_PATTERNS:
            match = re.search(pattern, folder_url)
            if match:
                return match.group(1)
        
        return None
    
    def is_configured(self) -> bool:
        """
        設定完了状態確認
        
        Returns:
            True: 設定完了, False: 未設定
        """
        return self.get_shared_folder_url() is not None
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """
        設定状態取得
        
        Returns:
            設定状態情報
        """
        folder_url = self.get_shared_folder_url()
        
        return {
            'configured': self.is_configured(),
            'folder_url': folder_url,
            'folder_id': self.extract_folder_id(folder_url) if folder_url else None,
            'url_valid': self.validate_folder_url(folder_url) if folder_url else False,
            'client_id_configured': 'google_sheets_client_id' in self._config_data,
            'client_secret_configured': 'google_sheets_client_secret' in self._config_data
        }
    
    def get_configuration_guidance(self) -> str:
        """
        設定ガイダンスメッセージ取得
        
        Returns:
            設定手順メッセージ
        """
        if self.is_configured():
            return "✅ Google共有フォルダが設定済みです。"
        
        guidance = """
🔧 Google Sheets連携の初期設定が必要です

【教員向け設定手順】
1. Google Driveで共有フォルダを作成
2. 学生に「編集者」権限を付与
3. フォルダのURLをコピー

【設定方法】
Option 1: config.pyに設定追加
```python
# Google Sheets設定
GOOGLE_SHEETS_SHARED_FOLDER_URL = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
```

Option 2: 環境変数で設定
```bash
export GOOGLE_SHEETS_SHARED_FOLDER_URL="https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
```

【フォルダURL例】
- https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
- https://drive.google.com/drive/u/0/folders/1a2b3c4d5e6f7g8h9i0j
"""
        return guidance
    
    def get_oauth_client_config(self) -> Dict[str, Optional[str]]:
        """
        OAuth認証クライアント設定取得
        
        Returns:
            クライアントID・シークレット設定
        """
        return {
            'client_id': self._config_data.get('google_sheets_client_id'),
            'client_secret': self._config_data.get('google_sheets_client_secret')
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        設定妥当性検証
        
        Returns:
            検証結果
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 共有フォルダURL検証
        folder_url = self.get_shared_folder_url()
        if not folder_url:
            results['valid'] = False
            results['errors'].append("Google共有フォルダURLが設定されていません")
        elif not self.validate_folder_url(folder_url):
            results['valid'] = False
            results['errors'].append(f"無効なGoogle DriveフォルダURL: {folder_url}")
        
        # OAuth設定警告
        oauth_config = self.get_oauth_client_config()
        if not oauth_config['client_id']:
            results['warnings'].append("Google OAuth クライアントIDが設定されていません")
        if not oauth_config['client_secret']:
            results['warnings'].append("Google OAuth クライアントシークレットが設定されていません")
        
        return results
    
    def create_sample_config_file(self, output_path: str = "config_sample.py") -> str:
        """
        サンプル設定ファイル作成
        
        Args:
            output_path: 出力ファイルパス
            
        Returns:
            作成されたファイルパス
        """
        sample_config = '''"""
Google Sheets連携設定 - サンプルファイル
設定後、このファイルを config.py にリネームしてください
"""

# Google Sheets連携設定
GOOGLE_SHEETS_SHARED_FOLDER_URL = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID_HERE"

# OAuth認証設定（Google Cloud Consoleから取得）
GOOGLE_SHEETS_CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_SHEETS_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# セキュリティ設定
GOOGLE_SHEETS_ANONYMIZE_STUDENT_IDS = False  # True: 学生ID匿名化
GOOGLE_SHEETS_HIDE_SOURCE_CODE = True       # True: ソースコード列非表示

# アップロード設定
GOOGLE_SHEETS_MAX_RETRIES = 3                # APIリトライ回数
GOOGLE_SHEETS_TIMEOUT_SECONDS = 30           # タイムアウト（秒）
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sample_config)
        
        self.logger.info(f"サンプル設定ファイルを作成しました: {output_path}")
        return output_path
    
    def get_teacher_setup_instructions(self) -> str:
        """
        教員向けセットアップ手順取得
        
        Returns:
            詳細セットアップ手順
        """
        return """
📚 教員向け Google Sheets連携セットアップ手順

【Step 1: Google Driveフォルダ作成】
1. Google Driveにアクセス
2. 「新規」→「フォルダ」で新しいフォルダ作成
3. フォルダ名例: "プログラミング演習_ログ共有"

【Step 2: 学生との共有設定】
1. 作成したフォルダを右クリック→「共有」
2. 「リンクを知っている全員」を選択
3. 権限を「編集者」に設定
4. 「リンクをコピー」でURLを取得

【Step 3: プログラム設定】
1. コピーしたURLを config.py に設定
2. または環境変数 GOOGLE_SHEETS_SHARED_FOLDER_URL に設定

【Step 4: OAuth認証設定（オプション）】
1. Google Cloud Consoleでプロジェクト作成
2. Google Sheets APIを有効化
3. OAuth 2.0認証情報を作成
4. client_id, client_secretを設定

【完了確認】
学生が `python upload.py stage01` を実行できることを確認
"""


# ヘルパー関数
def validate_google_drive_url(url: str) -> bool:
    """
    Google DriveフォルダURL検証ヘルパー
    
    Args:
        url: 検証するURL
        
    Returns:
        True: 有効, False: 無効
    """
    config_manager = SharedFolderConfigManager()
    return config_manager.validate_folder_url(url)


def extract_folder_id_from_url(url: str) -> Optional[str]:
    """
    URLからフォルダID抽出ヘルパー
    
    Args:
        url: Google DriveフォルダURL
        
    Returns:
        フォルダID、抽出できない場合はNone
    """
    config_manager = SharedFolderConfigManager()
    return config_manager.extract_folder_id(url)


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    
    config_manager = SharedFolderConfigManager()
    
    # 設定状態確認
    status = config_manager.get_configuration_status()
    print(f"設定状態: {status}")
    
    # 設定ガイダンス表示
    guidance = config_manager.get_configuration_guidance()
    print(guidance)
    
    # URL検証テスト
    test_urls = [
        "https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j",
        "https://drive.google.com/drive/u/0/folders/1a2b3c4d5e6f7g8h9i0j",
        "https://drive.google.com/open?id=1a2b3c4d5e6f7g8h9i0j",
        "https://invalid-url.com/folder"
    ]
    
    print("\\n=== URL検証テスト ===")
    for url in test_urls:
        is_valid = config_manager.validate_folder_url(url)
        folder_id = config_manager.extract_folder_id(url)
        print(f"URL: {url}")
        print(f"有効: {is_valid}, フォルダID: {folder_id}\\n")
    
    # サンプル設定ファイル作成
    sample_path = config_manager.create_sample_config_file()
    print(f"サンプル設定ファイル作成: {sample_path}")