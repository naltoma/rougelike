#!/usr/bin/env python3
"""
Webhook対応セッションログアップローダー
Webhook Session Log Uploader for Google Apps Script Integration

Google Apps Scriptのwebhookエンドポイントにセッションログを送信するシンプルなアップローダー
"""

import json
import logging
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .session_data_models import StudentLogEntry, LogSummaryItem


class WebhookUploadError(Exception):
    """Webhookアップロード関連エラー"""
    pass


class WebhookConfigManager:
    """Webhook設定管理"""
    
    def __init__(self, config_file: str = "webhook_config.json"):
        """
        Webhook設定管理の初期化
        
        Args:
            config_file: 設定ファイル名
        """
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"設定ファイル読み込みエラー: {e}")
        
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        """設定ファイル保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"設定を保存しました: {self.config_file}")
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}")
            raise WebhookUploadError(f"設定の保存に失敗しました: {e}")
    
    def get_webhook_url(self) -> Optional[str]:
        """Webhook URL取得"""
        return self._config.get('webhook_url')
    
    def set_webhook_url(self, webhook_url: str):
        """Webhook URL設定"""
        if not self._validate_webhook_url(webhook_url):
            raise WebhookUploadError(f"無効なWebhook URL: {webhook_url}")
        
        self._config['webhook_url'] = webhook_url
        self.save_config(self._config)
        self.logger.info("Webhook URLを設定しました")
    
    def _validate_webhook_url(self, url: str) -> bool:
        """Webhook URL検証"""
        if not url or not isinstance(url, str):
            return False
        
        # Google Apps Script URLの基本的な検証
        valid_patterns = [
            'script.google.com/macros/s/',
            'script.googleusercontent.com/macros/s/'
        ]
        
        return any(pattern in url for pattern in valid_patterns)
    
    def get_student_id(self) -> Optional[str]:
        """学生ID取得"""
        return self._config.get('student_id')
    
    def set_student_id(self, student_id: str):
        """学生ID設定"""
        import re
        if not re.match(r'^\d{6}[A-Z]$', student_id):
            raise WebhookUploadError(f"無効な学生ID形式: {student_id} (例: 123456A)")
        
        self._config['student_id'] = student_id
        self.save_config(self._config)
        self.logger.info(f"学生IDを設定しました: {student_id}")
    
    def is_configured(self) -> bool:
        """設定完了確認"""
        return (self.get_webhook_url() is not None and 
                self.get_student_id() is not None)


class WebhookUploader:
    """Webhookアップローダー"""
    
    def __init__(self, config_manager: Optional[WebhookConfigManager] = None):
        """
        Webhookアップローダーの初期化
        
        Args:
            config_manager: 設定管理インスタンス
        """
        self.config_manager = config_manager or WebhookConfigManager()
        self.logger = logging.getLogger(__name__)
        
        # 統計情報
        self.stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0
        }
    
    def upload_session_logs(self, entries: List[StudentLogEntry], 
                           progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        セッションログアップロード
        
        Args:
            entries: アップロード対象のログエントリ
            progress_callback: 進捗コールバック関数
            
        Returns:
            アップロード結果
        """
        if not self.config_manager.is_configured():
            raise WebhookUploadError(
                "Webhook設定が完了していません。\n"
                "python upload.py --setup で設定を行ってください。"
            )
        
        if not entries:
            return {
                'success': False,
                'error': 'アップロード対象のログエントリがありません',
                'uploaded_count': 0,
                'failed_count': 0
            }
        
        webhook_url = self.config_manager.get_webhook_url()
        student_id = self.config_manager.get_student_id()
        
        successful_uploads = 0
        failed_uploads = 0
        start_time = time.time()
        
        self.logger.info(f"Webhookアップロード開始: {len(entries)} エントリ")
        
        for i, entry in enumerate(entries):
            try:
                # エントリをWebhook用データに変換
                webhook_data = self._convert_entry_to_webhook_data(entry, student_id)
                
                # Webhookに送信
                response = self._send_webhook_request(webhook_url, webhook_data)
                
                if response.status_code == 200:
                    successful_uploads += 1
                    self.logger.debug(f"エントリ {i+1} アップロード成功")
                else:
                    failed_uploads += 1
                    self.logger.warning(f"エントリ {i+1} アップロード失敗: HTTP {response.status_code}")
                
                # 進捗コールバック
                if progress_callback:
                    progress = ((i + 1) / len(entries)) * 100
                    progress_callback(progress, f"{i+1}/{len(entries)} 完了")
                
                # レート制限対応（適度な間隔を空ける）
                time.sleep(0.1)
                
            except Exception as e:
                failed_uploads += 1
                self.logger.error(f"エントリ {i+1} 送信エラー: {e}")
        
        # 統計更新
        self.stats['total_uploads'] += len(entries)
        self.stats['successful_uploads'] += successful_uploads
        self.stats['failed_uploads'] += failed_uploads
        
        processing_time = time.time() - start_time
        success = failed_uploads == 0
        
        result = {
            'success': success,
            'uploaded_count': successful_uploads,
            'failed_count': failed_uploads,
            'total_count': len(entries),
            'processing_time_seconds': processing_time,
            'webhook_url': webhook_url
        }
        
        if not success:
            result['error'] = f"{failed_uploads} 件のアップロードに失敗しました"
        
        self.logger.info(
            f"アップロード完了: 成功={successful_uploads}, 失敗={failed_uploads}, "
            f"時間={processing_time:.2f}秒"
        )
        
        return result
    
    def _convert_entry_to_webhook_data(self, entry: StudentLogEntry, student_id: str) -> Dict[str, Any]:
        """ログエントリをWebhookデータに変換（v1.2.2セッション用7項目のみ）"""
        webhook_data = {
            'student_id': student_id,
            'stage_id': entry.stage,
            'end_time': entry.timestamp.isoformat(),
            'solve_code': entry.solve_code or '',
            'completed_successfully': entry.completed_successfully if entry.completed_successfully is not None else '',
            'action_count': entry.action_count if entry.action_count is not None else '',
            'code_lines': entry.code_lines if entry.code_lines is not None else ''
        }
        
        # デバッグ：送信データをログ出力
        self.logger.debug(f"Webhook送信データ: {webhook_data}")
        return webhook_data
    
    def _send_webhook_request(self, webhook_url: str, data: Dict[str, Any]) -> requests.Response:
        """Webhook リクエスト送信"""
        import json
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Rogue-like-Framework-v1.2.3'
        }
        
        try:
            self.logger.debug(f"=== Webhook送信開始 ===")
            self.logger.debug(f"送信URL: {webhook_url}")
            self.logger.debug(f"送信データ: {json.dumps(data, indent=2)}")
            self.logger.debug(f"送信ヘッダー: {headers}")
            
            response = requests.post(
                webhook_url,
                json=data,
                headers=headers,
                timeout=10
            )
            
            self.logger.debug(f"レスポンスコード: {response.status_code}")
            self.logger.debug(f"レスポンスヘッダー: {dict(response.headers)}")
            self.logger.debug(f"レスポンス本文: {response.text}")
            self.logger.debug(f"=== Webhook送信完了 ===")
            
            return response
            
        except requests.exceptions.Timeout:
            raise WebhookUploadError("Webhook送信がタイムアウトしました")
        except requests.exceptions.ConnectionError:
            raise WebhookUploadError("Webhookへの接続に失敗しました")
        except Exception as e:
            raise WebhookUploadError(f"Webhook送信エラー: {e}")
    
    def test_webhook_connection(self) -> tuple[bool, str]:
        """Webhook接続テスト"""
        if not self.config_manager.is_configured():
            return False, "Webhook設定が完了していません"
        
        webhook_url = self.config_manager.get_webhook_url()
        student_id = self.config_manager.get_student_id()
        
        # テストデータ作成
        from datetime import datetime
        import uuid
        
        test_data = {
            'student_id': student_id,
            'stage_id': 'test',
            'end_time': datetime.now().isoformat(),
            'solve_code': '# テストコード\nprint("Hello World")',
            'completed_successfully': True,
            'action_count': 1,
            'code_lines': 2
        }
        
        try:
            response = self._send_webhook_request(webhook_url, test_data)
            
            if response.status_code == 200:
                return True, "Webhook接続テスト成功"
            else:
                return False, f"Webhook接続テスト失敗: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"接続テストエラー: {e}"
    
    def get_statistics(self) -> Dict[str, int]:
        """アップロード統計取得"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """統計リセット"""
        self.stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0
        }


def create_sample_webhook_config() -> str:
    """サンプル設定ファイル作成"""
    sample_config = {
        "webhook_url": "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec",
        "student_id": "123456A",
        "description": "Google Apps Script Webhookアップロード設定",
        "created_at": datetime.now().isoformat()
    }
    
    config_path = Path("webhook_config_sample.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    return str(config_path)


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    
    # サンプル設定作成
    sample_path = create_sample_webhook_config()
    print(f"サンプル設定ファイルを作成しました: {sample_path}")
    
    # 設定管理テスト
    config_manager = WebhookConfigManager()
    print(f"設定状態: {config_manager.is_configured()}")
    
    # アップローダーテスト
    uploader = WebhookUploader(config_manager)
    print(f"統計: {uploader.get_statistics()}")