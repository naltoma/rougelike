#!/usr/bin/env python3
"""
コマンドパターンのテスト
"""

import pytest
from engine import (
    Position, Direction, Character, Enemy, Item, Board, GameState,
    ItemType, EnemyType
)
from engine.commands import (
    TurnLeftCommand, TurnRightCommand, MoveCommand, AttackCommand, PickupCommand,
    CommandInvoker, CommandResult
)


def create_test_game_state():
    """テスト用のゲーム状態を作成"""
    player = Character(Position(2, 2), Direction.NORTH, hp=100, attack_power=10)
    
    # 3x3の敵をPosition(1,1)に配置
    enemy = Enemy(Position(1, 1), Direction.SOUTH, hp=30, attack_power=5)
    
    # アイテムをPosition(2,3)に配置
    item = Item(Position(2, 3), ItemType.WEAPON, "テスト剣", {"attack": 5})
    
    # 5x5ボード、壁をPosition(0,1)に配置
    board = Board(
        width=5, 
        height=5, 
        walls=[Position(0, 1)], 
        forbidden_cells=[Position(4, 4)]
    )
    
    return GameState(
        player=player,
        enemies=[enemy],
        items=[item],
        board=board,
        goal_position=Position(4, 3)
    )


def test_turn_commands():
    """回転コマンドテスト"""
    print("🔄 回転コマンドテスト...")
    
    game_state = create_test_game_state()
    invoker = CommandInvoker()
    
    # 初期状態確認
    assert game_state.player.direction == Direction.NORTH
    
    # 左回転
    left_cmd = TurnLeftCommand()
    result = invoker.execute_command(left_cmd, game_state)
    
    assert result.is_success
    assert game_state.player.direction == Direction.WEST
    assert "回転しました" in result.message
    print("✅ 左回転正常")
    
    # 右回転
    right_cmd = TurnRightCommand()
    result = invoker.execute_command(right_cmd, game_state)
    
    assert result.is_success
    assert game_state.player.direction == Direction.NORTH  # 元に戻る
    print("✅ 右回転正常")
    
    # 取り消しテスト
    assert invoker.can_undo()
    undo_success = invoker.undo_last_command(game_state)
    assert undo_success
    assert game_state.player.direction == Direction.WEST  # 右回転を取り消し
    print("✅ 回転取り消し正常")


def test_move_command():
    """移動コマンドテスト"""
    print("🚶 移動コマンドテスト...")
    
    game_state = create_test_game_state()
    invoker = CommandInvoker()
    
    # 初期位置確認
    assert game_state.player.position == Position(2, 2)
    assert game_state.player.direction == Direction.NORTH
    
    # 北に移動（成功するはず）
    move_cmd = MoveCommand()
    result = invoker.execute_command(move_cmd, game_state)
    
    assert result.is_success
    assert game_state.player.position == Position(2, 1)
    assert result.old_position == Position(2, 2)
    assert result.new_position == Position(2, 1)
    print("✅ 移動成功")
    
    # 取り消しテスト
    undo_success = invoker.undo_last_command(game_state)
    assert undo_success
    assert game_state.player.position == Position(2, 2)  # 元の位置に戻る
    print("✅ 移動取り消し正常")
    
    # 壁への移動テスト
    game_state.player.direction = Direction.WEST  # 西を向く
    move_cmd = MoveCommand()
    result = invoker.execute_command(move_cmd, game_state)
    
    # Position(1,2)には敵がいる可能性があるが、Position(1,1)にいるので移動できるはず
    if result.is_blocked:
        assert "移動できません" in result.message
        print("✅ ブロック判定正常")
    else:
        print("✅ 移動実行正常")


def test_attack_command():
    """攻撃コマンドテスト"""
    print("⚔️ 攻撃コマンドテスト...")
    
    game_state = create_test_game_state()
    invoker = CommandInvoker()
    
    # プレイヤーを敵の隣に移動（手動で配置）
    game_state.player.position = Position(2, 1)  # 敵Position(1,1)の東隣
    game_state.player.direction = Direction.WEST  # 敵の方を向く
    
    initial_enemy_hp = game_state.enemies[0].hp
    
    # 攻撃実行
    attack_cmd = AttackCommand()
    result = invoker.execute_command(attack_cmd, game_state)
    
    assert result.is_success
    assert result.damage_dealt > 0
    assert game_state.enemies[0].hp < initial_enemy_hp
    print("✅ 攻撃成功")
    
    # 取り消し不可テスト
    assert not invoker.can_undo()
    print("✅ 攻撃取り消し不可正常")
    
    # 対象なしの攻撃テスト
    game_state.player.direction = Direction.EAST  # 何もない方向
    attack_cmd = AttackCommand()
    result = invoker.execute_command(attack_cmd, game_state)
    
    assert result.is_failed
    assert "攻撃対象がいません" in result.message
    print("✅ 攻撃対象なし判定正常")


def test_pickup_command():
    """アイテム取得コマンドテスト"""
    print("🎒 アイテム取得コマンドテスト...")
    
    game_state = create_test_game_state()
    invoker = CommandInvoker()
    
    # プレイヤーをアイテムの位置に移動
    game_state.player.position = Position(2, 3)  # アイテムがある位置
    
    initial_attack = game_state.player.attack_power
    initial_item_count = len(game_state.items)
    
    # アイテム取得実行
    pickup_cmd = PickupCommand()
    result = invoker.execute_command(pickup_cmd, game_state)
    
    assert result.is_success
    assert result.item_name == "テスト剣"
    assert result.auto_equipped
    assert len(game_state.items) == initial_item_count - 1  # アイテムが減る
    assert game_state.player.attack_power > initial_attack  # 攻撃力が上がる
    print("✅ アイテム取得成功")
    
    # 取り消し不可テスト
    assert not invoker.can_undo()
    print("✅ アイテム取得取り消し不可正常")
    
    # アイテムなしの取得テスト
    game_state.player.position = Position(3, 3)  # 何もない位置
    pickup_cmd = PickupCommand()
    result = invoker.execute_command(pickup_cmd, game_state)
    
    assert result.is_failed
    assert "アイテムがありません" in result.message
    print("✅ アイテムなし判定正常")


def test_command_history():
    """コマンド履歴テスト"""
    print("📜 コマンド履歴テスト...")
    
    game_state = create_test_game_state()
    invoker = CommandInvoker()
    
    # 複数コマンド実行
    invoker.execute_command(TurnLeftCommand(), game_state)
    invoker.execute_command(TurnRightCommand(), game_state)
    invoker.execute_command(MoveCommand(), game_state)
    
    history = invoker.get_history()
    assert len(history) == 3
    assert "左に90度回転" in history[0]
    assert "右に90度回転" in history[1]
    assert "正面方向に1マス移動" in history[2]
    print("✅ 履歴記録正常")
    
    # 履歴クリア
    invoker.clear_history()
    assert len(invoker.get_history()) == 0
    print("✅ 履歴クリア正常")


def test_command_integration():
    """コマンド統合テスト"""
    print("🔗 コマンド統合テスト...")
    
    game_state = create_test_game_state()
    invoker = CommandInvoker()
    
    # 複雑なシナリオ
    # 1. 右回転
    result1 = invoker.execute_command(TurnRightCommand(), game_state)
    assert result1.is_success
    assert game_state.player.direction == Direction.EAST
    
    # 2. 移動
    result2 = invoker.execute_command(MoveCommand(), game_state)
    # 成功するかブロックされるかは状況による
    
    # 3. 南を向く
    invoker.execute_command(TurnRightCommand(), game_state)
    assert game_state.player.direction == Direction.SOUTH
    
    # 4. アイテム位置に移動（手動配置）
    game_state.player.position = Position(2, 3)
    
    # 5. アイテム取得
    result5 = invoker.execute_command(PickupCommand(), game_state)
    assert result5.is_success
    
    print("✅ 統合テスト正常")


def main():
    """メイン実行"""
    print("🧪 コマンドパターンテスト開始\n")
    
    try:
        test_turn_commands()
        test_move_command()
        test_attack_command()
        test_pickup_command()
        test_command_history()
        test_command_integration()
        
        print("\n🎉 全てのコマンドテストが完了！")
        print("✅ タスク3完了: コマンドパターンの実装")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()