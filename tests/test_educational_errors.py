#!/usr/bin/env python3
"""
教育的エラーハンドリングシステムテスト
"""

import sys
sys.path.append('..')


def test_basic_error_handling():
    """基本エラーハンドリングテスト"""
    print("🧪 基本エラーハンドリングテスト")
    
    try:
        from engine.educational_errors import ErrorHandler, EducationalError
        
        # エラーハンドラー作成
        handler = ErrorHandler()
        print("✅ ErrorHandler作成成功")
        
        # 基本的なエラー処理テスト
        test_error = ValueError("引数が正しくありません")
        educational_error = handler.handle_error(test_error)
        
        print(f"✅ エラー分析成功: {educational_error.title}")
        print(f"   説明: {educational_error.explanation}")
        
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
        from engine.api import initialize_api, set_student_id, get_error_feedback
        
        # 教育的エラーハンドリングを有効にしてAPI初期化
        initialize_api("cui", enable_progression=False, enable_session_logging=False, 
                      enable_educational_errors=True)
        print("✅ API初期化成功（エラーハンドリング有効）")
        
        # 学生ID設定
        set_student_id("test_student")
        print("✅ 学生ID設定成功")
        
        # エラーフィードバック取得テスト
        feedback = get_error_feedback("NameError")
        if feedback:
            print("✅ エラーフィードバック取得成功")
        else:
            print("⚠️ エラーフィードバックなし")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_categorization():
    """エラー分類テスト"""
    print("\n🧪 エラー分類テスト")
    
    try:
        from engine.educational_errors import ErrorHandler
        
        handler = ErrorHandler()
        
        # 様々なタイプのエラーをテスト
        test_errors = [
            NameError("name 'undefined_variable' is not defined"),
            SyntaxError("invalid syntax"),
            TypeError("'int' object is not callable"),
            AttributeError("'str' object has no attribute 'append'"),
            IndexError("list index out of range")
        ]
        
        for error in test_errors:
            educational_error = handler.handle_error(error)
            print(f"✅ {type(error).__name__}: {educational_error.category}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_game_context_error():
    """ゲームコンテキストエラーテスト"""
    print("\n🧪 ゲームコンテキストエラーテスト")
    
    try:
        from engine.educational_errors import ErrorHandler
        from engine.api import APIUsageError
        
        handler = ErrorHandler()
        
        # API使用エラーのテスト
        api_error = APIUsageError("このステージでは 'attack' APIは使用できません")
        context = {
            "game_state": {
                "player_position": {"x": 2, "y": 3},
                "turn_count": 5,
                "stage_id": "stage01"
            },
            "recent_actions": ["move", "turn_right", "move"]
        }
        
        educational_error = handler.handle_error(api_error, context)
        print(f"✅ API使用エラー分析: {educational_error.title}")
        print(f"   ヒント数: {len(educational_error.hints)}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_common_mistake_detection():
    """よくあるミステイク検出テスト"""
    print("\n🧪 よくあるミステイク検出テスト")
    
    try:
        from engine.educational_errors import ErrorHandler
        
        handler = ErrorHandler()
        
        # よくあるパターンのシミュレート
        call_history = [
            {"api": "move", "message": "移動失敗: 壁があります"},
            {"api": "move", "message": "移動失敗: 壁があります"},
            {"api": "move", "message": "移動失敗: 壁があります"}
        ]
        
        mistakes = handler.check_common_patterns(call_history)
        print(f"✅ 検出されたミステイク数: {len(mistakes)}")
        
        for mistake in mistakes:
            print(f"   • {mistake}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 教育的エラーハンドリングシステムテスト開始")
    print("=" * 60)
    
    tests = [
        test_basic_error_handling,
        test_api_integration,
        test_error_categorization,
        test_game_context_error,
        test_common_mistake_detection
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
        print("🎉 全ての教育的エラーハンドリングテストが成功しました！")
        print("✅ 教育的エラーハンドリングシステムが正常に実装されています")
        print("💡 学生は詳細なエラーフィードバックを受け取ることができます")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")
        print("🔧 エラーハンドリング機能の修正が必要です")


if __name__ == "__main__":
    main()