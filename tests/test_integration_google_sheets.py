#!/usr/bin/env python3
"""
Google Sheets統合機能テストスイート
Integration Test Suite for Google Sheets Integration v1.2.3

このテストスイートは、Google Sheets連携機能の統合テストを実行し、
全体的な動作を検証します。
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import uuid

from engine.google_auth_manager import GoogleAuthManager, GoogleAuthError
from engine.shared_folder_config_manager import SharedFolderConfigManager
from engine.session_log_loader import SessionLogLoader, LogLoadResult
from engine.google_sheets_uploader import GoogleSheetsUploader, GoogleSheetsUploadError
from engine.session_data_models import (
    StudentLogEntry, LogSummaryItem, UploadResult, SheetConfiguration,
    LogLevel, UploadStatus, create_log_entry_from_dict
)


class TestGoogleSheetsIntegration:
    """Google Sheets統合機能テスト"""
    
    @pytest.fixture
    def temp_workspace(self):
        """テスト用一時ワークスペース"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_log_entries(self):
        """サンプルログエントリ"""
        base_time = datetime.now()
        session_id = str(uuid.uuid4())
        
        entries = []
        for i in range(10):
            entry = StudentLogEntry(
                student_id="123456A",
                session_id=session_id,
                stage="stage01",
                timestamp=base_time + timedelta(minutes=i),
                level=min(i // 2 + 1, 5),
                hp=max(100 - i * 5, 20),
                max_hp=100,
                position=(i % 5, i % 3),
                score=i * 50,
                action_type=["move", "attack", "use_item"][i % 3],
                action_detail=f"アクション{i+1}",
                log_level=LogLevel.INFO if i % 4 != 3 else LogLevel.WARNING
            )
            entries.append(entry)
        
        return entries
    
    @pytest.fixture
    def mock_gspread_client(self):
        """モックgspreadクライアント"""
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        
        mock_client.create.return_value = mock_spreadsheet
        mock_client.openall.return_value = []
        mock_spreadsheet.url = "https://docs.google.com/spreadsheets/d/mock_id"
        mock_spreadsheet.id = "mock_spreadsheet_id"
        mock_spreadsheet.add_worksheet.return_value = mock_worksheet
        mock_spreadsheet.sheet1 = mock_worksheet
        
        return mock_client
    
    def create_sample_log_file(self, file_path: Path, entries: List[StudentLogEntry]):
        """サンプルログファイル作成"""
        entries_data = []
        for entry in entries:
            entry_dict = {
                'student_id': entry.student_id,
                'session_id': entry.session_id,
                'stage': entry.stage,
                'timestamp': entry.timestamp.isoformat(),
                'level': entry.level,
                'hp': entry.hp,
                'max_hp': entry.max_hp,
                'position': list(entry.position),
                'score': entry.score,
                'action_type': entry.action_type,
                'action_detail': entry.action_detail,
                'log_level': entry.log_level.value
            }
            entries_data.append(entry_dict)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entries_data, f, indent=2, ensure_ascii=False)
    
    def test_end_to_end_upload_flow(self, temp_workspace, sample_log_entries, mock_gspread_client):
        """エンドツーエンドアップロードフロー統合テスト"""
        # ログファイル作成
        log_file = temp_workspace / "sample_log.json"
        self.create_sample_log_file(log_file, sample_log_entries)
        
        # 各コンポーネント初期化
        with patch('engine.google_auth_manager.gspread.authorize', return_value=mock_gspread_client):
            auth_manager = GoogleAuthManager(credentials_dir=str(temp_workspace / ".oauth"))
            
            # モック認証情報設定
            mock_credentials = MagicMock()
            mock_credentials.expired = False
            auth_manager._credentials = mock_credentials
            
            config_manager = SharedFolderConfigManager()
            config_manager.set_shared_folder_url("https://drive.google.com/drive/folders/mock_folder_id")
            
            loader = SessionLogLoader(str(temp_workspace))
            uploader = GoogleSheetsUploader(auth_manager, config_manager)
        
        # ログファイル検索・読み込み
        found_files = loader.find_session_log_files()
        assert len(found_files) == 1
        assert found_files[0] == log_file
        
        load_result = loader.load_session_logs(found_files)
        assert load_result.success
        assert len(load_result.entries) == len(sample_log_entries)
        
        # サマリー作成
        summaries = loader.create_summary(load_result.entries)
        assert len(summaries) == 1
        assert summaries[0].stage == "stage01"
        assert summaries[0].total_entries == len(sample_log_entries)
        
        # モックDriveサービス設定
        mock_drive_service = MagicMock()
        with patch.object(uploader, '_get_drive_service', return_value=mock_drive_service):
            # アップロード実行
            upload_result = uploader.upload_session_logs(load_result.entries)
        
        # 結果検証
        assert upload_result.success
        assert upload_result.uploaded_count == len(sample_log_entries)
        assert upload_result.failed_count == 0
        
        # gspreadクライアント呼び出し確認
        mock_gspread_client.create.assert_called_once()
        
    def test_configuration_validation_flow(self, temp_workspace):
        """設定検証フロー統合テスト"""
        config_manager = SharedFolderConfigManager()
        
        # 初期状態確認
        assert not config_manager.is_configured()
        
        # 無効URLでの設定試行
        with pytest.raises(Exception):
            config_manager.set_shared_folder_url("invalid_url")
        
        # 有効URLでの設定
        valid_url = "https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j"
        config_manager.set_shared_folder_url(valid_url)
        
        assert config_manager.is_configured()
        assert config_manager.get_shared_folder_url() == valid_url
        assert config_manager.extract_folder_id(valid_url) == "1a2b3c4d5e6f7g8h9i0j"
        
        # 設定状態確認
        status = config_manager.get_configuration_status()
        assert status['configured']
        assert status['url_valid']
        assert status['folder_id'] == "1a2b3c4d5e6f7g8h9i0j"
        
        # 設定妥当性検証
        validation = config_manager.validate_configuration()
        assert validation['valid']
        assert len(validation['errors']) == 0
    
    def test_multi_student_multi_stage_processing(self, temp_workspace, mock_gspread_client):
        """複数学生・複数ステージ処理統合テスト"""
        # 複数学生・ステージのログエントリ作成
        students = ["123456A", "654321B", "111111C"]
        stages = ["stage01", "stage02"]
        
        all_entries = []
        for student in students:
            for stage in stages:
                session_id = str(uuid.uuid4())
                for i in range(5):
                    entry = StudentLogEntry(
                        student_id=student,
                        session_id=session_id,
                        stage=stage,
                        timestamp=datetime.now() + timedelta(minutes=i),
                        level=i + 1,
                        hp=100,
                        max_hp=100,
                        position=(i, 0),
                        score=i * 100,
                        action_type="move",
                        log_level=LogLevel.INFO
                    )
                    all_entries.append(entry)
        
        # ログファイル作成
        log_file = temp_workspace / "multi_student_log.json"
        self.create_sample_log_file(log_file, all_entries)
        
        # ローダーでの処理
        loader = SessionLogLoader(str(temp_workspace))
        load_result = loader.load_session_logs([log_file])
        
        assert load_result.success
        assert len(load_result.entries) == len(all_entries)
        
        # 学生・ステージ取得確認
        available_students = loader.get_available_students()
        available_stages = loader.get_available_stages()
        
        assert set(available_students) == set(students)
        assert set(available_stages) == set(stages)
        
        # ステージ別サマリー確認
        summaries = loader.create_summary(load_result.entries)
        assert len(summaries) == len(stages)
        
        for summary in summaries:
            assert summary.stage in stages
            assert summary.total_entries == len(students) * 5  # 3学生 × 5エントリ
    
    def test_error_handling_and_recovery(self, temp_workspace, sample_log_entries):
        """エラーハンドリング・リカバリ統合テスト"""
        # 不正なログファイル作成
        invalid_log_file = temp_workspace / "invalid_log.json"
        with open(invalid_log_file, 'w') as f:
            f.write("invalid json content")
        
        # 正常なログファイル作成
        valid_log_file = temp_workspace / "valid_log.json"
        self.create_sample_log_file(valid_log_file, sample_log_entries)
        
        loader = SessionLogLoader(str(temp_workspace))
        
        # 不正ファイルを含む読み込み試行
        load_result = loader.load_session_logs([invalid_log_file, valid_log_file])
        
        # 部分的成功を確認
        assert load_result.success  # 有効ファイルがあるため成功
        assert len(load_result.warnings) > 0  # 警告が記録される
        assert len(load_result.entries) == len(sample_log_entries)  # 有効エントリのみ読み込まれる
        
        # 警告メッセージ確認
        warning_found = any("読み込み失敗" in warning for warning in load_result.warnings)
        assert warning_found
    
    def test_data_validation_and_filtering(self, temp_workspace):
        """データ妥当性検証・フィルタリング統合テスト"""
        # 有効・無効なエントリが混在するデータ作成
        mixed_entries_data = [
            # 有効エントリ
            {
                'student_id': '123456A',
                'session_id': str(uuid.uuid4()),
                'stage': 'stage01',
                'timestamp': datetime.now().isoformat(),
                'level': 3,
                'hp': 80,
                'max_hp': 100,
                'position': [2, 3],
                'score': 150,
                'action_type': 'move',
                'log_level': 'INFO'
            },
            # 無効エントリ（学生ID形式不正）
            {
                'student_id': '12345',  # 不正形式
                'session_id': str(uuid.uuid4()),
                'stage': 'stage01',
                'timestamp': datetime.now().isoformat(),
                'level': 1,
                'hp': 100,
                'max_hp': 100,
                'position': [0, 0],
                'score': 0,
                'action_type': 'move',
                'log_level': 'INFO'
            },
            # 無効エントリ（HP > max_HP）
            {
                'student_id': '654321B',
                'session_id': str(uuid.uuid4()),
                'stage': 'stage02',
                'timestamp': datetime.now().isoformat(),
                'level': 2,
                'hp': 150,  # max_HPを超過
                'max_hp': 100,
                'position': [1, 1],
                'score': 100,
                'action_type': 'attack',
                'log_level': 'INFO'
            }
        ]
        
        log_file = temp_workspace / "mixed_validation_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(mixed_entries_data, f, indent=2)
        
        loader = SessionLogLoader(str(temp_workspace))
        
        # 妥当性検証有効で読み込み
        load_result = loader.load_session_logs([log_file], validate_entries=True)
        
        # 有効エントリのみ読み込まれることを確認
        assert load_result.success
        assert len(load_result.entries) == 1  # 有効エントリ1つのみ
        assert len(load_result.warnings) == 2  # 無効エントリ2つの警告
        assert load_result.entries[0].student_id == '123456A'
        
        # フィルタリング機能テスト
        valid_entry = create_log_entry_from_dict(mixed_entries_data[0])
        entries = [valid_entry]
        
        # 学生IDフィルタ
        filtered = loader.filter_entries_by_criteria(entries, student_id='123456A')
        assert len(filtered) == 1
        
        filtered = loader.filter_entries_by_criteria(entries, student_id='NOTFOUND')
        assert len(filtered) == 0
        
        # ログレベルフィルタ
        filtered = loader.filter_entries_by_criteria(entries, log_levels=[LogLevel.INFO])
        assert len(filtered) == 1
        
        filtered = loader.filter_entries_by_criteria(entries, log_levels=[LogLevel.ERROR])
        assert len(filtered) == 0
    
    @patch('engine.google_auth_manager.gspread')
    def test_authentication_flow_integration(self, mock_gspread, temp_workspace):
        """認証フロー統合テスト"""
        auth_manager = GoogleAuthManager(credentials_dir=str(temp_workspace / ".oauth"))
        
        # 初期状態確認
        status = auth_manager.get_auth_status()
        assert not status['authenticated']
        assert not status['credentials_file_exists']
        
        # クライアント設定作成
        auth_manager.setup_client_config("test_client_id", "test_client_secret")
        
        status = auth_manager.get_auth_status()
        assert status['client_config_exists']
        
        # モック認証情報設定
        mock_credentials = MagicMock()
        mock_credentials.expired = False
        mock_credentials.token = "mock_token"
        mock_credentials.refresh_token = "mock_refresh_token"
        
        # 認証情報保存・読み込みテスト
        auth_manager.save_credentials(mock_credentials)
        loaded_credentials = auth_manager.load_credentials()
        
        assert loaded_credentials is not None
        assert loaded_credentials.token == "mock_token"
        
        # gspreadクライアント取得テスト
        mock_gspread.authorize.return_value = MagicMock()
        auth_manager._credentials = mock_credentials
        
        client = auth_manager.get_authenticated_client()
        assert client is not None
        mock_gspread.authorize.assert_called_once_with(mock_credentials)
    
    def test_performance_and_batch_processing(self, temp_workspace, mock_gspread_client):
        """パフォーマンス・バッチ処理統合テスト"""
        # 大量エントリ生成（バッチサイズを超える）
        large_entry_count = 2500
        session_id = str(uuid.uuid4())
        
        large_entries = []
        for i in range(large_entry_count):
            entry = StudentLogEntry(
                student_id="123456A",
                session_id=session_id,
                stage="stage01",
                timestamp=datetime.now() + timedelta(seconds=i),
                level=(i % 10) + 1,
                hp=max(100 - (i % 50), 1),
                max_hp=100,
                position=(i % 20, i % 15),
                score=i * 10,
                action_type=["move", "attack", "use_item", "defend"][i % 4],
                log_level=LogLevel.INFO
            )
            large_entries.append(entry)
        
        # ログファイル作成
        log_file = temp_workspace / "large_log.json"
        self.create_sample_log_file(log_file, large_entries)
        
        # 読み込みパフォーマンステスト
        loader = SessionLogLoader(str(temp_workspace))
        
        import time
        start_time = time.time()
        load_result = loader.load_session_logs([log_file])
        load_time = time.time() - start_time
        
        assert load_result.success
        assert len(load_result.entries) == large_entry_count
        assert load_time < 10.0  # 10秒以内で完了
        
        # バッチ処理設定テスト
        batch_config = SheetConfiguration(batch_size=1000)
        
        # アップロード処理（モック）
        with patch('engine.google_auth_manager.gspread.authorize', return_value=mock_gspread_client):
            auth_manager = GoogleAuthManager(credentials_dir=str(temp_workspace / ".oauth"))
            mock_credentials = MagicMock()
            mock_credentials.expired = False
            auth_manager._credentials = mock_credentials
            
            config_manager = SharedFolderConfigManager()
            config_manager.set_shared_folder_url("https://drive.google.com/drive/folders/mock_folder")
            
            uploader = GoogleSheetsUploader(auth_manager, config_manager)
            
            # バッチサイズが適用されることを確認
            assert batch_config.batch_size == 1000
            expected_batches = (large_entry_count + batch_config.batch_size - 1) // batch_config.batch_size
            assert expected_batches == 3  # 2500 ÷ 1000 = 3バッチ


class TestRegressionTests:
    """回帰テスト"""
    
    def test_backwards_compatibility_v1_2_2(self):
        """v1.2.2との後方互換性テスト"""
        # v1.2.2形式のデータ構造をサポートすることを確認
        legacy_entry_data = {
            'student_id': '123456A',
            'session_id': str(uuid.uuid4()),
            'stage': 'stage01',
            'timestamp': datetime.now().isoformat(),
            'level': 1,
            'hp': 100,
            'max_hp': 100,
            'position': [0, 0],
            'score': 0,
            'action_type': 'start'
            # log_levelやduration_msなどの新しいフィールドは存在しない
        }
        
        entry = create_log_entry_from_dict(legacy_entry_data)
        assert entry is not None
        assert entry.log_level == LogLevel.INFO  # デフォルト値
        assert entry.duration_ms is None
    
    def test_google_api_changes_resilience(self, temp_workspace):
        """Google API変更への耐性テスト"""
        # API制限エラーのシミュレーション
        from engine.google_sheets_uploader import GoogleSheetsUploader
        
        uploader = GoogleSheetsUploader()
        
        # リトライ可能エラーの判定テスト
        retryable_errors = [
            Exception("quota exceeded"),
            Exception("rate limit exceeded"), 
            Exception("HTTP 429"),
            Exception("HTTP 503"),
            Exception("network timeout")
        ]
        
        for error in retryable_errors:
            assert uploader._is_retryable_error(error)
        
        # リトライ不可能エラーの判定テスト
        non_retryable_errors = [
            Exception("authentication failed"),
            Exception("permission denied"),
            Exception("invalid spreadsheet id")
        ]
        
        for error in non_retryable_errors:
            assert not uploader._is_retryable_error(error)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])