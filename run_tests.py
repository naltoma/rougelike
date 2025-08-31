#!/usr/bin/env python3
"""
プロジェクトルート用テスト実行スクリプト - pytest対応版
"""

import sys
import os
import subprocess

def main():
    """pytest実行"""
    print("🧪 Python初学者向けローグライクフレームワーク - pytest実行")
    print("🚀 pytestを使用して高機能なテスト実行を開始します...\n")
    
    # run_pytest.pyが存在するかチェック
    pytest_script = os.path.join(os.path.dirname(__file__), 'run_pytest.py')
    
    if os.path.exists(pytest_script):
        # 新しいpytest対応スクリプトを実行
        try:
            result = subprocess.run([sys.executable, pytest_script] + sys.argv[1:])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ pytest実行エラー: {e}")
            print("📝 フォールバック: 従来のテスト実行を試みます...\n")
    
    # フォールバック: 従来のテスト実行
    print("⚠️ pytest対応スクリプトが見つかりません。従来方式で実行します...")
    
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if not os.path.exists(tests_dir):
        print("❌ エラー: tests/ディレクトリが見つかりません")
        return False
    
    try:
        # まずpytestを試す
        try:
            result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'])
            return result.returncode == 0
        except FileNotFoundError:
            print("⚠️ pytestが見つかりません。従来のテストランナーを使用します...")
            result = subprocess.run([sys.executable, 'run_tests.py'], cwd=tests_dir)
            return result.returncode == 0
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)