#!/usr/bin/env python3
"""
コアデータモデルのテスト
"""

import pytest
from datetime import datetime
from engine import (
    Direction, GameStatus, ItemType, EnemyType,
    Position, Character, Enemy, Item, Board,
    GameState, Stage, LogEntry
)

class TestDirection:
    """Direction enumのテスト"""
    
    def test_turn_left(self):
        """左回転テスト"""
        assert Direction.NORTH.turn_left() == Direction.WEST
        assert Direction.WEST.turn_left() == Direction.SOUTH
        assert Direction.SOUTH.turn_left() == Direction.EAST
        assert Direction.EAST.turn_left() == Direction.NORTH
    
    def test_turn_right(self):
        """右回転テスト"""
        assert Direction.NORTH.turn_right() == Direction.EAST
        assert Direction.EAST.turn_right() == Direction.SOUTH
        assert Direction.SOUTH.turn_right() == Direction.WEST
        assert Direction.WEST.turn_right() == Direction.NORTH
    
    def test_get_offset(self):
        """座標オフセット取得テスト"""
        assert Direction.NORTH.get_offset() == (0, -1)
        assert Direction.EAST.get_offset() == (1, 0)
        assert Direction.SOUTH.get_offset() == (0, 1)
        assert Direction.WEST.get_offset() == (-1, 0)

class TestPosition:
    """Position クラスのテスト"""
    
    def test_creation(self):
        """作成テスト"""
        pos = Position(3, 5)
        assert pos.x == 3
        assert pos.y == 5
    
    def test_validation(self):
        """バリデーションテスト"""
        with pytest.raises(ValueError):
            Position("3", 5)  # 文字列は無効
    
    def test_move(self):
        """移動テスト"""
        pos = Position(5, 5)
        
        # 上に移動
        new_pos = pos.move(Direction.NORTH)
        assert new_pos == Position(5, 4)
        
        # 右に移動
        new_pos = pos.move(Direction.EAST)
        assert new_pos == Position(6, 5)
        
        # 元の座標は変更されない（immutable）
        assert pos == Position(5, 5)
    
    def test_distance(self):
        """距離計算テスト"""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        assert pos1.distance_to(pos2) == 5.0  # 3-4-5三角形

class TestCharacter:
    """Character クラスのテスト"""
    
    def test_creation(self):
        """作成テスト"""
        char = Character(
            position=Position(1, 1),
            direction=Direction.NORTH,
            hp=100,
            attack_power=10
        )
        assert char.hp == 100
        assert char.is_alive()
    
    def test_damage(self):
        """ダメージテスト"""
        char = Character(Position(0, 0), Direction.NORTH, hp=100)
        
        # ダメージを受ける
        damage_taken = char.take_damage(30)
        assert damage_taken == 30
        assert char.hp == 70
        assert char.is_alive()
        
        # 致命的ダメージ
        damage_taken = char.take_damage(100)
        assert damage_taken == 70  # 実際に受けたのは残りHP
        assert char.hp == 0
        assert not char.is_alive()
    
    def test_heal(self):
        """回復テスト"""
        char = Character(Position(0, 0), Direction.NORTH, hp=50, max_hp=100)
        
        healed = char.heal(30)
        assert healed == 30
        assert char.hp == 80
        
        # 最大HPを超えて回復しない
        healed = char.heal(50)
        assert healed == 20
        assert char.hp == 100

class TestEnemy:
    """Enemy クラスのテスト"""
    
    def test_size(self):
        """サイズテスト"""
        # 通常敵
        enemy = Enemy(Position(0, 0), Direction.NORTH)
        assert enemy.get_size() == (1, 1)
        
        # 大型敵
        large_enemy = Enemy(
            Position(0, 0), 
            Direction.NORTH, 
            enemy_type=EnemyType.LARGE_2X2
        )
        assert large_enemy.get_size() == (2, 2)
    
    def test_occupied_positions(self):
        """占有座標テスト"""
        enemy = Enemy(
            Position(1, 1), 
            Direction.NORTH, 
            enemy_type=EnemyType.LARGE_2X2
        )
        positions = enemy.get_occupied_positions()
        expected = [
            Position(1, 1), Position(2, 1),
            Position(1, 2), Position(2, 2)
        ]
        assert positions == expected

class TestBoard:
    """Board クラスのテスト"""
    
    def test_creation(self):
        """作成テスト"""
        board = Board(
            width=5, 
            height=5, 
            walls=[Position(2, 2)], 
            forbidden_cells=[]
        )
        assert board.width == 5
        assert board.height == 5
    
    def test_position_checks(self):
        """座標チェックテスト"""
        board = Board(
            width=3, 
            height=3, 
            walls=[Position(1, 1)], 
            forbidden_cells=[Position(2, 2)]
        )
        
        # 有効座標
        assert board.is_valid_position(Position(0, 0))
        assert board.is_valid_position(Position(2, 2))
        assert not board.is_valid_position(Position(3, 3))  # 範囲外
        
        # 壁
        assert board.is_wall(Position(1, 1))
        assert not board.is_wall(Position(0, 0))
        
        # 移動不可マス
        assert board.is_forbidden(Position(2, 2))
        assert not board.is_forbidden(Position(0, 0))
        
        # 通行可能性
        assert board.is_passable(Position(0, 0))
        assert not board.is_passable(Position(1, 1))  # 壁
        assert not board.is_passable(Position(2, 2))  # 移動不可
        assert not board.is_passable(Position(3, 3))  # 範囲外

class TestGameState:
    """GameState クラスのテスト"""
    
    def test_creation(self):
        """作成テスト"""
        player = Character(Position(0, 0), Direction.NORTH)
        board = Board(5, 5, [], [])
        
        state = GameState(
            player=player,
            enemies=[],
            items=[],
            board=board,
            goal_position=Position(4, 4)
        )
        
        assert state.turn_count == 0
        assert state.status == GameStatus.PLAYING
        assert not state.is_game_over()
    
    def test_turn_increment(self):
        """ターン増加テスト"""
        player = Character(Position(0, 0), Direction.NORTH)
        board = Board(5, 5, [], [])
        
        state = GameState(
            player=player,
            enemies=[],
            items=[],
            board=board,
            max_turns=2
        )
        
        state.increment_turn()
        assert state.turn_count == 1
        assert state.status == GameStatus.PLAYING
        
        state.increment_turn()
        assert state.turn_count == 2
        assert state.status == GameStatus.TIMEOUT
        assert state.is_game_over()
    
    def test_goal_check(self):
        """ゴール判定テスト"""
        player = Character(Position(0, 0), Direction.NORTH)
        board = Board(5, 5, [], [])
        
        state = GameState(
            player=player,
            enemies=[],
            items=[],
            board=board,
            goal_position=Position(0, 0)
        )
        
        assert state.check_goal_reached()

def test_data_model_integration():
    """データモデル統合テスト"""
    # 実際のゲーム状況をシミュレート
    player = Character(Position(1, 1), Direction.EAST, hp=100)
    enemy = Enemy(Position(3, 3), Direction.WEST, hp=50)
    item = Item(
        Position(2, 2), 
        ItemType.WEAPON, 
        "剣", 
        {"attack": 5}
    )
    
    board = Board(
        width=5,
        height=5,
        walls=[Position(0, 2), Position(4, 2)],
        forbidden_cells=[]
    )
    
    state = GameState(
        player=player,
        enemies=[enemy],
        items=[item],
        board=board,
        goal_position=Position(4, 4)
    )
    
    # プレイヤーが右に移動
    player.position = player.position.move(Direction.EAST)
    assert player.position == Position(2, 1)
    
    # アイテムチェック
    item_at_pos = state.get_item_at(Position(2, 2))
    assert item_at_pos == item
    
    # 敵チェック
    enemy_at_pos = state.get_enemy_at(Position(3, 3))
    assert enemy_at_pos == enemy
    
    print("✅ すべてのデータモデルテストが完了しました")

if __name__ == "__main__":
    test_data_model_integration()