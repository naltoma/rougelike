#!/usr/bin/env python3
"""
pytest統合実行スクリプト
失敗テストの再実行機能と詳細レポート付き
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Any

def install_pytest_if_needed():
    """pytestがインストールされていない場合はインストール"""
    try:
        import pytest
        return True
    except ImportError:
        print("📦 pytestがインストールされていません。インストールを試みます...")
        print("💡 以下のコマンドでインストールしてください:")
        print("   pip install -r requirements.txt")
        return False

def run_pytest_with_json_report(args: List[str] = None) -> Dict[str, Any]:
    """pytest実行とJSONレポート生成"""
    if args is None:
        args = []
    
    # JSON出力用の一時ファイル
    json_report_file = "pytest_report.json"
    
    pytest_args = [
        sys.executable, "-m", "pytest",
        "--json-report",
        f"--json-report-file={json_report_file}",
        "-v",
        "--tb=short",
        "--color=yes"
    ] + args
    
    print(f"🧪 実行コマンド: {' '.join(pytest_args)}")
    print("=" * 80)
    
    start_time = time.time()
    result = subprocess.run(pytest_args, capture_output=False, text=True)
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # JSONレポート読み込み
    report_data = {}
    if os.path.exists(json_report_file):
        try:
            with open(json_report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ JSONレポートの読み込みに失敗しました")
    
    return {
        'returncode': result.returncode,
        'execution_time': execution_time,
        'report': report_data
    }

def analyze_test_results(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """テスト結果を分析"""
    if not report_data:
        return {}
    
    summary = report_data.get('summary', {})
    tests = report_data.get('tests', [])
    
    passed_tests = [t for t in tests if t['outcome'] == 'passed']
    failed_tests = [t for t in tests if t['outcome'] == 'failed']
    skipped_tests = [t for t in tests if t['outcome'] == 'skipped']
    error_tests = [t for t in tests if t['outcome'] == 'error']
    
    return {
        'total': summary.get('total', 0),
        'passed': len(passed_tests),
        'failed': len(failed_tests),
        'skipped': len(skipped_tests),
        'errors': len(error_tests),
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'skipped_tests': skipped_tests,
        'error_tests': error_tests
    }

def print_detailed_results(analysis: Dict[str, Any], execution_time: float):
    """詳細な結果表示"""
    if not analysis:
        return
    
    print("\n" + "=" * 80)
    print("📊 テスト実行結果サマリー")
    print("=" * 80)
    
    total = analysis['total']
    passed = analysis['passed']
    failed = analysis['failed']
    skipped = analysis['skipped']
    errors = analysis['errors']
    
    # 成功率計算
    if total > 0:
        success_rate = (passed / total) * 100
    else:
        success_rate = 0
    
    print(f"🎯 総合結果: {passed}/{total} テスト成功")
    print(f"⏱️  実行時間: {execution_time:.2f}秒")
    print(f"📈 成功率: {success_rate:.1f}%")
    print(f"✅ 成功: {passed}")
    print(f"❌ 失敗: {failed}")
    print(f"⚠️ スキップ: {skipped}")
    print(f"🚨 エラー: {errors}")
    
    # 失敗したテストの詳細
    if analysis['failed_tests']:
        print(f"\n❌ 失敗したテスト ({len(analysis['failed_tests'])}個):")
        failed_files = []
        for test in analysis['failed_tests']:
            test_name = test.get('nodeid', 'Unknown')
            test_file = test_name.split('::')[0] if '::' in test_name else test_name
            failed_files.append(test_file)
            print(f"   • {test_name}")
            
            # エラー内容を簡潔に表示
            if 'call' in test and 'longrepr' in test['call']:
                longrepr = test['call']['longrepr']
                if isinstance(longrepr, str):
                    # エラーメッセージの最後の行を取得
                    error_lines = longrepr.strip().split('\n')
                    if error_lines:
                        last_line = error_lines[-1].strip()
                        if last_line:
                            print(f"     └─ {last_line}")
        
        # 失敗したテストの再実行コマンド
        print(f"\n🔄 失敗したテストのみ再実行:")
        unique_failed_files = list(set(failed_files))
        if len(unique_failed_files) <= 5:  # ファイル数が少ない場合は個別に表示
            for file in unique_failed_files:
                print(f"   pytest {file} -v")
        else:  # ファイル数が多い場合は一括コマンド
            print(f"   pytest --lf -v  # 前回失敗したテストのみ")
    
    # エラーテストの詳細
    if analysis['error_tests']:
        print(f"\n🚨 エラーが発生したテスト ({len(analysis['error_tests'])}個):")
        for test in analysis['error_tests']:
            test_name = test.get('nodeid', 'Unknown')
            print(f"   • {test_name}")
    
    # スキップしたテストの詳細
    if analysis['skipped_tests']:
        print(f"\n⚠️ スキップしたテスト ({len(analysis['skipped_tests'])}個):")
        skip_reasons = {}
        for test in analysis['skipped_tests']:
            reason = "理由不明"
            if 'call' in test and 'longrepr' in test['call']:
                longrepr = test['call']['longrepr']
                if isinstance(longrepr, str) and 'SKIPPED' in longrepr:
                    reason = longrepr.split('SKIPPED')[-1].strip().strip('[').strip(']')
            
            if reason not in skip_reasons:
                skip_reasons[reason] = []
            skip_reasons[reason].append(test.get('nodeid', 'Unknown'))
        
        for reason, tests in skip_reasons.items():
            print(f"   📋 {reason}: {len(tests)}個")
            if len(tests) <= 3:
                for test in tests:
                    print(f"      • {test}")

def print_usage_help():
    """使用方法の表示"""
    print("\n💡 便利なpytestコマンド:")
    print("   pytest -v                    # 詳細表示で全テスト実行")
    print("   pytest --lf                  # 前回失敗したテストのみ実行")
    print("   pytest -k pattern            # パターンマッチするテスト実行")
    print("   pytest tests/test_api.py     # 特定ファイルのみ実行")
    print("   pytest -m unit               # 単体テストのみ実行")
    print("   pytest -m 'not gui'          # GUIテスト以外を実行")
    print("   pytest --maxfail=1           # 最初の失敗で停止")
    print("   pytest --tb=long             # 詳細なトレースバック表示")

def main():
    """メイン実行"""
    print("🧪 Python初学者向けローグライクフレームワーク")
    print("📋 pytest統合テストスイート")
    
    # pytest availability check
    if not install_pytest_if_needed():
        print("❌ pytestが利用できません。手動でインストールしてください: pip install -r requirements.txt")
        return False
    
    # pytest-json-report の確認（requirements.txtに含まれているはず）
    try:
        import pytest_jsonreport
    except ImportError:
        print("⚠️ pytest-json-reportが見つかりません。")
        print("💡 以下のコマンドでインストールしてください:")
        print("   pip install -r requirements.txt")
    
    # コマンドライン引数の処理
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not pytest_args:
        print("🔍 全テストを実行します...")
        pytest_args = ["tests/"]
    
    # pytest実行
    result = run_pytest_with_json_report(pytest_args)
    
    # 結果分析と表示
    analysis = analyze_test_results(result.get('report', {}))
    print_detailed_results(analysis, result['execution_time'])
    
    # 品質判定
    if analysis:
        success_rate = (analysis['passed'] / analysis['total']) * 100 if analysis['total'] > 0 else 0
        
        print("\n" + "=" * 80)
        if success_rate >= 90:
            print("🎉 品質評価: 優秀")
            print("✨ フレームワークは本格運用可能な状態です")
        elif success_rate >= 70:
            print("⭐ 品質評価: 良好")
            print("🔧 一部改善により完全な動作が期待できます")
        else:
            print("⚠️ 品質評価: 要改善")
            print("🔨 多くのコンポーネントに修正が必要です")
    
    print_usage_help()
    
    # クリーンアップ
    if os.path.exists("pytest_report.json"):
        os.remove("pytest_report.json")
    
    return result['returncode'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)