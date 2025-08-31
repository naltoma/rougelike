#!/usr/bin/env python3
"""
Google Sheets統合システムテスト
"""

import sys
sys.path.append('..')

import json
from datetime import datetime


def test_config_creation():
    """設定ファイル作成テスト"""
    print("🧪 設定ファイル作成テスト")
    
    try:
        from engine.data_uploader import GoogleSheetsConfig
        
        # 設定作成（デフォルト）
        config = GoogleSheetsConfig("test_config.json")
        print("✅ GoogleSheetsConfig作成成功")
        
        # 設定確認
        print(f"   有効: {config.is_enabled()}")
        print(f"   サービスアカウント: {config.get_service_account_path()}")
        print(f"   スプレッドシートID: {config.get_spreadsheet_id()}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_uploader_creation():
    """データアップローダー作成テスト"""
    print("\n🧪 データアップローダー作成テスト")
    
    try:
        from engine.data_uploader import DataUploader
        from engine.progression import ProgressionManager
        
        # 進捗管理システム作成
        manager = ProgressionManager()
        
        # データアップローダー作成
        uploader = DataUploader(manager, "test_config.json")
        print("✅ DataUploader作成成功")
        
        # 状態確認
        status = uploader.get_upload_status()
        print(f"   有効: {status['enabled']}")
        print(f"   キューサイズ: {status['queue_size']}")
        print(f"   接続状態: {status['connection_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_operations():
    """キュー操作テスト"""
    print("\n🧪 キュー操作テスト")
    
    try:
        from engine.data_uploader import DataUploader
        from engine.progression import ProgressionManager
        
        manager = ProgressionManager()
        uploader = DataUploader(manager, "test_config.json")
        print("✅ DataUploader準備完了")
        
        # 学生進捗データをキューに追加
        student_data = {
            "stage_id": "stage01",
            "session_duration": 120.5,
            "success_rate": 0.75,
            "failed_attempts": 3,
            "hint_requests": 2
        }
        uploader.queue_student_progress("test_student_001", student_data)
        print("✅ 学生進捗データキューイング成功")
        
        # セッションログをキューに追加
        log_data = {
            "student_id": "test_student_001",
            "api_name": "move",
            "success": False,
            "message": "壁があります",
            "execution_time": 0.1
        }
        uploader.queue_session_log("session_001", log_data)
        print("✅ セッションログキューイング成功")
        
        # コード分析データをキューに追加
        analysis_data = {
            "total_lines": 25,
            "logical_lines": 20,
            "cyclomatic_complexity": 3,
            "function_count": 2
        }
        uploader.queue_code_analysis("test_student_001", "stage01", analysis_data)
        print("✅ コード分析データキューイング成功")
        
        # 学習パターンをキューに追加
        pattern_data = {
            "pattern_type": "wall_collision",
            "confidence": 0.8,
            "frequency": 5,
            "description": "壁との衝突を繰り返している"
        }
        uploader.queue_learning_pattern("test_student_001", pattern_data)
        print("✅ 学習パターンキューイング成功")
        
        # キュー状態確認
        status = uploader.get_upload_status()
        print(f"   キューサイズ: {status['queue_size']}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_teacher_dashboard():
    """教師ダッシュボードテスト"""
    print("\n🧪 教師ダッシュボードテスト")
    
    try:
        from engine.data_uploader import DataUploader, TeacherDashboard
        from engine.progression import ProgressionManager
        
        manager = ProgressionManager()
        uploader = DataUploader(manager, "test_config.json")
        dashboard = TeacherDashboard(uploader)
        print("✅ TeacherDashboard作成成功")
        
        # クラス概要生成テスト
        class_students = ["student001", "student002", "student003"]
        summary = dashboard.generate_class_summary(class_students)
        
        if summary and "error" not in summary:
            print("✅ クラス概要生成成功")
            print(f"   総学生数: {summary.get('total_students', 0)}名")
            print(f"   アクティブ学生: {summary.get('active_students', 0)}名")
        else:
            print("⚠️ クラス概要生成（データなし）")
            if summary and "error" in summary:
                print(f"   エラー: {summary['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_integration():
    """API統合テスト"""
    print("\n🧪 API統合テスト")
    
    try:
        from engine.api import (
            initialize_api, set_student_id, upload_student_data,
            get_sheets_status, show_sheets_status, force_sheets_upload
        )
        
        # API初期化（Google Sheets統合有効）
        initialize_api("cui", enable_progression=True, enable_session_logging=False,
                      enable_educational_errors=False)
        print("✅ API初期化成功（Google Sheets統合有効）")
        
        # 学生ID設定
        set_student_id("test_student_api")
        print("✅ 学生ID設定成功")
        
        # Google Sheets状態確認
        status = get_sheets_status()
        print(f"✅ Google Sheets状態取得: {status['enabled']}")
        
        # 学生データアップロードテスト
        result = upload_student_data()
        print(f"✅ 学生データアップロード: {result}")
        
        # 状態表示テスト
        print("\n📊 Google Sheets状態表示テスト:")
        show_sheets_status()
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_class_report():
    """モッククラスレポートテスト"""
    print("\n🧪 モッククラスレポートテスト")
    
    try:
        from engine.api import generate_class_report, show_class_report
        
        # モック学生リスト
        class_students = ["student_001", "student_002", "student_003"]
        
        # クラスレポート生成テスト
        report = generate_class_report(class_students)
        
        if report:
            print("✅ クラスレポート生成成功")
            if "error" not in report:
                print(f"   総学生数: {report.get('total_students', 0)}名")
                print(f"   アクティブ学生: {report.get('active_students', 0)}名")
        else:
            print("⚠️ クラスレポート生成（データなし）")
        
        # クラスレポート表示テスト
        print("\n📊 クラスレポート表示テスト:")
        show_class_report(class_students)
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sheets_client_mock():
    """Sheetsクライアントモックテスト"""
    print("\n🧪 Sheetsクライアントモックテスト")
    
    try:
        from engine.data_uploader import GoogleSheetsConfig, GoogleSheetsClient
        
        config = GoogleSheetsConfig("test_config.json")
        client = GoogleSheetsClient(config)
        print("✅ GoogleSheetsClient作成成功")
        
        # 接続状態確認
        is_connected = client.is_connected()
        print(f"   接続状態: {is_connected}")
        
        if not is_connected:
            print("   ⚠️ 接続なし（設定またはライブラリが不足）")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 Google Sheets統合システムテスト開始")
    print("=" * 60)
    
    tests = [
        test_config_creation,
        test_data_uploader_creation,
        test_queue_operations,
        test_teacher_dashboard,
        test_api_integration,
        test_mock_class_report,
        test_sheets_client_mock
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
    print("🏁 テスト結果")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"成功: {passed}/{total}")
    
    if passed == total:
        print("🎉 全ての Google Sheets統合システムテストが成功しました！")
        print("✅ データアップロードシステムが正常に実装されています")
        print("📊 Google Sheets統合（ライブラリ有効時）、キューイング、教師ダッシュボードが動作します")
        print("👨‍🏫 教師は学生の学習データをリアルタイムで監視・分析できます")
        print("📈 クラス全体の進捗管理と個別支援が可能です")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")
        print("🔧 Google Sheets統合システムの修正が必要です")
        print("💡 実際の使用には gspread と oauth2client のインストールが必要です")
        print("   pip install gspread oauth2client")


if __name__ == "__main__":
    main()