#!/usr/bin/env python3
"""
ポーション回復機能のテスト
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import api as game_api


def test_potion_healing():
    print("=== ポーション回復テスト ===")

    # ゲーム初期化
    game_api.initialize_api()
    game_api.initialize_stage('stage07')  # 既存のstage07を使用

    # 現在位置[6,0], 方向W, HP100でスタート
    print("初期状態:")
    state = game_api.see()
    player = state['player']
    print(f"  HP: {player['hp']}")
    print(f"  位置: {player['position']}")
    print(f"  方向: {player['direction']}")

    # 近くのポーション potion_3 (位置[0,4], value:37) を取りに行く
    # [6,0] -> [0,4] への移動パス

    print("\nポーション potion_3 へ移動中...")

    # 西に6歩移動 ([6,0] -> [0,0])
    for i in range(6):
        result = game_api.move()
        print(f"  西に移動 {i+1}/6: {result}")

    # 南向きに転回 (W -> S)
    game_api.turn_left()

    # 南に4歩移動 ([0,0] -> [0,4])
    for i in range(4):
        result = game_api.move()
        print(f"  南に移動 {i+1}/4: {result}")

    # ポーション取得前の状態確認
    print("\nポーション取得前:")
    state = game_api.see()
    player = state['player']
    print(f"  HP: {player['hp']}")
    print(f"  位置: {player['position']}")

    # 足元のアイテム確認
    items = [item for item in state.get('items', []) if item.get('position') == player['position']]
    print(f"  足元のアイテム数: {len(items)}")
    if items:
        for item in items:
            print(f"    アイテム: {item}")

    # ポーション取得
    print("\nポーション取得実行...")
    pickup_result = game_api.pickup()
    print(f"pickup結果: {pickup_result}")

    # 取得後の状態確認
    print("\nポーション取得後:")
    state = game_api.see()
    player = state['player']
    print(f"  HP: {player['hp']}")
    print(f"  位置: {player['position']}")

    # 結果評価
    if player['hp'] > 100:
        heal_amount = player['hp'] - 100
        print(f"\n✅ HP回復確認: +{heal_amount}HP回復 (100 -> {player['hp']})")
    else:
        print(f"\n❌ HP回復なし: HP = {player['hp']}")


if __name__ == "__main__":
    test_potion_healing()