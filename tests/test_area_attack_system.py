#!/usr/bin/env python3
"""
v1.2.8 範囲攻撃システムの単体テスト
Task 5: 範囲攻撃計算・実行テスト
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import Enemy, EnemyType, EnemyMode, Position, Direction
from engine.enemy_system import LargeEnemySystem

class TestAreaAttackRange:
    """範囲攻撃座標計算テスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.system = LargeEnemySystem()
    
    def test_2x2_enemy_area_attack_range(self):
        """2x2大型敵の範囲攻撃座標計算テスト"""
        enemy = Enemy(
            position=Position(2, 2),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        self.system.initialize_large_enemy(enemy, "enemy1")
        
        # 範囲攻撃座標取得
        attack_range = self.system.get_area_attack_range("enemy1")
        
        # 2x2敵（位置 2,2-3,3）の周囲1マス範囲
        expected_positions = [
            # 上辺周囲
            Position(1, 1), Position(2, 1), Position(3, 1), Position(4, 1),
            # 左右辺
            Position(1, 2), Position(4, 2),
            Position(1, 3), Position(4, 3),
            # 下辺周囲
            Position(1, 4), Position(2, 4), Position(3, 4), Position(4, 4)
        ]
        
        assert len(attack_range) == len(expected_positions), f"攻撃範囲座標数が不正: {len(attack_range)}"
        for pos in expected_positions:
            assert pos in attack_range, f"座標 {pos} が攻撃範囲に含まれていない"
    
    def test_3x3_enemy_area_attack_range(self):
        """3x3大型敵の範囲攻撃座標計算テスト"""
        enemy = Enemy(
            position=Position(1, 1),
            direction=Direction.NORTH,
            hp=150,
            max_hp=150,
            attack_power=30,
            enemy_type=EnemyType.LARGE_3X3
        )
        self.system.initialize_large_enemy(enemy, "enemy1")
        
        # 範囲攻撃座標取得
        attack_range = self.system.get_area_attack_range("enemy1")
        
        # 3x3敵（位置 1,1-3,3）の周囲1マス範囲
        expected_positions = [
            # 上辺周囲
            Position(0, 0), Position(1, 0), Position(2, 0), Position(3, 0), Position(4, 0),
            # 左右辺
            Position(0, 1), Position(4, 1),
            Position(0, 2), Position(4, 2),
            Position(0, 3), Position(4, 3),
            # 下辺周囲
            Position(0, 4), Position(1, 4), Position(2, 4), Position(3, 4), Position(4, 4)
        ]
        
        assert len(attack_range) == len(expected_positions), f"攻撃範囲座標数が不正: {len(attack_range)}"
        for pos in expected_positions:
            assert pos in attack_range, f"座標 {pos} が攻撃範囲に含まれていない"
    
    def test_area_attack_range_no_overlap_with_enemy(self):
        """攻撃範囲が敵占有マスと重複しないテスト"""
        enemy = Enemy(
            position=Position(5, 5),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        self.system.initialize_large_enemy(enemy, "enemy1")
        
        # 攻撃範囲取得
        attack_range = self.system.get_area_attack_range("enemy1")
        
        # 敵占有マス取得
        occupied_positions = enemy.get_occupied_positions()
        
        # 攻撃範囲と敵占有マスが重複しないことを確認
        for attack_pos in attack_range:
            assert attack_pos not in occupied_positions, f"攻撃範囲 {attack_pos} が敵占有マス {occupied_positions} と重複"

class TestAreaAttackExecution:
    """範囲攻撃実行テスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.system = LargeEnemySystem()
        self.enemy = Enemy(
            position=Position(5, 5),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=25,
            enemy_type=EnemyType.LARGE_2X2
        )
        self.system.initialize_large_enemy(self.enemy, "test_enemy")
    
    def test_area_attack_in_rage_mode_hits_player(self):
        """怒りモード中の範囲攻撃でプレイヤーがヒットするテスト"""
        # 敵を怒りモードに
        self.enemy.enemy_mode = EnemyMode.RAGE
        
        # プレイヤーを攻撃範囲内に配置
        player_position = Position(4, 5)  # 敵の左隣
        
        # 範囲攻撃実行
        hit, damage = self.system.execute_area_attack("test_enemy", player_position)
        
        assert hit is True, "プレイヤーに攻撃がヒットしなかった"
        assert damage == 25, f"ダメージが期待値と異なる: {damage}"
        assert self.enemy.rage_state.area_attack_executed is True, "area_attack_executedフラグが設定されていない"
    
    def test_area_attack_in_rage_mode_misses_player(self):
        """怒りモード中の範囲攻撃でプレイヤーがミスするテスト"""
        # 敵を怒りモードに
        self.enemy.enemy_mode = EnemyMode.RAGE
        
        # プレイヤーを攻撃範囲外に配置
        player_position = Position(0, 0)  # 範囲外
        
        # 範囲攻撃実行
        hit, damage = self.system.execute_area_attack("test_enemy", player_position)
        
        assert hit is False, "プレイヤーに攻撃がヒットしてしまった"
        assert damage == 0, f"ダメージが0でない: {damage}"
        assert self.enemy.rage_state.area_attack_executed is True, "area_attack_executedフラグが設定されていない"
    
    def test_area_attack_in_calm_mode_fails(self):
        """平常モード中は範囲攻撃できないテスト"""
        # 敵を平常モードに（デフォルト）
        assert self.enemy.enemy_mode == EnemyMode.CALM
        
        # プレイヤーを攻撃範囲内に配置
        player_position = Position(4, 5)
        
        # 範囲攻撃実行
        hit, damage = self.system.execute_area_attack("test_enemy", player_position)
        
        assert hit is False, "平常モードで攻撃がヒットしてしまった"
        assert damage == 0, f"平常モードでダメージが発生: {damage}"
    
    def test_area_attack_nonexistent_enemy(self):
        """存在しない敵への範囲攻撃テスト"""
        player_position = Position(1, 1)
        
        # 存在しない敵への攻撃
        hit, damage = self.system.execute_area_attack("nonexistent", player_position)
        
        assert hit is False, "存在しない敵で攻撃がヒットしてしまった"
        assert damage == 0, f"存在しない敵でダメージが発生: {damage}"

class TestAreaAttackWithRageController:
    """範囲攻撃と怒りモード制御器の統合テスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.system = LargeEnemySystem()
        self.enemy = Enemy(
            position=Position(3, 3),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        self.system.initialize_large_enemy(self.enemy, "test_enemy")
    
    def test_rage_mode_to_area_attack_to_calm_mode_cycle(self):
        """怒りモード→範囲攻撃→平常モード サイクルテスト"""
        # 怒りモード発動
        self.system.trigger_rage_mode("test_enemy")
        assert self.enemy.enemy_mode == EnemyMode.TRANSITIONING
        
        # 1ターン経過で怒りモードに
        self.system.update_rage_turn_for_enemy("test_enemy")
        assert self.enemy.enemy_mode == EnemyMode.RAGE
        assert self.enemy.rage_state.turns_in_rage == 1  # 怒りモード最初のターン
        
        # さらに1ターン経過で範囲攻撃実行
        self.system.update_rage_turn_for_enemy("test_enemy")
        assert self.enemy.rage_state.area_attack_executed is True  # _prepare_area_attack で設定
        
        # さらに1ターン経過で平常モードに復帰
        self.system.update_rage_turn_for_enemy("test_enemy")
        assert self.enemy.enemy_mode == EnemyMode.CALM
        assert self.enemy.rage_state.is_active is False
    
    def test_multiple_area_attacks_different_enemies(self):
        """複数大型敵の独立範囲攻撃テスト"""
        # 2体目の敵作成
        enemy2 = Enemy(
            position=Position(8, 8),
            direction=Direction.NORTH,
            hp=150,
            max_hp=150,
            attack_power=30,
            enemy_type=EnemyType.LARGE_3X3
        )
        self.system.initialize_large_enemy(enemy2, "enemy2")
        
        # 両方とも怒りモードに
        self.system.trigger_rage_mode("test_enemy")
        self.system.trigger_rage_mode("enemy2")
        
        # 遷移
        self.system.update_rage_turn_for_enemy("test_enemy")
        self.system.update_rage_turn_for_enemy("enemy2")
        
        # プレイヤー位置
        player_pos = Position(2, 3)  # 1体目の攻撃範囲内、2体目の範囲外
        
        # 1体目の範囲攻撃（ヒット）
        hit1, damage1 = self.system.execute_area_attack("test_enemy", player_pos)
        assert hit1 is True
        assert damage1 == 20
        
        # 2体目の範囲攻撃（ミス）
        hit2, damage2 = self.system.execute_area_attack("enemy2", player_pos)
        assert hit2 is False
        assert damage2 == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])