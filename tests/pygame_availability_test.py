#!/usr/bin/env python3
"""
pygame利用可能性テスト
"""

def check_pygame_availability():
    """pygame利用可能性をチェック"""
    print("🧪 pygame利用可能性テスト")
    
    try:
        import pygame
        print("✅ pygame インポート成功")
        print(f"📦 pygame バージョン: {pygame.version.ver}")
        
        # pygame初期化テスト
        try:
            pygame.init()
            print("✅ pygame.init() 成功")
            
            # ディスプレイ初期化テスト
            try:
                screen = pygame.display.set_mode((800, 600))
                print("✅ pygame.display.set_mode() 成功")
                print(f"🖥️ 画面サイズ: {screen.get_size()}")
                pygame.quit()
                print("✅ pygame.quit() 成功")
                return True
            except Exception as e:
                print(f"❌ ディスプレイ初期化エラー: {e}")
                return False
        except Exception as e:
            print(f"❌ pygame初期化エラー: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ pygame インポートエラー: {e}")
        return False

def test_renderer_creation():
    """レンダラー作成テスト"""
    print("\n🧪 レンダラー作成テスト")
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from engine.renderer import RendererFactory, PYGAME_AVAILABLE
        print(f"✅ renderer module インポート成功")
        print(f"🔧 PYGAME_AVAILABLE = {PYGAME_AVAILABLE}")
        
        # CUI レンダラーテスト
        cui_renderer = RendererFactory.create_renderer("cui")
        print(f"✅ CUI レンダラー作成成功: {type(cui_renderer).__name__}")
        
        # GUI レンダラーテスト
        try:
            gui_renderer = RendererFactory.create_renderer("gui")
            print(f"✅ GUI レンダラー作成成功: {type(gui_renderer).__name__}")
            
            # 初期化テスト
            gui_renderer.initialize(10, 10)
            print("✅ GUI レンダラー初期化成功")
            return True
        except Exception as e:
            print(f"❌ GUI レンダラー作成/初期化エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ renderer module インポートエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    pygame_ok = check_pygame_availability()
    renderer_ok = test_renderer_creation()
    
    print(f"\n🎯 テスト結果:")
    print(f"   pygame: {'✅' if pygame_ok else '❌'}")
    print(f"   renderer: {'✅' if renderer_ok else '❌'}")
    
    if pygame_ok and renderer_ok:
        print("🎉 全てのテストが成功しました")
    else:
        print("⚠️ 問題が発見されました")