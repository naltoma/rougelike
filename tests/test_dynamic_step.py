#!/usr/bin/env python3
"""
動的solve()解析によるステップ実行のテスト
"""

import sys

def test_dynamic_step_execution():
    """動的ステップ実行をテスト"""
    print("🧪 動的ステップ実行テスト開始")
    
    # main.pyから必要な関数をインポート
    sys.path.insert(0, '.')
    from main import solve, _initialize_solve_parser, _execute_solve_step
    import main
    
    # solve()関数解析の初期化
    print("🔍 solve()関数を解析中...")
    if not _initialize_solve_parser():
        print("❌ solve()解析に失敗しました")
        return False
    
    print(f"✅ solve()解析完了: {main.solve_parser.total_steps}ステップ検出")
    
    # APIレイヤー初期化
    from engine.api import initialize_api, initialize_stage
    initialize_api("cui")
    
    if not initialize_stage("stage01"):
        print("❌ ステージ初期化失敗")
        return False
        
    print("✅ ステージ初期化完了")
    
    # 各ステップを実行
    print(f"\n🎮 {main.solve_parser.total_steps}ステップの動的実行開始:")
    
    for step in range(1, main.solve_parser.total_steps + 1):
        print(f"\n--- ステップ {step}/{main.solve_parser.total_steps} ---")
        success = _execute_solve_step(step)
        if not success:
            print(f"❌ ステップ {step} で失敗しました")
            break
        
        # ゲーム状態確認
        from engine.api import get_game_result
        result = get_game_result()
        print(f"   ゲーム状態: {result}")
        
        if "ゴール到達" in result or "ゲームクリア" in result:
            print("🎉 ゲームクリア!")
            break
    
    # 最終結果確認
    print(f"\n📊 最終結果:")
    final_result = get_game_result()
    print(f"   ゲーム結果: {final_result}")
    
    # セッションログ確認
    from engine.api import _global_api
    if _global_api and _global_api.action_tracker:
        action_count = _global_api.action_tracker.get_action_count()
        print(f"   実行アクション数: {action_count}")
    
    print("✅ 動的ステップ実行テスト完了")
    
    # ゲームがクリアされなかったことを確認
    if "ゲーム継続中" in final_result:
        print("🎯 期待通り: solve()の現在の実装ではゲームクリアしない")
        return True
    elif "ゴール到達" in final_result:
        print("⚠️ 予期しない結果: ゲームがクリアされてしまいました")
        print("   これは動的解析が正しく機能していない可能性があります")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = test_dynamic_step_execution()
        if success:
            print("\n🎉 テスト成功: 動的solve()解析によるステップ実行が正常に動作")
        else:
            print("\n❌ テスト失敗: 動的解析に問題があります")
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()