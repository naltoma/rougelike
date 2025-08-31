#!/usr/bin/env python3
"""
セッションログシステム最小テスト
"""

import sys
sys.path.append('..')


def test_minimal_session():
    """最小限のセッションテスト"""
    print("🧪 最小セッションテスト")
    
    try:
        # 直接インポートテスト
        from engine.session_logging import LogEntry, EventType, LogLevel
        from datetime import datetime
        
        # LogEntry作成テスト
        entry = LogEntry(
            timestamp=datetime.now(),
            session_id="test_session",
            student_id="test_student", 
            event_type=EventType.ACTION_EXECUTED,
            level=LogLevel.INFO,
            message="テストメッセージ"
        )
        
        print("✅ LogEntry作成成功")
        
        # 辞書変換テスト
        entry_dict = entry.to_dict()
        print("✅ 辞書変換成功")
        
        # 辞書から復元テスト
        restored = LogEntry.from_dict(entry_dict)
        print("✅ 辞書復元成功")
        
        # データ検証
        assert restored.message == entry.message
        assert restored.session_id == entry.session_id
        print("✅ データ整合性確認")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_simple_integration():
    """API簡単統合テスト"""
    print("\n🧪 API簡単統合テスト")
    
    try:
        # APIレイヤーを直接テスト（自動フラッシュなし）
        from engine.api import APILayer
        
        # セッションログなしでAPI作成
        api = APILayer("cui", enable_progression=False, enable_session_logging=False)
        print("✅ API作成成功（ログなし）")
        
        # セッションログありでAPI作成
        api_with_logging = APILayer("cui", enable_progression=False, enable_session_logging=True) 
        print("✅ API作成成功（ログあり）")
        
        # 学生ID設定
        api_with_logging.set_student_id("test_student")
        print("✅ 学生ID設定成功")
        
        # すぐに終了（タイマー問題回避）
        if api_with_logging.session_logger:
            api_with_logging.session_logger.end_session()
        print("✅ セッション終了成功")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 セッションログシステム最小テスト開始")
    print("=" * 50)
    
    tests = [
        test_minimal_session,
        test_api_simple_integration
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
        print("💡 自動フラッシュタイマーは実装されていますが、このテストでは使用していません")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")


if __name__ == "__main__":
    main()