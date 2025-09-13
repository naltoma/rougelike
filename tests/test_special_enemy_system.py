#!/usr/bin/env python3
"""
v1.2.8 特殊敵システム・条件付き戦闘管理システムの単体テスト
Task 6-7: 特殊敵システム・条件付き戦闘管理システムテスト
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import Enemy, EnemyType, EnemyMode, Position, Direction
from engine.enemy_system import SpecialEnemySystem, ConditionalBattleManager

class TestSpecialEnemySystem:
    """特殊敵システムテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.system = SpecialEnemySystem()
        self.special_enemy = Enemy(
            position=Position(5, 5),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=50,
            enemy_type=EnemyType.SPECIAL_2X3
        )
    
    def test_special_enemy_initialization(self):
        """特殊敵初期化テスト（HP/ATK=10000設定）"""
        self.system.initialize_special_enemy(self.special_enemy, "special1")
        
        # HP・攻撃力が10000に設定されること
        assert self.special_enemy.hp == 10000, f"HPが10000に設定されていない: {self.special_enemy.hp}"
        assert self.special_enemy.max_hp == 10000, f"最大HPが10000に設定されていない: {self.special_enemy.max_hp}"
        assert self.special_enemy.attack_power == 10000, f"攻撃力が10000に設定されていない: {self.special_enemy.attack_power}"
        
        # 特殊敵登録確認
        assert "special1" in self.system.special_enemies
        assert self.system.special_enemies["special1"] is self.special_enemy
        
        # 条件付き行動状態初期化確認
        assert self.special_enemy.conditional_behavior is not None
        assert self.special_enemy.enemy_mode == EnemyMode.CALM
    
    def test_invalid_enemy_type_initialization(self):
        """無効敵タイプ初期化エラーテスト"""
        normal_enemy = Enemy(
            position=Position(0, 0),
            direction=Direction.NORTH,
            hp=50,
            max_hp=50,
            attack_power=10,
            enemy_type=EnemyType.NORMAL
        )
        
        with pytest.raises(ValueError, match="特殊敵タイプではありません"):
            self.system.initialize_special_enemy(normal_enemy, "invalid")
    
    def test_behavior_restriction_in_calm_mode(self):
        """平常時行動制限テスト（移動・巡視・追跡無効化）"""
        self.system.initialize_special_enemy(self.special_enemy, "special1")
        
        # 平常モードでは行動制限
        assert self.system.is_behavior_restricted("special1") is True
        assert self.system.get_special_enemy_mode("special1") == "calm"
    
    def test_hunting_mode_activation(self):
        """条件違反時プレイヤー追跡モード発動テスト"""
        self.system.initialize_special_enemy(self.special_enemy, "special1")
        
        # 追跡モード発動
        target_pos = Position(3, 3)
        self.system.activate_hunting_mode("special1", target_pos)
        
        # 追跡モード確認
        assert self.special_enemy.enemy_mode == EnemyMode.HUNTING
        assert self.special_enemy.conditional_behavior.violation_detected is True
        assert self.special_enemy.conditional_behavior.hunting_target == target_pos
        
        # 行動制限解除確認
        assert self.system.is_behavior_restricted("special1") is False
    
    def test_auto_eliminate_with_correct_sequence(self):
        """条件達成時特殊敵消去テスト"""
        self.system.initialize_special_enemy(self.special_enemy, "special1")
        
        # 必須攻撃順序設定
        self.special_enemy.conditional_behavior.required_sequence = ["2x2大型敵", "3x3大型敵"]
        
        # 正しい攻撃順序設定
        self.system.update_conditional_behavior("special1", ["2x2大型敵", "3x3大型敵"])
        
        # 自動消去実行
        eliminated = self.system.auto_eliminate("special1")
        
        assert eliminated is True, "正しい攻撃順序で特殊敵が消去されなかった"
        assert self.special_enemy.hp == 0, "特殊敵のHPが0になっていない"
    
    def test_auto_eliminate_with_incorrect_sequence(self):
        """間違った攻撃順序での特殊敵消去失敗テスト"""
        self.system.initialize_special_enemy(self.special_enemy, "special1")
        
        # 必須攻撃順序設定
        self.special_enemy.conditional_behavior.required_sequence = ["2x2大型敵", "3x3大型敵"]
        
        # 間違った攻撃順序設定
        self.system.update_conditional_behavior("special1", ["3x3大型敵", "2x2大型敵"])
        
        # 自動消去実行
        eliminated = self.system.auto_eliminate("special1")
        
        assert eliminated is False, "間違った攻撃順序で特殊敵が消去されてしまった"
        assert self.special_enemy.hp == 10000, "特殊敵のHPが変更されてしまった"
    
    def test_nonexistent_enemy_operations(self):
        """存在しない特殊敵への操作テスト"""
        # 存在しない敵への操作は静かに無視される
        self.system.activate_hunting_mode("nonexistent", Position(1, 1))
        self.system.update_conditional_behavior("nonexistent", ["test"])
        
        # 存在しない敵の消去はFalse
        assert self.system.auto_eliminate("nonexistent") is False
        
        # 存在しない敵の制限チェックはFalse
        assert self.system.is_behavior_restricted("nonexistent") is False
        
        # 存在しない敵のモード取得はNone
        assert self.system.get_special_enemy_mode("nonexistent") is None

class TestConditionalBattleManager:
    """条件付き戦闘管理システムテスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.manager = ConditionalBattleManager()
    
    def test_attack_sequence_registration(self):
        """攻撃順序記録テスト"""
        self.manager.register_attack_sequence("large_2x2")
        self.manager.register_attack_sequence("large_3x3")
        
        expected_sequence = ["2x2大型敵", "3x3大型敵"]
        assert self.manager.attack_sequence == expected_sequence
    
    def test_valid_attack_sequence_validation(self):
        """正しい攻撃順序検証テスト"""
        # 正しい順序で攻撃
        self.manager.register_attack_sequence("large_2x2")
        self.manager.register_attack_sequence("large_3x3")
        
        # 検証成功
        assert self.manager.validate_attack_sequence() is True
        assert self.manager.check_conditional_violation() is False
    
    def test_invalid_attack_sequence_validation(self):
        """間違った攻撃順序検証テスト"""
        # 間違った順序で攻撃
        self.manager.register_attack_sequence("large_3x3")
        self.manager.register_attack_sequence("large_2x2")
        
        # 検証失敗
        assert self.manager.validate_attack_sequence() is False
        assert self.manager.check_conditional_violation() is True
    
    def test_educational_feedback_generation(self):
        """教育的フィードバック生成テスト"""
        # 正しい順序の場合
        self.manager.register_attack_sequence("large_2x2")
        feedback = self.manager.get_violation_feedback()
        assert "正しい攻撃順序で進行しています。" in feedback
        
        # 間違った順序の場合
        self.manager.reset_sequence()
        self.manager.register_attack_sequence("large_3x3")
        self.manager.register_attack_sequence("large_2x2")
        self.manager.check_conditional_violation()  # 違反を記録
        
        feedback = self.manager.get_violation_feedback()
        assert len(feedback) > 1, "違反フィードバックが生成されていない"
        assert "攻撃順序違反" in feedback[0]
        assert "ヒント" in feedback[-1]
    
    def test_sequence_reset(self):
        """攻撃順序リセットテスト"""
        # 攻撃順序記録
        self.manager.register_attack_sequence("large_2x2")
        self.manager.register_attack_sequence("large_3x3")
        self.manager.check_conditional_violation()
        
        # リセット
        self.manager.reset_sequence()
        
        assert len(self.manager.attack_sequence) == 0, "攻撃順序がリセットされていない"
        assert len(self.manager.violation_feedback) == 0, "違反フィードバックがリセットされていない"
    
    def test_custom_required_sequence(self):
        """カスタム必須攻撃順序テスト"""
        # カスタム順序設定
        custom_sequence = ["special_2x3", "large_2x2"]
        self.manager.set_required_sequence(custom_sequence)
        
        # カスタム順序で攻撃
        self.manager.register_attack_sequence("special_2x3")
        self.manager.register_attack_sequence("large_2x2")
        
        # 検証成功
        assert self.manager.validate_attack_sequence() is True
    
    def test_partial_sequence_validation(self):
        """部分的攻撃順序検証テスト"""
        # 最初の1体だけ攻撃
        self.manager.register_attack_sequence("large_2x2")
        
        # まだ判定段階ではないのでTrue
        assert self.manager.validate_attack_sequence() is True
        assert self.manager.check_conditional_violation() is False

class TestSpecialEnemyIntegration:
    """特殊敵システムと条件付き戦闘管理の統合テスト"""
    
    def setup_method(self):
        """各テスト前の初期化"""
        self.special_system = SpecialEnemySystem()
        self.battle_manager = ConditionalBattleManager()
        
        self.special_enemy = Enemy(
            position=Position(8, 8),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=50,
            enemy_type=EnemyType.SPECIAL_2X3
        )
        
        self.special_system.initialize_special_enemy(self.special_enemy, "special1")
    
    def test_violation_triggers_hunting_mode(self):
        """条件違反時の追跡モード発動統合テスト"""
        # 間違った攻撃順序で違反発生
        self.battle_manager.register_attack_sequence("large_3x3")
        self.battle_manager.register_attack_sequence("large_2x2")
        
        # 条件違反チェック
        is_violation = self.battle_manager.check_conditional_violation()
        assert is_violation is True
        
        # 違反時に追跡モード発動
        if is_violation:
            player_pos = Position(5, 5)
            self.special_system.activate_hunting_mode("special1", player_pos)
        
        # 追跡モード確認
        assert self.special_enemy.enemy_mode == EnemyMode.HUNTING
        assert self.special_enemy.conditional_behavior.violation_detected is True
    
    def test_correct_sequence_eliminates_special_enemy(self):
        """正しい攻撃順序での特殊敵消去統合テスト"""
        # 特殊敵に必須順序設定
        self.special_enemy.conditional_behavior.required_sequence = ["2x2大型敵", "3x3大型敵"]
        
        # 正しい攻撃順序実行
        self.battle_manager.register_attack_sequence("large_2x2")
        self.battle_manager.register_attack_sequence("large_3x3")
        
        # 条件チェック（違反なし）
        is_violation = self.battle_manager.check_conditional_violation()
        assert is_violation is False
        
        # 特殊敵に攻撃順序反映
        attack_sequence = ["2x2大型敵", "3x3大型敵"]
        self.special_system.update_conditional_behavior("special1", attack_sequence)
        
        # 特殊敵消去
        eliminated = self.special_system.auto_eliminate("special1")
        assert eliminated is True
        assert self.special_enemy.hp == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])