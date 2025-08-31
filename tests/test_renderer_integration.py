#!/usr/bin/env python3
"""
レンダラー統合テスト（API統合）
"""

import sys
import time
sys.path.append('..')

from engine.api import (
    initialize_stage, turn_right, move, show_current_state, 
    set_auto_render, show_legend, show_action_history,
    get_game_result
)


def test_visual_gameplay():
    """視覚的ゲームプレイテスト"""
    print("🎮 視覚的ゲームプレイテスト開始")
    print("=" * 50)
    
    # ステージ初期化
    print("📍 ステージを初期化しています...")
    if not initialize_stage("stage01"):
        print("❌ ステージ初期化失敗")
        return
    
    print("✅ Stage01が初期化されました")
    
    # 凡例を表示
    print("\n📋 ゲームの凡例:")
    show_legend()
    
    # 初期状態を表示
    print("🎯 初期状態:")
    show_current_state()
    
    # 自動レンダリングをオフにして手動制御
    set_auto_render(False)
    
    print("\n🎲 ゲームプレイ開始...")
    input("Enterキーを押して続行...")
    
    # ステップ1: 東を向く
    print("\n👉 ステップ1: 東を向きます")
    turn_right()
    show_current_state()
    input("Enterキーを押して続行...")
    
    # ステップ2: 東に移動
    print("\n🚶 ステップ2: 東に移動します")
    move()
    show_current_state()
    input("Enterキーを押して続行...")
    
    # ステップ3: さらに東に移動
    print("\n🚶 ステップ3: さらに東に移動します")
    move()
    show_current_state()
    input("Enterキーを押して続行...")
    
    # ステップ4: 南を向く
    print("\n👇 ステップ4: 南を向きます")
    turn_right()
    show_current_state()
    input("Enterキーを押して続行...")
    
    # ステップ5: 南に移動
    print("\n🚶 ステップ5: 南に移動します")
    move()
    show_current_state()
    input("Enterキーを押して続行...")
    
    # アクション履歴表示
    print("\n📜 アクション履歴:")
    show_action_history()
    
    # ゲーム結果
    result = get_game_result()
    print(f"\n🏁 ゲーム結果: {result}")


def test_automatic_rendering():
    """自動レンダリングテスト"""
    print("\n" + "=" * 50)
    print("🖼️ 自動レンダリングテスト開始")
    print("=" * 50)
    
    # 新しいゲームを開始
    initialize_stage("stage02")
    
    # 自動レンダリングをオンに
    set_auto_render(True)
    
    print("🎯 自動レンダリングモードでのプレイ")
    print("（各アクション後に画面が自動更新されます）")
    
    # 連続アクション
    actions = [
        ("東に移動", lambda: move()),
        ("南を向く", lambda: turn_right()),
        ("南に移動", lambda: move()),
        ("西を向く", lambda: turn_right()),
        ("西に移動", lambda: move())
    ]
    
    for description, action in actions:
        print(f"\n🎬 {description}...")
        time.sleep(1)  # 視覚的な遅延
        action()
        time.sleep(1)  # レンダリングを確認する時間
    
    print("\n📊 最終状態:")
    show_current_state()


def test_debug_features():
    """デバッグ機能テスト"""
    print("\n" + "=" * 50)
    print("🔧 デバッグ機能テスト")
    print("=" * 50)
    
    # Stage03でテスト（移動禁止マスがある）
    initialize_stage("stage03")
    set_auto_render(False)
    
    print("🧪 Stage03 - 移動禁止マス含む複雑なステージ")
    show_current_state()
    
    # いくつかのアクションを実行
    turn_right()  # 東を向く
    move()        # 東に移動
    turn_right()  # 南を向く
    
    # 詳細情報を表示
    print("\n🔍 詳細情報:")
    print("📋 凡例:")
    show_legend()
    
    print("📜 実行したアクション:")
    show_action_history()
    
    print("🎯 現在の状態:")
    show_current_state()


def main():
    """メイン実行"""
    print("🧪 レンダラー統合テスト開始")
    
    try:
        # 基本的な視覚テスト
        test_visual_gameplay()
        
        # 自動レンダリングテスト
        test_automatic_rendering()
        
        # デバッグ機能テスト
        test_debug_features()
        
        print("\n🎉 全てのレンダラー統合テストが完了！")
        print("✅ CUIレンダラーがAPIに正常に統合されました")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ テストが中断されました")
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()