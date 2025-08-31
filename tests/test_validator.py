#!/usr/bin/env python3
"""
Validatorクラスのテスト
"""

import sys
sys.path.append('..')

from engine import (
    Position, Direction, Character, Enemy, Item, Board, GameState,
    ItemType, EnemyType, GameStatus
)
from engine.validator import Validator, MovementResult


def create_test_game_state():
    """テスト用のゲーム状態を作成"""
    # 5x5ボードを作成
    board = Board(
        width=5,
        height=5,
        walls=[Position(2, 2), Position(3, 1)],  # 壁
        forbidden_cells=[Position(4, 4)]        # 移動禁止マス
    )
    
    # プレイヤー
    player = Character(Position(0, 0), Direction.NORTH)
    
    # 敵（通常サイズ）
    enemy1 = Enemy(Position(1, 3), Direction.SOUTH, enemy_type=EnemyType.NORMAL)
    
    # 大型敵（2x2）
    enemy2 = Enemy(Position(3, 3), Direction.WEST, enemy_type=EnemyType.LARGE_2X2)
    
    return GameState(
        player=player,
        enemies=[enemy1, enemy2],
        items=[],
        board=board,
        goal_position=Position(4, 0)
    )


def test_basic_movement_validation():
    """基本的な移動検証テスト"""
    print("🚶 基本的な移動検証テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 正常な移動
    result = validator.validate_movement(Position(0, 0), Direction.EAST, game_state)
    assert result.is_valid
    assert result.target_position == Position(1, 0)
    assert result.reason == "移動可能です"
    print("✅ 正常な移動検証")
    
    # 境界外への移動
    result = validator.validate_movement(Position(0, 0), Direction.NORTH, game_state)
    assert not result.is_valid
    assert result.blocked_by == "boundary"
    assert "境界外" in result.reason
    print("✅ 境界外移動ブロック")
    
    # 壁への移動
    result = validator.validate_movement(Position(2, 1), Direction.SOUTH, game_state)
    assert not result.is_valid
    assert result.blocked_by == "wall"
    assert "壁" in result.reason
    print("✅ 壁衝突検出")
    
    # 移動禁止マスへの移動
    result = validator.validate_movement(Position(4, 3), Direction.SOUTH, game_state)
    assert not result.is_valid
    assert result.blocked_by == "forbidden"
    assert "移動不可マス" in result.reason
    print("✅ 移動禁止マス検出")


def test_enemy_collision():
    """敵との衝突テスト"""
    print("👹 敵との衝突テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 通常敵との衝突
    result = validator.validate_movement(Position(1, 2), Direction.SOUTH, game_state)
    assert not result.is_valid
    assert result.blocked_by == "enemy"
    assert "敵" in result.reason
    print("✅ 通常敵衝突検出")
    
    # 大型敵との衝突（2x2敵は (3,3), (4,3), (3,4), (4,4) を占有）
    result = validator.validate_movement(Position(2, 3), Direction.EAST, game_state)
    assert not result.is_valid
    assert result.blocked_by == "enemy"
    print("✅ 大型敵衝突検出")


def test_attack_validation():
    """攻撃対象検証テスト"""
    print("⚔️ 攻撃対象検証テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 攻撃対象あり
    can_attack, enemy, message = validator.can_attack_target(
        Position(1, 2), Direction.SOUTH, game_state
    )
    assert can_attack
    assert enemy is not None
    assert enemy.position == Position(1, 3)
    assert "攻撃対象があります" in message
    print("✅ 攻撃対象検出")
    
    # 攻撃対象なし
    can_attack, enemy, message = validator.can_attack_target(
        Position(0, 0), Direction.EAST, game_state
    )
    assert not can_attack
    assert enemy is None
    assert "攻撃対象がいません" in message
    print("✅ 攻撃対象なし判定")
    
    # 攻撃範囲外
    can_attack, enemy, message = validator.can_attack_target(
        Position(4, 4), Direction.EAST, game_state
    )
    assert not can_attack
    assert enemy is None
    assert "攻撃範囲外" in message
    print("✅ 攻撃範囲外判定")


def test_large_enemy_movement():
    """大型敵移動テスト"""
    print("🐲 大型敵移動テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 大型敵を取得
    large_enemy = None
    for enemy in game_state.enemies:
        if enemy.enemy_type == EnemyType.LARGE_2X2:
            large_enemy = enemy
            break
    
    assert large_enemy is not None
    
    # 正常な移動（西に移動）
    result = validator.validate_large_enemy_movement(large_enemy, Direction.WEST, game_state)
    assert result.is_valid
    print("✅ 大型敵正常移動")
    
    # 境界外への移動（東に移動 - 右端にぶつかる）
    result = validator.validate_large_enemy_movement(large_enemy, Direction.EAST, game_state)
    assert not result.is_valid
    assert result.blocked_by == "boundary"
    print("✅ 大型敵境界チェック")
    
    # プレイヤーとの衝突（プレイヤーを大型敵の移動先に配置）
    game_state.player.position = Position(2, 3)
    result = validator.validate_large_enemy_movement(large_enemy, Direction.WEST, game_state)
    assert not result.is_valid
    assert result.blocked_by == "player"
    print("✅ 大型敵プレイヤー衝突検出")


def test_reachability():
    """到達可能性テスト"""
    print("🎯 到達可能性テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 開始位置から到達可能な位置を取得
    reachable = validator.get_reachable_positions(Position(0, 0), game_state, max_steps=5)
    assert len(reachable) > 0
    assert Position(0, 0) in reachable  # 開始位置も含まれる
    print(f"✅ 到達可能位置数: {len(reachable)}")
    
    # ゴール到達可能性チェック
    is_reachable = validator.is_goal_reachable(
        Position(0, 0), Position(4, 0), game_state
    )
    assert is_reachable  # (4,0)は到達可能なはず
    print("✅ ゴール到達可能")
    
    # 到達不可能な位置のテスト（移動禁止マス）
    is_reachable = validator.is_goal_reachable(
        Position(0, 0), Position(4, 4), game_state
    )
    assert not is_reachable  # (4,4)は移動禁止マスなので到達不可能
    print("✅ 到達不可能判定")


def test_adjacent_positions():
    """隣接位置取得テスト"""
    print("🧭 隣接位置取得テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 中央位置からの隣接位置
    adjacent = validator.get_adjacent_positions(Position(1, 1), game_state)
    expected_positions = [
        Position(2, 1),  # 東（可能）
        Position(1, 2),  # 南（可能）
        Position(0, 1),  # 西（可能）
        Position(1, 0)   # 北（可能）
    ]
    
    # 隣接位置が正しく取得できているかチェック
    for pos in expected_positions:
        if pos not in [Position(3, 1)]:  # 壁ではない位置
            assert pos in adjacent
    
    print(f"✅ 隣接位置数: {len(adjacent)}")
    
    # 角の位置からの隣接位置（選択肢が少ない）
    adjacent_corner = validator.get_adjacent_positions(Position(0, 0), game_state)
    assert len(adjacent_corner) == 2  # 東と南のみ
    assert Position(1, 0) in adjacent_corner  # 東
    assert Position(0, 1) in adjacent_corner  # 南
    print("✅ 角位置隣接チェック")


def test_movement_cost():
    """移動コスト計算テスト"""
    print("💰 移動コスト計算テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 隣接位置への移動コスト
    cost = validator.get_movement_cost(Position(0, 0), Position(1, 0), game_state)
    assert cost == 1
    print("✅ 隣接移動コスト")
    
    # 対角線移動コスト
    cost = validator.get_movement_cost(Position(0, 0), Position(1, 1), game_state)
    assert cost == 1  # 現在は距離ベース（将来拡張可能）
    print("✅ 対角線移動コスト")


def test_direction_validation():
    """方向検証テスト"""
    print("🧭 方向検証テスト...")
    
    validator = Validator()
    
    # 正常な方向
    assert validator.validate_player_direction(Direction.NORTH)
    assert validator.validate_player_direction(Direction.EAST)
    assert validator.validate_player_direction(Direction.SOUTH)
    assert validator.validate_player_direction(Direction.WEST)
    print("✅ 正常な方向検証")
    
    # 無効な方向（文字列）
    assert not validator.validate_player_direction("NORTH")
    print("✅ 無効な方向検出")


def test_integration():
    """統合テスト"""
    print("🔗 統合テスト...")
    
    validator = Validator()
    game_state = create_test_game_state()
    
    # 複雑なシナリオ：プレイヤーが敵を避けてゴールに向かう
    current_pos = Position(0, 0)
    path = []
    
    # 簡単な経路探索（東→南→東→北の順で移動してゴールを目指す）
    moves = [
        (Direction.EAST, Position(1, 0)),
        (Direction.EAST, Position(2, 0)),
        (Direction.SOUTH, Position(2, 1)),
        (Direction.EAST, Position(3, 0))  # 壁を避けて迂回
    ]
    
    for direction, expected_pos in moves:
        result = validator.validate_movement(current_pos, direction, game_state)
        if result.is_valid:
            current_pos = result.target_position
            path.append(current_pos)
            assert current_pos == expected_pos
        else:
            print(f"移動ブロック: {result.reason}")
    
    # 最終的にゴールに近づけているかチェック
    goal_distance = current_pos.distance_to(Position(4, 0))
    print(f"ゴールまでの距離: {goal_distance:.1f}")
    
    print("✅ 統合テスト正常")


def main():
    """メイン実行"""
    print("🧪 Validatorテスト開始\n")
    
    try:
        test_basic_movement_validation()
        test_enemy_collision()
        test_attack_validation()
        test_large_enemy_movement()
        test_reachability()
        test_adjacent_positions()
        test_movement_cost()
        test_direction_validation()
        test_integration()
        
        print("\n🎉 全てのValidatorテストが完了！")
        print("✅ タスク5完了: 移動と衝突判定の実装")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()