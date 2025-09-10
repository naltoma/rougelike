#!/usr/bin/env python3
"""
code_lines計算機能のテスト（必須行除外版）
def, from, set_auto_renderを除外したcode_linesが正しく計算されることを確認
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.session_log_manager import SessionLogManager

def test_code_lines_exclude():
    """必須行除外版code_lines計算機能をテスト"""
    print("🧪 code_lines必須行除外テスト開始")
    
    # テスト用のsolve()コード例（main_stage04.pyのようなコード）
    test_codes = {
        "main_stage04.py形式": '''def solve():
    """
    学生が編集する関数
    """
    # ここに攻略コードを書いてください
    
    # 例: Stage04の攻略解法（敵を倒してからゴールへ）
    from engine.api import turn_right, move, attack, set_auto_render
    
    print("🎮 Stage04攻略を実行します...")
    set_auto_render(True)  # 自動レンダリングをオン
    
    # 1. 敵の隣まで移動
    move()
    
    # 2. 敵を攻撃で倒す（HP=10なので1回攻撃）
    attack()
    
    # 3. ゴールまで移動
    move()
    move()
    move()''',
        
        "シンプルな学生コード": '''def solve():
    move()
    attack()
    move()''',
        
        "importなしコード": '''def solve():
    """攻略法"""
    # 移動
    move()
    move()
    
    # 攻撃
    attack()
    
    # ゴールへ
    move()
    move()''',
    }
    
    # SessionLogManagerのインスタンス作成
    session_manager = SessionLogManager()
    
    # ダミーのセッション開始でSessionLoggerを作成
    result = session_manager.enable_default_logging("test999Z", "stage04")
    if not result.success:
        print("❌ セッションログ初期化失敗")
        return
    
    for test_name, code in test_codes.items():
        print(f"\n📋 テスト: {test_name}")
        print("=" * 50)
        
        # SessionLoggerの_calculate_code_metricsメソッドを使用
        metrics = session_manager.session_logger._calculate_code_metrics(code)
        
        print(f"コード:")
        for i, line in enumerate(code.split('\n'), 1):
            stripped = line.strip()
            is_excluded = (stripped.startswith('def ') or 
                          stripped.startswith('from ') or 
                          'set_auto_render' in stripped)
            marker = " [除外]" if is_excluded else ""
            print(f"{i:2d}: {repr(line)}{marker}")
        
        print(f"\n📊 計算結果:")
        print(f"   総行数: {metrics['line_count']}")
        print(f"   実行可能コード行数: {metrics['code_lines']} (def/from/set_auto_render除外後)")
        print(f"   コメント行数: {metrics['comment_lines']}")
        print(f"   空行数: {metrics['blank_lines']}")
        
        # 期待される結果を正確に計算（複数行文字列考慮）
        lines = code.split('\n')
        expected_code_lines = 0
        in_multiline_string = False
        multiline_quote = None
        
        for line in lines:
            stripped = line.strip()
            if not stripped:  # 空行
                continue
                
            # 複数行文字列処理
            if not in_multiline_string:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if stripped.startswith('"""'):
                        multiline_quote = '"""'
                    else:
                        multiline_quote = "'''"
                    
                    if stripped.count(multiline_quote) >= 2:
                        # 単行docstring
                        continue
                    else:
                        # 複数行開始
                        in_multiline_string = True
                        continue
                        
                if stripped.startswith('#'):  # コメント
                    continue
                if (stripped.startswith('def ') or 
                    stripped.startswith('from ') or 
                    'set_auto_render' in stripped or
                    stripped.startswith('print(')):  # 除外対象
                    continue
                expected_code_lines += 1
            else:
                # 複数行文字列中
                if multiline_quote in stripped:
                    in_multiline_string = False
                    multiline_quote = None
                # 複数行文字列中の行はカウントしない
                continue
        
        print(f"   期待値: {expected_code_lines}")
        
        if metrics['code_lines'] == expected_code_lines:
            print("✅ 計算結果が期待値と一致")
        else:
            print(f"❌ 計算結果が期待値と不一致")
    
    print("\n🎉 code_lines必須行除外テスト完了")

if __name__ == "__main__":
    test_code_lines_exclude()