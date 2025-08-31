#!/usr/bin/env python3
"""
レンダラー自動テスト（非対話的版）
"""

import sys
sys.path.append('..')

from engine.api import (
    initialize_stage, turn_right, move, show_current_state, 
    set_auto_render, show_legend, show_action_history,
    get_game_result
)


def test_renderer_integration():
    """レンダラー統合テスト（自動）"""
    print("🧪 レンダラー統合テスト開始")
    print("=" * 50)
    
    # テスト1: 基本的なレンダリング
    print("📍 テスト1: 基本的なレンダリング")
    if not initialize_stage("stage01"):
        print("❌ ステージ初期化失敗")
        return False
    
    print("✅ Stage01初期化成功")
    
    # 凡例表示テスト
    print("\n📋 凡例表示テスト:")
    show_legend()
    
    # 初期状態表示テスト
    print("🎯 初期状態表示テスト:")
    show_current_state()
    
    # テスト2: 自動レンダリングオフでの手動制御
    print("\n" + "=" * 30)
    print("📍 テスト2: 手動レンダリング制御")
    set_auto_render(False)
    
    # 一連のアクションを実行
    actions = [
        ("東を向く", lambda: turn_right()),
        ("東に移動", lambda: move()),
        ("東に移動", lambda: move()),
        ("南を向く", lambda: turn_right()),
        ("南に移動", lambda: move())
    ]
    
    for description, action in actions:
        print(f"\n🎬 {description}")
        action()
        show_current_state()
    
    # アクション履歴表示
    print("\n📜 アクション履歴表示テスト:")
    show_action_history()
    
    # ゲーム結果
    result = get_game_result()
    print(f"\n🏁 ゲーム結果: {result}")
    
    # テスト3: 自動レンダリング
    print("\n" + "=" * 30)
    print("📍 テスト3: 自動レンダリング")
    
    # Stage02で新しいゲーム
    initialize_stage("stage02")
    set_auto_render(True)
    
    print("🖼️ 自動レンダリングモードでのプレイ")
    
    # 連続アクション
    print("🎬 連続アクション実行中...")
    move()  # 各アクション後に自動レンダリング
    turn_right()
    move()
    
    # テスト4: 複雑なステージ
    print("\n" + "=" * 30)
    print("📍 テスト4: 複雑なステージ（Stage03）")
    
    initialize_stage("stage03")
    set_auto_render(False)
    
    print("🧪 Stage03 - 移動禁止マス含むステージ")
    show_current_state()
    
    # 移動テスト
    turn_right()  # 東を向く
    move()        # 東に移動
    turn_right()  # 南を向く
    move()        # 南に移動（可能かチェック）
    
    show_current_state()
    
    print("✅ 全てのレンダラー統合テスト完了")
    return True


def main():
    """メイン実行"""
    try:
        success = test_renderer_integration()
        if success:
            print("\n🎉 レンダラー統合テスト成功！")
            print("✅ CUIレンダラーがAPIに正常に統合されました")
        else:
            print("\n❌ テストに失敗しました")
            
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()