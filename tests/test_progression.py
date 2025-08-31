#!/usr/bin/env python3
"""
進捗管理システムテスト
Progression Management System Tests
"""

import sys
sys.path.append('..')

import time
from datetime import datetime, timedelta
from pathlib import Path


def test_progression_classes():
    """進捗管理クラスの基本テスト"""
    print("🧪 進捗管理クラステスト")
    print("=" * 50)
    
    try:
        from engine.progression import (
            SkillLevel, MetricType, StageAttempt, SkillProgress, 
            LearningMetrics, StudentProgress, ProgressionManager
        )
        
        # StageAttempt テスト
        print("📊 StageAttempt テスト...")
        attempt = StageAttempt(
            stage_id="stage01",
            attempt_number=1,
            start_time=datetime.now(),
            max_turns=20,
            turns_used=15
        )
        attempt.end_time = datetime.now() + timedelta(seconds=30)
        attempt.success = True
        
        print(f"  効率性スコア: {attempt.efficiency_score:.2f}")
        print(f"  正確性スコア: {attempt.accuracy_score:.2f}")
        print(f"  実行時間: {attempt.duration}")
        
        # SkillProgress テスト
        print("\n🎓 SkillProgress テスト...")
        skill = SkillProgress(
            skill_type=MetricType.EFFICIENCY,
            current_level=SkillLevel.BEGINNER
        )
        
        print(f"  初期レベル: {skill.current_level.value}")
        skill.add_experience(50)
        print(f"  経験値50追加後: {skill.current_level.value}, 経験値: {skill.experience_points}")
        
        skill.add_experience(100)
        print(f"  経験値100追加後: {skill.current_level.value}, 経験値: {skill.experience_points}")
        
        # StudentProgress テスト
        print("\n👤 StudentProgress テスト...")
        student = StudentProgress(student_id="test_student")
        student.add_stage_attempt(attempt)
        
        print(f"  総挑戦回数: {student.overall_metrics.total_attempts}")
        print(f"  成功率: {student.overall_metrics.success_rate:.1%}")
        
        summary = student.get_overall_summary()
        print(f"  サマリー作成: {'✅' if summary else '❌'}")
        
        print("✅ 進捗管理クラステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_progression_manager():
    """ProgressionManager テスト"""
    print("\n🧪 ProgressionManager テスト")
    print("=" * 50)
    
    try:
        from engine.progression import ProgressionManager
        from engine import GameState, GameStatus, Position, Direction, Character, Board
        
        # テスト用データディレクトリ
        test_dir = "test_data/progression"
        manager = ProgressionManager(test_dir)
        
        # 学生初期化
        print("👤 学生初期化...")
        student_progress = manager.initialize_student("test_student_001")
        print(f"  学生ID: {student_progress.student_id}")
        
        # ステージ挑戦開始
        print("\n🎯 ステージ挑戦開始...")
        attempt = manager.start_stage_attempt("test_student_001", "stage01")
        print(f"  挑戦開始: {attempt.stage_id}")
        
        # いくつかのアクションを記録
        print("\n📝 アクション記録...")
        actions = ["turn_right", "move", "move", "turn_right", "move"]
        for action in actions:
            manager.record_action(f"{action}: 成功")
        
        # エラー記録
        manager.record_error("壁にぶつかりました")
        
        # ゲーム状態を作成して終了
        print("\n🏁 ゲーム終了...")
        
        # テスト用ゲーム状態
        player = Character(
            position=Position(4, 4),
            direction=Direction.EAST,
            hp=100,
            max_hp=100,
            attack_power=10
        )
        
        board = Board(width=5, height=5, walls=[], forbidden_cells=[])
        
        game_state = GameState(
            player=player,
            board=board,
            enemies=[],
            items=[],
            goal_position=Position(4, 4),
            status=GameStatus.WON,
            turn_count=5,
            max_turns=20
        )
        
        manager.end_stage_attempt(game_state)
        
        # 進捗レポート取得
        print("\n📊 進捗レポート...")
        overall_report = manager.get_progress_report()
        print(f"  総挑戦回数: {overall_report.get('total_attempts', 0)}")
        print(f"  成功率: {overall_report.get('overall_success_rate', 0):.1%}")
        
        stage_report = manager.get_progress_report("stage01")
        print(f"  Stage01 成功率: {stage_report.get('success_rate', 0):.1%}")
        
        # 推奨事項
        recommendations = manager.get_recommendations()
        print(f"\n💡 推奨事項: {len(recommendations)}件")
        for rec in recommendations:
            print(f"  {rec}")
        
        print("\n✅ ProgressionManager テスト完了")
        
        # テストファイル削除
        import shutil
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print("🧹 テストデータをクリーンアップしました")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_integration():
    """API統合テスト"""
    print("\n🧪 API統合テスト")
    print("=" * 50)
    
    try:
        from engine.api import (
            initialize_api, set_student_id, initialize_stage, 
            turn_right, move, show_progress_summary, get_progress_report
        )
        
        # API初期化（進捗管理有効）
        print("📺 API初期化...")
        initialize_api("cui", enable_progression=True, student_id="test_api_001")
        
        # ステージ初期化
        print("\n🎯 ステージ初期化...")
        if initialize_stage("stage01"):
            print("✅ ステージ初期化成功")
            
            # いくつかのアクション実行
            print("\n🎮 ゲームプレイ...")
            turn_right()  # 東を向く
            for i in range(3):
                move()    # 東に移動
            
            turn_right()  # 南を向く  
            for i in range(3):
                move()    # 南に移動
            
            # 進捗表示
            print("\n📊 進捗確認...")
            show_progress_summary()
            
            # レポート取得
            report = get_progress_report()
            print(f"\nレポート取得: {'✅' if report else '❌'}")
            
        else:
            print("❌ ステージ初期化失敗")
            return False
        
        print("\n✅ API統合テスト完了")
        
        # テストデータクリーンアップ
        test_file = Path("data/progression/test_api_001.json")
        if test_file.exists():
            test_file.unlink()
            print("🧹 テストデータをクリーンアップしました")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_skill_progression():
    """スキル進歩テスト"""
    print("\n🧪 スキル進歩テスト")
    print("=" * 50)
    
    try:
        from engine.progression import SkillProgress, MetricType, SkillLevel
        
        skill = SkillProgress(
            skill_type=MetricType.EFFICIENCY,
            current_level=SkillLevel.BEGINNER
        )
        
        print(f"初期状態: {skill.current_level.value} (XP: {skill.experience_points})")
        
        # レベルアップテスト
        xp_amounts = [25, 30, 50, 100, 200, 150]
        
        for i, xp in enumerate(xp_amounts, 1):
            old_level = skill.current_level
            level_up = skill.add_experience(xp)
            
            print(f"ステップ{i}: +{xp}XP → {skill.current_level.value} "
                  f"(XP: {skill.experience_points}, 進捗: {skill.level_progress:.1%})")
            
            if level_up:
                print(f"  🎉 レベルアップ！ {old_level.value} → {skill.current_level.value}")
        
        print("✅ スキル進歩テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 進捗管理システム統合テスト開始")
    print("=" * 60)
    
    tests = [
        test_progression_classes,
        test_progression_manager,
        test_skill_progression,
        test_api_integration
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
        print("🎉 全ての進捗管理テストが成功しました！")
        print("✅ 進捗管理システムが正常に実装されています")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")


if __name__ == "__main__":
    main()