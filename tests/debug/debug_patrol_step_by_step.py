#!/usr/bin/env python3
"""Step-by-step patrol behavior debug for A* vs actual game engine"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import yaml
from stage_generator.data_models import StageConfiguration, BoardConfiguration, PlayerConfiguration, GoalConfiguration, EnemyConfiguration, ConstraintConfiguration
from stage_validator.pathfinding import StagePathfinder, GameState, EnemyState, ActionType

def load_stage_444():
    """Load generated_patrol_444 stage configuration"""
    stage_file = Path("stages/generated_patrol_444.yml")
    with open(stage_file, 'r') as f:
        data = yaml.safe_load(f)

    board = BoardConfiguration(
        size=data['board']['size'],
        grid=data['board']['grid'],
        legend=data['board']['legend']
    )

    player = PlayerConfiguration(
        start=data['player']['start'],
        direction=data['player']['direction'],
        hp=data['player']['hp'],
        max_hp=data['player']['max_hp'],
        attack_power=data['player']['attack_power']
    )

    goal = GoalConfiguration(position=data['goal']['position'])

    enemies = []
    for enemy_data in data['enemies']:
        enemy = EnemyConfiguration(
            id=enemy_data['id'],
            type=enemy_data['type'],
            position=enemy_data['position'],
            direction=enemy_data['direction'],
            hp=enemy_data['hp'],
            max_hp=enemy_data['max_hp'],
            attack_power=enemy_data['attack_power'],
            behavior=enemy_data['behavior'],
            patrol_path=enemy_data.get('patrol_path', []),
            vision_range=enemy_data.get('vision_range', 2)
        )
        enemies.append(enemy)

    constraints = ConstraintConfiguration(
        max_turns=data['constraints']['max_turns'],
        allowed_apis=data['constraints']['allowed_apis']
    )

    return StageConfiguration(
        id=data['id'],
        title=data['title'],
        description=data['description'],
        board=board,
        player=player,
        goal=goal,
        enemies=enemies,
        items=[],
        constraints=constraints,
        victory_conditions=data['victory_conditions']
    )

def debug_step_by_step_patrol():
    """Debug A* patrol behavior step by step"""
    print("=== STEP-BY-STEP PATROL DEBUG ===\n")

    stage = load_stage_444()
    pathfinder = StagePathfinder(stage)
    patrol_enemy = stage.enemies[0]  # patrol_guard

    print(f"Patrol path: {[tuple(pos) for pos in patrol_enemy.patrol_path]}")
    print(f"Initial enemy position: {patrol_enemy.position}")
    print()

    # Expected actual game engine states from manual execution
    actual_states = [
        (0, (3, 5), "W", 3),  # Step, position, direction, expected_patrol_index
        (1, (2, 5), "W", 4),
        (2, (1, 5), "W", 5),
        (3, (1, 4), "N", 6),
        (4, (1, 3), "N", 7),
        (5, (2, 3), "E", 0),
        (6, (3, 3), "E", 1),
        (7, (3, 4), "S", 2),
        (8, (3, 5), "S", 3),
        (9, (3, 3), "S", 0),  # KEY: This is where combat occurs
    ]

    # Manual solution steps leading to step 9
    manual_steps = [
        ActionType.TURN_LEFT,  # 1
        ActionType.MOVE,       # 2
        ActionType.MOVE,       # 3
        ActionType.MOVE,       # 4
        ActionType.MOVE,       # 5
        ActionType.MOVE,       # 6
        ActionType.TURN_LEFT,  # 7
        ActionType.MOVE,       # 8
        ActionType.MOVE,       # 9
    ]

    # Create initial A* state
    current_state = GameState(
        player_pos=tuple(stage.player.start),
        player_dir=stage.player.direction,
        player_hp=stage.player.hp,
        enemies={
            patrol_enemy.id: EnemyState(
                position=tuple(patrol_enemy.position),
                direction=patrol_enemy.direction,
                hp=patrol_enemy.hp,
                max_hp=patrol_enemy.max_hp,
                attack_power=patrol_enemy.attack_power,
                behavior=patrol_enemy.behavior,
                is_alive=True,
                patrol_path=[tuple(pos) for pos in patrol_enemy.patrol_path],
                patrol_index=pathfinder._calculate_initial_patrol_index(patrol_enemy),
                vision_range=patrol_enemy.vision_range,
                is_alert=False,
                last_seen_player=None
            )
        },
        collected_items=set(),
        turn_count=0
    )

    print(f"A* Initial patrol index: {current_state.enemies['patrol_guard'].patrol_index}")
    print()

    # Execute steps and compare with actual game engine
    for step_num, action in enumerate(manual_steps):
        print(f"=== STEP {step_num + 1}: {action.value} ===")

        # Apply action to A*
        new_state = pathfinder._apply_action(current_state, action)
        if new_state is None:
            print(f"A* action failed at step {step_num + 1}")
            break

        enemy_state = new_state.enemies['patrol_guard']
        actual_step, actual_pos, actual_dir, expected_index = actual_states[step_num + 1]

        print(f"Expected (actual game):  pos={actual_pos}, dir={actual_dir}, index={expected_index}")
        print(f"A* simulation result:   pos={enemy_state.position}, dir={enemy_state.direction}, index={enemy_state.patrol_index}")

        if enemy_state.position != actual_pos:
            print(f"❌ POSITION MISMATCH at step {step_num + 1}")
        if enemy_state.direction != actual_dir:
            print(f"❌ DIRECTION MISMATCH at step {step_num + 1}")

        print()
        current_state = new_state

    print("=== FINAL COMPARISON ===")
    final_enemy = current_state.enemies['patrol_guard']
    print(f"A* final state: pos={final_enemy.position}, dir={final_enemy.direction}")
    print(f"Expected combat state: pos=(3,3), dir=S")
    print(f"Combat possible: {final_enemy.position == (3, 3) and final_enemy.direction == 'S'}")

if __name__ == "__main__":
    debug_step_by_step_patrol()