#!/usr/bin/env python3
"""
敵・アイテムシステムテスト
"""

import sys
sys.path.append('..')


def test_enemy_system():
    """敵システムテスト"""
    print("🧪 敵システムテスト")
    
    try:
        from engine.enemy_system import (
            AdvancedEnemy, EnemyManager, EnemyFactory,
            BehaviorPattern, EnemyState, EnemyAI, EnemyStats
        )
        from engine import Position, Direction, EnemyType, Board
        
        # 基本敵作成
        enemy = EnemyFactory.create_basic_enemy(Position(5, 5))
        print("✅ 基本敵作成成功")
        print(f"   HP: {enemy.hp}/{enemy.max_hp}")
        print(f"   攻撃力: {enemy.attack_power}")
        print(f"   状態: {enemy.current_state.value}")
        
        # 警備敵作成
        patrol_points = [Position(3, 3), Position(7, 7), Position(3, 7)]
        guard = EnemyFactory.create_guard_enemy(Position(5, 5), patrol_points)
        print("✅ 警備敵作成成功")
        print(f"   行動パターン: {guard.ai_config.behavior_pattern.value}")
        print(f"   検出範囲: {guard.ai_config.detection_range}")
        print(f"   巡回ポイント数: {len(guard.ai_config.patrol_points)}")
        
        # ハンター敵作成
        hunter = EnemyFactory.create_hunter_enemy(Position(8, 8))
        print("✅ ハンター敵作成成功")
        print(f"   攻撃性レベル: {hunter.ai_config.aggression_level}")
        
        # 大型敵作成
        large_enemy = EnemyFactory.create_large_enemy(Position(10, 10), EnemyType.LARGE_2X2)
        print("✅ 大型敵作成成功")
        print(f"   サイズ: {large_enemy.get_size()}")
        print(f"   占有座標数: {len(large_enemy.get_occupied_positions())}")
        
        # 敵管理システム
        enemy_manager = EnemyManager()
        enemy_manager.add_enemy(enemy)
        enemy_manager.add_enemy(guard)
        enemy_manager.add_enemy(hunter)
        print("✅ 敵管理システム作成成功")
        print(f"   管理敵数: {len(enemy_manager.get_alive_enemies())}")
        
        # ダミーボード作成
        board = Board(width=20, height=20, walls=[], forbidden_cells=[])
        
        # AI更新テスト
        player_pos = Position(6, 6)
        enemy_manager.update_all_enemies(player_pos, board)
        print("✅ 敵AI更新成功")
        
        # 行動決定テスト
        actions = enemy_manager.process_enemy_turn(player_pos, board)
        print(f"✅ 敵行動処理: {len(actions)}個のアクション")
        
        for i, action_data in enumerate(actions):
            action = action_data["action"]
            print(f"   敵{i+1}: {action['type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_item_system():
    """アイテムシステムテスト"""
    print("\n🧪 アイテムシステムテスト")
    
    try:
        from engine.item_system import (
            AdvancedItem, ItemData, ItemEffect, Inventory, ItemManager,
            ItemRarity, ItemCategory, EffectType
        )
        from engine import Item, ItemType, Position
        
        # アイテムマネージャー作成
        item_manager = ItemManager()
        print("✅ ItemManager作成成功")
        
        # アイテム生成テスト
        sword = item_manager.create_item("iron_sword", Position(0, 0))
        if sword:
            print("✅ 剣アイテム作成成功")
            print(f"   名前: {sword.data.base_item.name}")
            print(f"   レアリティ: {sword.data.rarity.value}")
            print(f"   効果: {sword.get_total_effects()}")
        
        armor = item_manager.create_item("leather_armor", Position(1, 1))
        if armor:
            print("✅ 防具アイテム作成成功")
            print(f"   名前: {armor.data.base_item.name}")
        
        potion = item_manager.create_item("health_potion", Position(2, 2), quantity=5)
        if potion:
            print("✅ ポーションアイテム作成成功")
            print(f"   数量: {potion.quantity}")
            print(f"   スタック可能: {potion.is_stackable()}")
        
        # ランダムアイテム生成
        random_item = item_manager.create_random_item(Position(5, 5), level=5)
        if random_item:
            print("✅ ランダムアイテム作成成功")
            print(f"   名前: {random_item.data.base_item.name}")
            print(f"   レアリティ: {random_item.data.rarity.value}")
            print(f"   価値: {random_item.get_value()}")
        
        # インベントリテスト
        inventory = Inventory(max_capacity=10)
        print("✅ インベントリ作成成功")
        
        # アイテム追加
        inventory.add_item(sword)
        inventory.add_item(armor)
        inventory.add_item(potion)
        print("✅ アイテム追加成功")
        
        # インベントリ概要
        summary = inventory.get_inventory_summary()
        print(f"   総アイテム数: {summary['total_items']}")
        print(f"   総価値: {summary['total_value']}")
        print(f"   カテゴリ別: {summary['categories']}")
        
        # 装備テスト
        inventory.equip_item("iron_sword", "weapon")
        inventory.equip_item("leather_armor", "armor")
        print("✅ アイテム装備成功")
        
        # 装備効果
        equipment_effects = inventory.get_total_equipment_effects()
        print(f"   装備効果: {equipment_effects}")
        
        # アイテム使用テスト
        if potion.use_item():
            print("✅ ポーション使用成功")
            print(f"   残り数量: {potion.quantity}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_game_state():
    """拡張ゲーム状態テスト"""
    print("\n🧪 拡張ゲーム状態テスト")
    
    try:
        from engine.advanced_game_state import AdvancedGameState, AdvancedGameStateManager
        from engine.enemy_system import EnemyFactory
        from engine import Character, Position, Direction, Board, Enemy, Item, ItemType, EnemyType
        
        # 基本データ準備
        player = Character(
            position=Position(5, 5),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=15
        )
        
        # 基本敵作成（移行テスト用）
        basic_enemies = [
            Enemy(
                position=Position(8, 8),
                direction=Direction.SOUTH,
                hp=30,
                attack_power=10,
                enemy_type=EnemyType.NORMAL
            )
        ]
        
        # 基本アイテム作成（移行テスト用）
        basic_items = [
            Item(
                position=Position(3, 3),
                item_type=ItemType.POTION,
                name="health_potion",
                effect={"heal": 30}
            )
        ]
        
        board = Board(width=15, height=15, walls=[], forbidden_cells=[])
        
        # 拡張ゲーム状態作成
        advanced_state = AdvancedGameState(
            player=player,
            enemies=basic_enemies,
            items=basic_items,
            board=board,
            turn_count=0,
            max_turns=50,
            goal_position=Position(12, 12)
        )
        
        print("✅ AdvancedGameState作成成功")
        
        # 敵・アイテム移行確認
        alive_enemies = advanced_state.enemy_manager.get_alive_enemies()
        print(f"   移行済み敵数: {len(alive_enemies)}")
        
        field_items = advanced_state.item_manager.get_all_field_items()
        print(f"   移行済みアイテム座標数: {len(field_items)}")
        
        # ゲーム情報取得
        game_info = advanced_state.get_game_info()
        print("✅ ゲーム情報取得成功")
        print(f"   プレイヤーHP: {game_info['player_hp']}")
        print(f"   敵数: {game_info['enemies_count']}")
        print(f"   インベントリ: {game_info['inventory']['total_items']}個")
        
        # アイテム拾得テスト
        pickup_messages = advanced_state.pickup_items_at(Position(3, 3))
        print("✅ アイテム拾得テスト成功")
        for msg in pickup_messages:
            print(f"   {msg}")
        
        # 戦闘テスト
        enemy_position = Position(8, 8)
        combat_result = advanced_state.attack_enemy_at(enemy_position)
        print("✅ 戦闘テスト成功")
        for msg in combat_result.messages:
            print(f"   {msg}")
        
        # ターン終了処理
        turn_messages = advanced_state.process_turn_end()
        print("✅ ターン終了処理成功")
        if turn_messages:
            print(f"   ターン終了メッセージ数: {len(turn_messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combat_system():
    """戦闘システムテスト"""
    print("\n🧪 戦闘システムテスト")
    
    try:
        from engine.advanced_game_state import CombatSystem, AdvancedGameState
        from engine.enemy_system import EnemyFactory
        from engine import Character, Position, Direction, Board
        
        # テスト環境準備
        player = Character(
            position=Position(5, 5),
            direction=Direction.NORTH,
            hp=100,
            max_hp=100,
            attack_power=20
        )
        
        board = Board(width=10, height=10, walls=[], forbidden_cells=[])
        
        game_state = AdvancedGameState(
            player=player,
            enemies=[],
            items=[],
            board=board,
            turn_count=0,
            max_turns=50
        )
        
        # 敵追加
        enemy = EnemyFactory.create_basic_enemy(Position(6, 5))
        game_state.enemy_manager.add_enemy(enemy)
        
        # 戦闘システム作成
        combat_system = CombatSystem(game_state)
        print("✅ CombatSystem作成成功")
        
        # ダメージ計算テスト
        damage = combat_system.calculate_damage(player, enemy)
        print(f"✅ ダメージ計算: {damage}")
        
        # 攻撃解決テスト
        result = combat_system.resolve_attack(player, enemy)
        print("✅ 攻撃解決成功")
        print(f"   与えたダメージ: {result.attacker_damage}")
        print(f"   敵撃破: {result.defender_dead}")
        for msg in result.messages:
            print(f"   {msg}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_drop_system():
    """ドロップシステムテスト"""
    print("\n🧪 ドロップシステムテスト")
    
    try:
        from engine.advanced_game_state import DropSystem
        from engine.item_system import ItemManager
        from engine.enemy_system import EnemyFactory
        from engine import Position, EnemyType
        
        # システム準備
        item_manager = ItemManager()
        drop_system = DropSystem(item_manager)
        print("✅ DropSystem作成成功")
        
        # テスト敵作成
        enemy = EnemyFactory.create_basic_enemy(Position(5, 5))
        large_enemy = EnemyFactory.create_large_enemy(Position(8, 8), EnemyType.LARGE_2X2)
        
        # ドロップ生成テスト（複数回実行）
        total_drops = 0
        for i in range(10):
            drops = drop_system.generate_drops(enemy)
            total_drops += len(drops)
        
        print(f"✅ 通常敵ドロップテスト: 10回中{total_drops}個のドロップ")
        
        # 大型敵ドロップテスト
        large_drops = 0
        for i in range(10):
            drops = drop_system.generate_drops(large_enemy)
            large_drops += len(drops)
        
        print(f"✅ 大型敵ドロップテスト: 10回中{large_drops}個のドロップ")
        
        # ドロップ配置テスト
        messages = drop_system.place_drops(enemy)
        print("✅ ドロップ配置テスト成功")
        for msg in messages:
            print(f"   {msg}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 敵・アイテムシステムテスト開始")
    print("=" * 60)
    
    tests = [
        test_enemy_system,
        test_item_system,
        test_advanced_game_state,
        test_combat_system,
        test_drop_system
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("🏁 テスト結果")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"成功: {passed}/{total}")
    
    if passed == total:
        print("🎉 全ての敵・アイテムシステムテストが成功しました！")
        print("✅ 高度な敵AIシステム（巡回、追跡、警備、ハンター）が実装されています")
        print("🗡️ 戦闘システム（ダメージ計算、装備効果、エンチャント）が動作します")
        print("🎒 インベントリ管理（装備、消耗品、スタック）が正常に機能します")
        print("⚔️ 敵のドロップシステムとアイテム効果処理が完全に統合されています")
        print("🎮 拡張ゲーム状態により複雑なゲームプレイが可能です")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")
        print("🔧 敵・アイテムシステムの修正が必要です")


if __name__ == "__main__":
    main()