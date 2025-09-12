"""
WaitCommandの単体テスト
"""

import pytest
from unittest.mock import Mock, MagicMock

from engine import GameState, Position, Direction, GameStatus
from engine.commands import WaitCommand, WaitResult, CommandResult
from engine import Character, Enemy, Item, Board, ItemType, EnemyType


@pytest.fixture
def basic_game_state():
    """基本的なゲーム状態"""
    board = Board(
        width=5,
        height=5,
        walls=[Position(2, 2)],
        forbidden_cells=[]
    )
    
    player = Character(
        position=Position(1, 1),
        direction=Direction.EAST,
        hp=100,
        attack_power=30
    )
    
    enemy = Enemy(
        position=Position(3, 1),
        direction=Direction.WEST,
        hp=50,
        attack_power=20,
        enemy_type=EnemyType.NORMAL
    )
    
    return GameState(
        player=player,
        enemies=[enemy],
        items=[],
        board=board,
        turn_count=0,
        max_turns=50,
        status=GameStatus.PLAYING,
        goal_position=Position(4, 4)
    )


@pytest.fixture
def adjacent_enemy_game_state():
    """隣接敵がいるゲーム状態"""
    board = Board(
        width=5,
        height=5,
        walls=[],
        forbidden_cells=[]
    )
    
    player = Character(
        position=Position(2, 2),
        direction=Direction.EAST,
        hp=80,
        attack_power=30
    )
    
    # 隣接位置の敵（距離1）
    adjacent_enemy = Enemy(
        position=Position(3, 2),
        direction=Direction.WEST,
        hp=40,
        attack_power=25,
        enemy_type=EnemyType.GOBLIN
    )
    
    return GameState(
        player=player,
        enemies=[adjacent_enemy],
        items=[],
        board=board,
        turn_count=5,
        max_turns=50,
        status=GameStatus.PLAYING,
        goal_position=Position(4, 4)
    )


class TestWaitCommand:
    """WaitCommandのテストクラス"""
    
    def test_wait_command_basic_execution(self, basic_game_state):
        """基本的な待機コマンド実行テスト"""
        command = WaitCommand()
        
        # 実行前の状態確認
        assert not command.executed
        assert command.result is None
        
        # コマンド実行
        result = command.execute(basic_game_state)
        
        # 実行結果検証
        assert isinstance(result, WaitResult)
        assert result.result == CommandResult.SUCCESS
        assert "1ターン待機しました" in result.message
        assert command.executed
        assert command.result == result
    
    def test_wait_with_adjacent_enemy(self, adjacent_enemy_game_state):
        """隣接敵処理テスト"""
        command = WaitCommand()
        player = adjacent_enemy_game_state.player
        enemy = adjacent_enemy_game_state.enemies[0]
        
        # 実行前のHP記録
        player_hp_before = player.hp
        
        # コマンド実行
        result = command.execute(adjacent_enemy_game_state)
        
        # 結果検証
        assert result.result == CommandResult.SUCCESS
        assert result.enemy_actions_triggered >= 1
        assert "敵から" in result.message
        
        # プレイヤーがダメージを受けたことを確認
        assert player.hp < player_hp_before
        
        # 敵がプレイヤーの方向を向いていることを確認
        assert enemy.direction == Direction.WEST
    
    def test_wait_with_distant_enemy(self, basic_game_state):
        """遠距離敵処理テスト"""
        command = WaitCommand()
        player = basic_game_state.player
        enemy = basic_game_state.enemies[0]
        
        # 敵を遠い位置に配置
        enemy.position = Position(4, 3)  # 距離2以上
        
        # 実行前のHP記録
        player_hp_before = player.hp
        enemy_pos_before = enemy.position
        
        # コマンド実行
        result = command.execute(basic_game_state)
        
        # 結果検証
        assert result.result == CommandResult.SUCCESS
        assert result.enemy_actions_triggered >= 0
        
        # プレイヤーはダメージを受けていない（敵が遠いため）
        assert player.hp == player_hp_before
        
        # 敵が移動している可能性を確認（プレイヤーに近づく）
        distance_before = abs(enemy_pos_before.x - player.position.x) + abs(enemy_pos_before.y - player.position.y)
        distance_after = abs(enemy.position.x - player.position.x) + abs(enemy.position.y - player.position.y)
        assert distance_after <= distance_before
    
    def test_wait_enemy_ai_response(self, basic_game_state):
        """敵AI応答確認テスト"""
        command = WaitCommand()
        enemy = basic_game_state.enemies[0]
        
        # 敵を隣接位置に配置
        enemy.position = Position(2, 1)  # プレイヤー[1,1]から距離1
        
        # コマンド実行
        result = command.execute(basic_game_state)
        
        # 結果検証
        assert result.result == CommandResult.SUCCESS
        assert result.enemy_actions_triggered > 0
        
        # 敵がプレイヤー方向を向いている
        expected_direction = Direction.WEST  # 敵[2,1]からプレイヤー[1,1]への方向
        assert enemy.direction == expected_direction
    
    def test_wait_multiple_enemies(self):
        """複数敵処理テスト"""
        board = Board(width=7, height=7, walls=[], forbidden_cells=[])
        
        player = Character(
            position=Position(3, 3),
            direction=Direction.NORTH,
            hp=100,
            attack_power=30
        )
        
        # 複数の敵を配置
        enemies = [
            Enemy(
                position=Position(4, 3),  # 隣接敵1
                direction=Direction.WEST,
                hp=30,
                attack_power=15,
                enemy_type=EnemyType.GOBLIN
            ),
            Enemy(
                position=Position(3, 4),  # 隣接敵2
                direction=Direction.NORTH,
                hp=40,
                attack_power=20,
                enemy_type=EnemyType.ORC
            ),
            Enemy(
                position=Position(6, 6),  # 遠い敵
                direction=Direction.SOUTH,
                hp=50,
                attack_power=25,
                enemy_type=EnemyType.NORMAL
            )
        ]
        
        game_state = GameState(
            player=player,
            enemies=enemies,
            items=[],
            board=board,
            turn_count=10,
            max_turns=100,
            status=GameStatus.PLAYING,
            goal_position=Position(6, 6)
        )
        
        command = WaitCommand()
        player_hp_before = player.hp
        
        # コマンド実行
        result = command.execute(game_state)
        
        # 結果検証
        assert result.result == CommandResult.SUCCESS
        assert result.enemy_actions_triggered >= 2  # 隣接敵2体が行動
        
        # プレイヤーが複数回攻撃を受けた
        assert player.hp < player_hp_before
    
    def test_wait_error_handling(self):
        """エラーケーステスト"""
        command = WaitCommand()
        
        # 無効なゲーム状態でのテスト（Noneではなく、壊れた状態）
        board = Board(width=3, height=3, walls=[], forbidden_cells=[])
        
        player = Character(
            position=Position(1, 1),
            direction=Direction.EAST,
            hp=0,  # HP0のプレイヤー（異常状態）
            attack_power=30
        )
        
        game_state = GameState(
            player=player,
            enemies=[],
            items=[],
            board=board,
            turn_count=0,
            max_turns=50,
            status=GameStatus.FAILED,  # 既に失敗状態
            goal_position=Position(2, 2)
        )
        
        # コマンド実行（異常状態でも動作すること）
        result = command.execute(game_state)
        
        # 結果検証（成功するが、メッセージが適切）
        assert result.result == CommandResult.SUCCESS
        assert "1ターン待機しました" in result.message
    
    def test_wait_command_undo_behavior(self, basic_game_state):
        """取り消し動作テスト"""
        command = WaitCommand()
        
        # 実行
        command.execute(basic_game_state)
        
        # 取り消しテスト
        assert not command.can_undo()
        assert not command.undo(basic_game_state)
    
    def test_wait_command_description(self):
        """説明文テスト"""
        command = WaitCommand()
        description = command.get_description()
        
        assert description == "1ターン待機"
        assert isinstance(description, str)
        assert len(description) > 0


@pytest.mark.integration
class TestWaitCommandIntegration:
    """WaitCommandの統合テスト"""
    
    def test_wait_integration_with_game_flow(self):
        """ゲームフロー統合テスト"""
        # より複雑なシナリオでの統合テスト
        board = Board(width=8, height=8, walls=[Position(4, 4)], forbidden_cells=[])
        
        player = Character(
            position=Position(2, 2),
            direction=Direction.EAST,
            hp=120,
            attack_power=35
        )
        
        enemy = Enemy(
            position=Position(5, 5),
            direction=Direction.WEST,
            hp=60,
            attack_power=30,
            enemy_type=EnemyType.ORC
        )
        
        game_state = GameState(
            player=player,
            enemies=[enemy],
            items=[],
            board=board,
            turn_count=0,
            max_turns=100,
            status=GameStatus.PLAYING,
            goal_position=Position(7, 7)
        )
        
        command = WaitCommand()
        
        # 複数回実行してゲーム状態の変化を確認
        for i in range(3):
            result = command.execute(game_state)
            assert result.result == CommandResult.SUCCESS
            
            # ターン数は変化しないが、敵の位置は変化する可能性
            if result.enemy_actions_triggered > 0:
                # 敵が何らかの行動をとった
                assert len(game_state.enemies) == 1
                assert game_state.enemies[0].is_alive()