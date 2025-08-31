#!/usr/bin/env python3
"""
Google Sheets統合システム
教師用データ管理・分析機能
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import warnings

# Google Sheets API依存関係の条件付きインポート
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    warnings.warn("Google Sheets機能を使用するには gspread と oauth2client をインストールしてください:\n"
                 "pip install gspread oauth2client", ImportWarning)

from .progression import ProgressionManager
from .educational_feedback import StudentProfile


class GoogleSheetsConfig:
    """Google Sheets設定管理"""
    
    def __init__(self, config_path: str = "config/google_sheets.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 設定ファイル読み込みエラー: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """デフォルト設定作成"""
        default_config = {
            "enabled": False,
            "service_account_path": "config/service-account.json",
            "spreadsheet_id": "",
            "worksheets": {
                "student_progress": "学生進捗",
                "session_logs": "セッション記録", 
                "code_analysis": "コード分析",
                "learning_patterns": "学習パターン"
            },
            "update_frequency": 300,  # 5分
            "batch_size": 50,
            "retry_attempts": 3
        }
        
        # 設定ディレクトリ作成
        config_dir = os.path.dirname(self.config_path)
        if config_dir:  # ディレクトリパスが空でない場合のみ作成
            os.makedirs(config_dir, exist_ok=True)
        
        # デフォルト設定保存
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"📄 デフォルト設定を作成: {self.config_path}")
        except Exception as e:
            print(f"⚠️ 設定ファイル作成エラー: {e}")
        
        return default_config
    
    def is_enabled(self) -> bool:
        """Google Sheets統合が有効か"""
        return self.config.get("enabled", False) and GSPREAD_AVAILABLE
    
    def get_service_account_path(self) -> str:
        """サービスアカウントファイルパス取得"""
        return self.config.get("service_account_path", "")
    
    def get_spreadsheet_id(self) -> str:
        """スプレッドシートID取得"""
        return self.config.get("spreadsheet_id", "")


class GoogleSheetsClient:
    """Google Sheets API クライアント"""
    
    def __init__(self, config: GoogleSheetsConfig):
        self.config = config
        self.client = None
        self.spreadsheet = None
        self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """クライアント初期化"""
        if not self.config.is_enabled():
            return False
        
        try:
            # 認証スコープ設定
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # サービスアカウント認証
            service_account_path = self.config.get_service_account_path()
            if not os.path.exists(service_account_path):
                print(f"⚠️ サービスアカウントファイルが見つかりません: {service_account_path}")
                return False
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                service_account_path, scope
            )
            self.client = gspread.authorize(credentials)
            
            # スプレッドシート開く
            spreadsheet_id = self.config.get_spreadsheet_id()
            if spreadsheet_id:
                self.spreadsheet = self.client.open_by_key(spreadsheet_id)
                print("✅ Google Sheets接続成功")
                return True
            else:
                print("⚠️ スプレッドシートIDが設定されていません")
                return False
                
        except Exception as e:
            print(f"❌ Google Sheets初期化エラー: {e}")
            return False
    
    def is_connected(self) -> bool:
        """接続状態確認"""
        return self.client is not None and self.spreadsheet is not None
    
    def get_or_create_worksheet(self, name: str, headers: List[str]) -> Optional[Any]:
        """ワークシート取得または作成"""
        if not self.is_connected():
            return None
        
        try:
            # 既存ワークシート検索
            try:
                worksheet = self.spreadsheet.worksheet(name)
                return worksheet
            except gspread.WorksheetNotFound:
                pass
            
            # 新規ワークシート作成
            worksheet = self.spreadsheet.add_worksheet(
                title=name, rows=1000, cols=len(headers)
            )
            
            # ヘッダー設定
            if headers:
                worksheet.insert_row(headers, index=1)
                
            print(f"📊 ワークシート作成: {name}")
            return worksheet
            
        except Exception as e:
            print(f"❌ ワークシート操作エラー: {e}")
            return None
    
    def append_rows(self, worksheet_name: str, rows: List[List[Any]]) -> bool:
        """行データ追加"""
        if not self.is_connected():
            return False
        
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            
            # バッチ追加
            for row in rows:
                worksheet.append_row(row)
            
            return True
            
        except Exception as e:
            print(f"❌ データ追加エラー: {e}")
            return False
    
    def update_range(self, worksheet_name: str, range_name: str, 
                    values: List[List[Any]]) -> bool:
        """範囲更新"""
        if not self.is_connected():
            return False
        
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            worksheet.update(range_name, values)
            return True
            
        except Exception as e:
            print(f"❌ 範囲更新エラー: {e}")
            return False


class DataUploader:
    """データアップロードシステム"""
    
    def __init__(self, progression_manager: ProgressionManager, 
                 config_path: str = "config/google_sheets.json"):
        self.progression_manager = progression_manager
        self.config = GoogleSheetsConfig(config_path)
        self.sheets_client = GoogleSheetsClient(self.config)
        self.upload_queue: List[Dict[str, Any]] = []
        self.last_upload_time = 0.0
    
    def is_enabled(self) -> bool:
        """アップロード機能が有効か"""
        return self.config.is_enabled() and self.sheets_client.is_connected()
    
    def queue_student_progress(self, student_id: str, session_data: Dict[str, Any]) -> None:
        """学生進捗データをキューに追加"""
        if not self.is_enabled():
            return
        
        progress_data = {
            "type": "student_progress",
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
            "data": session_data
        }
        
        self.upload_queue.append(progress_data)
        self._check_auto_upload()
    
    def queue_session_log(self, session_id: str, log_data: Dict[str, Any]) -> None:
        """セッションログをキューに追加"""
        if not self.is_enabled():
            return
        
        session_data = {
            "type": "session_log", 
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "data": log_data
        }
        
        self.upload_queue.append(session_data)
        self._check_auto_upload()
    
    def queue_code_analysis(self, student_id: str, stage_id: str, 
                           analysis_data: Dict[str, Any]) -> None:
        """コード分析データをキューに追加"""
        if not self.is_enabled():
            return
        
        code_data = {
            "type": "code_analysis",
            "timestamp": datetime.now().isoformat(), 
            "student_id": student_id,
            "stage_id": stage_id,
            "data": analysis_data
        }
        
        self.upload_queue.append(code_data)
        self._check_auto_upload()
    
    def queue_learning_pattern(self, student_id: str, pattern_data: Dict[str, Any]) -> None:
        """学習パターンデータをキューに追加"""
        if not self.is_enabled():
            return
        
        pattern_entry = {
            "type": "learning_pattern",
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
            "data": pattern_data
        }
        
        self.upload_queue.append(pattern_entry)
        self._check_auto_upload()
    
    def _check_auto_upload(self) -> None:
        """自動アップロード確認"""
        current_time = time.time()
        update_frequency = self.config.config.get("update_frequency", 300)
        batch_size = self.config.config.get("batch_size", 50)
        
        should_upload = (
            len(self.upload_queue) >= batch_size or
            (self.upload_queue and current_time - self.last_upload_time >= update_frequency)
        )
        
        if should_upload:
            self.upload_queued_data()
    
    def upload_queued_data(self) -> bool:
        """キューデータをアップロード"""
        if not self.is_enabled() or not self.upload_queue:
            return False
        
        try:
            # データ種別でグループ化
            grouped_data = self._group_queue_data()
            
            success = True
            for data_type, items in grouped_data.items():
                if not self._upload_data_batch(data_type, items):
                    success = False
            
            if success:
                self.upload_queue.clear()
                self.last_upload_time = time.time()
                print(f"✅ データアップロード完了: {len(self.upload_queue)}件")
            
            return success
            
        except Exception as e:
            print(f"❌ アップロードエラー: {e}")
            return False
    
    def _group_queue_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """キューデータをタイプ別にグループ化"""
        grouped = {}
        for item in self.upload_queue:
            data_type = item["type"]
            if data_type not in grouped:
                grouped[data_type] = []
            grouped[data_type].append(item)
        return grouped
    
    def _upload_data_batch(self, data_type: str, items: List[Dict[str, Any]]) -> bool:
        """データバッチアップロード"""
        worksheet_mapping = {
            "student_progress": self._upload_student_progress,
            "session_log": self._upload_session_logs,
            "code_analysis": self._upload_code_analysis,
            "learning_pattern": self._upload_learning_patterns
        }
        
        upload_func = worksheet_mapping.get(data_type)
        if upload_func:
            return upload_func(items)
        
        print(f"⚠️ 未知のデータタイプ: {data_type}")
        return False
    
    def _upload_student_progress(self, items: List[Dict[str, Any]]) -> bool:
        """学生進捗データアップロード"""
        headers = [
            "日時", "学生ID", "ステージID", "セッション時間", "成功率",
            "失敗回数", "ヒント使用", "コード行数", "複雑度", "学習段階"
        ]
        
        worksheet = self.sheets_client.get_or_create_worksheet(
            self.config.config["worksheets"]["student_progress"], headers
        )
        
        if not worksheet:
            return False
        
        rows = []
        for item in items:
            data = item["data"]
            row = [
                item["timestamp"],
                item["student_id"],
                data.get("stage_id", ""),
                data.get("session_duration", 0),
                data.get("success_rate", 0.0),
                data.get("failed_attempts", 0),
                data.get("hint_requests", 0),
                data.get("code_lines", 0),
                data.get("complexity", 0),
                data.get("learning_stage", "beginner")
            ]
            rows.append(row)
        
        return self.sheets_client.append_rows(
            self.config.config["worksheets"]["student_progress"], rows
        )
    
    def _upload_session_logs(self, items: List[Dict[str, Any]]) -> bool:
        """セッションログアップロード"""
        headers = [
            "日時", "セッションID", "学生ID", "API呼び出し", "成功",
            "実行時間", "エラーメッセージ", "位置"
        ]
        
        worksheet = self.sheets_client.get_or_create_worksheet(
            self.config.config["worksheets"]["session_logs"], headers
        )
        
        if not worksheet:
            return False
        
        rows = []
        for item in items:
            data = item["data"]
            row = [
                item["timestamp"],
                item["session_id"],
                data.get("student_id", ""),
                data.get("api_name", ""),
                data.get("success", False),
                data.get("execution_time", 0.0),
                data.get("error_message", ""),
                str(data.get("position", ""))
            ]
            rows.append(row)
        
        return self.sheets_client.append_rows(
            self.config.config["worksheets"]["session_logs"], rows
        )
    
    def _upload_code_analysis(self, items: List[Dict[str, Any]]) -> bool:
        """コード分析データアップロード"""
        headers = [
            "日時", "学生ID", "ステージID", "総行数", "論理行数", "複雑度",
            "関数数", "クラス数", "保守性指数", "重複率"
        ]
        
        worksheet = self.sheets_client.get_or_create_worksheet(
            self.config.config["worksheets"]["code_analysis"], headers
        )
        
        if not worksheet:
            return False
        
        rows = []
        for item in items:
            data = item["data"]
            row = [
                item["timestamp"],
                item["student_id"],
                item["stage_id"],
                data.get("total_lines", 0),
                data.get("logical_lines", 0),
                data.get("cyclomatic_complexity", 0),
                data.get("function_count", 0),
                data.get("class_count", 0),
                data.get("maintainability_index", 0.0),
                data.get("duplication_ratio", 0.0)
            ]
            rows.append(row)
        
        return self.sheets_client.append_rows(
            self.config.config["worksheets"]["code_analysis"], rows
        )
    
    def _upload_learning_patterns(self, items: List[Dict[str, Any]]) -> bool:
        """学習パターンアップロード"""
        headers = [
            "日時", "学生ID", "パターンタイプ", "信頼度", "頻度", 
            "説明", "推奨アクション"
        ]
        
        worksheet = self.sheets_client.get_or_create_worksheet(
            self.config.config["worksheets"]["learning_patterns"], headers
        )
        
        if not worksheet:
            return False
        
        rows = []
        for item in items:
            data = item["data"]
            row = [
                item["timestamp"],
                item["student_id"],
                data.get("pattern_type", ""),
                data.get("confidence", 0.0),
                data.get("frequency", 0),
                data.get("description", ""),
                data.get("recommended_action", "")
            ]
            rows.append(row)
        
        return self.sheets_client.append_rows(
            self.config.config["worksheets"]["learning_patterns"], rows
        )
    
    def force_upload(self) -> bool:
        """強制アップロード"""
        print("🔄 データを強制アップロードします...")
        return self.upload_queued_data()
    
    def get_upload_status(self) -> Dict[str, Any]:
        """アップロード状態取得"""
        return {
            "enabled": self.is_enabled(),
            "queue_size": len(self.upload_queue),
            "last_upload": datetime.fromtimestamp(self.last_upload_time).isoformat() if self.last_upload_time > 0 else None,
            "connection_status": "connected" if self.sheets_client.is_connected() else "disconnected"
        }


class TeacherDashboard:
    """教師用ダッシュボード機能"""
    
    def __init__(self, data_uploader: DataUploader):
        self.data_uploader = data_uploader
    
    def generate_class_summary(self, class_students: List[str]) -> Dict[str, Any]:
        """クラス概要生成"""
        if not self.data_uploader.is_enabled():
            return {"error": "Google Sheets統合が無効です"}
        
        try:
            # 進捗データディレクトリ検索
            data_dir = Path("data/progress")
            student_summaries = []
            
            for student_id in class_students:
                student_data = self._collect_student_data(student_id, data_dir)
                if student_data:
                    student_summaries.append(student_data)
            
            class_summary = {
                "generated_at": datetime.now().isoformat(),
                "total_students": len(class_students),
                "active_students": len(student_summaries),
                "average_progress": self._calculate_average_progress(student_summaries),
                "common_issues": self._identify_common_issues(student_summaries),
                "top_performers": self._get_top_performers(student_summaries),
                "students_needing_help": self._get_students_needing_help(student_summaries)
            }
            
            return class_summary
            
        except Exception as e:
            return {"error": f"概要生成エラー: {e}"}
    
    def _collect_student_data(self, student_id: str, data_dir: Path) -> Optional[Dict[str, Any]]:
        """学生データ収集"""
        try:
            student_files = list(data_dir.glob(f"*{student_id}*"))
            if not student_files:
                return None
            
            # 最新ファイル読み込み
            latest_file = max(student_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "student_id": student_id,
                "last_activity": data.get("generated_at"),
                "progress_data": data
            }
            
        except Exception:
            return None
    
    def _calculate_average_progress(self, student_data: List[Dict[str, Any]]) -> float:
        """平均進捗計算"""
        if not student_data:
            return 0.0
        
        total_score = sum(
            data["progress_data"].get("overall_score", 0.0) 
            for data in student_data
        )
        return total_score / len(student_data)
    
    def _identify_common_issues(self, student_data: List[Dict[str, Any]]) -> List[str]:
        """共通課題特定"""
        issue_counts = {}
        
        for data in student_data:
            improvements = data["progress_data"].get("improvements", [])
            for issue in improvements:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # 頻度順ソート
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:5]]
    
    def _get_top_performers(self, student_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """優秀学生取得"""
        sorted_students = sorted(
            student_data,
            key=lambda x: x["progress_data"].get("overall_score", 0.0),
            reverse=True
        )
        
        return [
            {
                "student_id": data["student_id"],
                "score": data["progress_data"].get("overall_score", 0.0),
                "grade": data["progress_data"].get("learning_grade", "")
            }
            for data in sorted_students[:5]
        ]
    
    def _get_students_needing_help(self, student_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """支援が必要な学生取得"""
        help_needed = []
        
        for data in student_data:
            score = data["progress_data"].get("overall_score", 1.0)
            improvements = len(data["progress_data"].get("improvements", []))
            
            if score < 0.6 or improvements > 3:
                help_needed.append({
                    "student_id": data["student_id"],
                    "score": score,
                    "issues": improvements,
                    "last_activity": data["last_activity"]
                })
        
        return sorted(help_needed, key=lambda x: x["score"])


# Global instance
_data_uploader: Optional[DataUploader] = None

def get_data_uploader() -> Optional[DataUploader]:
    """データアップローダー取得"""
    global _data_uploader
    return _data_uploader

def initialize_data_uploader(progression_manager: ProgressionManager, 
                           config_path: str = "config/google_sheets.json") -> DataUploader:
    """データアップローダー初期化"""
    global _data_uploader
    _data_uploader = DataUploader(progression_manager, config_path)
    
    if _data_uploader.is_enabled():
        print("✅ Google Sheets統合システム初期化完了")
    else:
        print("⚠️ Google Sheets統合システムは無効です（設定またはライブラリが不足）")
    
    return _data_uploader

def upload_student_data(student_id: str, session_data: Dict[str, Any]) -> None:
    """学生データアップロード"""
    uploader = get_data_uploader()
    if uploader:
        uploader.queue_student_progress(student_id, session_data)

def upload_session_log(session_id: str, log_data: Dict[str, Any]) -> None:
    """セッションログアップロード"""
    uploader = get_data_uploader()
    if uploader:
        uploader.queue_session_log(session_id, log_data)

def force_data_upload() -> bool:
    """データ強制アップロード"""
    uploader = get_data_uploader()
    return uploader.force_upload() if uploader else False

def get_upload_status() -> Dict[str, Any]:
    """アップロード状態取得"""
    uploader = get_data_uploader()
    return uploader.get_upload_status() if uploader else {"enabled": False}