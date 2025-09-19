#!/usr/bin/env python3
"""ステップバイステップ詳細デバッグ"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "engine"))

from engine.api import initialize_api, initialize_stage
from engine.api import turn_left, turn_right, move, attack, see, wait, show_current_state
from engine import Direction, Position

STAGE_ID = "generated_patrol_2026"

def get_game_state():
    """グローバルAPIからゲーム状態を取得"""
    from engine.api import _global_api
    return _global_api.game_manager.get_current_state()

def detailed_step_analysis():
    """詳細なステップ分析"""

    print("=== 詳細ステップ分析 ===")

    # Initialize API
    initialize_api("cui")

    # Initialize stage
    if not initialize_stage(STAGE_ID):
        print("❌ Stage initialization failed")
        return

    # 初期状態
    game_state = get_game_state()
    print(f"初期状態:")
    print(f"プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
    for i, enemy in enumerate(game_state.enemies):
        print(f"敵{i}: {enemy.position} 向き: {enemy.direction}")

    # Step 1-6 実行
    steps = [
        ("turn_left", turn_left),
        ("move", move),
        ("move", move),
        ("move", move),
        ("turn_left", turn_left),
        ("move", move)
    ]

    for step_num, (action_name, action_func) in enumerate(steps, 1):
        print(f"\n=== Step {step_num}: {action_name} ===")

        # アクション実行前の状態
        game_state = get_game_state()
        print(f"実行前:")
        print(f"  プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
        for i, enemy in enumerate(game_state.enemies):
            print(f"  敵{i}: {enemy.position} 向き: {enemy.direction}")

        # アクション実行
        action_func()

        # アクション実行後の状態
        game_state = get_game_state()
        print(f"実行後:")
        print(f"  プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
        for i, enemy in enumerate(game_state.enemies):
            print(f"  敵{i}: {enemy.position} 向き: {enemy.direction}")

if __name__ == "__main__":
    detailed_step_analysis()