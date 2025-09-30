#!/usr/bin/env python3
"""
ポーション回復機能の詳細テスト
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import api as game_api


def test_potion_healing_detailed():
    print("=== 詳細ポーション回復テスト ===")

    # ゲーム初期化
    game_api.initialize_api()
    game_api.initialize_stage('stage07')  # 既存のstage07を使用

    # 初期状態確認
    print("初期状態:")
    state = game_api.see()
    player = state['player']
    print(f"  HP: {player['hp']}")
    print(f"  位置: {player['position']}")

    # プレイヤーのHPを60に下げてテスト
    print("\n=== プレイヤーのHPを60に設定（テスト用） ===")
    # game内部アクセス - デバッグ目的
    game_state_manager = game_api._global_api.game_state_manager
    game_state = game_state_manager.current_state
    original_hp = game_state.player.hp
    game_state.player.hp = 60
    print(f"HP変更: {original_hp} -> 60")

    # 全アイテム情報を確認
    print("\n=== ゲーム内部のアイテム情報確認 ===")
    for i, item in enumerate(game_state.items):
        print(f"  アイテム{i+1}: {item.id}")
        print(f"    type: {item.item_type}")
        print(f"    position: ({item.position.x}, {item.position.y})")
        print(f"    name: {item.name}")
        print(f"    value: {item.value}")
        print(f"    effect: {item.effect}")
        if item.item_type.value == "potion":
            print(f"    *** これはポーションです ***")

    # ポーション位置に直接移動
    potion = None
    for item in game_state.items:
        if item.item_type.value == "potion":
            potion = item
            break

    if potion:
        print(f"\n=== プレイヤーをポーション位置に移動: ({potion.position.x}, {potion.position.y}) ===")
        game_state.player.position.x = potion.position.x
        game_state.player.position.y = potion.position.y

        # pickup実行前の状態
        print(f"pickup前HP: {game_state.player.hp}")

        # pickup実行
        print("\nポーション取得実行...")
        pickup_result = game_api.pickup()
        print(f"pickup結果: {pickup_result}")

        # pickup実行後の状態
        print(f"pickup後HP: {game_state.player.hp}")

        # 期待値と実際値の比較
        expected_hp = min(game_state.player.max_hp, 60 + potion.value)
        actual_hp = game_state.player.hp
        print(f"\n=== 回復結果 ===")
        print(f"期待HP: {expected_hp} (60 + {potion.value})")
        print(f"実際HP: {actual_hp}")

        if actual_hp > 60:
            healed = actual_hp - 60
            print(f"✅ 回復成功: +{healed}HP")
        else:
            print(f"❌ 回復失敗: HP変化なし")

    else:
        print("❌ ポーションが見つかりませんでした")


if __name__ == "__main__":
    test_potion_healing_detailed()