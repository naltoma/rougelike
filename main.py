#!/usr/bin/env python3
"""
Python初学者向けローグライク演習フレームワーク
メインエントリーポイント

学生の皆さんへ：
このファイルを実行してゲームを開始します。
あなたのタスクは下記のsolve()関数を編集することです。

使用方法:
- GUI モード（推奨）: python main.py
- CUI モード: python main.py --cui
"""

import argparse
import logging
import sys
from pathlib import Path

# プロジェクト設定
import config

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

def solve():
    """
    学生が編集する関数
    
    ここにステージを攻略するコードを書いてください。
    
    使用できる関数:
    - turn_left(): 左に90度回転
    - turn_right(): 右に90度回転  
    - move(): 正面方向に1マス移動
    - see(): 周囲の状況を確認 (辞書形式で返却)
    
    例:
    turn_right()  # 右を向く
    move()        # 1マス前進
    info = see()  # 周囲を確認
    """
    # ここに攻略コードを書いてください
    
    # 例: Stage01の簡単な解法（視覚的表示付き）
    from engine.api import (
        initialize_api, initialize_stage, turn_right, move, get_game_result,
        show_current_state, show_legend, set_auto_render
    )
    
    print("🎮 ゲーム開始！")
    
    # ステージ初期化
    if not initialize_stage("stage01"):
        print("❌ ステージ初期化失敗")
        return
    
    # 凡例と初期状態を表示
    print("📋 ゲーム画面の見方:")
    show_legend()
    
    print("🎯 初期状態:")
    show_current_state()
    
    print("🎮 自動解法を実行します...")
    set_auto_render(True)  # 自動レンダリングをオン
    
    # 東を向いて移動
    print("➡️ 東方向へ移動中...")
    turn_right()  # 東を向く
    for i in range(4):
        move()    # 東に移動
    
    # 南を向いて移動
    print("⬇️ 南方向へ移動中...")
    turn_right()  # 南を向く
    for i in range(4):
        move()    # 南に移動
    
    # 結果表示
    result = get_game_result()
    print(f"\n🏁 最終結果: {result}")
    
    print("🎯 最終状態:")
    show_current_state()

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Python初学者向けローグライク演習フレームワーク"
    )
    parser.add_argument(
        "--cui", 
        action="store_true", 
        help="CUIモードで実行（デフォルトはGUIモード）"
    )
    parser.add_argument(
        "--gui",
        action="store_true", 
        help="GUIモードで実行"
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="stage01",
        help="実行するステージ名（デフォルト: stage01）"
    )
    
    args = parser.parse_args()
    
    # 表示モード選択
    if args.cui:
        display_mode = "cui"
    elif args.gui:
        display_mode = "gui"
    else:
        # デフォルトはGUI（pygame利用可能時）
        try:
            import pygame
            display_mode = "gui"
        except ImportError:
            display_mode = "cui"
            print("⚠️ pygame が見つかりません。CUIモードで実行します。")
    
    stage_name = args.stage
    
    logger.info(f"ローグライク演習フレームワーク開始")
    logger.info(f"表示モード: {display_mode.upper()}")
    logger.info(f"ステージ: {stage_name}")
    logger.info(f"学生ID: {config.STUDENT_ID}")
    
    print("🎮 ローグライク演習フレームワーク")
    print(f"📺 表示モード: {display_mode.upper()}")
    print(f"🎯 ステージ: {stage_name}")
    print(f"👤 学生ID: {config.STUDENT_ID}")
    print()
    print("🔥 ゲームエンジン実装完了！")
    print("solve()関数を編集してゲームを攻略してください！")
    
    # APIレイヤーを指定されたモードで初期化
    from engine.api import initialize_api
    initialize_api(display_mode)
    
    try:
        # solve()関数の実行テスト
        print("\n🔍 solve()関数を実行中...")
        solve()
        print("✅ solve()関数の実行が完了しました")
    except Exception as e:
        print(f"❌ solve()関数でエラーが発生: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 基本APIレイヤー実装完了！")
    print("📚 使用可能な学生向け関数:")
    print("  - initialize_stage(stage_id): ステージを初期化")
    print("  - turn_left(): 左に90度回転")
    print("  - turn_right(): 右に90度回転")
    print("  - move(): 正面方向に1マス移動")
    print("  - see(): 周囲の状況を確認")
    print("  - get_game_result(): ゲーム結果を取得")
    print("  - is_game_finished(): ゲーム終了判定")
    print("\n💡 より詳しい使用例は student_example.py を参照してください！")

if __name__ == "__main__":
    main()