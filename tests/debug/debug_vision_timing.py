#!/usr/bin/env python3
"""視界検出タイミング詳細調査"""

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

def analyze_enemy_vision():
    """敵の視界と向きの関係を詳細分析"""

    print("=== 敵視界検出タイミング分析 ===")

    # Initialize API
    initialize_api("cui")

    # Initialize stage
    if not initialize_stage(STAGE_ID):
        print("❌ Stage initialization failed")
        return

    # ゲーム状態取得
    game_state = get_game_state()

    print(f"初期状態:")
    print(f"プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
    for i, enemy in enumerate(game_state.enemies):
        print(f"敵{i}: {enemy.position} 向き: {enemy.direction} vision_range: {enemy.vision_range}")
        vision_cells = enemy.get_vision_cells(game_state.board)
        print(f"  視界セル: {[(cell.x, cell.y) for cell in vision_cells]}")

    print("\n=== Step-by-step 分析 ===")

    # Step 1-6: プレイヤー移動（敵は視界外）
    print("\nStep 1-6: プレイヤー初期移動")
    turn_left()  # Step 1
    move()       # Step 2: (6,2)
    move()       # Step 3: (5,2)
    move()       # Step 4: (4,2)
    turn_left()  # Step 5
    move()       # Step 6: (4,3)

    game_state = get_game_state()
    print(f"Step 6後:")
    print(f"プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
    for i, enemy in enumerate(game_state.enemies):
        print(f"敵{i}: {enemy.position} 向き: {enemy.direction}")
        vision_cells = enemy.get_vision_cells(game_state.board)
        print(f"  視界セル: {[(cell.x, cell.y) for cell in vision_cells]}")
        can_see = enemy.can_see_player(game_state.player.position, game_state.board)
        print(f"  プレイヤー検出: {can_see}")

    # Step 7: プレイヤー(4,4)移動（重要なステップ）
    print("\nStep 7: プレイヤー(4,4)移動")
    move()       # Step 7: (4,4)S

    game_state = get_game_state()
    print(f"Step 7後:")
    print(f"プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
    for i, enemy in enumerate(game_state.enemies):
        print(f"敵{i}: {enemy.position} 向き: {enemy.direction}")
        vision_cells = enemy.get_vision_cells(game_state.board)
        print(f"  視界セル: {[(cell.x, cell.y) for cell in vision_cells]}")
        can_see = enemy.can_see_player(game_state.player.position, game_state.board)
        print(f"  プレイヤー検出: {can_see}")

        # 距離計算
        distance = enemy.position.distance_to(game_state.player.position)
        print(f"  プレイヤーとの距離: {distance}")

    # Step 8: プレイヤー継続移動
    print("\nStep 8: プレイヤー継続移動")
    move()       # Step 8: (4,5)S

    game_state = get_game_state()
    print(f"Step 8後:")
    print(f"プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
    for i, enemy in enumerate(game_state.enemies):
        print(f"敵{i}: {enemy.position} 向き: {enemy.direction}")
        vision_cells = enemy.get_vision_cells(game_state.board)
        print(f"  視界セル: {[(cell.x, cell.y) for cell in vision_cells]}")
        can_see = enemy.can_see_player(game_state.player.position, game_state.board)
        print(f"  プレイヤー検出: {can_see}")

    # 追加のステップで検証
    for step in range(9, 15):
        print(f"\nStep {step}:")
        if step == 9:
            wait()
        elif step == 10:
            turn_right()
        elif step == 11:
            turn_left()
        elif step == 12:
            move()
        elif step == 13:
            turn_right()
        elif step == 14:
            wait()

        game_state = get_game_state()
        print(f"Step {step}後:")
        print(f"プレイヤー: {game_state.player.position} 向き: {game_state.player.direction}")
        for i, enemy in enumerate(game_state.enemies):
            print(f"敵{i}: {enemy.position} 向き: {enemy.direction}")
            vision_cells = enemy.get_vision_cells(game_state.board)
            print(f"  視界セル: {[(cell.x, cell.y) for cell in vision_cells]}")
            can_see = enemy.can_see_player(game_state.player.position, game_state.board)
            print(f"  プレイヤー検出: {can_see}")

if __name__ == "__main__":
    analyze_enemy_vision()