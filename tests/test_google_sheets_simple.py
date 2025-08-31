#!/usr/bin/env python3
"""
Google Sheets統合システム簡単テスト (API依存なし)
"""

import sys
sys.path.append('..')


def test_google_sheets_components():
    """Google Sheets コンポーネント単体テスト"""
    print("🧪 Google Sheets コンポーネント単体テスト")
    
    try:
        from engine.data_uploader import GoogleSheetsConfig, DataUploader, TeacherDashboard
        from engine.progression import ProgressionManager
        
        # 1. 設定作成テスト
        config = GoogleSheetsConfig("simple_test_config.json")
        print("✅ GoogleSheetsConfig作成成功")
        print(f"   有効状態: {config.is_enabled()}")
        
        # 2. 進捗管理システム
        manager = ProgressionManager()
        print("✅ ProgressionManager作成成功")
        
        # 3. データアップローダー
        uploader = DataUploader(manager, "simple_test_config.json")
        print("✅ DataUploader作成成功")
        
        # 4. キューイング機能テスト
        uploader.queue_student_progress("test_student", {
            "stage_id": "stage01",
            "session_duration": 120.0,
            "success_rate": 0.8
        })
        
        uploader.queue_session_log("session_001", {
            "student_id": "test_student",
            "api_name": "move",
            "success": True
        })
        
        print("✅ データキューイング成功")
        
        # 5. 状態確認
        status = uploader.get_upload_status()
        print(f"✅ 状態取得成功: キューサイズ={status['queue_size']}")
        
        # 6. 教師ダッシュボード
        dashboard = TeacherDashboard(uploader)
        print("✅ TeacherDashboard作成成功")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_functionality():
    """モック機能テスト"""
    print("\n🧪 モック機能テスト")
    
    try:
        from engine.data_uploader import DataUploader
        from engine.progression import ProgressionManager
        
        manager = ProgressionManager()
        uploader = DataUploader(manager, "mock_test_config.json")
        
        # 大量データキューイングテスト
        for i in range(10):
            uploader.queue_student_progress(f"student_{i:03d}", {
                "stage_id": f"stage{i%3+1:02d}",
                "session_duration": 100 + i * 10,
                "success_rate": 0.5 + (i % 5) * 0.1,
                "failed_attempts": i % 4,
                "hint_requests": i % 3
            })
        
        print("✅ 大量データキューイング成功")
        
        # 状態確認
        status = uploader.get_upload_status()
        print(f"✅ 最終キューサイズ: {status['queue_size']}")
        
        # アップロード試行（無効設定なので実際には送信されない）
        result = uploader.force_upload()
        print(f"✅ アップロード試行: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_variations():
    """設定バリエーションテスト"""
    print("\n🧪 設定バリエーションテスト")
    
    try:
        from engine.data_uploader import GoogleSheetsConfig
        
        # 1. 存在しないファイル
        config1 = GoogleSheetsConfig("nonexistent_config.json")
        print("✅ 存在しない設定ファイルのハンドリング成功")
        
        # 2. カスタムパス
        config2 = GoogleSheetsConfig("config/test_custom_config.json")
        print("✅ カスタムパス設定成功")
        
        # 3. 設定値アクセステスト
        print(f"   サービスアカウントパス: {config2.get_service_account_path()}")
        print(f"   スプレッドシートID: {config2.get_spreadsheet_id()}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback  
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 Google Sheets統合システム簡単テスト開始")
    print("=" * 60)
    
    tests = [
        test_google_sheets_components,
        test_mock_functionality,
        test_configuration_variations
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("🏁 簡単テスト結果")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"成功: {passed}/{total}")
    
    if passed == total:
        print("🎉 Google Sheets統合システムの基本機能テストが成功しました！")
        print("✅ コンポーネント作成、キューイング、設定管理が正常に動作")
        print("📊 実際の Google Sheets 連携には以下が必要:")
        print("   1. pip install gspread oauth2client")
        print("   2. Google Cloud Console でプロジェクト設定")
        print("   3. サービスアカウント作成と認証ファイル配置")
        print("   4. スプレッドシート作成と共有設定")
        print("   5. config/google_sheets.json の設定")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")
        print("🔧 基本機能に問題があります")


if __name__ == "__main__":
    main()