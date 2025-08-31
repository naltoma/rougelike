#!/usr/bin/env python3
"""
GameStateManagerのテスト
"""

import sys
sys.path.append('..')

from engine import (
    Position, Direction, Character, Enemy, Item, Board, GameState,
    ItemType, EnemyType, GameStatus
)
from engine.game_state import GameStateManager
from engine.commands import TurnLeftCommand, MoveCommand, AttackCommand


def create_test_board():
    """テスト用のボードを作成"""
    return Board(
        width=5,
        height=5,
        walls=[Position(2, 2), Position(3, 3)],
        forbidden_cells=[Position(4, 4)]
    )


def test_initialization():
    """初期化テスト"""
    print("🔧 GameStateManager初期化テスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    # 敵とアイテムを作成
    enemy = Enemy(Position(1, 1), Direction.SOUTH, hp=30)
    item = Item(Position(3, 1), ItemType.WEAPON, "テスト剣", {"attack": 5})
    
    # ゲーム初期化
    state = manager.initialize_game(
        player_start=Position(0, 0),
        player_direction=Direction.NORTH,
        board=board,
        enemies=[enemy],
        items=[item],
        goal_position=Position(4, 0),
        max_turns=50
    )
    
    assert state is not None
    assert state.player.position == Position(0, 0)
    assert state.player.direction == Direction.NORTH
    assert len(state.enemies) == 1
    assert len(state.items) == 1
    assert state.turn_count == 0
    assert state.max_turns == 50
    assert state.status == GameStatus.PLAYING
    assert not manager.is_game_finished()
    
    print("✅ 初期化正常")


def test_command_execution():
    """コマンド実行テスト"""
    print("⚡ コマンド実行テスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    state = manager.initialize_game(
        player_start=Position(0, 0),
        player_direction=Direction.NORTH,
        board=board,
        goal_position=Position(4, 4),  # ゴールを設定して勝利条件を明確にする
        max_turns=10
    )
    
    initial_turn = state.turn_count
    
    # 回転コマンド実行
    turn_cmd = TurnLeftCommand()
    result = manager.execute_command(turn_cmd)
    
    assert result.is_success
    assert state.player.direction == Direction.WEST
    assert state.turn_count == initial_turn + 1
    print("✅ 回転コマンド実行正常")
    
    # 移動コマンド実行（西に移動 - 境界外になる）
    move_cmd = MoveCommand()
    result = manager.execute_command(move_cmd)
    
    assert result.is_blocked  # 境界外なのでブロック
    assert state.player.position == Position(0, 0)  # 位置は変わらない
    print("✅ 移動ブロック判定正常")
    
    # 有効な移動（東を向いて移動）
    turn_right_cmd = TurnLeftCommand()  # 西→南
    manager.execute_command(turn_right_cmd)
    turn_right_cmd2 = TurnLeftCommand()  # 南→東
    manager.execute_command(turn_right_cmd2)
    
    assert state.player.direction == Direction.EAST
    
    move_cmd = MoveCommand()
    result = manager.execute_command(move_cmd)
    
    assert result.is_success
    assert state.player.position == Position(1, 0)
    print("✅ 移動成功正常")


def test_undo_functionality():
    """取り消し機能テスト"""
    print("↩️ 取り消し機能テスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    state = manager.initialize_game(
        player_start=Position(1, 1),
        player_direction=Direction.NORTH,
        board=board
    )
    
    initial_position = state.player.position
    initial_direction = state.player.direction
    initial_turn = state.turn_count
    
    # 回転実行
    turn_cmd = TurnLeftCommand()
    manager.execute_command(turn_cmd)
    
    assert state.player.direction == Direction.WEST
    assert state.turn_count == initial_turn + 1
    assert manager.can_undo_last_action()
    
    # 取り消し実行
    success = manager.undo_last_action()
    assert success
    assert state.player.direction == initial_direction
    assert state.turn_count == initial_turn  # ターン数も戻る
    
    print("✅ 取り消し正常")


def test_game_completion():
    """ゲーム完了テスト"""
    print("🏆 ゲーム完了テスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    # プレイヤーをゴールの隣に配置
    state = manager.initialize_game(
        player_start=Position(3, 0),
        player_direction=Direction.EAST,
        board=board,
        goal_position=Position(4, 0)
    )
    
    assert not manager.is_game_finished()
    assert manager.get_game_result() == GameStatus.PLAYING
    
    # ゴールに移動
    move_cmd = MoveCommand()
    result = manager.execute_command(move_cmd)
    
    assert result.is_success
    assert state.player.position == Position(4, 0)
    assert manager.is_game_finished()
    assert manager.get_game_result() == GameStatus.WON
    
    print("✅ 勝利判定正常")


def test_timeout():
    """タイムアウトテスト"""
    print("⏰ タイムアウトテスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    state = manager.initialize_game(
        player_start=Position(1, 1),
        player_direction=Direction.NORTH,
        board=board,
        goal_position=Position(4, 4),  # ゴールを設定
        max_turns=2
    )
    
    assert manager.get_remaining_turns() == 2
    
    # 1ターン実行
    turn_cmd = TurnLeftCommand()
    manager.execute_command(turn_cmd)
    
    assert state.turn_count == 1
    assert state.status == GameStatus.PLAYING
    assert manager.get_remaining_turns() == 1
    
    # 2ターン実行
    manager.execute_command(turn_cmd)
    
    assert state.turn_count == 2
    assert state.status == GameStatus.TIMEOUT
    assert manager.is_game_finished()
    assert manager.get_remaining_turns() == 0
    
    print("✅ タイムアウト判定正常")


def test_reset_functionality():
    """リセット機能テスト"""
    print("🔄 リセット機能テスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    enemy = Enemy(Position(2, 1), Direction.SOUTH, hp=30)
    
    state = manager.initialize_game(
        player_start=Position(0, 0),
        player_direction=Direction.NORTH,
        board=board,
        enemies=[enemy]
    )
    
    initial_position = state.player.position
    initial_hp = state.enemies[0].hp
    
    # 何らかの変更を加える
    turn_cmd = TurnLeftCommand()
    manager.execute_command(turn_cmd)
    
    # 敵にダメージを与える（位置を調整して攻撃）
    state.player.position = Position(1, 1)  # 敵の隣
    state.player.direction = Direction.EAST  # 敵の方向
    
    attack_cmd = AttackCommand()
    manager.execute_command(attack_cmd)
    
    assert state.enemies[0].hp < initial_hp
    assert state.turn_count > 0
    
    # リセット実行
    success = manager.reset_game()
    assert success
    
    state = manager.get_current_state()
    assert state.player.position == initial_position
    assert state.player.direction == Direction.NORTH
    assert state.enemies[0].hp == initial_hp
    assert state.turn_count == 0
    assert len(manager.get_action_history()) == 0
    
    print("✅ リセット正常")


def test_history_tracking():
    """履歴追跡テスト"""
    print("📖 履歴追跡テスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    manager.initialize_game(
        player_start=Position(1, 1),
        player_direction=Direction.NORTH,
        board=board,
        goal_position=Position(4, 4)
    )
    
    # 複数のコマンドを実行
    manager.execute_command(TurnLeftCommand())
    manager.execute_command(TurnLeftCommand())
    manager.execute_command(MoveCommand())
    
    history = manager.get_action_history()
    assert len(history) == 3
    assert "左に90度回転" in history[0]
    assert "左に90度回転" in history[1]
    assert "正面方向に1マス移動" in history[2]
    
    print("✅ 履歴追跡正常")


def test_integration():
    """統合テスト"""
    print("🔗 統合テスト...")
    
    manager = GameStateManager()
    board = create_test_board()
    
    enemy = Enemy(Position(2, 1), Direction.SOUTH, hp=20)
    item = Item(Position(1, 0), ItemType.WEAPON, "強化剣", {"attack": 10})
    
    state = manager.initialize_game(
        player_start=Position(0, 0),
        player_direction=Direction.EAST,
        board=board,
        enemies=[enemy],
        items=[item],
        goal_position=Position(4, 1),
        max_turns=20
    )
    
    # アイテム取得のためのシーケンス
    # 東に移動してアイテム位置へ
    result = manager.execute_command(MoveCommand())
    assert result.is_success
    assert state.player.position == Position(1, 0)
    
    # アイテムを取得（位置を合わせる）
    from engine.commands import PickupCommand
    pickup_cmd = PickupCommand()
    result = manager.execute_command(pickup_cmd)
    assert result.is_success
    assert len(state.items) == 0  # アイテムが取得された
    
    # 敵を攻撃するための位置に移動
    state.player.position = Position(1, 1)  # 手動で敵の隣に配置
    state.player.direction = Direction.EAST  # 敵の方向を向く
    
    initial_enemy_hp = state.enemies[0].hp
    result = manager.execute_command(AttackCommand())
    assert result.is_success
    
    # 敵が倒されたかどうかをチェック
    if len(state.enemies) > 0:
        assert state.enemies[0].hp < initial_enemy_hp
    else:
        print("敵が倒されました")
    
    print("✅ 統合テスト正常")


def main():
    """メイン実行"""
    print("🧪 GameStateManagerテスト開始\n")
    
    try:
        test_initialization()
        test_command_execution()
        test_undo_functionality()
        test_game_completion()
        test_timeout()
        test_reset_functionality()
        test_history_tracking()
        test_integration()
        
        print("\n🎉 全てのGameStateManagerテストが完了！")
        print("✅ タスク4完了: GameStateManagerの実装")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()