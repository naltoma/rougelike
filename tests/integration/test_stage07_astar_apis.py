#!/usr/bin/env python3
"""
Test A* allowed_apis constraints in stage07
"""

import sys
import os
# プロジェクトルートをsys.pathに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.stage_generator.data_models import StageConfiguration
from src.stage_validator.pathfinding import StagePathfinder, GameState, EnemyState
import yaml

def test_stage07_api_constraints():
    print("Stage07 A* API制約テスト")
    print("=" * 50)

    # Stage07読み込み
    stage_path = os.path.join(project_root, 'stages', 'stage07.yml')
    with open(stage_path, 'r', encoding='utf-8') as f:
        stage_data = yaml.safe_load(f)

    stage_config = StageConfiguration.from_dict(stage_data)
    pathfinder = StagePathfinder(stage_config)

    print(f"allowed_apis: {stage_config.constraints.allowed_apis}")
    print(f"is_available含まれる: {'is_available' in stage_config.constraints.allowed_apis}")
    print(f"dispose含まれる: {'dispose' in stage_config.constraints.allowed_apis}")

    # 初期状態作成
    initial_state = GameState(
        player_pos=tuple(stage_config.player.start),
        player_dir=stage_config.player.direction,
        player_hp=stage_config.player.hp,
        enemies={
            enemy.id: EnemyState(
                position=tuple(enemy.position),
                direction=enemy.direction,
                hp=enemy.hp,
                max_hp=enemy.max_hp,
                attack_power=enemy.attack_power,
                behavior=enemy.behavior,
                enemy_type=getattr(enemy, 'type', 'normal'),
                is_alive=True,
                patrol_path=None,
                patrol_index=0,
                vision_range=enemy.vision_range,
                is_alert=False,
                last_seen_player=None
            )
            for enemy in stage_config.enemies
        },
        collected_items=set(),
        turn_count=0
    )

    # アイテム位置（2,2）に移動した状態を作成
    item_position_state = GameState(
        player_pos=(2, 2),  # 武器位置
        player_dir="E",
        player_hp=100,
        enemies=initial_state.enemies.copy(),
        collected_items=set(),
        turn_count=2
    )

    print(f"\n初期状態での有効アクション:")
    valid_actions_initial = pathfinder._get_valid_actions(initial_state)
    print(f"   {[action.value for action in valid_actions_initial]}")

    print(f"\nアイテム位置(2,2)での有効アクション:")
    valid_actions_item = pathfinder._get_valid_actions(item_position_state)
    print(f"   {[action.value for action in valid_actions_item]}")

    # 不正なアクションがないかチェック
    allowed_action_strings = set(stage_config.constraints.allowed_apis)

    print(f"\n=== API制約違反チェック ===")
    for action in valid_actions_item:
        action_string = action.value
        if action_string not in allowed_action_strings:
            print(f"🚨 制約違反: {action_string} は allowed_apis に含まれていません！")
            print(f"   allowed_apis: {sorted(allowed_action_strings)}")
            print(f"   detected: {action_string}")
        else:
            print(f"✅ 正常: {action_string}")

    # A*探索実行
    print(f"\n=== A*探索実行 ===")
    pathfinder.max_nodes = 1000  # 制限設定
    solution = pathfinder.find_path()

    if solution:
        print(f"解法発見: {len(solution)}ステップ")
        action_summary = {}
        for action in solution:
            action_str = action.value
            action_summary[action_str] = action_summary.get(action_str, 0) + 1

        print(f"使用されたアクション:")
        for action_str, count in action_summary.items():
            violation = "" if action_str in allowed_action_strings else " 🚨 制約違反"
            print(f"   {action_str}: {count}回{violation}")

    else:
        print(f"解法未発見")

if __name__ == "__main__":
    test_stage07_api_constraints()