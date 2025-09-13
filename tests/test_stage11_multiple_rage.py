#!/usr/bin/env python3
"""
Stage11 複数回怒りモードテスト用スクリプト
"""

from engine.framework import initialize_stage

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def solve():
    # 最初の位置調整
    for i in range(6): move()
    turn_right()
    move()
    
    # 第1回怒りモードサイクル：HP1000→480（26回攻撃で50%を下回る）
    print("=== 第1回怒りモードサイクル開始 ===")
    for i in range(26):
        attack()
        info = see()
        front_enemy = info["surroundings"]["front"]
        if isinstance(front_enemy, dict) and front_enemy["type"] == "enemy":
            enemy_hp = front_enemy["hp"]
            enemy_alerted = front_enemy["alerted"]
            hp_ratio = enemy_hp / front_enemy["max_hp"]
            print(f"攻撃{i+1}回目: HP={enemy_hp}, 率={hp_ratio:.2f}, 警戒={enemy_alerted}")
    
    # 回避行動（3ターン）
    print("=== 回避行動開始（3ターン） ===")
    turn_left()  # 1ターン目：左向き
    print("回避1ターン目：左向き")
    
    turn_left()  # 2ターン目：後ろ向き
    print("回避2ターン目：後ろ向き（180度回転完了）")
    
    move()  # 3ターン目：移動（距離を取る）
    print("回避3ターン目：移動（安全圏へ）")
    
    # 4ターン目：敵の範囲攻撃発動（プレイヤーは安全圏）
    wait()
    print("4ターン目：敵範囲攻撃発動（プレイヤーは安全圏）")
    
    # 5ターン目：クールダウン状態
    wait()
    print("5ターン目：敵クールダウン中")
    
    # 6ターン目：敵平常モード復帰
    wait()
    print("6ターン目：敵平常モード復帰")
    
    # 再接敵
    print("=== 再接敵開始 ===")
    turn_right()  # 右向き
    turn_right()  # 元の向き（東向き）に復帰
    move()  # 敵に隣接
    
    # 第2回怒りモードサイクル：数回攻撃後に再び怒りモード発動
    print("=== 第2回怒りモードサイクル開始 ===")
    for i in range(5):  # 数回攻撃
        attack()
        info = see()
        front_enemy = info["surroundings"]["front"]
        if isinstance(front_enemy, dict) and front_enemy["type"] == "enemy":
            enemy_hp = front_enemy["hp"]
            enemy_alerted = front_enemy["alerted"]
            hp_ratio = enemy_hp / front_enemy["max_hp"]
            print(f"第2回攻撃{i+1}回目: HP={enemy_hp}, 率={hp_ratio:.2f}, 警戒={enemy_alerted}")
    
    # 第2回回避行動
    print("=== 第2回回避行動開始（3ターン） ===")
    turn_left()  # 1ターン目
    print("第2回回避1ターン目：左向き")
    
    turn_left()  # 2ターン目
    print("第2回回避2ターン目：後ろ向き")
    
    move()  # 3ターン目
    print("第2回回避3ターン目：移動")

if __name__ == "__main__":
    # フレームワークを初期化して実行
    initialize_stage("stage11", "test_student")
    
    try:
        solve()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()