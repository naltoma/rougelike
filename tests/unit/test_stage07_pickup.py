#!/usr/bin/env python3
"""
Test stage07 pickup() mechanism and player ATK updates
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from engine import api as game_api

def test_stage07_pickup():
    print("Stage07 pickup()機能テスト")
    print("=" * 50)

    # ゲーム初期化
    game_api.initialize_api()
    game_api.initialize_stage("stage07")

    print("=== 初期状態 ===")
    state = game_api.see()

    # プレイヤー初期状態
    player = state['player']
    print(f"プレイヤー: pos={player['position']}, dir={player['direction']}, HP={player['hp']}")
    print(f"プレイヤー攻撃力: {player.get('attack_power', 'N/A')}")

    # アイテム状態
    items = state.get('items', [])
    print(f"アイテム数: {len(items)}")
    for item in items:
        print(f"   {item.get('id', 'unknown')}: {item.get('name', 'unknown')} at {item.get('position', 'unknown')}")
        if 'effect' in item:
            print(f"      効果: {item['effect']}")

    # 敵状態
    enemies = state.get('enemies', [])
    print(f"敵数: {len(enemies)}")
    for enemy in enemies:
        print(f"   {enemy.get('id', 'unknown')}: pos={enemy.get('position', 'unknown')}, HP={enemy.get('hp', 'unknown')}")

    # 提供された解法を実行
    solution = [
        "move",     # Step 1: (0,2) -> (1,2)
        "move",     # Step 2: (1,2) -> (2,2) 武器位置に到達
    ]

    for step_num, action in enumerate(solution, 1):
        print(f"\n=== ステップ {step_num}: {action} ===")

        if action == "move":
            result = game_api.move()

        state = game_api.see()
        player = state['player']
        print(f"実行後: pos={player['position']}, HP={player['hp']}")
        print(f"攻撃力: {player.get('attack_power', 'N/A')}")

    # 武器位置でis_available()チェック
    print(f"\n=== is_available()チェック ===")
    try:
        available = game_api.is_available()
        print(f"is_available(): {available}")
    except Exception as e:
        print(f"is_available() エラー: {e}")

    # pickup()実行
    print(f"\n=== pickup()実行 ===")
    try:
        pickup_result = game_api.pickup()
        print(f"pickup() 結果: {pickup_result}")
    except Exception as e:
        print(f"pickup() エラー: {e}")

    # pickup()後の状態確認
    print(f"\n=== pickup()後の状態 ===")
    state = game_api.see()
    player = state['player']
    print(f"プレイヤー: pos={player['position']}, HP={player['hp']}")
    print(f"攻撃力: {player.get('attack_power', 'N/A')}")

    # 装備アイテム確認
    equipped_items = player.get('equipped_items', [])
    print(f"装備アイテム: {equipped_items}")

    # インベントリ確認
    inventory = player.get('inventory', [])
    print(f"インベントリ: {inventory}")

    # アイテム状態（pickup後）
    items = state.get('items', [])
    print(f"残りアイテム数: {len(items)}")

    # 攻撃力変化の確認
    expected_attack = 30 + 35  # 基本攻撃力 + 武器効果
    actual_attack = player.get('attack_power', 30)

    print(f"\n=== 攻撃力検証 ===")
    print(f"期待値: {expected_attack} (基本30 + 武器35)")
    print(f"実際値: {actual_attack}")
    print(f"正常動作: {'✅' if actual_attack == expected_attack else '❌'}")

    if actual_attack != expected_attack:
        print(f"🚨 BUG: pickup()後に攻撃力が更新されていません")
        print(f"   武器効果が適用されていない可能性があります")

if __name__ == "__main__":
    test_stage07_pickup()