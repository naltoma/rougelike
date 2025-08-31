#!/usr/bin/env python3
"""
学生向けサンプルスクリプト
ローグライクゲームの基本的な使用例
"""

# ゲームAPI関数をインポート
from engine.api import (
    initialize_api, initialize_stage, turn_left, turn_right, move, see,
    is_game_finished, get_game_result, get_call_history,
    show_current_state, set_auto_render, show_legend, show_action_history,
    set_student_id, show_progress_summary, get_progress_report, 
    get_learning_recommendations, use_hint
)


def solve(use_gui=False):
    """
    学生が実装するべき関数
    この関数内でゲームをクリアするアルゴリズムを実装してください
    
    Args:
        use_gui: Trueの場合GUIモードを使用
    """
    print("🎮 ゲーム開始！")
    
    # APIを初期化（CUI または GUI）
    if use_gui:
        print("📺 GUIモードで初期化します...")
        initialize_api("gui")
    else:
        print("📺 CUIモードで初期化します...")
        initialize_api("cui")
    
    # ステージを初期化
    if not initialize_stage("stage01"):
        print("❌ ステージの初期化に失敗しました")
        return
    
    # 凡例を表示
    print("📋 ゲーム画面の見方:")
    show_legend()
    
    # 初期状態を視覚的に表示
    print("🎯 初期状態:")
    show_current_state()
    
    # 自動レンダリングをオンにして視覚的にプレイ
    print("\n🖼️ 視覚的モードでプレイを開始...")
    set_auto_render(True)
    
    # 簡単な解法例: 東に移動してから南に移動
    # stage01: 開始(0,0) → ゴール(4,4)
    
    # 東を向く（初期は北向き）
    print("🔄 東を向きます...")
    turn_right()
    
    # 東に4回移動
    print("➡️ 東方向に移動...")
    for i in range(4):
        if move():
            current_info = see()
            pos = current_info['player']['position']
            print(f"   位置: {pos}")
        else:
            print("   移動失敗")
            break
    
    # 南を向く
    print("🔄 南を向きます...")
    turn_right()
    
    # 南に移動（壁を避けながら）
    print("⬇️ 南方向に移動...")
    for i in range(4):
        current_info = see()
        
        # 正面の状況をチェック
        front_situation = current_info['surroundings']['front']
        
        if front_situation == "wall":
            print("   壁を発見。迂回します...")
            use_hint()  # ヒント使用を記録
            # 迂回ロジック
            turn_left()   # 東を向く
            if move():
                print("   東に迂回移動")
            turn_right()  # 南を向く
        
        if move():
            pos = current_info['player']['position']
            print(f"   位置: {pos}")
        else:
            print("   移動失敗")
            
        # ゲーム終了チェック
        if is_game_finished():
            break
    
    # 最終結果
    print("\n📊 ゲーム結果:")
    result = get_game_result()
    print(f"結果: {result}")
    
    # 最終状態を表示
    print("\n🎯 最終状態:")
    show_current_state()
    
    # アクション履歴を表示
    print("\n📜 実行したアクション履歴:")
    show_action_history()
    
    # 進捗情報を表示
    print("\n📊 学習進捗:")
    show_progress_summary()


def solve_interactive(use_gui=False):
    """
    対話的な解法例
    ユーザーの入力を受けながら進める
    
    Args:
        use_gui: Trueの場合GUIモードを使用
    """
    print("🎮 対話的ゲーム開始！")
    print("コマンド: l=左回転, r=右回転, m=移動, s=状況確認, q=終了")
    
    # APIを初期化
    initialize_api("gui" if use_gui else "cui")
    
    if not initialize_stage("stage01"):
        print("❌ ステージの初期化に失敗しました")
        return
    
    while not is_game_finished():
        # 現在の状況表示
        info = see()
        print(f"\n現在位置: {info['player']['position']}, 向き: {info['player']['direction']}")
        print(f"残りターン: {info['game_status']['remaining_turns']}")
        
        # ユーザー入力
        command = input("コマンドを入力 > ").lower().strip()
        
        if command == 'q':
            break
        elif command == 'l':
            if turn_left():
                print("⬅️ 左回転しました")
            else:
                print("❌ 左回転に失敗しました")
        elif command == 'r':
            if turn_right():
                print("➡️ 右回転しました")
            else:
                print("❌ 右回転に失敗しました")
        elif command == 'm':
            if move():
                print("🚶 移動しました")
            else:
                print("❌ 移動に失敗しました")
        elif command == 's':
            info = see()
            print("周囲の状況:")
            for direction, content in info['surroundings'].items():
                print(f"  {direction}: {content}")
        else:
            print("無効なコマンドです")
    
    # 最終結果
    result = get_game_result()
    print(f"\n🏁 ゲーム終了: {result}")


def solve_stage02(use_gui=False):
    """
    Stage02の解法例（迷路）
    
    Args:
        use_gui: Trueの場合GUIモードを使用
    """
    print("🎮 Stage02: 迷路ナビゲーション")
    
    # APIを初期化
    initialize_api("gui" if use_gui else "cui")
    
    if not initialize_stage("stage02"):
        print("❌ ステージの初期化に失敗しました")
        return
    
    print("🧭 右手法で迷路を攻略します...")
    
    # 右手法（右手を壁につけて進む）アルゴリズム
    turn_count = 0
    max_turns = 100  # 無限ループ防止
    
    while not is_game_finished() and turn_count < max_turns:
        info = see()
        
        # 右側をチェック
        right_situation = info['surroundings']['right']
        front_situation = info['surroundings']['front']
        
        if right_situation not in ["wall", "boundary"]:
            # 右側に進路があれば右に回転して前進
            turn_right()
            move()
            print("🔄➡️ 右手法: 右に回転して前進")
        elif front_situation not in ["wall", "boundary"]:
            # 正面に進路があれば前進
            move()
            print("⬆️ 右手法: 直進")
        else:
            # 行き止まりなので左に回転
            turn_left()
            print("🔄⬅️ 右手法: 左に回転")
        
        turn_count += 1
    
    result = get_game_result()
    print(f"\n🏁 Stage02結果: {result}")
    print(f"使用ターン数: {turn_count}")


def demonstrate_features(use_gui=False):
    """
    フレームワークの機能をデモンストレーション
    
    Args:
        use_gui: Trueの場合GUIモードを使用
    """
    print("🧪 フレームワーク機能デモ")
    
    # APIを初期化
    initialize_api("gui" if use_gui else "cui")
    
    # 複数ステージのテスト
    for stage_id in ["stage01", "stage02", "stage03"]:
        print(f"\n📂 {stage_id} をテスト...")
        
        if initialize_stage(stage_id):
            info = see()
            print(f"  開始位置: {info['player']['position']}")
            print(f"  開始方向: {info['player']['direction']}")
            print(f"  最大ターン: {info['game_status']['max_turns']}")
            
            # 少し動いてみる
            turn_right()
            if move():
                print("  移動テスト: ✅")
            else:
                print("  移動テスト: ❌")
        else:
            print(f"  ❌ {stage_id} の初期化に失敗")


def demonstrate_progression_features():
    """進捗管理機能のデモンストレーション"""
    print("📊 進捗管理機能デモ")
    print("=" * 50)
    
    # API初期化（進捗管理有効）
    initialize_api("cui", enable_progression=True)
    
    # 学生IDを設定（実際の使用時は学生の実際のIDを使用）
    set_student_id("demo_student_001")
    
    # 複数回のステージ挑戦をシミュレート
    for attempt in range(3):
        print(f"\n🎯 挑戦 {attempt + 1}")
        
        if initialize_stage("stage01"):
            # 異なる効率性でプレイ
            turn_right()
            
            if attempt == 0:
                # 1回目: 非効率的
                print("非効率的なプレイ...")
                for i in range(6):
                    move()
                turn_right()
                for i in range(6):
                    move()
            elif attempt == 1:
                # 2回目: 普通
                print("普通のプレイ...")
                for i in range(4):
                    move()
                turn_right()
                for i in range(4):
                    move()
            else:
                # 3回目: 効率的
                print("効率的なプレイ...")
                for i in range(4):
                    move()
                turn_right()
                for i in range(4):
                    move()
    
    # 最終進捗表示
    print("\n📊 最終学習進捗:")
    show_progress_summary()
    
    # 推奨事項表示
    recommendations = get_learning_recommendations()
    if recommendations:
        print("\n💡 AI からの学習推奨事項:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # ステージ別レポート
    stage_report = get_progress_report("stage01")
    if stage_report:
        print(f"\n📈 Stage01 詳細レポート:")
        print(f"  挑戦回数: {stage_report.get('total_attempts', 0)}")
        print(f"  成功率: {stage_report.get('success_rate', 0):.1%}")
        print(f"  最高効率性: {stage_report.get('best_efficiency', 0):.1%}")
        print(f"  改善率: {stage_report.get('improvement_rate', 0):.1%}")
    
    print("\n✨ 進捗管理機能デモ完了")
    print("💡 実際の授業では、この機能により学生の学習状況を詳細に追跡できます。")


if __name__ == "__main__":
    print("=" * 50)
    print("🎓 Python初学者向けローグライクフレームワーク")
    print("=" * 50)
    
    print("\n使用可能な関数:")
    print("- solve(use_gui=False): 自動解法の例")
    print("- solve_interactive(use_gui=False): 対話的ゲーム")
    print("- solve_stage02(use_gui=False): Stage02攻略例")
    print("- demonstrate_features(use_gui=False): 機能デモ")
    print("- demonstrate_progression_features(): 進捗管理機能デモ")
    print("\n💡 use_gui=True にするとGUIモードで実行されます")
    print("💡 進捗管理機能により学習の進歩を追跡できます")
    
    print("\n🎯 基本的な自動解法を実行します...")
    
    # GUIモードが利用可能かチェック
    try:
        import pygame
        use_gui_mode = True
        print("🎮 GUIモードで実行します")
    except ImportError:
        use_gui_mode = False
        print("📺 CUIモードで実行します")
    
    solve(use_gui=use_gui_mode)
    
    print("\n" + "=" * 50)
    print("💡 このスクリプトを参考に、独自の解法を実装してみましょう！")
    print("💡 solve() 関数を編集して、より効率的なアルゴリズムを作ってください。")
    print("💡 GUIモード: solve(use_gui=True)")
    print("💡 CUIモード: solve(use_gui=False)")
    print("=" * 50)