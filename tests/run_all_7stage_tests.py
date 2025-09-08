#!/usr/bin/env python3
"""
🚀 v1.2.5: 7-Stage Speed Control Test Runner
7段階速度制御システム包括的テストランナー
"""

import unittest
import sys
import os
import time
from io import StringIO

# プロジェクトパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# テストモジュールをインポート
from test_enhanced_7stage_speed_control import *
from test_gui_integration import *
from test_error_handling_integration import *
from test_session_logging_integration import *


class ColoredTextTestResult(unittest.TextTestResult):
    """カラー出力対応テスト結果クラス"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'end': '\033[0m'
        }
    
    def addSuccess(self, test):
        super().addSuccess(test)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['green']}✓ PASS{self.colors['end']} ")
            self.stream.write(f"{test._testMethodName}\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['red']}✗ ERROR{self.colors['end']} ")
            self.stream.write(f"{test._testMethodName}\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['red']}✗ FAIL{self.colors['end']} ")
            self.stream.write(f"{test._testMethodName}\n")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['yellow']}⊝ SKIP{self.colors['end']} ")
            self.stream.write(f"{test._testMethodName}: {reason}\n")


class Enhanced7StageTestRunner:
    """7段階速度制御テストランナー"""
    
    def __init__(self):
        self.test_suites = [
            ('Core Speed Control', [
                'TestEnhanced7StageSpeedControlManager',
                'TestUltraHighSpeedController',
                'TestSpeedControlErrorClasses',
                'TestIntegrationScenarios',
                'TestPerformanceBenchmarks'
            ]),
            ('GUI Integration', [
                'TestGuiSpeedControlIntegration',
                'TestGUIEventHandling',
                'TestGUIPerformanceUnderLoad'
            ]),
            ('Error Handling', [
                'TestErrorHandlingIntegration',
                'TestSpeedControlErrorHandler',
                'TestSpeedControlErrorManager',
                'TestErrorRecoveryScenarios'
            ]),
            ('Session Logging', [
                'TestSessionLogging7StageIntegration',
                'TestSessionLoggerPerformanceWith7Stage'
            ])
        ]
        
        self.results = {}
    
    def run_test_suite(self, suite_name, test_classes):
        """テストスイート実行"""
        print(f"\n{'='*60}")
        print(f"🚀 {suite_name} Test Suite")
        print(f"{'='*60}")
        
        suite = unittest.TestSuite()
        
        # テストクラスを追加
        for class_name in test_classes:
            try:
                test_class = globals()[class_name]
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                suite.addTests(tests)
            except KeyError:
                print(f"⚠️  Warning: Test class '{class_name}' not found")
                continue
        
        # テスト実行
        runner = unittest.TextTestRunner(
            verbosity=2,
            resultclass=ColoredTextTestResult,
            stream=sys.stdout
        )
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # 結果を記録
        self.results[suite_name] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
            'execution_time': end_time - start_time
        }
        
        return result
    
    def run_all_tests(self):
        """全テストスイート実行"""
        print("🚀 v1.2.5: 7段階速度制御システム包括テスト開始")
        print(f"{'='*80}")
        
        overall_start_time = time.time()
        all_results = []
        
        for suite_name, test_classes in self.test_suites:
            result = self.run_test_suite(suite_name, test_classes)
            all_results.append(result)
        
        overall_end_time = time.time()
        
        # 総合結果の表示
        self.display_summary(overall_end_time - overall_start_time)
        
        # 全テストが成功したかを判定
        total_failures = sum(len(r.failures) for r in all_results)
        total_errors = sum(len(r.errors) for r in all_results)
        
        return total_failures == 0 and total_errors == 0
    
    def display_summary(self, total_time):
        """テスト結果サマリー表示"""
        print(f"\n{'='*80}")
        print("📊 テスト実行サマリー")
        print(f"{'='*80}")
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        
        for suite_name, results in self.results.items():
            print(f"\n📋 {suite_name}:")
            print(f"  実行: {results['tests_run']}件")
            print(f"  成功: {results['tests_run'] - results['failures'] - results['errors']}件")
            print(f"  失敗: {results['failures']}件")
            print(f"  エラー: {results['errors']}件")
            print(f"  スキップ: {results['skipped']}件")
            print(f"  成功率: {results['success_rate']:.1f}%")
            print(f"  実行時間: {results['execution_time']:.2f}秒")
            
            total_tests += results['tests_run']
            total_failures += results['failures']
            total_errors += results['errors']
            total_skipped += results['skipped']
        
        overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 総合結果:")
        print(f"  総テスト数: {total_tests}件")
        print(f"  成功: {total_tests - total_failures - total_errors}件")
        print(f"  失敗: {total_failures}件")
        print(f"  エラー: {total_errors}件")
        print(f"  スキップ: {total_skipped}件")
        print(f"  総合成功率: {overall_success_rate:.1f}%")
        print(f"  総実行時間: {total_time:.2f}秒")
        
        if total_failures == 0 and total_errors == 0:
            print(f"\n🎉 全テスト成功！ 7段階速度制御システムv1.2.5の品質が確認されました。")
        else:
            print(f"\n⚠️  {total_failures + total_errors}件の問題が検出されました。詳細を確認してください。")
    
    def run_specific_tests(self, test_pattern=None):
        """特定のテストパターンを実行"""
        if not test_pattern:
            return self.run_all_tests()
        
        print(f"🎯 パターンマッチテスト実行: '{test_pattern}'")
        
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        
        # パターンにマッチするテストを収集
        for suite_name, test_classes in self.test_suites:
            for class_name in test_classes:
                if test_pattern.lower() in class_name.lower():
                    try:
                        test_class = globals()[class_name]
                        tests = loader.loadTestsFromTestCase(test_class)
                        suite.addTests(tests)
                        print(f"  ✓ {class_name} を実行対象に追加")
                    except KeyError:
                        continue
        
        if suite.countTestCases() == 0:
            print(f"❌ パターン '{test_pattern}' にマッチするテストが見つかりません。")
            return False
        
        # マッチしたテストを実行
        runner = unittest.TextTestRunner(
            verbosity=2,
            resultclass=ColoredTextTestResult
        )
        
        result = runner.run(suite)
        return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='7段階速度制御システム包括テストランナー',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python run_all_7stage_tests.py                    # 全テスト実行
  python run_all_7stage_tests.py --pattern speed    # "speed"を含むテストのみ実行
  python run_all_7stage_tests.py --pattern gui      # "gui"を含むテストのみ実行
  python run_all_7stage_tests.py --pattern error    # "error"を含むテストのみ実行
        """
    )
    
    parser.add_argument(
        '--pattern', '-p',
        type=str,
        help='実行するテストクラス名のパターン（部分マッチ）'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細出力を有効にする'
    )
    
    args = parser.parse_args()
    
    # テストランナー初期化
    test_runner = Enhanced7StageTestRunner()
    
    # テスト実行
    try:
        if args.pattern:
            success = test_runner.run_specific_tests(args.pattern)
        else:
            success = test_runner.run_all_tests()
        
        # 終了コード設定
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  テスト実行が中断されました。")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ テスト実行中に予期しないエラーが発生しました: {e}")
        sys.exit(3)


if __name__ == '__main__':
    main()