#!/usr/bin/env python3
"""
セッションログシステム簡易テスト
"""

import sys
sys.path.append('..')

import time
from pathlib import Path


def test_session_logger_import():
    """セッションロガーのインポートテスト"""
    print("🧪 セッションロガーインポートテスト")
    
    try:
        from engine.session_logging import (
            SessionLogger, EventType, LogLevel, LogEntry, SessionSummary
        )
        print("✅ セッションログモジュールのインポート成功")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False


def test_basic_logging():
    """基本ログ機能テスト"""
    print("\n🧪 基本ログ機能テスト")
    
    try:
        from engine.session_logging import SessionLogger
        
        test_dir = "test_data/simple_session"
        logger = SessionLogger(test_dir, max_log_files=5)
        
        # セッション開始
        session_id = logger.start_session("test_student")
        print(f"✅ セッション開始: {session_id}")
        
        # 基本ログ記録
        logger.log_stage_start("stage01")
        logger.log_action("move", True, "移動成功")
        logger.log_stage_end("stage01", True)
        
        # セッション終了
        summary = logger.end_session()
        if summary:
            print(f"✅ セッション終了: {summary.total_actions}アクション")
        
        # クリーンアップ
        import shutil
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print("🧹 テストデータクリーンアップ")
        
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
        from engine.api import initialize_api, set_student_id
        
        # API初期化
        initialize_api("cui", enable_progression=True, 
                      enable_session_logging=True, student_id="simple_test")
        
        print("✅ セッションログ付きAPI初期化成功")
        
        # セッションログ機能確認
        from engine.api import get_session_summary, end_session
        
        summary = get_session_summary()
        if summary:
            print("✅ セッションサマリー取得成功")
        
        end_session()
        print("✅ セッション終了成功")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 セッションログシステム簡易テスト開始")
    print("=" * 50)
    
    tests = [
        test_session_logger_import,
        test_basic_logging,
        test_api_integration
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🏁 テスト結果")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"成功: {passed}/{total}")
    
    if passed == total:
        print("🎉 全てのセッションログテストが成功しました！")
        print("✅ セッションログシステムが正常に実装されています")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")


if __name__ == "__main__":
    main()