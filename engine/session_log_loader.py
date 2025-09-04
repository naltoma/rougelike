"""
セッションログ読み込みシステム
Session Log Loading System for Google Sheets Integration v1.2.3

このモジュールは、学生のセッションログファイルを読み込み、
Google Sheetsアップロード用にデータを整理します。
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import re
import uuid

from .session_data_models import (
    StudentLogEntry, LogSummaryItem, LogLevel, UploadStatus,
    create_log_entry_from_dict, validate_student_id
)


class SessionLogLoadError(Exception):
    """セッションログ読み込み関連エラー"""
    pass


@dataclass
class LogLoadResult:
    """ログ読み込み結果"""
    success: bool
    entries: List[StudentLogEntry] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.entries is None:
            self.entries = []
        if self.warnings is None:
            self.warnings = []


class SessionLogLoader:
    """セッションログ読み込みシステム"""
    
    # サポートするログファイル形式
    SUPPORTED_EXTENSIONS = ['.json', '.jsonl', '.log']
    
    # デフォルトログディレクトリ
    DEFAULT_LOG_DIRECTORIES = ['data/', 'logs/', './']
    
    def __init__(self, log_base_directory: str = "data"):
        """
        SessionLogLoaderの初期化
        
        Args:
            log_base_directory: ログファイルのベースディレクトリ
        """
        self.log_base_directory = Path(log_base_directory)
        self.logger = logging.getLogger(__name__)
        
        # ログディレクトリ存在確認
        if not self.log_base_directory.exists():
            self.logger.warning(f"ログディレクトリが存在しません: {self.log_base_directory}")
    
    def find_session_log_files(self, student_id: Optional[str] = None, 
                              stage: Optional[str] = None) -> List[Path]:
        """
        セッションログファイル検索
        
        Args:
            student_id: 学生ID（指定時はそのIDのログのみ）
            stage: ステージ名（指定時はそのステージのログのみ）
            
        Returns:
            見つかったログファイルのパスリスト
        """
        found_files = []
        
        # 検索対象ディレクトリの決定
        search_dirs = []
        
        if self.log_base_directory.exists():
            search_dirs.append(self.log_base_directory)
        
        # デフォルトディレクトリも検索
        for default_dir in self.DEFAULT_LOG_DIRECTORIES:
            dir_path = Path(default_dir)
            if dir_path.exists() and dir_path not in search_dirs:
                search_dirs.append(dir_path)
        
        # ファイル検索実行
        for search_dir in search_dirs:
            try:
                # 再帰的にファイル検索
                for ext in self.SUPPORTED_EXTENSIONS:
                    pattern = f"**/*{ext}"
                    for file_path in search_dir.glob(pattern):
                        if self._matches_criteria(file_path, student_id, stage):
                            found_files.append(file_path)
                            
            except Exception as e:
                self.logger.warning(f"ディレクトリ検索エラー {search_dir}: {e}")
        
        # 重複削除とソート
        unique_files = list(set(found_files))
        unique_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)  # 新しい順
        
        self.logger.info(f"セッションログファイル {len(unique_files)} 件見つかりました")
        return unique_files
    
    def _matches_criteria(self, file_path: Path, student_id: Optional[str], 
                         stage: Optional[str]) -> bool:
        """ファイルが検索条件に一致するかチェック"""
        filename = file_path.name.lower()
        file_path_str = str(file_path).lower()
        
        # 学生IDフィルタ
        if student_id:
            if student_id.lower() not in filename:
                return False
        
        # ステージフィルタ（パス全体でチェック）
        if stage:
            if stage.lower() not in file_path_str:
                return False
        
        return True
    
    def load_session_logs(self, file_paths: List[Path],
                         validate_entries: bool = True) -> LogLoadResult:
        """
        セッションログファイル読み込み
        
        Args:
            file_paths: 読み込むファイルパスリスト
            validate_entries: エントリの妥当性検証を行うか
            
        Returns:
            ログ読み込み結果
        """
        all_entries = []
        warnings = []
        
        try:
            for file_path in file_paths:
                self.logger.info(f"ファイル読み込み開始: {file_path}")
                
                try:
                    file_entries = self._load_single_file(file_path)
                    
                    if validate_entries:
                        file_entries, file_warnings = self._validate_entries(file_entries)
                        warnings.extend(file_warnings)
                    
                    all_entries.extend(file_entries)
                    self.logger.info(f"ファイル読み込み完了: {len(file_entries)} エントリ")
                    
                except Exception as e:
                    warning_msg = f"ファイル読み込み失敗 {file_path}: {e}"
                    warnings.append(warning_msg)
                    self.logger.warning(warning_msg)
            
            # エントリソート（時間順）
            all_entries.sort(key=lambda entry: entry.timestamp)
            
            return LogLoadResult(
                success=True,
                entries=all_entries,
                warnings=warnings
            )
            
        except Exception as e:
            error_msg = f"セッションログ読み込み中にエラーが発生しました: {e}"
            self.logger.error(error_msg)
            return LogLoadResult(
                success=False,
                error_message=error_msg,
                warnings=warnings
            )
    
    def _load_single_file(self, file_path: Path) -> List[StudentLogEntry]:
        """単一ファイル読み込み"""
        if file_path.suffix.lower() == '.json':
            return self._load_json_file(file_path)
        elif file_path.suffix.lower() == '.jsonl':
            return self._load_jsonl_file(file_path)
        elif file_path.suffix.lower() == '.log':
            return self._load_log_file(file_path)
        else:
            raise SessionLogLoadError(f"サポートされていないファイル形式: {file_path.suffix}")
    
    def _load_json_file(self, file_path: Path) -> List[StudentLogEntry]:
        """JSON形式ファイル読み込み"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entries = []
            
            # データ形式判定
            if isinstance(data, list):
                # エントリのリスト
                for item in data:
                    result = create_log_entry_from_dict(item)
                    if result:
                        if isinstance(result, list):
                            entries.extend(result)
                        else:
                            entries.append(result)
            elif isinstance(data, dict):
                if 'entries' in data:
                    # ラップされた形式
                    for item in data['entries']:
                        result = create_log_entry_from_dict(item)
                        if result:
                            if isinstance(result, list):
                                entries.extend(result)
                            else:
                                entries.append(result)
                else:
                    # 単一エントリまたはv1.2.2セッションログ
                    result = create_log_entry_from_dict(data)
                    if result:
                        if isinstance(result, list):
                            entries.extend(result)
                        else:
                            entries.append(result)
            
            return entries
            
        except Exception as e:
            raise SessionLogLoadError(f"JSONファイル読み込みエラー: {e}")
    
    def _load_jsonl_file(self, file_path: Path) -> List[StudentLogEntry]:
        """JSON Lines形式ファイル読み込み"""
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        result = create_log_entry_from_dict(data)
                        if result:
                            if isinstance(result, list):
                                entries.extend(result)
                            else:
                                entries.append(result)
                    except Exception as e:
                        self.logger.warning(f"行 {line_num} の解析に失敗: {e}")
            
            return entries
            
        except Exception as e:
            raise SessionLogLoadError(f"JSONLファイル読み込みエラー: {e}")
    
    def _load_log_file(self, file_path: Path) -> List[StudentLogEntry]:
        """ログ形式ファイル読み込み（構造化ログ想定）"""
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        # JSON形式の行を期待
                        if line.startswith('{'):
                            data = json.loads(line)
                            result = create_log_entry_from_dict(data)
                            if result:
                                if isinstance(result, list):
                                    entries.extend(result)
                                else:
                                    entries.append(result)
                    except Exception as e:
                        self.logger.debug(f"行 {line_num} はJSON形式ではありません: {e}")
            
            return entries
            
        except Exception as e:
            raise SessionLogLoadError(f"ログファイル読み込みエラー: {e}")
    
    def _validate_entries(self, entries: List[StudentLogEntry]) -> Tuple[List[StudentLogEntry], List[str]]:
        """エントリ妥当性検証"""
        valid_entries = []
        warnings = []
        
        for i, entry in enumerate(entries):
            is_valid, errors = entry.validate()
            
            if is_valid:
                valid_entries.append(entry)
            else:
                warning_msg = f"エントリ {i+1}: 妥当性検証失敗 - {', '.join(errors)}"
                warnings.append(warning_msg)
        
        self.logger.info(f"妥当性検証: {len(valid_entries)}/{len(entries)} エントリが有効")
        
        return valid_entries, warnings
    
    def create_summary(self, entries: List[StudentLogEntry]) -> List[LogSummaryItem]:
        """
        ログエントリからサマリー作成
        
        Args:
            entries: ログエントリリスト
            
        Returns:
            ステージ別サマリーリスト
        """
        if not entries:
            return []
        
        # ステージ別グループ化
        stage_groups = {}
        for entry in entries:
            if entry.stage not in stage_groups:
                stage_groups[entry.stage] = []
            stage_groups[entry.stage].append(entry)
        
        summaries = []
        
        for stage, stage_entries in stage_groups.items():
            # 基本統計計算
            total_entries = len(stage_entries)
            success_actions = len([e for e in stage_entries 
                                 if e.log_level in [LogLevel.INFO, LogLevel.DEBUG]])
            error_count = len([e for e in stage_entries 
                             if e.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]])
            
            # セッション時間計算
            timestamps = [e.timestamp for e in stage_entries]
            session_duration_minutes = 0.0
            if len(timestamps) > 1:
                duration = max(timestamps) - min(timestamps)
                session_duration_minutes = duration.total_seconds() / 60
            
            # スコア統計
            scores = [e.score for e in stage_entries if e.score is not None]
            average_score = sum(scores) / len(scores) if scores else 0.0
            
            # 最高レベル
            levels = [e.level for e in stage_entries if e.level is not None]
            max_level_reached = max(levels) if levels else 0
            
            # ユニークイベント
            unique_events = set()
            for entry in stage_entries:
                if entry.event_type:
                    unique_events.add(entry.event_type)
            
            summary = LogSummaryItem(
                stage=stage,
                total_entries=total_entries,
                success_actions=success_actions,
                error_count=error_count,
                session_duration_minutes=session_duration_minutes,
                average_score=average_score,
                max_level_reached=max_level_reached,
                unique_events=unique_events
            )
            
            summaries.append(summary)
        
        # ステージ名でソート
        summaries.sort(key=lambda s: s.stage)
        return summaries
    
    def filter_entries_by_criteria(self, entries: List[StudentLogEntry],
                                  student_id: Optional[str] = None,
                                  stage: Optional[str] = None,
                                  start_time: Optional[datetime] = None,
                                  end_time: Optional[datetime] = None,
                                  min_level: Optional[int] = None,
                                  log_levels: Optional[List[LogLevel]] = None) -> List[StudentLogEntry]:
        """
        エントリフィルタリング
        
        Args:
            entries: フィルタ対象エントリ
            student_id: 学生IDフィルタ
            stage: ステージフィルタ
            start_time: 開始時刻フィルタ
            end_time: 終了時刻フィルタ
            min_level: 最小レベルフィルタ
            log_levels: ログレベルフィルタ
            
        Returns:
            フィルタ後エントリリスト
        """
        filtered = entries
        
        if student_id:
            filtered = [e for e in filtered if e.student_id == student_id]
        
        if stage:
            filtered = [e for e in filtered if e.stage == stage]
        
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
        
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
        
        if min_level is not None:
            filtered = [e for e in filtered if e.level >= min_level]
        
        if log_levels:
            filtered = [e for e in filtered if e.log_level in log_levels]
        
        return filtered
    
    def get_available_students(self) -> List[str]:
        """利用可能な学生IDリスト取得"""
        log_files = self.find_session_log_files()
        student_ids = set()
        
        for file_path in log_files:
            try:
                entries = self._load_single_file(file_path)
                for entry in entries:
                    if validate_student_id(entry.student_id):
                        student_ids.add(entry.student_id)
            except Exception:
                continue
        
        return sorted(list(student_ids))
    
    def get_available_stages(self, student_id: Optional[str] = None) -> List[str]:
        """利用可能なステージリスト取得"""
        log_files = self.find_session_log_files(student_id=student_id)
        stages = set()
        
        for file_path in log_files:
            try:
                entries = self._load_single_file(file_path)
                for entry in entries:
                    if not student_id or entry.student_id == student_id:
                        stages.add(entry.stage)
            except Exception:
                continue
        
        # ステージ名でソート（stage01, stage02...）
        stage_list = sorted(list(stages))
        return stage_list


# 使用例とテスト用ヘルパー関数
def create_sample_log_file(file_path: Path, student_id: str = "123456A", 
                          stage: str = "stage01", entry_count: int = 10) -> None:
    """
    サンプルログファイル作成（テスト用）
    
    Args:
        file_path: 作成するファイルパス
        student_id: 学生ID
        stage: ステージ名
        entry_count: エントリ数
    """
    import uuid
    from datetime import datetime, timedelta
    import random
    
    session_id = str(uuid.uuid4())
    entries_data = []
    
    base_time = datetime.now() - timedelta(hours=1)
    
    for i in range(entry_count):
        entry_data = {
            "student_id": student_id,
            "session_id": session_id,
            "stage": stage,
            "timestamp": (base_time + timedelta(seconds=i*30)).isoformat(),
            "level": random.randint(1, 5),
            "hp": random.randint(50, 100),
            "max_hp": 100,
            "position": [random.randint(0, 10), random.randint(0, 10)],
            "score": random.randint(100, 500),
            "action_type": random.choice(["move", "attack", "use_item"]),
            "log_level": random.choice(["INFO", "WARNING", "ERROR"]),
            "duration_ms": random.randint(50, 300)
        }
        entries_data.append(entry_data)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(entries_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # テスト実行
    import tempfile
    
    logging.basicConfig(level=logging.INFO)
    
    # テスト用ログファイル作成
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # サンプルファイル作成
        sample_file = temp_path / "sample_log.json"
        create_sample_log_file(sample_file)
        
        # ローダーテスト
        loader = SessionLogLoader(temp_dir)
        
        # ファイル検索テスト
        found_files = loader.find_session_log_files()
        print(f"見つかったファイル: {found_files}")
        
        # ログ読み込みテスト
        result = loader.load_session_logs(found_files)
        print(f"読み込み結果: 成功={result.success}, エントリ数={len(result.entries)}")
        
        if result.warnings:
            print(f"警告: {result.warnings}")
        
        # サマリー作成テスト
        summaries = loader.create_summary(result.entries)
        for summary in summaries:
            print(f"サマリー: {summary.get_display_summary()}")
        
        # 学生・ステージ取得テスト
        students = loader.get_available_students()
        stages = loader.get_available_stages()
        print(f"利用可能学生: {students}")
        print(f"利用可能ステージ: {stages}")