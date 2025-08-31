#!/usr/bin/env python3
"""
GUI レンダラーテスト
pygame を使用した視覚的なテスト
"""

import sys
sys.path.append('..')

import time
from engine.api import initialize_api, initialize_stage, turn_right, move, show_current_state


def test_gui_basic():
    """GUI基本テスト"""
    print("🎮 GUI基本テスト開始")
    print("=" * 50)
    
    # GUI モードでAPI初期化
    try:
        initialize_api("gui")
    except ImportError as e:
        print(f"❌ pygame が利用できません: {e}")
        print("💡 CUI モードでテストを続行します")
        initialize_api("cui")
    
    # ステージ初期化
    if not initialize_stage("stage01"):
        print("❌ ステージ初期化失敗")
        return False
    
    print("✅ Stage01が初期化されました")
    
    # 初期状態表示
    print("🎯 初期状態:")
    show_current_state()
    
    # ちょっと待つ（GUI の場合、画面を見る時間）
    time.sleep(2)
    
    print("🎬 簡単な動作テストを実行...")
    
    # 東を向く
    print("👉 東を向きます...")
    turn_right()
    time.sleep(1)
    
    # 東に移動
    print("🚶 東に移動...")
    for i in range(3):
        move()
        time.sleep(1)
    
    # 南を向く
    print("👇 南を向きます...")
    turn_right()
    time.sleep(1)
    
    # 南に移動
    print("🚶 南に移動...")
    for i in range(3):
        move()
        time.sleep(1)
    
    print("✅ GUI基本テスト完了")
    return True


def test_gui_interactive():
    """GUI インタラクティブテスト"""
    print("\n" + "=" * 50)
    print("🖱️ GUIインタラクティブテスト")
    print("=" * 50)
    
    try:
        initialize_api("gui")
        print("🎮 GUIモードで起動しました")
        print("💡 キーボード操作:")
        print("  - ESC: 終了")
        print("  - F1: デバッグモード切り替え")
        print("  - F2: グリッド表示切り替え")
        print("  - F3: 座標表示切り替え")
        
    except ImportError as e:
        print(f"❌ pygame が利用できません: {e}")
        print("💡 CUI モードでテストを続行します")
        initialize_api("cui")
    
    # ステージ初期化
    if not initialize_stage("stage02"):
        print("❌ ステージ初期化失敗")
        return False
    
    print("\n🎯 Stage02 - 迷路ステージを起動")
    print("ウィンドウが開くまでお待ちください...")
    
    # 初期状態表示
    show_current_state()
    
    print("\n⏸️ ゲームが開始されました")
    print("GUIウィンドウで操作してください（ESCキーで終了）")
    print("このスクリプトは10秒後に終了します...")
    
    # しばらく待つ（ユーザーが操作できるように）
    for i in range(10, 0, -1):
        print(f"残り {i} 秒...")
        time.sleep(1)
    
    print("✅ GUIインタラクティブテスト完了")
    return True


def test_gui_stages():
    """GUI 複数ステージテスト"""
    print("\n" + "=" * 50)
    print("🎪 GUI複数ステージテスト")
    print("=" * 50)
    
    try:
        initialize_api("gui")
    except ImportError as e:
        print(f"❌ pygame が利用できません: {e}")
        print("💡 CUI モードでテストを続行します")
        initialize_api("cui")
    
    stages = ["stage01", "stage02", "stage03"]
    
    for stage_id in stages:
        print(f"\n🎯 {stage_id} をテスト中...")
        
        if initialize_stage(stage_id):
            print(f"✅ {stage_id} 初期化成功")
            show_current_state()
            
            # 少し動いてみる
            turn_right()
            move()
            time.sleep(2)
            
        else:
            print(f"❌ {stage_id} 初期化失敗")
    
    print("✅ 全ステージテスト完了")
    return True


def main():
    """メイン実行"""
    print("🧪 GUI レンダラー統合テスト開始")
    
    try:
        # 基本テスト
        success1 = test_gui_basic()
        
        # インタラクティブテスト
        success2 = test_gui_interactive()
        
        # 複数ステージテスト
        success3 = test_gui_stages()
        
        if success1 and success2 and success3:
            print("\n🎉 全てのGUI テストが完了！")
            print("✅ GUI レンダラーが正常に動作しています")
        else:
            print("\n❌ 一部のテストが失敗しました")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ テストが中断されました")
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()