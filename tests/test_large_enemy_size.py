#!/usr/bin/env python3
"""
v1.2.8 大型敵・特殊敵サイズ定義拡張の単体テスト
Task 2: 新敵タイプのサイズ計算・座標占有確認テスト
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import Enemy, EnemyType, Position, Direction

class TestLargeEnemySize:
    """大型敵・特殊敵のサイズ計算テスト"""
    
    def test_large_2x2_enemy_size(self):
        """2x2大型敵のサイズ計算テスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        
        width, height = enemy.get_size()
        assert width == 2, f"2x2敵の幅は2であるべき: {width}"
        assert height == 2, f"2x2敵の高さは2であるべき: {height}"
    
    def test_large_3x3_enemy_size(self):
        """3x3大型敵のサイズ計算テスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_3X3
        )
        
        width, height = enemy.get_size()
        assert width == 3, f"3x3敵の幅は3であるべき: {width}"
        assert height == 3, f"3x3敵の高さは3であるべき: {height}"
    
    def test_special_2x3_enemy_size(self):
        """2x3特殊敵のサイズ計算テスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=10000,
            max_hp=10000,
            attack_power=10000,
            enemy_type=EnemyType.SPECIAL_2X3
        )
        
        width, height = enemy.get_size()
        assert width == 2, f"2x3特殊敵の幅は2であるべき: {width}"
        assert height == 3, f"2x3特殊敵の高さは3であるべき: {height}"

class TestLargeEnemyPositions:
    """大型敵・特殊敵の座標占有計算テスト"""
    
    def test_large_2x2_occupied_positions(self):
        """2x2大型敵の座標占有テスト"""
        enemy = Enemy(
            position=Position(1, 1),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        
        occupied = enemy.get_occupied_positions()
        expected = [
            Position(1, 1), Position(2, 1),
            Position(1, 2), Position(2, 2)
        ]
        
        assert len(occupied) == 4, f"2x2敵は4マス占有すべき: {len(occupied)}"
        for pos in expected:
            assert pos in occupied, f"座標 {pos} が占有されていない"
    
    def test_large_3x3_occupied_positions(self):
        """3x3大型敵の座標占有テスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_3X3
        )
        
        occupied = enemy.get_occupied_positions()
        expected = [
            Position(0, 0), Position(1, 0), Position(2, 0),
            Position(0, 1), Position(1, 1), Position(2, 1),
            Position(0, 2), Position(1, 2), Position(2, 2)
        ]
        
        assert len(occupied) == 9, f"3x3敵は9マス占有すべき: {len(occupied)}"
        for pos in expected:
            assert pos in occupied, f"座標 {pos} が占有されていない"
    
    def test_special_2x3_occupied_positions(self):
        """2x3特殊敵の座標占有テスト"""
        enemy = Enemy(
            position=Position(2, 3),
            direction=Direction.NORTH,
            hp=10000,
            max_hp=10000,
            attack_power=10000,
            enemy_type=EnemyType.SPECIAL_2X3
        )
        
        occupied = enemy.get_occupied_positions()
        expected = [
            Position(2, 3), Position(3, 3),
            Position(2, 4), Position(3, 4),
            Position(2, 5), Position(3, 5)
        ]
        
        assert len(occupied) == 6, f"2x3特殊敵は6マス占有すべき: {len(occupied)}"
        for pos in expected:
            assert pos in occupied, f"座標 {pos} が占有されていない"

class TestEnemyAutoInitialization:
    """v1.2.8 敵の自動初期化テスト"""
    
    def test_large_2x2_rage_state_initialization(self):
        """2x2大型敵のRageState自動初期化テスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_2X2
        )
        
        assert enemy.rage_state is not None, "2x2大型敵にRageStateが自動初期化されていない"
        assert enemy.rage_state.is_active is False, "初期状態では怒りモードは非アクティブ"
        assert enemy.rage_state.trigger_hp_threshold == 0.5, "HP50%閾値が設定されていない"
    
    def test_large_3x3_rage_state_initialization(self):
        """3x3大型敵のRageState自動初期化テスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20,
            enemy_type=EnemyType.LARGE_3X3
        )
        
        assert enemy.rage_state is not None, "3x3大型敵にRageStateが自動初期化されていない"
        assert enemy.rage_state.is_active is False, "初期状態では怒りモードは非アクティブ"
        assert enemy.rage_state.trigger_hp_threshold == 0.5, "HP50%閾値が設定されていない"
    
    def test_special_2x3_conditional_behavior_initialization(self):
        """2x3特殊敵のConditionalBehavior自動初期化テスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=10000,
            max_hp=10000,
            attack_power=10000,
            enemy_type=EnemyType.SPECIAL_2X3
        )
        
        assert enemy.conditional_behavior is not None, "2x3特殊敵にConditionalBehaviorが自動初期化されていない"
        assert enemy.conditional_behavior.violation_detected is False, "初期状態では条件違反は検出されていない"
        assert enemy.conditional_behavior.required_sequence == [], "必須攻撃順序が初期化されていない"
        assert enemy.conditional_behavior.current_sequence == [], "現在攻撃順序が初期化されていない"
    
    def test_normal_enemy_no_auto_initialization(self):
        """通常敵では自動初期化されないテスト"""
        enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=50,
            max_hp=50,
            attack_power=10,
            enemy_type=EnemyType.NORMAL
        )
        
        assert enemy.rage_state is None, "通常敵にはRageStateが初期化されるべきではない"
        assert enemy.conditional_behavior is None, "通常敵にはConditionalBehaviorが初期化されるべきではない"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])