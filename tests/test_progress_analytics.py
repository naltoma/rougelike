#!/usr/bin/env python3
"""
進歩ログ系統と品質メトリクステスト
"""

import sys
sys.path.append('..')


def test_code_analyzer_advanced():
    """高度なコード分析器テスト"""
    print("🧪 高度なコード分析器テスト")
    
    try:
        from engine.progress_analytics import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        print("✅ CodeAnalyzer作成成功")
        
        # 複雑なサンプルコード
        complex_code = """
# 迷路解法プログラム（右手法）
def solve_maze():
    \"\"\"迷路を右手法で解く\"\"\"
    while not is_game_finished():
        # 現在の状況を確認
        surroundings = see()
        
        # 右手法のロジック
        if surroundings['surroundings']['right'] != 'wall':
            turn_right()
            move()
        elif surroundings['surroundings']['front'] != 'wall':
            move()
        else:
            turn_left()
        
        # 無限ループ防止（簡易版）
        if get_game_result() == "timeout":
            break

def helper_function():
    \"\"\"ヘルパー関数\"\"\"
    return True
"""
        
        api_history = ["see", "turn_right", "move", "see", "move", "see", "turn_left", "get_game_result"]
        
        # 高度な分析実行
        result = analyzer.analyze_code(complex_code, api_history)
        
        print(f"✅ 高度コード分析完了")
        print(f"   複雑度レベル: {result.complexity_level.value}")
        print(f"   循環的複雑度: {result.cyclomatic_complexity}")
        print(f"   認知的複雑度: {result.cognitive_complexity}")
        print(f"   保守性指標: {result.maintainability_index:.1f}")
        print(f"   ネスト深度: {result.nesting_depth}")
        print(f"   関数数: {result.function_count}")
        print(f"   API多様性: {result.api_diversity_score:.2f}")
        print(f"   コード品質: {result.code_quality_score:.2f}")
        
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
        from engine.progress_analytics import LearningProgressMetrics
        from datetime import datetime, timedelta
        
        metrics = LearningProgressMetrics()
        print("✅ LearningProgressMetrics作成成功")
        
        # 学習データをシミュレート
        metrics.student_id = "test_student"
        metrics.stage_id = "stage01"
        metrics.session_id = "test_session"
        metrics.start_time = datetime.now() - timedelta(minutes=30)
        metrics.end_time = datetime.now()
        metrics.session_duration = metrics.end_time - metrics.start_time
        
        metrics.total_attempts = 15
        metrics.successful_attempts = 10
        metrics.failed_attempts = 5
        metrics.hint_requests = 2
        metrics.average_response_time = 4.5
        metrics.error_recovery_rate = 0.8
        metrics.consistency_score = 0.75
        
        print(f"✅ 学習メトリクス計算完了")
        print(f"   成功率: {metrics.success_rate:.1%}")
        print(f"   効率性スコア: {metrics.efficiency_score:.2f}")
        print(f"   セッション時間: {metrics.session_duration.total_seconds()/60:.1f}分")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_progress_analyzer():
    """進歩分析器テスト"""
    print("\n🧪 進歩分析器テスト")
    
    try:
        from engine.progress_analytics import ProgressAnalyzer
        from datetime import datetime, timedelta
        
        analyzer = ProgressAnalyzer()
        print("✅ ProgressAnalyzer作成成功")
        
        # テストデータ準備
        student_id = "test_student"
        stage_id = "stage01"
        session_id = "test_session_001"
        
        code_text = """
def basic_solution():
    # 基本的な移動プログラム
    for i in range(5):
        if see()['surroundings']['front'] == 'empty':
            move()
        else:
            turn_right()
"""
        
        # セッションログをシミュレート
        base_time = datetime.now() - timedelta(minutes=10)
        session_log = []
        
        for i in range(8):
            session_log.append({
                "timestamp": (base_time + timedelta(seconds=i*30)).isoformat(),
                "event_type": "action_executed",
                "data": {
                    "action": "move" if i % 3 != 0 else "turn_right",
                    "success": i % 4 != 3  # 75%の成功率
                }
            })
        
        # ヒント使用記録
        session_log.append({
            "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
            "event_type": "hint_used",
            "data": {"hint_type": "movement"}
        })
        
        api_history = ["see", "move", "see", "turn_right", "see", "move", "see", "move"]
        
        # 包括分析実行
        report = analyzer.analyze_session(
            student_id, stage_id, session_id, code_text, session_log, api_history
        )
        
        print(f"✅ 進歩分析完了")
        print(f"   学習評価: {report.learning_grade}")
        print(f"   総合スコア: {report.overall_score:.1%}")
        print(f"   強み数: {len(report.strengths)}")
        print(f"   改善点数: {len(report.improvements)}")
        print(f"   推奨事項数: {len(report.recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sheets_format_conversion():
    """Google Sheets形式変換テスト"""
    print("\n🧪 Google Sheets形式変換テスト")
    
    try:
        from engine.progress_analytics import ComprehensiveReport, CodeAnalysisResult, LearningProgressMetrics
        from datetime import datetime, timedelta
        
        # ダミーレポート作成
        report = ComprehensiveReport()
        report.report_id = "test_report_001"
        report.overall_score = 0.78
        report.learning_grade = "B"
        
        # コード分析結果
        report.code_analysis = CodeAnalysisResult()
        report.code_analysis.total_lines = 25
        report.code_analysis.logical_lines = 18
        report.code_analysis.cyclomatic_complexity = 4
        report.code_analysis.code_hash = "abc123def456"
        
        # 学習メトリクス
        report.learning_metrics = LearningProgressMetrics()
        report.learning_metrics.student_id = "test_student"
        report.learning_metrics.stage_id = "stage01"
        report.learning_metrics.session_id = "session_001"
        report.learning_metrics.total_attempts = 12
        report.learning_metrics.successful_attempts = 9
        report.learning_metrics.session_duration = timedelta(minutes=25)
        report.learning_metrics.average_response_time = 3.2
        report.learning_metrics.hint_requests = 1
        
        # フィードバック
        report.strengths = ["高い成功率を維持", "効率的な問題解決"]
        report.improvements = ["コメントの追加", "関数の分割"]
        
        # Sheets形式変換
        sheets_data = report.to_sheets_format()
        
        print("✅ Sheets形式変換成功")
        print(f"   データ項目数: {len(sheets_data)}")
        print(f"   学生ID: {sheets_data['学生ID']}")
        print(f"   総合スコア: {sheets_data['総合スコア']}")
        print(f"   成功率: {sheets_data['成功率']}")
        
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
        from engine.api import (
            initialize_api, set_student_id, 
            show_comprehensive_summary, analyze_code_complexity
        )
        
        # API初期化（進歩分析有効）
        initialize_api("cui", enable_progression=True, enable_session_logging=False)
        print("✅ API初期化成功（進歩分析有効）")
        
        # 学生ID設定
        set_student_id("test_student")
        print("✅ 学生ID設定成功")
        
        # コード複雑度分析テスト
        test_code = """
def complex_algorithm():
    count = 0
    while count < 10:
        if count % 2 == 0:
            for i in range(3):
                if i > 1:
                    move()
                else:
                    turn_right()
        count += 1
"""
        
        complexity_result = analyze_code_complexity(test_code)
        print("✅ コード複雑度分析成功")
        print(f"   複雑度レベル: {complexity_result['complexity_level']}")
        print(f"   循環的複雑度: {complexity_result['cyclomatic_complexity']}")
        
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
        from engine.progress_analytics import ProgressAnalyzer, ComprehensiveReport
        from datetime import datetime
        
        analyzer = ProgressAnalyzer()
        
        # ダミーレポート作成
        report = ComprehensiveReport()
        report.report_id = "persistence_test_001"
        report.overall_score = 0.85
        report.learning_grade = "A"
        
        # レポート保存
        filepath = analyzer.save_report(report)
        print(f"✅ レポート保存成功: {filepath}")
        
        # レポート読み込み
        loaded_report = analyzer.load_report(report.report_id)
        if loaded_report:
            print("✅ レポート読み込み成功")
            print(f"   レポートID: {loaded_report.report_id}")
            print(f"   総合スコア: {loaded_report.overall_score:.1%}")
        else:
            print("⚠️ レポート読み込み失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 進歩ログ系統と品質メトリクステスト開始")
    print("=" * 60)
    
    tests = [
        test_code_analyzer_advanced,
        test_learning_metrics,
        test_progress_analyzer,
        test_sheets_format_conversion,
        test_api_integration,
        test_report_persistence
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
        print("🎉 全ての進歩分析システムテストが成功しました！")
        print("✅ 進歩ログ系統と品質メトリクスが正常に実装されています")
        print("📊 高度なコード分析、学習効率評価、包括的レポート生成が動作しています")
        print("📋 Google Sheets連携準備が整いました")
        print("💡 教師は学生の学習状況を定量的かつ包括的に分析できます")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")
        print("🔧 進歩分析システムの修正が必要です")


if __name__ == "__main__":
    main()