#!/usr/bin/env python3
"""
code_lines計算のデバッグ
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.session_log_manager import SessionLogManager

def debug_code_lines():
    """code_lines計算を行ごとにデバッグ"""
    
    test_code = '''def solve():
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
    move()'''
    
    print("🔍 行ごとの詳細解析:")
    print("=" * 60)
    
    lines = test_code.split('\n')
    in_multiline_string = False
    multiline_quote = None
    code_count = 0
    comment_count = 0
    blank_count = 0
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        line_type = ""
        
        # 空行チェック
        if not stripped:
            blank_count += 1
            line_type = "空行"
        
        # 複数行文字列の処理
        elif not in_multiline_string:
            # 複数行文字列の開始チェック
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if stripped.startswith('"""'):
                    multiline_quote = '"""'
                else:
                    multiline_quote = "'''"
                
                # 同じ行で終了している場合
                if stripped.count(multiline_quote) >= 2:
                    comment_count += 1
                    line_type = "単行docstring"
                else:
                    in_multiline_string = True
                    comment_count += 1
                    line_type = "複数行docstring開始"
            elif stripped.startswith('#'):
                comment_count += 1
                line_type = "コメント"
            elif (stripped.startswith('def ') or 
                  stripped.startswith('from ') or 
                  'set_auto_render' in stripped):
                line_type = "除外対象"
            else:
                code_count += 1
                line_type = "実行コード"
        else:
            # 複数行文字列の終了チェック
            if multiline_quote in stripped:
                in_multiline_string = False
                multiline_quote = None
                comment_count += 1
                line_type = "複数行docstring終了"
            else:
                comment_count += 1
                line_type = "複数行docstring中"
        
        print(f"{i:2d}: {line_type:15s} | {repr(line)}")
    
    print("=" * 60)
    print(f"📊 手動計算結果:")
    print(f"   実行コード行数: {code_count}")
    print(f"   コメント行数: {comment_count}")
    print(f"   空行数: {blank_count}")
    print(f"   総行数: {len(lines)}")

if __name__ == "__main__":
    debug_code_lines()