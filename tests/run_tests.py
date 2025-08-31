#!/usr/bin/env python3
"""
テスト実行メインスクリプト
全テストの一括実行と結果サマリー
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append('..')

def run_test_file(test_file):
    """個別テストファイルを実行"""
    print(f"\n{'='*60}")
    print(f"🧪 実行中: {test_file}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, test_file], 
            capture_output=True, 
            text=True, 
            cwd='.'
        )
        end_time = time.time()
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        execution_time = end_time - start_time
        success = result.returncode == 0
        
        return {
            'file': test_file,
            'success': success,
            'execution_time': execution_time,
            'returncode': result.returncode
        }
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return {
            'file': test_file,
            'success': False,
            'execution_time': 0,
            'error': str(e)
        }

def main():
    """メインテスト実行"""
    print("🧪 Python初学者向けローグライクフレームワーク")
    print("📋 総合テストスイート実行")
    print(f"{'='*60}")
    
    # テストファイル一覧取得
    test_files = sorted([
        f for f in os.listdir('.') 
        if f.startswith('test_') and f.endswith('.py') and f != 'run_tests.py'
    ])
    
    if not test_files:
        print("❌ テストファイルが見つかりません")
        return
    
    print(f"📁 発見されたテストファイル: {len(test_files)}個")
    for i, test_file in enumerate(test_files, 1):
        print(f"   {i:2d}. {test_file}")
    
    # 全テスト実行
    results = []
    total_start_time = time.time()
    
    for test_file in test_files:
        result = run_test_file(test_file)
        results.append(result)
    
    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    
    # 結果サマリー
    print(f"\n{'='*60}")
    print("📊 テスト実行結果サマリー")
    print(f"{'='*60}")
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"🎯 総合結果: {len(successful_tests)}/{len(results)} テスト成功")
    print(f"⏱️  総実行時間: {total_execution_time:.2f}秒")
    print(f"📈 成功率: {len(successful_tests)/len(results)*100:.1f}%")
    
    if successful_tests:
        print(f"\n✅ 成功したテスト ({len(successful_tests)}個):")
        for result in successful_tests:
            print(f"   • {result['file']} ({result['execution_time']:.2f}s)")
    
    if failed_tests:
        print(f"\n❌ 失敗したテスト ({len(failed_tests)}個):")
        for result in failed_tests:
            error_info = result.get('error', f"exit code {result.get('returncode', 'unknown')}")
            print(f"   • {result['file']} - {error_info}")
    
    # 推奨テスト実行順序
    print(f"\n💡 推奨個別テスト実行順序:")
    recommended_order = [
        "test_progression.py",           # 基本システム
        "test_session_logging.py",       # ログシステム 
        "test_educational_errors.py",    # エラー処理
        "test_quality_assurance.py",     # 品質保証
        "test_educational_feedback.py",  # フィードバック
        "test_google_sheets_simple.py",  # Google Sheets
        "test_enemy_item_systems.py",    # 敵・アイテム
        "test_main_game_loop_simple.py", # メインループ
        "test_comprehensive_integration.py" # 統合テスト
    ]
    
    for i, test_file in enumerate(recommended_order, 1):
        if test_file in test_files:
            print(f"   {i:2d}. python {test_file}")
    
    # 品質判定
    success_rate = len(successful_tests) / len(results)
    if success_rate >= 0.9:
        print(f"\n🎉 品質評価: 優秀 (成功率 {success_rate*100:.1f}%)")
        print("✨ フレームワークは本格運用可能な状態です")
    elif success_rate >= 0.7:
        print(f"\n⭐ 品質評価: 良好 (成功率 {success_rate*100:.1f}%)")
        print("🔧 一部改善により完全な動作が期待できます")
    else:
        print(f"\n⚠️ 品質評価: 要改善 (成功率 {success_rate*100:.1f}%)")
        print("🔨 多くのコンポーネントに修正が必要です")
    
    print(f"\n📝 個別テスト実行方法:")
    print(f"   cd tests")
    print(f"   python test_[テスト名].py")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)