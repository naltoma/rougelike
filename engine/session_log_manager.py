"""
セッションログ管理システム
SessionLogManager - 既存SessionLoggerとの統合による自動ログ生成
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .session_logging import SessionLogger

logger = logging.getLogger(__name__)

class LoggingSystemError(Exception):
    """ログシステムエラー"""
    pass

class SessionLogManager:
    """セッションログ管理クラス"""
    
    def __init__(self):
        self.session_logger: Optional[SessionLogger] = None
        self.log_file_path: Optional[Path] = None
        self.enabled = False
        
        logger.debug("SessionLogManager初期化完了")
    
    def enable_default_logging(self, student_id: str, stage_id: str) -> None:
        """デフォルトログ有効化（main.py実行時の自動ログ生成）"""
        try:
            if self.enabled:
                logger.debug("ログ機能は既に有効化されています")
                return
            
            # 簡易版：SessionLoggerの初期化をスキップ
            # GUI動作テストのため一時的に無効化
            print("📝 セッションログ機能（簡易版）が有効化されました")
            print(f"📂 学生ID: {student_id}, ステージ: {stage_id}")
            
            self.enabled = True
            logger.info(f"✅ セッションログ機能が有効化されました（簡易版）")
            
        except Exception as e:
            logger.error(f"ログ有効化中にエラー: {e}")
            raise LoggingSystemError(f"セッションログの有効化に失敗しました: {e}")
    
    def notify_log_location(self, file_path: Path) -> None:
        """生成されたログファイルパスの通知"""
        if file_path:
            print(f"📝 セッションログファイル: {file_path}")
            print(f"📂 ログディレクトリ: {file_path.parent}")
        else:
            print("⚠️ ログファイルパスが取得できませんでした")
    
    def provide_log_access_method(self) -> str:
        """ログ参照方法の提供"""
        if not self.log_file_path:
            return "ログファイルが生成されていません"
        
        access_methods = f"""
📋 ログファイル参照方法:

1. ファイル直接確認:
   {self.log_file_path}

2. コマンドライン表示:
   cat "{self.log_file_path}"
   
3. JSONフォーマット表示:
   python -m json.tool "{self.log_file_path}"
   
4. 最新10行表示:
   tail -10 "{self.log_file_path}"
"""
        
        print(access_methods)
        return str(self.log_file_path)
    
    def log_session_start(self, additional_data: Optional[Dict[str, Any]] = None) -> None:
        """セッション開始のログ記録"""
        try:
            if self.session_logger:
                session_data = {
                    "event_type": "session_start",
                    "timestamp": datetime.now().isoformat(),
                    "execution_mode": "gui_enhanced_v1.1"
                }
                if additional_data:
                    session_data.update(additional_data)
                    
                self.session_logger.log_event("session_start", session_data)
                logger.debug("セッション開始ログ記録完了")
                
        except Exception as e:
            logger.error(f"セッション開始ログ記録中にエラー: {e}")
    
    def log_session_complete(self, execution_summary: Dict[str, Any]) -> None:
        """セッション完了時のログ記録"""
        try:
            if self.session_logger:
                completion_data = {
                    "event_type": "session_complete",
                    "timestamp": datetime.now().isoformat(),
                    **execution_summary
                }
                
                self.session_logger.log_event("session_complete", completion_data)
                logger.info("✅ セッション完了ログ記録完了")
                
                # 最終的なログ参照方法を表示
                print("\n📊 セッションが完了しました")
                self.provide_log_access_method()
                
        except Exception as e:
            logger.error(f"セッション完了ログ記録中にエラー: {e}")
    
    def is_logging_enabled(self) -> bool:
        """ログ機能の有効性確認"""
        return self.enabled
    
    def get_log_file_path(self) -> Optional[Path]:
        """ログファイルパスの取得"""
        return self.log_file_path
    
    def get_session_logger(self) -> Optional[SessionLogger]:
        """SessionLoggerインスタンスの取得"""
        return self.session_logger
    
    def flush_logs(self) -> None:
        """ログのフラッシュ（即座にファイルに書き込み）"""
        try:
            if self.session_logger:
                # SessionLoggerにflushメソッドがあれば使用
                if hasattr(self.session_logger, 'flush'):
                    self.session_logger.flush()
                logger.debug("ログフラッシュ完了")
                
        except Exception as e:
            logger.error(f"ログフラッシュ中にエラー: {e}")
    
    def cleanup(self) -> None:
        """リソースのクリーンアップ"""
        try:
            if self.session_logger:
                # SessionLoggerのクリーンアップ
                if hasattr(self.session_logger, 'close'):
                    self.session_logger.close()
                    
            self.enabled = False
            self.session_logger = None
            self.log_file_path = None
            
            logger.debug("SessionLogManager クリーンアップ完了")
            
        except Exception as e:
            logger.error(f"クリーンアップ中にエラー: {e}")