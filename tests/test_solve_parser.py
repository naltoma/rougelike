#!/usr/bin/env python3
"""
実際のsolve()関数でSolveParserをテスト
"""

from engine.solve_parser import parse_solve_function
import sys

def test_real_solve():
    """main.pyの実際のsolve()関数を解析"""
    print("🧪 実際のsolve()関数解析テスト")
    
    # main.pyからsolve関数をインポート
    sys.path.insert(0, '.')
    from main import solve
    
    # solve()関数を解析
    parser = parse_solve_function(solve)
    
    print(f"📊 解析結果:")
    print(f"   総ステップ数: {parser.total_steps}")
    print(f"   現在のステップ: {parser.current_step}")
    
    print(f"\n📋 検出されたアクション:")
    for i, action in enumerate(parser.actions, 1):
        print(f"   {i}. {action.action_type} (line {action.line_number}): {action.source_line}")
    
    print(f"\n🎯 進捗情報:")
    progress = parser.get_progress_info()
    print(f"   完了率: {progress['progress_percent']:.1f}%")
    print(f"   残りステップ: {progress['remaining_steps']}")
    
    print(f"\n🔍 ステップ実行シミュレーション:")
    parser.reset()
    step_count = 0
    while not parser.is_completed() and step_count < 10:  # 無限ループ防止
        action = parser.get_next_action()
        if action:
            step_count += 1
            print(f"   ステップ {step_count}: {action.action_type}")
            if action.action_type == 'move':
                print(f"     → {action.source_line.strip()}")
        else:
            break
    
    print(f"\n✅ 解析完了: {parser.is_completed()}")
    return parser

if __name__ == "__main__":
    test_real_solve()