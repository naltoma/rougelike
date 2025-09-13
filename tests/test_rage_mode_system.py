#!/usr/bin/env python3
"""
v1.2.8 怒りモード状態遷移システムの単体テスト
Task 4: 怒りモード状態管理・遷移テスト
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import Enemy, EnemyType, EnemyMode, Position, Direction, RageState
from engine.enemy_system import LargeEnemySystem, RageModeController

class TestRageModeSystem:
    """怒りモード状態遷移システムテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.system = LargeEnemySystem()
        self.enemy_2x2 = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        self.enemy_3x3 = Enemy(
            position=Position(5, 5),
            direction=Direction.NORTH,
            hp=150,
            max_hp=150,
            attack_power=30,
            enemy_type=EnemyType.LARGE_3X3
        )
    
    def test_large_enemy_initialization(self):
        """大型敵初期化テスト"""
        self.system.initialize_large_enemy(self.enemy_2x2, "enemy1")
        
        # 大型敵登録確認
        assert "enemy1" in self.system.large_enemies
        assert self.system.large_enemies["enemy1"] is self.enemy_2x2
        
        # 怒りモード状態初期化確認
        assert self.enemy_2x2.enemy_mode == EnemyMode.CALM
        assert self.enemy_2x2.rage_state is not None
        assert self.enemy_2x2.rage_state.is_active is False
        
        # 制御器作成確認
        assert "enemy1" in self.system.rage_controllers
    
    def test_hp_threshold_rage_trigger(self):
        """HP50%以下での怒りモード発動テスト"""
        self.system.initialize_large_enemy(self.enemy_2x2, "enemy1")
        
        # HP51%では怒りモード発動しない
        self.system.update_rage_state("enemy1", 51)
        assert self.enemy_2x2.enemy_mode == EnemyMode.CALM
        assert self.enemy_2x2.rage_state.is_active is False
        
        # HP50%で怒りモード発動
        self.system.update_rage_state("enemy1", 50)
        assert self.enemy_2x2.enemy_mode == EnemyMode.TRANSITIONING
        assert self.enemy_2x2.rage_state.is_active is True
        assert self.enemy_2x2.rage_state.transition_turn_count == 1
    
    def test_rage_mode_turn_progression(self):
        """怒りモードターン進行テスト"""
        self.system.initialize_large_enemy(self.enemy_2x2, "enemy1")
        
        # 怒りモード発動
        self.system.trigger_rage_mode("enemy1")
        assert self.enemy_2x2.enemy_mode == EnemyMode.TRANSITIONING
        
        # 1ターン経過で怒りモードに遷移
        self.system.update_rage_turn_for_enemy("enemy1")
        assert self.enemy_2x2.enemy_mode == EnemyMode.RAGE
        assert self.enemy_2x2.rage_state.turns_in_rage == 1
    
    def test_multiple_large_enemies(self):
        """複数大型敵の独立管理テスト"""
        self.system.initialize_large_enemy(self.enemy_2x2, "enemy1")
        self.system.initialize_large_enemy(self.enemy_3x3, "enemy2")
        
        # 異なる敵の独立した状態管理
        self.system.trigger_rage_mode("enemy1")
        assert self.enemy_2x2.enemy_mode == EnemyMode.TRANSITIONING
        assert self.enemy_3x3.enemy_mode == EnemyMode.CALM
        
        # 敵2も怒りモード発動
        self.system.trigger_rage_mode("enemy2")
        assert self.enemy_3x3.enemy_mode == EnemyMode.TRANSITIONING
        
        # 独立したモード取得
        assert self.system.get_enemy_mode("enemy1") == "transitioning"
        assert self.system.get_enemy_mode("enemy2") == "transitioning"
    
    def test_rage_mode_reset(self):
        """怒りモードリセットテスト"""
        self.system.initialize_large_enemy(self.enemy_2x2, "enemy1")
        
        # 怒りモード発動
        self.system.trigger_rage_mode("enemy1")
        assert self.enemy_2x2.rage_state.is_active is True
        
        # 平常モード復帰
        self.system.reset_to_calm_mode("enemy1")
        assert self.enemy_2x2.enemy_mode == EnemyMode.CALM
        assert self.enemy_2x2.rage_state.is_active is False
        assert self.enemy_2x2.rage_state.turns_in_rage == 0
        assert self.enemy_2x2.rage_state.area_attack_executed is False

class TestRageModeController:
    """怒りモード制御器の詳細テスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.system = LargeEnemySystem()
        self.enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        self.system.initialize_large_enemy(self.enemy, "test_enemy")
        self.controller = self.system.rage_controllers["test_enemy"]
    
    def test_transitioning_to_rage(self):
        """TRANSITIONING → RAGE 状態遷移テスト"""
        # 手動で状態遷移モードに設定
        self.enemy.enemy_mode = EnemyMode.TRANSITIONING
        self.enemy.rage_state.transition_turn_count = 1
        
        # 1ターン進行で怒りモードに遷移
        self.controller.update_rage_turn()
        assert self.enemy.enemy_mode == EnemyMode.RAGE
        assert self.enemy.rage_state.transition_turn_count == 0
    
    def test_rage_turn_counting(self):
        """怒りモード中のターン数カウントテスト"""
        # 手動で怒りモードに設定
        self.enemy.enemy_mode = EnemyMode.RAGE
        self.enemy.rage_state.turns_in_rage = 0
        
        # 複数ターン進行
        for expected_turns in range(1, 5):
            self.controller.update_rage_turn()
            assert self.enemy.rage_state.turns_in_rage == expected_turns
    
    def test_enemy_id_lookup(self):
        """敵ID逆引きテスト"""
        enemy_id = self.controller._get_enemy_id()
        assert enemy_id == "test_enemy"
        
        # 存在しない敵の場合
        orphan_enemy = Enemy(
            position=Position(10, 10),
            direction=Direction.SOUTH,
            hp=50,
            max_hp=50,
            attack_power=15,
            enemy_type=EnemyType.LARGE_2X2
        )
        orphan_controller = RageModeController(orphan_enemy, self.system)
        assert orphan_controller._get_enemy_id() is None

class TestRageModeEdgeCases:
    """怒りモードエッジケーステスト"""
    
    def test_invalid_enemy_type_initialization(self):
        """無効敵タイプ初期化エラーテスト"""
        system = LargeEnemySystem()
        normal_enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=50,
            max_hp=50,
            attack_power=10,
            enemy_type=EnemyType.NORMAL
        )
        
        with pytest.raises(ValueError, match="大型敵タイプではありません"):
            system.initialize_large_enemy(normal_enemy, "invalid")
    
    def test_nonexistent_enemy_operations(self):
        """存在しない敵への操作テスト"""
        system = LargeEnemySystem()
        
        # 存在しない敵への操作は静かに無視される
        system.update_rage_state("nonexistent", 25)  # 例外が発生しない
        system.trigger_rage_mode("nonexistent")       # 例外が発生しない
        system.reset_to_calm_mode("nonexistent")      # 例外が発生しない
        
        # 存在しない敵のモード取得はNone
        assert system.get_enemy_mode("nonexistent") is None
    
    def test_repeated_rage_trigger(self):
        """重複怒りモード発動テスト"""
        system = LargeEnemySystem()
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        system.initialize_large_enemy(enemy, "test")
        
        # 初回発動
        system.trigger_rage_mode("test")
        first_transition_count = enemy.rage_state.transition_turn_count
        
        # 重複発動（状態がリセットされる）
        system.trigger_rage_mode("test")
        assert enemy.rage_state.transition_turn_count == 1
        assert enemy.enemy_mode == EnemyMode.TRANSITIONING

if __name__ == "__main__":
    pytest.main([__file__, "-v"])