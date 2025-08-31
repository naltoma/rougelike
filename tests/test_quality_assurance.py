#!/usr/bin/env python3
"""
学習メトリクスと品質保証システムテスト
"""

import sys
sys.path.append('..')


def test_code_analyzer():
    """コード分析器テスト"""
    print("🧪 コード分析器テスト")
    
    try:
        from engine.quality_assurance import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        print("✅ CodeAnalyzer作成成功")
        
        # サンプルコード
        sample_code = """
# ゴールに向かって移動するプログラム
def reach_goal():
    while not is_game_finished():
        info = see()
        if info['surroundings']['front'] == 'goal':
            move()
            break
        elif info['surroundings']['front'] == 'empty':
            move()
        else:
            turn_right()
"""
        
        api_calls = ["see", "move", "turn_right", "see", "move", "see", "turn_right"]
        
        # コード品質分析
        metrics = analyzer.analyze_code_quality(sample_code, api_calls)
        print(f"✅ コード分析完了: {metrics.overall_quality.value}")
        print(f"   可読性スコア: {metrics.readability_score:.2f}")
        print(f"   効率性スコア: {metrics.efficiency_score:.2f}")
        print(f"   API多様性: {metrics.api_usage_diversity}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_learning_analyzer():
    """学習分析器テスト"""
    print("\n🧪 学習分析器テスト")
    
    try:
        from engine.quality_assurance import LearningAnalyzer
        from datetime import datetime, timedelta
        
        analyzer = LearningAnalyzer()
        print("✅ LearningAnalyzer作成成功")
        
        # サンプルセッションデータ
        base_time = datetime.now()
        session_data = []
        
        for i in range(10):
            session_data.append({
                "timestamp": (base_time + timedelta(seconds=i*5)).isoformat(),
                "event_type": "action_executed",
                "data": {
                    "action": "move",
                    "success": i % 3 != 0  # 成功率約66%
                }
            })
        
        # 学習パターン分析
        metrics = analyzer.analyze_learning_pattern(session_data)
        print(f"✅ 学習分析完了: {metrics.learning_efficiency.value}")
        print(f"   成功率: {metrics.success_rate:.1%}")
        print(f"   総試行数: {metrics.total_attempts}")
        print(f"   改善率: {metrics.improvement_rate:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_report_generation():
    """品質レポート生成テスト"""
    print("\n🧪 品質レポート生成テスト")
    
    try:
        from engine.quality_assurance import QualityAssuranceManager
        from datetime import datetime, timedelta
        
        manager = QualityAssuranceManager()
        print("✅ QualityAssuranceManager作成成功")
        
        # テストデータ
        student_id = "test_student"
        session_id = "test_session_001"
        code_text = """
def simple_move():
    move()
    turn_right()
    move()
"""
        api_calls = ["move", "turn_right", "move"]
        
        # セッションデータ
        base_time = datetime.now()
        session_data = [
            {
                "timestamp": base_time.isoformat(),
                "event_type": "action_executed",
                "data": {"action": "move", "success": True}
            },
            {
                "timestamp": (base_time + timedelta(seconds=2)).isoformat(),
                "event_type": "action_executed", 
                "data": {"action": "turn_right", "success": True}
            },
            {
                "timestamp": (base_time + timedelta(seconds=4)).isoformat(),
                "event_type": "action_executed",
                "data": {"action": "move", "success": True}
            }
        ]
        
        # 品質レポート生成
        report = manager.generate_quality_report(
            student_id, session_id, code_text, api_calls, session_data
        )
        
        print("✅ 品質レポート生成成功")
        print(f"   学生ID: {report.student_id}")
        print(f"   総合スコア: {report.overall_score:.1%}")
        print(f"   コード品質: {report.code_metrics.overall_quality.value}")
        print(f"   学習効率: {report.learning_metrics.learning_efficiency.value}")
        print(f"   推奨事項数: {len(report.recommendations)}")
        print(f"   達成項目数: {len(report.achievements)}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_integration():
    """API統合テスト"""
    print("\n🧪 API統合テスト")
    
    try:
        from engine.api import initialize_api, set_student_id, analyze_code_quality
        
        # API初期化（品質保証システム有効）
        initialize_api("cui", enable_progression=True, enable_session_logging=False)
        print("✅ API初期化成功（品質保証有効）")
        
        # 学生ID設定
        set_student_id("test_student")
        print("✅ 学生ID設定成功")
        
        # コード品質分析テスト
        test_code = """
# 基本移動プログラム
def basic_movement():
    for i in range(3):
        move()
        turn_right()
"""
        
        quality_result = analyze_code_quality(test_code)
        print("✅ コード品質分析成功")
        print(f"   全体品質: {quality_result['overall_quality']}")
        print(f"   可読性: {quality_result['readability_score']:.2f}")
        print(f"   効率性: {quality_result['efficiency_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_persistence():
    """レポート永続化テスト"""
    print("\n🧪 レポート永続化テスト")
    
    try:
        from engine.quality_assurance import QualityAssuranceManager
        from datetime import datetime
        
        manager = QualityAssuranceManager()
        
        # ダミーレポート作成
        from engine.quality_assurance import QualityReport, CodeMetrics, LearningMetrics
        
        report = QualityReport(
            student_id="test_student",
            session_id="persistence_test",
            timestamp=datetime.now(),
            code_metrics=CodeMetrics(lines_of_code=10, readability_score=0.8),
            learning_metrics=LearningMetrics(total_attempts=5, successful_attempts=4),
            overall_score=0.75,
            recommendations=["テスト推奨事項"],
            achievements=["テスト達成項目"]
        )
        
        # レポート保存
        filepath = manager.save_report(report)
        print(f"✅ レポート保存成功: {filepath}")
        
        # レポート読み込み
        loaded_report = manager.load_report(filepath)
        if loaded_report:
            print("✅ レポート読み込み成功")
            print(f"   学生ID: {loaded_report.student_id}")
            print(f"   総合スコア: {loaded_report.overall_score:.1%}")
        else:
            print("❌ レポート読み込み失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_learning_metrics():
    """学習メトリクステスト"""
    print("\n🧪 学習メトリクステスト")
    
    try:
        from engine.quality_assurance import LearningMetrics
        
        metrics = LearningMetrics()
        print("✅ LearningMetrics作成成功")
        
        # 複数の試行をシミュレート
        test_cases = [
            (True, 2.5),   # 成功、2.5秒
            (False, 4.0),  # 失敗、4.0秒
            (True, 1.8),   # 成功、1.8秒
            (True, 2.2),   # 成功、2.2秒
            (False, 3.1),  # 失敗、3.1秒
        ]
        
        for success, response_time in test_cases:
            metrics.add_attempt(success, response_time)
        
        print(f"✅ 学習メトリクス更新完了")
        print(f"   成功率: {metrics.success_rate:.1%}")
        print(f"   平均応答時間: {metrics.average_response_time:.1f}秒")
        print(f"   学習効率: {metrics.learning_efficiency.value}")
        print(f"   改善率: {metrics.improvement_rate:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 学習メトリクスと品質保証システムテスト開始")
    print("=" * 60)
    
    tests = [
        test_code_analyzer,
        test_learning_analyzer,
        test_quality_report_generation,
        test_api_integration,
        test_report_persistence,
        test_learning_metrics
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
        print("🎉 全ての品質保証システムテストが成功しました！")
        print("✅ 学習メトリクスと品質保証システムが正常に実装されています")
        print("📊 コード品質分析、学習効率評価、レポート生成機能が動作しています")
        print("💡 教師は学生の学習状況を定量的に評価できます")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")
        print("🔧 品質保証システムの修正が必要です")


if __name__ == "__main__":
    main()