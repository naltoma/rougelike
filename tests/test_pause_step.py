#!/usr/bin/env python3
"""
Pause→Step実行テスト
main_stage09.pyを使用してPause→Step動作を確認
"""

import time
import subprocess
import threading
from pathlib import Path

def create_test_solve():
    """テスト用solve()関数をmain_stage09.pyに作成"""
    test_solve = '''
def solve():
    """テスト用solve関数 - pause→step検証"""
    for i in range(5):
        turn_right()
        move()
    print("solve()完了")
'''
    
    # main_stage09.pyを作成
    main_file = Path("main_stage09.py")
    content = f'''#!/usr/bin/env python3
"""Stage 09 - ループ+攻撃練習ステージ"""

# APIの直接インポート
from engine.api import (
    turn_left, turn_right, move, attack, pickup, wait, see,
    check_position, check_hp, check_inventory, is_goal_reached
)

{test_solve}

if __name__ == "__main__":
    import time
    from engine import setup_stage, teardown_stage, get_execution_controller
    
    try:
        # ステージ初期化
        game_manager, execution_controller = setup_stage("stage09", "test_student")
        
        # solve()関数を登録
        execution_controller.pause_before_solve()
        
        print("テスト開始 - pause→step動作確認")
        print("以下の手順で確認してください:")
        print("1. Stepを1回押す")  
        print("2. Pauseを押す")
        print("3. Stepを押す（ここで複数アクション実行されるかチェック）")
        
        # GUIループを開始
        from engine.api import start_gui_loop
        start_gui_loop(solve)
        
    except Exception as e:
        print(f"エラー: {{e}}")
        import traceback
        traceback.print_exc()
    finally:
        teardown_stage()
'''
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"テストファイル作成: {main_file}")

if __name__ == "__main__":
    create_test_solve()
    print("テスト準備完了")
    print("python main_stage09.py を実行してpause→step動作を確認してください")