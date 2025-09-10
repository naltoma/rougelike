"""
セッションログ管理システム
SessionLogManager - 既存SessionLoggerとの統合による自動ログ生成
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from .session_logging import SessionLogger, LogLevel, EventType

logger = logging.getLogger(__name__)


@dataclass
class LogResult:
    """ログ操作の結果と状態情報"""
    success: bool
    log_path: Optional[Path]
    error_message: Optional[str]
    session_id: Optional[str]


@dataclass  
class DiagnosticReport:
    """システム診断結果とトラブルシューティング情報"""
    timestamp: datetime
    session_logger_enabled: bool
    log_directory_exists: bool
    permissions_valid: bool
    issues: List[str]
    recommendations: List[str]
    
    def has_issues(self) -> bool:
        """問題があるかどうかを判定"""
        return len(self.issues) > 0
    
    def format_report(self) -> str:
        """診断情報をコンソール表示用にフォーマット"""
        report_lines = [
            f"🔍 システム診断レポート - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📊 システム状況:",
            f"  • SessionLogger有効: {'✅' if self.session_logger_enabled else '❌'}",
            f"  • ログディレクトリ: {'✅' if self.log_directory_exists else '❌'}",
            f"  • 書き込み権限: {'✅' if self.permissions_valid else '❌'}",
            ""
        ]
        
        if self.issues:
            report_lines.extend([
                "⚠️  検出された問題:",
                *[f"  • {issue}" for issue in self.issues],
                ""
            ])
        
        if self.recommendations:
            report_lines.extend([
                "💡 推奨事項:",
                *[f"  • {rec}" for rec in self.recommendations],
                ""
            ])
        
        if not self.has_issues():
            report_lines.append("✅ システムは正常です")
        
        return "\n".join(report_lines)


@dataclass
class LogFileInfo:
    """ログファイルのメタデータと統計"""
    file_path: Path
    student_id: str
    session_id: str
    created_at: datetime
    file_size: int
    entry_count: int
    last_modified: datetime


@dataclass
class LogConfig:
    """ログ設定とカスタマイズオプション"""
    logging_level: str = 'INFO'
    max_file_size_mb: int = 10
    max_log_files: int = 100
    google_sheets_enabled: bool = False
    google_sheets_url: str = ''
    backup_enabled: bool = True
    auto_cleanup_enabled: bool = True


@dataclass
class ValidationResult:
    """ログ整合性検証結果"""
    is_valid: bool
    total_entries: int
    valid_entries: int
    corrupted_entries: List[int]
    missing_fields: List[str]
    error_details: List[str]
    
    def get_recovery_suggestions(self) -> List[str]:
        """修復推奨事項を返却"""
        suggestions = [
            "ログファイルのバックアップを確認してください",
            "破損したエントリをスキップして続行できます",
        ]
        
        if self.corrupted_entries:
            suggestions.append(f"破損したエントリ: 行 {', '.join(map(str, self.corrupted_entries))}")
            
        return suggestions


class LoggingSystemError(Exception):
    """ログシステムエラー（基底クラス）"""
    pass


class LogFileAccessError(LoggingSystemError):
    """ログファイルアクセス/権限エラー"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None):
        super().__init__(message)
        self.file_path = file_path
    
    def suggest_recovery(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "ファイルパーミッションを確認してください (chmod 644)",
            "親ディレクトリの書き込み権限を確認してください",
        ]
        
        if self.file_path:
            suggestions.append(f"ファイルパス: {self.file_path}")
            
        return suggestions


class LogValidationError(LoggingSystemError):
    """ログ検証/整合性エラー"""
    
    def __init__(self, message: str, corrupted_entries: Optional[List[int]] = None):
        super().__init__(message)
        self.corrupted_entries = corrupted_entries or []
    
    def suggest_recovery(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "ログファイルのバックアップを確認してください",
            "破損したエントリをスキップして続行できます",
        ]
        
        if self.corrupted_entries:
            suggestions.append(f"破損したエントリ: 行 {', '.join(map(str, self.corrupted_entries))}")
            
        return suggestions


class ConfigurationError(LoggingSystemError):
    """設定/セットアップエラー"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key
    
    def suggest_recovery(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "config.pyの設定を確認してください",
            "環境変数が正しく設定されているか確認してください",
            "デフォルト設定での実行を試してください",
        ]
        
        if self.config_key:
            suggestions.append(f"問題の設定項目: {self.config_key}")
            
        return suggestions

class SessionLogManager:
    """セッションログ管理クラス"""
    
    def __init__(self):
        self.session_logger: Optional[SessionLogger] = None
        self.log_file_path: Optional[Path] = None
        self.enabled = False
        # 設定管理システム初期化
        self._max_file_size = 10 * 1024 * 1024  # 10MB
        self._max_log_files = 100
        self._google_sheets_enabled = False
        
        logger.debug("SessionLogManager初期化完了")
    
    def diagnose_logging_system(self) -> DiagnosticReport:
        """システム診断を実行してレポートを生成"""
        issues = []
        recommendations = []
        
        # SessionLoggerの状態確認
        session_logger_enabled = self.session_logger is not None
        if not session_logger_enabled:
            issues.append("SessionLoggerが初期化されていません")
            recommendations.append("enable_default_logging()を呼び出してください")
        
        # ログディレクトリの存在確認
        log_directory_exists = self._check_log_directories()
        if not log_directory_exists:
            issues.append("ログディレクトリが存在しません")
            recommendations.append("data/sessionsディレクトリを作成してください")
        
        # 書き込み権限の確認
        permissions_valid = self._verify_permissions()
        if not permissions_valid:
            issues.append("ログディレクトリへの書き込み権限がありません")
            recommendations.append("ディレクトリの権限設定を確認してください")
        
        return DiagnosticReport(
            timestamp=datetime.now(),
            session_logger_enabled=session_logger_enabled,
            log_directory_exists=log_directory_exists,
            permissions_valid=permissions_valid,
            issues=issues,
            recommendations=recommendations
        )
    
    def _check_log_directories(self) -> bool:
        """ログディレクトリの存在を確認"""
        try:
            # config.pyから設定を読み込む
            import config
            data_dir = config.ROOT_DIR / "data"
            sessions_dir = data_dir / "sessions"
            
            # 必要なディレクトリが存在するかチェック
            return sessions_dir.exists() and sessions_dir.is_dir()
        except Exception as e:
            logger.error(f"ログディレクトリチェック中にエラー: {e}")
            return False
    
    def _check_session_logger_status(self) -> bool:
        """SessionLoggerの状態をチェック"""
        if not self.session_logger:
            return False
        
        # SessionLoggerが適切に初期化されているかチェック
        return hasattr(self.session_logger, 'log_event')
    
    def _verify_permissions(self) -> bool:
        """書き込み権限を確認"""
        try:
            import config
            sessions_dir = config.ROOT_DIR / "data" / "sessions"
            
            if not sessions_dir.exists():
                # ディレクトリが存在しない場合は作成を試行
                sessions_dir.mkdir(parents=True, exist_ok=True)
            
            # テストファイルの作成を試行
            test_file = sessions_dir / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()  # テストファイルを削除
            
            return True
        except Exception as e:
            logger.error(f"権限確認中にエラー: {e}")
            return False
    
    def enable_default_logging(self, student_id: str, stage_id: str, force_enable: bool = True) -> LogResult:
        """デフォルトログ有効化（main.py実行時の自動ログ生成）"""
        try:
            if self.enabled and not force_enable:
                logger.debug("ログ機能は既に有効化されています")
                return LogResult(
                    success=True,
                    log_path=self.log_file_path,
                    error_message=None,
                    session_id=self.session_logger.session_id if self.session_logger else None
                )
            
            # デフォルト学生IDの使用
            if not student_id or student_id == "":
                student_id = "DEFAULT_USER"
                logger.info("デフォルト学生IDを使用します: DEFAULT_USER")
            
            # ログディレクトリの準備
            self._ensure_log_directories()
            
            # ステージ別ログディレクトリの初期化
            import config
            base_log_dir = config.ROOT_DIR / "data" / "sessions"
            log_dir = base_log_dir / stage_id  # data/sessions/stage01/
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 簡易版ログ実装（SessionLoggerの複雑性を回避）
            from datetime import datetime
            import uuid
            import json
            
            generated_session_id = str(uuid.uuid4())[:8]
            
            # ログファイルパスを構築
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = f"{timestamp}_{student_id}.json"  # JSON形式に変更
            self.log_file_path = log_dir / log_filename
            
            # 簡易版のSessionLogger代替クラス作成
            self._create_simple_logger(log_dir, generated_session_id, student_id)
            
            # セッション情報を設定（attempt_countは除去）
            self.session_logger.set_session_info(stage_id)
            
            self.enabled = True
            
            print(f"✅ セッションログが有効化されました")
            print(f"📂 ログファイル: {self.log_file_path}")
            print(f"👤 学生ID: {student_id}")
            print(f"🎯 ステージ: {stage_id}")
            
            logger.info(f"SessionLogger初期化完了: {generated_session_id}")
            
            return LogResult(
                success=True,
                log_path=self.log_file_path,
                error_message=None,
                session_id=generated_session_id
            )
            
        except Exception as e:
            error_msg = f"セッションログの有効化に失敗しました: {e}"
            logger.error(f"ログ有効化中にエラー: {e}")
            
            return LogResult(
                success=False,
                log_path=None,
                error_message=error_msg,
                session_id=None
            )
    
    def _ensure_log_directories(self) -> None:
        """必要なログディレクトリを作成"""
        try:
            import config
            directories = [
                config.ROOT_DIR / "data",
                config.ROOT_DIR / "data" / "sessions",
                config.ROOT_DIR / "data" / "diagnostics",
                config.ROOT_DIR / "data" / "exports",
                config.ROOT_DIR / "data" / "backup" / "archived"
            ]
            
            for dir_path in directories:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"ディレクトリを作成/確認: {dir_path}")
                
        except Exception as e:
            logger.error(f"ディレクトリ作成中にエラー: {e}")
            raise LogFileAccessError(f"ログディレクトリの作成に失敗しました: {e}")
    
    def show_log_info(self) -> List[LogFileInfo]:
        """利用可能なログファイル一覧を表示"""
        try:
            import config
            import json
            from os import stat
            
            log_files = []
            sessions_dir = config.ROOT_DIR / "data" / "sessions"
            
            if not sessions_dir.exists():
                print("📂 ログファイルが見つかりませんでした")
                print(f"   ディレクトリが存在しません: {sessions_dir}")
                return []
            
            # ステージ別ディレクトリを含む.jsonファイルを再帰的に検索（新形式）と.jsonlファイル（旧形式）の両方をサポート
            json_files = list(sessions_dir.rglob("*.json"))
            jsonl_files = list(sessions_dir.rglob("*.jsonl"))
            all_files = json_files + jsonl_files
            
            if not all_files:
                print("📂 ログファイルが見つかりませんでした")
                print(f"   ディレクトリ: {sessions_dir}")
                return []
            
            print(f"📊 ログファイル情報 ({len(all_files)}件)")
            print("=" * 60)
            
            for file_path in sorted(all_files, key=lambda f: f.stat().st_mtime, reverse=True):
                try:
                    # ファイルメタデータを取得
                    stat_info = file_path.stat()
                    file_size = stat_info.st_size
                    last_modified = datetime.fromtimestamp(stat_info.st_mtime)
                    
                    # ファイル名から学生IDを抽出
                    student_id = self._extract_student_id_from_filename(file_path.name)
                    
                    # エントリ数をカウント
                    entry_count = self._count_log_entries(file_path)
                    
                    # セッションIDを取得
                    session_id = self._extract_session_id_from_file(file_path)
                    
                    # 作成日時（ファイル名から推測）
                    created_at = self._extract_created_at_from_filename(file_path.name) or last_modified
                    
                    log_info = LogFileInfo(
                        file_path=file_path,
                        student_id=student_id,
                        session_id=session_id,
                        created_at=created_at,
                        file_size=file_size,
                        entry_count=entry_count,
                        last_modified=last_modified
                    )
                    
                    log_files.append(log_info)
                    
                    # コンソール表示
                    print(f"📝 {file_path.name}")
                    print(f"   👤 学生ID: {student_id}")
                    print(f"   🆔 セッション: {session_id}")
                    print(f"   📅 作成: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   📏 サイズ: {self._format_file_size(file_size)}")
                    print(f"   📊 エントリ数: {entry_count}")
                    print(f"   🔄 更新: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
                    print()
                    
                except Exception as e:
                    logger.error(f"ログファイル情報取得エラー ({file_path}): {e}")
                    continue
            
            return log_files
            
        except Exception as e:
            logger.error(f"ログ情報表示中にエラー: {e}")
            print(f"❌ ログ情報の取得に失敗しました: {e}")
            return []
    
    def get_latest_log_path(self) -> Optional[Path]:
        """最新のログファイルパスを返却（ステージ別ディレクトリ対応）"""
        try:
            import config
            sessions_dir = config.ROOT_DIR / "data" / "sessions"
            
            if not sessions_dir.exists():
                return None
            
            # ステージ別ディレクトリを含む全ファイルを再帰的に検索
            json_files = list(sessions_dir.rglob("*.json"))
            jsonl_files = list(sessions_dir.rglob("*.jsonl"))
            all_files = json_files + jsonl_files
            
            if not all_files:
                return None
            
            # 最新のファイルを取得（更新時刻順）
            latest_file = max(all_files, key=lambda f: f.stat().st_mtime)
            
            print(f"📂 最新のログファイル: {latest_file}")
            print(f"   🔄 更新時刻: {datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            
            return latest_file
            
        except Exception as e:
            logger.error(f"最新ログファイル取得中にエラー: {e}")
            return None
    
    def _extract_student_id_from_filename(self, filename: str) -> str:
        """ファイル名から学生IDを抽出"""
        try:
            # ファイル名形式: YYYYMMDD_HHMMSS_STUDENT_ID.json/.jsonl
            parts = filename.replace('.jsonl', '').replace('.json', '').split('_')
            if len(parts) >= 3:
                return parts[2]  # 3番目の部分が学生ID
            return "UNKNOWN"
        except Exception:
            return "UNKNOWN"
    
    def _extract_created_at_from_filename(self, filename: str) -> Optional[datetime]:
        """ファイル名から作成日時を抽出"""
        try:
            # ファイル名形式: YYYYMMDD_HHMMSS_STUDENT_ID.json/.jsonl
            parts = filename.replace('.jsonl', '').replace('.json', '').split('_')
            if len(parts) >= 2:
                date_part = parts[0]  # YYYYMMDD
                time_part = parts[1]  # HHMMSS
                datetime_str = f"{date_part}_{time_part}"
                return datetime.strptime(datetime_str, '%Y%m%d_%H%M%S')
        except Exception:
            pass
        return None
    
    def _extract_session_id_from_file(self, file_path: Path) -> str:
        """ログファイルからセッションIDを抽出（JSON/JSONL両対応）"""
        try:
            import json
            
            if file_path.suffix == '.json':
                # 新形式：統合JSONファイル
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict) and 'session_id' in data:
                    return data['session_id']
            else:
                # 旧形式：JSONLファイル
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        if line_num > 10:  # 最初の10行のみチェック
                            break
                        try:
                            entry = json.loads(line.strip())
                            if 'session_id' in entry:
                                return entry['session_id']
                        except json.JSONDecodeError:
                            continue
            return "UNKNOWN"
        except Exception:
            return "UNKNOWN"
    
    def _count_log_entries(self, file_path: Path) -> int:
        """ログファイルのエントリ数をカウント（JSON/JSONL両対応）"""
        try:
            import json
            
            if file_path.suffix == '.json':
                # 新形式：統合JSONファイル
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict) and 'events' in data:
                    return len(data['events'])
                else:
                    return 1  # 単一エントリ
            else:
                # 旧形式：JSONLファイル
                with open(file_path, 'r', encoding='utf-8') as f:
                    return sum(1 for line in f if line.strip())
        except Exception:
            return 0
    
    def _format_file_size(self, size_bytes: int) -> str:
        """ファイルサイズを読みやすい形式にフォーマット"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def configure_logging(self, config: LogConfig) -> bool:
        """ログ設定の適用"""
        try:
            import os
            
            # 環境変数からの設定読み込み
            logging_level = os.getenv('LOGGING_LEVEL', config.logging_level)
            max_file_size = int(os.getenv('MAX_LOG_FILE_SIZE', str(config.max_file_size_mb))) * 1024 * 1024
            max_log_files = int(os.getenv('MAX_LOG_FILES', str(config.max_log_files)))
            
            # ログレベル設定
            import logging as log_module
            level_map = {
                'DEBUG': log_module.DEBUG,
                'INFO': log_module.INFO,
                'WARNING': log_module.WARNING,
                'ERROR': log_module.ERROR
            }
            log_module.getLogger().setLevel(level_map.get(logging_level.upper(), log_module.INFO))
            
            # Google Sheets設定
            self._google_sheets_enabled = config.google_sheets_enabled
            if config.google_sheets_url:
                os.environ['GOOGLE_SHEETS_URL'] = config.google_sheets_url
            
            # ログローテーション設定を保存
            self._max_file_size = max_file_size
            self._max_log_files = max_log_files
            
            # SessionLoggerに設定を適用（既に初期化されている場合）
            if self.session_logger:
                self.session_logger.max_log_files = max_log_files
            
            # 設定の保存
            self._save_config_to_file(config)
            
            logger.info(f"ログ設定を適用しました - レベル: {logging_level}, 最大ファイルサイズ: {max_file_size}B")
            return True
            
        except Exception as e:
            logger.error(f"ログ設定の適用中にエラー: {e}")
            return False
    
    def _save_config_to_file(self, config: LogConfig) -> None:
        """設定をファイルに保存"""
        try:
            import config as app_config
            import json
            
            config_dir = app_config.ROOT_DIR / "data" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = config_dir / "logging_config.json"
            
            config_data = {
                "logging_level": config.logging_level,
                "max_file_size_mb": config.max_file_size_mb,
                "max_log_files": config.max_log_files,
                "google_sheets_enabled": config.google_sheets_enabled,
                "google_sheets_url": config.google_sheets_url,
                "backup_enabled": config.backup_enabled,
                "auto_cleanup_enabled": config.auto_cleanup_enabled,
                "updated_at": datetime.now().isoformat()
            }
            
            with config_file.open('w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"設定をファイルに保存しました: {config_file}")
            
        except Exception as e:
            logger.error(f"設定ファイル保存中にエラー: {e}")
    
    def load_config_from_file(self) -> LogConfig:
        """設定ファイルから設定を読み込み"""
        try:
            import config as app_config
            import json
            
            config_file = app_config.ROOT_DIR / "data" / "config" / "logging_config.json"
            
            if not config_file.exists():
                logger.info("設定ファイルが存在しません。デフォルト設定を使用します")
                return self._get_default_config()
            
            with config_file.open('r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return LogConfig(
                logging_level=config_data.get('logging_level', 'INFO'),
                max_file_size_mb=config_data.get('max_file_size_mb', 10),
                max_log_files=config_data.get('max_log_files', 100),
                google_sheets_enabled=config_data.get('google_sheets_enabled', False),
                google_sheets_url=config_data.get('google_sheets_url', ''),
                backup_enabled=config_data.get('backup_enabled', True),
                auto_cleanup_enabled=config_data.get('auto_cleanup_enabled', True)
            )
            
        except Exception as e:
            logger.error(f"設定ファイル読み込み中にエラー: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> LogConfig:
        """デフォルト設定を返却"""
        return LogConfig()
    
    def reset_to_default_config(self) -> bool:
        """デフォルト設定にリセット"""
        try:
            default_config = self._get_default_config()
            success = self.configure_logging(default_config)
            
            if success:
                logger.info("ログ設定をデフォルトにリセットしました")
                print("✅ ログ設定をデフォルトにリセットしました")
            else:
                logger.error("デフォルト設定のリセットに失敗しました")
                print("❌ デフォルト設定のリセットに失敗しました")
            
            return success
            
        except Exception as e:
            logger.error(f"デフォルト設定リセット中にエラー: {e}")
            return False
    
    def apply_log_rotation(self) -> bool:
        """ログローテーションを実行"""
        try:
            import config as app_config
            
            sessions_dir = app_config.ROOT_DIR / "data" / "sessions"
            if not sessions_dir.exists():
                return True
            
            # ログファイル一覧を取得
            log_files = list(sessions_dir.glob("*.jsonl"))
            
            # ファイルサイズによるローテーション
            for log_file in log_files:
                if log_file.stat().st_size > self._max_file_size:
                    self._rotate_large_file(log_file)
            
            # ファイル数による古いファイルの削除
            if len(log_files) > self._max_log_files:
                self._cleanup_old_files(log_files)
            
            logger.debug("ログローテーションが完了しました")
            return True
            
        except Exception as e:
            logger.error(f"ログローテーション中にエラー: {e}")
            return False
    
    def _rotate_large_file(self, log_file: Path) -> None:
        """大きなファイルのローテーション"""
        try:
            import config as app_config
            import shutil
            
            backup_dir = app_config.ROOT_DIR / "data" / "backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # タイムスタンプ付きファイル名でバックアップ
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{log_file.stem}_backup_{timestamp}.jsonl"
            backup_path = backup_dir / backup_name
            
            shutil.move(str(log_file), str(backup_path))
            logger.info(f"大きなログファイルをローテーション: {log_file.name} -> {backup_name}")
            
        except Exception as e:
            logger.error(f"ファイルローテーション中にエラー ({log_file}): {e}")
    
    def _cleanup_old_files(self, log_files: List[Path]) -> None:
        """古いログファイルのクリーンアップ"""
        try:
            import config as app_config
            
            # ファイルを更新時刻でソート（古いものから）
            sorted_files = sorted(log_files, key=lambda f: f.stat().st_mtime)
            
            # 制限を超える分を削除
            files_to_remove = len(sorted_files) - self._max_log_files
            if files_to_remove > 0:
                archived_dir = app_config.ROOT_DIR / "data" / "backup" / "archived"
                archived_dir.mkdir(parents=True, exist_ok=True)
                
                for file_to_archive in sorted_files[:files_to_remove]:
                    try:
                        import shutil
                        archived_path = archived_dir / file_to_archive.name
                        shutil.move(str(file_to_archive), str(archived_path))
                        logger.info(f"古いログファイルをアーカイブ: {file_to_archive.name}")
                    except Exception as e:
                        logger.error(f"ファイルアーカイブ中にエラー ({file_to_archive}): {e}")
                        
        except Exception as e:
            logger.error(f"古いファイルのクリーンアップ中にエラー: {e}")
    
    def show_current_config(self) -> None:
        """現在の設定を表示"""
        try:
            config = self.load_config_from_file()
            
            print("\n⚙️  現在のログ設定")
            print("=" * 50)
            print(f"📊 ログレベル: {config.logging_level}")
            print(f"📏 最大ファイルサイズ: {config.max_file_size_mb} MB")
            print(f"📁 最大ログファイル数: {config.max_log_files}")
            print(f"🔗 Google Sheets連携: {'有効' if config.google_sheets_enabled else '無効'}")
            if config.google_sheets_url:
                print(f"📋 Google Sheets URL: {config.google_sheets_url}")
            print(f"💾 バックアップ: {'有効' if config.backup_enabled else '無効'}")
            print(f"🧹 自動クリーンアップ: {'有効' if config.auto_cleanup_enabled else '無効'}")
            print()
            
        except Exception as e:
            logger.error(f"設定表示中にエラー: {e}")
            print(f"❌ 設定の表示に失敗しました: {e}")
    
    def validate_log_integrity(self, file_path: Optional[Path] = None) -> ValidationResult:
        """ログファイル整合性検証"""
        try:
            import config as app_config
            import json
            
            # 検証対象ファイルの決定
            if file_path is None:
                file_path = self.get_latest_log_path()
            
            if file_path is None or not file_path.exists():
                return ValidationResult(
                    is_valid=False,
                    total_entries=0,
                    valid_entries=0,
                    corrupted_entries=[],
                    missing_fields=[],
                    error_details=["検証対象のログファイルが存在しません"]
                )
            
            valid_entries = 0
            total_entries = 0
            corrupted_entries = []
            missing_fields = []
            error_details = []
            
            required_fields = {'timestamp', 'event_type'}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    total_entries += 1
                    
                    try:
                        entry = json.loads(line)
                        
                        if not isinstance(entry, dict):
                            corrupted_entries.append(line_num)
                            error_details.append(f"行{line_num}: JSONオブジェクトではありません")
                            continue
                        
                        # 必須フィールドチェック
                        entry_missing_fields = []
                        for field in required_fields:
                            if field not in entry:
                                entry_missing_fields.append(field)
                        
                        if entry_missing_fields:
                            missing_fields.extend([(line_num, field) for field in entry_missing_fields])
                            error_details.append(f"行{line_num}: 必須フィールド不足: {', '.join(entry_missing_fields)}")
                        else:
                            valid_entries += 1
                            
                    except json.JSONDecodeError as e:
                        corrupted_entries.append(line_num)
                        error_details.append(f"行{line_num}: JSON解析エラー - {str(e)}")
                    except Exception as e:
                        corrupted_entries.append(line_num)
                        error_details.append(f"行{line_num}: 予期しないエラー - {str(e)}")
            
            is_valid = (len(corrupted_entries) == 0 and len(missing_fields) == 0 and valid_entries > 0)
            
            result = ValidationResult(
                is_valid=is_valid,
                total_entries=total_entries,
                valid_entries=valid_entries,
                corrupted_entries=corrupted_entries,
                missing_fields=[field for _, field in missing_fields],
                error_details=error_details
            )
            
            # 検証結果のログ出力
            if is_valid:
                logger.info(f"ログファイル検証完了: {file_path.name} - 全{total_entries}エントリが有効")
            else:
                logger.warning(f"ログファイル検証で問題検出: {file_path.name} - 有効:{valid_entries}/{total_entries}")
            
            return result
            
        except Exception as e:
            logger.error(f"ログ整合性検証中にエラー: {e}")
            return ValidationResult(
                is_valid=False,
                total_entries=0,
                valid_entries=0,
                corrupted_entries=[],
                missing_fields=[],
                error_details=[f"検証処理中にエラーが発生しました: {e}"]
            )
    
    def repair_log_file(self, file_path: Path, backup: bool = True) -> bool:
        """破損ログファイルの修復"""
        try:
            import config as app_config
            import json
            import shutil
            
            if not file_path.exists():
                logger.error(f"修復対象ファイルが存在しません: {file_path}")
                return False
            
            # バックアップ作成
            if backup:
                backup_dir = app_config.ROOT_DIR / "data" / "backup"
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = backup_dir / f"{file_path.stem}_before_repair_{timestamp}.jsonl"
                shutil.copy2(str(file_path), str(backup_path))
                logger.info(f"修復前バックアップ作成: {backup_path}")
            
            # 有効なエントリのみを抽出
            valid_entries = []
            repaired_entries = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        
                        if isinstance(entry, dict):
                            # 基本的な修復を試行
                            if 'timestamp' not in entry:
                                entry['timestamp'] = datetime.now().isoformat()
                                repaired_entries += 1
                            
                            if 'event_type' not in entry:
                                entry['event_type'] = 'unknown'
                                repaired_entries += 1
                            
                            valid_entries.append(entry)
                    except json.JSONDecodeError:
                        logger.warning(f"修復不可能なエントリをスキップ: 行{line_num}")
                        continue
            
            # 修復したファイルの書き戻し
            with open(file_path, 'w', encoding='utf-8') as f:
                for entry in valid_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logger.info(f"ログファイル修復完了: {file_path} - {len(valid_entries)}エントリ保持, {repaired_entries}エントリ修復")
            print(f"✅ ログファイル修復完了: {len(valid_entries)}エントリ保持, {repaired_entries}エントリ修復")
            
            return True
            
        except Exception as e:
            logger.error(f"ログファイル修復中にエラー: {e}")
            print(f"❌ ログファイル修復に失敗しました: {e}")
            return False
    
    def show_validation_report(self, result: ValidationResult) -> None:
        """検証レポートの表示"""
        try:
            print("\n🔍 ログファイル整合性検証レポート")
            print("=" * 60)
            
            if result.is_valid:
                print("✅ ログファイルは正常です")
                print(f"📊 総エントリ数: {result.total_entries}")
                print(f"✅ 有効エントリ数: {result.valid_entries}")
            else:
                print("⚠️  ログファイルに問題が検出されました")
                print(f"📊 総エントリ数: {result.total_entries}")
                print(f"✅ 有効エントリ数: {result.valid_entries}")
                print(f"❌ 破損エントリ数: {len(result.corrupted_entries)}")
                print(f"⚠️  不足フィールド数: {len(result.missing_fields)}")
                
                if result.corrupted_entries:
                    print(f"\n🔍 破損エントリ (行番号): {', '.join(map(str, result.corrupted_entries))}")
                
                if result.missing_fields:
                    print(f"\n🔍 不足フィールド: {', '.join(set(result.missing_fields))}")
                
                if result.error_details:
                    print("\n📝 詳細エラー情報:")
                    for detail in result.error_details[:5]:  # 最大5件表示
                        print(f"   • {detail}")
                    if len(result.error_details) > 5:
                        print(f"   ... 他 {len(result.error_details) - 5} 件")
                
                # 修復推奨事項
                suggestions = result.get_recovery_suggestions()
                if suggestions:
                    print("\n💡 推奨事項:")
                    for suggestion in suggestions:
                        print(f"   • {suggestion}")
            
            print()
            
        except Exception as e:
            logger.error(f"検証レポート表示中にエラー: {e}")
            print(f"❌ 検証レポートの表示に失敗しました: {e}")
    
    def _create_simple_logger(self, log_dir: Path, session_id: str, student_id: str) -> None:
        """簡易版SessionLogger代替の作成"""
        
        class SimpleSessionLogger:
            def __init__(self, log_file_path: Path, session_id: str, student_id: str):
                self.log_file_path = log_file_path
                self.session_id = session_id
                self.student_id = student_id
                self.session_data = {
                    "session_id": session_id,
                    "student_id": student_id,
                    "start_time": None,
                    "end_time": None,
                    "stage_id": None,
                    "solve_code": None,  # solve()関数のコード
                    "events": [],
                    "result": None  # action_countはここに統合
                }
            
            def set_session_info(self, stage_id: str, solve_code: str = None):
                """セッション情報を設定"""
                self.session_data["stage_id"] = stage_id
                self.session_data["solve_code"] = solve_code
                if not self.session_data["start_time"]:
                    from datetime import datetime
                    self.session_data["start_time"] = datetime.now().isoformat()
            
            def log_event(self, event_type: str, data: dict = None) -> None:
                """イベントログの記録（統合形式）"""
                from datetime import datetime
                
                try:
                    # eventsセクションにはaction_count、total_execution_time、completed_successfullyを含めない
                    if event_type == "session_complete" and data:
                        # session_completeイベントではresultセクションのデータを除外
                        event_data = {
                            "timestamp": datetime.now().isoformat(),
                            "event_type": event_type
                        }
                    else:
                        event_data = {
                            "timestamp": datetime.now().isoformat(),
                            "event_type": event_type,
                            **(data or {})
                        }
                    
                    self.session_data["events"].append(event_data)
                    
                    # セッション完了時に統合ログを書き込み
                    if event_type == "session_complete":
                        self.session_data["end_time"] = datetime.now().isoformat()
                        # resultセクションに統合（total_execution_timeを除去）
                        result_data = {
                            "completed_successfully": data.get("completed_successfully", False),
                            "action_count": data.get("action_count", 0)
                        }
                        # コード品質メトリクス（行数カウント）を追加
                        if self.session_data.get("solve_code"):
                            result_data["code_quality"] = self._calculate_code_metrics(self.session_data["solve_code"])
                        self.session_data["result"] = result_data
                        self._write_consolidated_log()
                        
                except Exception as e:
                    logger.error(f"イベントログ記録エラー: {e}")
            
            def _calculate_code_metrics(self, solve_code: str) -> dict:
                """コード品質メトリクス（行数カウント等）を計算
                
                コメント行・空行を除外したcode_linesを正確に計算する
                """
                try:
                    if not solve_code:
                        return {"line_count": 0, "code_lines": 0, "comment_lines": 0, "blank_lines": 0}
                    
                    lines = solve_code.split('\n')
                    total_lines = len(lines)
                    comment_lines = 0
                    blank_lines = 0
                    code_lines = 0
                    
                    in_multiline_string = False
                    multiline_quote = None
                    
                    for line in lines:
                        stripped = line.strip()
                        
                        # 空行チェック
                        if not stripped:
                            blank_lines += 1
                            continue
                        
                        # 複数行文字列の処理
                        if not in_multiline_string:
                            # 複数行文字列の開始チェック
                            if stripped.startswith('"""') or stripped.startswith("'''"):
                                if stripped.startswith('"""'):
                                    multiline_quote = '"""'
                                else:
                                    multiline_quote = "'''"
                                
                                # 同じ行で終了している場合
                                if stripped.count(multiline_quote) >= 2:
                                    # 同じ行で開始・終了 -> docstringの可能性が高い
                                    comment_lines += 1
                                else:
                                    # 複数行の開始
                                    in_multiline_string = True
                                    comment_lines += 1
                                continue
                        else:
                            # 複数行文字列の終了チェック
                            if multiline_quote in stripped:
                                in_multiline_string = False
                                multiline_quote = None
                                comment_lines += 1
                                continue
                            else:
                                # 複数行文字列の中
                                comment_lines += 1
                                continue
                        
                        # 単行コメント（#で始まる行）
                        if stripped.startswith('#'):
                            comment_lines += 1
                            continue
                        
                        # インラインコメントを含む行の処理
                        # クォート内の#は無視する必要があるが、簡略化のため
                        # #が含まれていてもコードがある場合は実行行とする
                        
                        # キャラクタ操作とは無関係な必須行を除外
                        if (stripped.startswith('def ') or 
                            stripped.startswith('from ') or 
                            'set_auto_render' in stripped or
                            stripped.startswith('print(')):
                            # 必須行としてカウントしない
                            continue
                        
                        # 実行可能コード行
                        code_lines += 1
                    
                    return {
                        "line_count": total_lines,
                        "code_lines": code_lines,
                        "comment_lines": comment_lines,
                        "blank_lines": blank_lines
                    }
                except Exception as e:
                    logger.error(f"コード品質メトリクス計算エラー: {e}")
                    return {"line_count": 0, "code_lines": 0, "comment_lines": 0, "blank_lines": 0}
            
            def _write_consolidated_log(self):
                """統合ログファイルの書き込み"""
                import json
                
                try:
                    with open(self.log_file_path, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(self.session_data, ensure_ascii=False, indent=2))
                except Exception as e:
                    logger.error(f"統合ログ書き込みエラー: {e}")
        
        self.session_logger = SimpleSessionLogger(self.log_file_path, session_id, student_id)
    
    def get_attempt_count_for_stage(self, student_id: str, stage_id: str) -> int:
        """指定されたステージの挑戦回数を取得（ファイル数ベース）"""
        try:
            import config
            base_sessions_dir = config.ROOT_DIR / "data" / "sessions"
            stage_dir = base_sessions_dir / stage_id  # data/sessions/stage01/
            
            if not stage_dir.exists():
                return 0
            
            # ステージディレクトリ内のファイル数をカウント
            json_files = list(stage_dir.glob(f"*_{student_id}.json"))
            return len(json_files)
            
        except Exception as e:
            logger.error(f"挑戦回数取得中にエラー: {e}")
            return 0
    
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