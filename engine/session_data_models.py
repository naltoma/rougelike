"""
セッションログデータモデル
Session Log Data Models for Google Sheets Integration v1.2.3

このモジュールは、学生のセッションログをGoogle Sheetsにアップロードするための
データモデルを定義します。
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Set, Union
from datetime import datetime
from pathlib import Path
from enum import Enum
import json


class LogLevel(Enum):
    """ログレベル列挙型"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class UploadStatus(Enum):
    """アップロード状態列挙型"""
    PENDING = "pending"      # アップロード待機中
    SUCCESS = "success"      # アップロード成功
    FAILED = "failed"        # アップロード失敗
    RETRYING = "retrying"    # リトライ中


@dataclass
class StudentLogEntry:
    """
    学生セッションログエントリ
    Google Sheetsの1行に対応するデータ構造
    """
    # 基本識別情報
    student_id: str                    # 学生ID（6桁数字+1文字）
    session_id: str                    # セッションID (UUID形式)
    stage: str                         # ステージ名 (stage01, stage02等)
    timestamp: datetime               # ログ生成日時
    
    # ゲーム状態情報
    level: int                        # 現在レベル
    hp: int                          # 現在HP
    max_hp: int                      # 最大HP
    position: Tuple[int, int]         # プレイヤー位置 (x, y)
    score: int                       # 現在スコア
    
    # アクション詳細
    action_type: str                 # アクション種類 (move, attack, use_item等)
    action_detail: Optional[str] = None  # アクション詳細情報
    
    # ゲームイベント
    event_type: Optional[str] = None      # イベント種類
    event_description: Optional[str] = None  # イベント説明
    
    # エラー・デバッグ情報
    log_level: LogLevel = LogLevel.INFO   # ログレベル
    error_message: Optional[str] = None   # エラーメッセージ
    stack_trace: Optional[str] = None     # スタックトレース
    
    # メタデータ
    duration_ms: Optional[int] = None     # アクション実行時間(ミリ秒)
    cpu_usage: Optional[float] = None     # CPU使用率
    memory_usage: Optional[float] = None  # メモリ使用量(MB)
    
    # アップロード管理
    uploaded_at: Optional[datetime] = None  # アップロード日時
    upload_status: UploadStatus = UploadStatus.PENDING
    retry_count: int = 0                   # リトライ回数
    
    # v1.2.2セッション情報（オプション）
    solve_code: Optional[str] = None       # 学生が書いたコード
    completed_successfully: Optional[bool] = None  # セッション完了フラグ
    action_count: Optional[int] = None     # 総アクション数
    code_lines: Optional[int] = None       # コード行数
    
    def to_row_data(self, include_source_code: bool = True, 
                   anonymize_student: bool = False) -> List[str]:
        """
        Google Sheetsの行データに変換
        
        Args:
            include_source_code: ソースコード列を含めるか
            anonymize_student: 学生IDを匿名化するか
            
        Returns:
            行データのリスト
        """
        student_display = self._anonymize_student_id() if anonymize_student else self.student_id
        
        base_data = [
            student_display,
            self.session_id,
            self.stage,
            self.timestamp.isoformat(),
            str(self.level),
            str(self.hp),
            str(self.max_hp),
            f"({self.position[0]}, {self.position[1]})",
            str(self.score),
            self.action_type,
            self.action_detail or "",
            self.event_type or "",
            self.event_description or "",
            self.log_level.value,
            self.error_message or "",
            str(self.duration_ms) if self.duration_ms else "",
            f"{self.cpu_usage:.2f}%" if self.cpu_usage else "",
            f"{self.memory_usage:.2f}MB" if self.memory_usage else ""
        ]
        
        # ソースコード列（オプション）
        if include_source_code:
            base_data.append(self.stack_trace or "")
        
        return base_data
    
    def to_v122_row_data(self) -> List[str]:
        """
        v1.2.2セッション用の簡素化行データ（7項目のみ）
        
        Returns:
            student_id, stage_id, end_time, solve_code, completed_successfully, action_count, code_lines
        """
        return [
            self.student_id,
            self.stage, 
            self.timestamp.isoformat(),
            self.solve_code or "",
            str(self.completed_successfully) if self.completed_successfully is not None else "",
            str(self.action_count) if self.action_count is not None else "",
            str(self.code_lines) if self.code_lines is not None else ""
        ]
    
    @classmethod
    def get_v122_header_row(cls) -> List[str]:
        """v1.2.2セッション用ヘッダー行（7項目）"""
        return [
            "student_id", "stage_id", "end_time", "solve_code", 
            "completed_successfully", "action_count", "code_lines"
        ]
    
    def _anonymize_student_id(self) -> str:
        """学生ID匿名化（ハッシュ化）"""
        import hashlib
        return f"student_{hashlib.sha256(self.student_id.encode()).hexdigest()[:8]}"
    
    @classmethod
    def get_header_row(cls, include_source_code: bool = True) -> List[str]:
        """
        Google Sheetsヘッダー行取得
        
        Args:
            include_source_code: ソースコード列を含めるか
            
        Returns:
            ヘッダー行のリスト
        """
        headers = [
            "学生ID", "セッションID", "ステージ", "日時", "レベル", "HP", "最大HP",
            "位置", "スコア", "アクション", "アクション詳細", "イベント種類", 
            "イベント説明", "ログレベル", "エラー", "実行時間", "CPU使用率", "メモリ使用量"
        ]
        
        if include_source_code:
            headers.append("スタックトレース")
        
        return headers
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        データ妥当性検証
        
        Returns:
            (妥当性, エラーリスト)
        """
        errors = []
        
        # 学生ID形式検証（6桁数字+1英字）
        import re
        if not re.match(r'^\d{6}[A-Z]$', self.student_id):
            errors.append(f"無効な学生ID形式: {self.student_id}")
        
        # セッションID検証（UUID形式または短い形式）
        try:
            import uuid
            # UUID形式を試行
            uuid.UUID(self.session_id)
        except ValueError:
            # v1.2.2形式の短いIDもチェック
            if not re.match(r'^[a-f0-9]{8}$', self.session_id):
                errors.append(f"無効なセッションID形式: {self.session_id}")
        
        # ステージ名検証
        if not re.match(r'^stage\d{2}$', self.stage):
            errors.append(f"無効なステージ名: {self.stage}")
        
        # 数値範囲検証
        if self.hp < 0 or self.max_hp < 0:
            errors.append("HPは0以上である必要があります")
        
        if self.hp > self.max_hp:
            errors.append("HPは最大HPを超えることはできません")
        
        if self.level < 1:
            errors.append("レベルは1以上である必要があります")
        
        return len(errors) == 0, errors


@dataclass 
class LogSummaryItem:
    """
    ログサマリ項目（アップロード前の確認用）
    """
    stage: str                        # ステージ名
    total_entries: int               # 総エントリ数
    success_actions: int             # 成功アクション数
    error_count: int                 # エラー数
    session_duration_minutes: float  # セッション時間（分）
    average_score: float             # 平均スコア
    max_level_reached: int           # 到達最高レベル
    unique_events: Set[str] = field(default_factory=set)  # 発生イベント種類
    
    def get_display_summary(self) -> str:
        """表示用サマリー文字列取得"""
        return (
            f"{self.stage}: {self.total_entries}件のログ "
            f"(成功: {self.success_actions}, エラー: {self.error_count}) "
            f"時間: {self.session_duration_minutes:.1f}分 "
            f"最高レベル: {self.max_level_reached}"
        )


@dataclass
class UploadResult:
    """
    アップロード結果
    """
    success: bool                    # アップロード成功
    sheet_url: Optional[str] = None   # 作成されたシートURL
    uploaded_count: int = 0          # アップロード済み件数
    failed_count: int = 0            # 失敗件数
    error_message: Optional[str] = None  # エラーメッセージ
    retry_suggested: bool = False    # リトライ推奨
    
    # 詳細結果
    sheet_id: Optional[str] = None   # Google SheetsのシートID
    total_rows: int = 0              # 総行数
    processing_time_seconds: float = 0.0  # 処理時間
    
    def get_status_message(self) -> str:
        """ステータスメッセージ取得"""
        if self.success:
            return f"✅ アップロード完了: {self.uploaded_count}件のログをアップロードしました"
        else:
            message = f"❌ アップロード失敗: {self.error_message}"
            if self.retry_suggested:
                message += "\n🔄 リトライをお試しください"
            return message


@dataclass
class SheetConfiguration:
    """
    Google Sheetsスタイル設定
    """
    # シート基本設定
    sheet_title_template: str = "{student_id}_{stage}_{date}"  # シートタイトル
    include_source_code: bool = True      # ソースコード列含める
    anonymize_student_ids: bool = False   # 学生ID匿名化
    
    # 表示設定
    freeze_header_row: bool = True        # ヘッダー行固定
    auto_resize_columns: bool = True      # 列幅自動調整
    apply_color_coding: bool = True       # ログレベル別色分け
    
    # フィルタ・ソート設定
    enable_filters: bool = True           # フィルタ有効化
    default_sort_column: str = "日時"      # デフォルトソート列
    sort_descending: bool = True          # 降順ソート
    
    # パフォーマンス設定
    batch_size: int = 1000               # バッチサイズ
    max_retries: int = 3                 # 最大リトライ回数
    timeout_seconds: int = 30            # タイムアウト秒数
    
    def get_sheet_title(self, student_id: str, stage: str) -> str:
        """シートタイトル生成"""
        from datetime import datetime
        return self.sheet_title_template.format(
            student_id=student_id,
            stage=stage,
            date=datetime.now().strftime("%Y%m%d")
        )
    
    def get_color_for_log_level(self, log_level: LogLevel) -> Optional[Dict[str, float]]:
        """ログレベル別色設定取得"""
        if not self.apply_color_coding:
            return None
        
        # RGB色設定（0.0-1.0）
        color_map = {
            LogLevel.DEBUG: {"red": 0.9, "green": 0.9, "blue": 0.9},      # 薄灰色
            LogLevel.INFO: {"red": 1.0, "green": 1.0, "blue": 1.0},       # 白色
            LogLevel.WARNING: {"red": 1.0, "green": 1.0, "blue": 0.8},    # 薄黄色
            LogLevel.ERROR: {"red": 1.0, "green": 0.8, "blue": 0.8},      # 薄赤色
            LogLevel.CRITICAL: {"red": 0.8, "green": 0.2, "blue": 0.2}    # 赤色
        }
        
        return color_map.get(log_level)


# ヘルパー関数群
def validate_student_id(student_id: str) -> bool:
    """
    学生ID形式検証ヘルパー
    
    Args:
        student_id: 学生ID
        
    Returns:
        True: 有効, False: 無効
    """
    import re
    return bool(re.match(r'^\d{6}[A-Z]$', student_id))


def create_log_entry_from_dict(data: Dict[str, Any]) -> Union[Optional[StudentLogEntry], List[StudentLogEntry]]:
    """
    辞書からStudentLogEntry作成ヘルパー
    
    Args:
        data: ログデータ辞書
        
    Returns:
        StudentLogEntryオブジェクト（v1.2.3形式）、
        StudentLogEntryリスト（v1.2.2形式）、
        変換失敗時はNone
    """
    try:
        # v1.2.2形式のセッションログ変換
        if 'events' in data and 'session_id' in data:
            return convert_v122_session_to_entries(data)
        
        # 必須フィールド確認
        required_fields = ['student_id', 'session_id', 'stage', 'timestamp', 
                          'level', 'hp', 'max_hp', 'position', 'score', 'action_type']
        
        for field in required_fields:
            if field not in data:
                return None
        
        # datetime変換
        if isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        # LogLevel変換
        if 'log_level' in data and isinstance(data['log_level'], str):
            data['log_level'] = LogLevel(data['log_level'])
        
        # UploadStatus変換
        if 'upload_status' in data and isinstance(data['upload_status'], str):
            data['upload_status'] = UploadStatus(data['upload_status'])
        
        # position tuple変換
        if isinstance(data['position'], list):
            data['position'] = tuple(data['position'])
        
        return StudentLogEntry(**data)
        
    except Exception:
        return None


def convert_v122_session_to_entries(session_data: Dict[str, Any]) -> List[StudentLogEntry]:
    """
    v1.2.2形式のセッションログをStudentLogEntry（1件）に変換
    
    Args:
        session_data: v1.2.2形式のセッションデータ
        
    Returns:
        変換されたStudentLogEntry（1件のリスト）
    """
    try:
        session_id = session_data.get('session_id', '')
        student_id = session_data.get('student_id', '')
        stage = session_data.get('stage_id', 'unknown')
        
        # end_timeを使用（なければstart_time）
        end_time = session_data.get('end_time', session_data.get('start_time', datetime.now().isoformat()))
        timestamp = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # result情報を取得
        result = session_data.get('result', {})
        action_count = result.get('action_count', 0)
        completed_successfully = result.get('completed_successfully', False)
        
        # code_quality情報を取得
        code_quality = result.get('code_quality', {})
        code_lines = code_quality.get('code_lines', 0)
        
        # solve_code
        solve_code = session_data.get('solve_code', '')
        
        # 単一エントリ作成（セッションサマリとして）
        entry = StudentLogEntry(
            student_id=student_id,
            session_id=session_id,
            stage=stage,
            timestamp=timestamp,
            level=1,  # v1.2.2では未使用
            hp=100,   # v1.2.2では未使用
            max_hp=100,  # v1.2.2では未使用
            position=(0, 0),  # v1.2.2では未使用
            score=action_count,  # action_countをスコアに使用
            action_type='session_complete',
            action_detail=f'completed={completed_successfully}, actions={action_count}, code_lines={code_lines}',
            event_type='session_summary',
            event_description=f'Session completed: {stage}',
            log_level=LogLevel.INFO,
            # v1.2.2セッション固有情報
            solve_code=solve_code,
            completed_successfully=completed_successfully,
            action_count=action_count,
            code_lines=code_lines
        )
        
        return [entry]
        
    except Exception as e:
        # エラーログ出力（デバッグ用）
        import logging
        logging.getLogger(__name__).warning(f"v1.2.2セッション変換エラー: {e}")
        return []


def load_log_entries_from_json(json_path: Path) -> List[StudentLogEntry]:
    """
    JSONファイルからログエントリ読み込み
    
    Args:
        json_path: JSONファイルパス
        
    Returns:
        ログエントリリスト
    """
    if not json_path.exists():
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        entries = []
        for data in data_list:
            entry = create_log_entry_from_dict(data)
            if entry:
                entries.append(entry)
        
        return entries
        
    except Exception:
        return []


if __name__ == "__main__":
    # テスト実行
    from datetime import datetime
    
    # サンプルデータ作成
    sample_entry = StudentLogEntry(
        student_id="123456A",
        session_id="12345678-1234-1234-1234-123456789abc",
        stage="stage01",
        timestamp=datetime.now(),
        level=3,
        hp=80,
        max_hp=100,
        position=(5, 7),
        score=250,
        action_type="move",
        action_detail="north",
        event_type="enemy_encounter",
        event_description="スライムに遭遇",
        log_level=LogLevel.INFO,
        duration_ms=150
    )
    
    # データ妥当性検証
    is_valid, errors = sample_entry.validate()
    print(f"妥当性検証: {is_valid}")
    if errors:
        print(f"エラー: {errors}")
    
    # 行データ変換テスト
    row_data = sample_entry.to_row_data()
    headers = StudentLogEntry.get_header_row()
    
    print("\nヘッダー:")
    print(headers)
    print("\nデータ:")
    print(row_data)
    
    # サマリー作成テスト
    summary = LogSummaryItem(
        stage="stage01",
        total_entries=50,
        success_actions=45,
        error_count=5,
        session_duration_minutes=23.5,
        average_score=320.5,
        max_level_reached=5,
        unique_events={"enemy_encounter", "level_up", "item_found"}
    )
    
    print(f"\nサマリー: {summary.get_display_summary()}")