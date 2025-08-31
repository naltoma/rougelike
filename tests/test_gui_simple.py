#!/usr/bin/env python3
"""
GUI レンダラー簡易テスト（非対話的）
"""

import sys
sys.path.append('..')

def test_gui_import():
    """GUI レンダラーのインポートテスト"""
    print("🧪 GUI レンダラーインポートテスト")
    
    try:
        from engine.renderer import GuiRenderer, RendererFactory
        print("✅ GUI レンダラーのインポート成功")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False


def test_pygame_availability():
    """pygame 可用性テスト"""
    print("\n🧪 pygame 可用性テスト")
    
    try:
        import pygame
        print("✅ pygame が利用可能です")
        print(f"pygame バージョン: {pygame.version.ver}")
        return True
    except ImportError as e:
        print(f"❌ pygame が利用できません: {e}")
        return False


def test_renderer_factory():
    """レンダラーファクトリーテスト"""
    print("\n🧪 レンダラーファクトリーテスト")
    
    try:
        from engine.renderer import RendererFactory
        
        # CUI レンダラーテスト
        cui_renderer = RendererFactory.create_renderer("cui")
        print("✅ CUI レンダラー作成成功")
        
        # GUI レンダラーテスト
        try:
            gui_renderer = RendererFactory.create_renderer("gui")
            print("✅ GUI レンダラー作成成功")
            
            # クリーンアップ
            gui_renderer.cleanup()
            print("✅ GUI レンダラークリーンアップ成功")
            
        except ImportError:
            print("⚠️ pygame が利用できないため、GUI レンダラーは CUI レンダラーにフォールバックされました")
        
        return True
        
    except Exception as e:
        print(f"❌ レンダラーファクトリーテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_integration():
    """API統合テスト"""
    print("\n🧪 API統合テスト")
    
    try:
        from engine.api import initialize_api
        
        # CUIモードテスト
        print("CUIモードでAPI初期化...")
        initialize_api("cui")
        print("✅ CUI API初期化成功")
        
        # GUIモードテスト
        print("GUIモードでAPI初期化...")
        try:
            initialize_api("gui")
            print("✅ GUI API初期化成功")
        except ImportError:
            print("⚠️ pygame が利用できないため、GUI APIは CUI にフォールバックされました")
        
        return True
        
    except Exception as e:
        print(f"❌ API統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 GUI レンダラー簡易テスト開始")
    print("=" * 50)
    
    tests = [
        test_pygame_availability,
        test_gui_import,
        test_renderer_factory,
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
        print("🎉 全てのテストが成功しました！")
        print("✅ GUI レンダラーが正常に実装されています")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")


if __name__ == "__main__":
    main()