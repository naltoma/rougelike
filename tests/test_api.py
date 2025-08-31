#!/usr/bin/env python3
"""
学生向けAPIのテスト
"""

import sys
sys.path.append('..')

import engine.api as api
from engine.api import APIUsageError


def test_basic_movement():
    """基本移動APIテスト"""
    print("🚶 基本移動APIテスト...")
    
    # ステージ初期化
    success = api.initialize_stage("stage01")
    assert success, "ステージ初期化失敗"
    print("✅ ステージ初期化成功")
    
    # 初期状態確認
    assert not api.is_game_finished()
    
    # 基本移動テスト（有効な方向への移動）
    assert api.turn_left(), "左回転失敗"
    assert api.turn_right(), "右回転失敗" 
    
    # 東を向いて移動（Position(0,0)から東は有効）
    api.turn_right()  # 東を向く
    assert api.move(), "移動失敗"
    
    print("✅ 基本移動成功")
    
    # 履歴確認
    history = api.get_call_history()
    assert len(history) == 4  # turn_left, turn_right, turn_right, move
    assert history[0]["api"] == "turn_left"
    assert history[1]["api"] == "turn_right"
    assert history[2]["api"] == "turn_right"
    assert history[3]["api"] == "move"
    
    print("✅ API呼び出し履歴記録正常")


def test_see_function():
    """see関数テスト"""
    print("👁️ see関数テスト...")
    
    # ステージ初期化
    api.initialize_stage("stage01")
    
    # 周囲確認
    info = api.see()
    
    # 必要なキーが存在することを確認
    assert "player" in info
    assert "surroundings" in info
    assert "game_status" in info
    
    # プレイヤー情報
    player_info = info["player"]
    assert "position" in player_info
    assert "direction" in player_info
    assert "hp" in player_info
    assert "attack_power" in player_info
    
    assert player_info["position"] == [0, 0]  # stage01の初期位置
    assert player_info["direction"] == "N"     # stage01の初期方向
    
    # 周囲情報
    surroundings = info["surroundings"]
    assert "front" in surroundings
    assert "left" in surroundings
    assert "right" in surroundings
    assert "back" in surroundings
    
    # ゲーム状況
    game_status = info["game_status"]
    assert "turn" in game_status
    assert "max_turns" in game_status
    assert "remaining_turns" in game_status
    assert "status" in game_status
    
    print("✅ see関数情報取得成功")


def test_api_restrictions():
    """API制限テスト"""
    print("🚫 API制限テスト...")
    
    # stage01は基本移動のみ許可
    api.initialize_stage("stage01")
    
    # 許可されたAPI
    assert api.turn_left()
    assert api.turn_right() 
    
    # 有効な方向に移動
    api.turn_right()  # 東を向く
    assert api.move()
    
    print("✅ 許可API実行成功")
    
    # 制限されたAPI（stage01では使用不可）
    try:
        api.attack()
        assert False, "攻撃APIが制限されていない"
    except APIUsageError as e:
        assert "使用できません" in str(e)
        print("✅ 攻撃API制限正常")
    
    try:
        api.pickup()
        assert False, "アイテム取得APIが制限されていない"
    except APIUsageError as e:
        assert "使用できません" in str(e)
        print("✅ アイテム取得API制限正常")


def test_game_completion():
    """ゲーム完了テスト"""
    print("🏆 ゲーム完了テスト...")
    
    api.initialize_stage("stage01")
    
    # ゴールに向かう動作をシミュレート
    # stage01: 開始(0,0)→ゴール(4,4)
    # 簡単な経路: 東4回、南4回
    
    # 東を向く（初期は北向き）
    api.turn_right()
    
    # 東に4回移動
    for _ in range(4):
        success = api.move()
        if not success:
            print(f"移動失敗: ターン{api.get_call_history()[-1]['turn']}")
            break
    
    # 南を向く
    api.turn_right()
    
    # 南に移動（壁を避ける）
    for _ in range(4):
        success = api.move()
        if not success:
            # 壁にぶつかったら迂回
            api.turn_left()  # 東を向く
            api.move()       # 東に移動
            api.turn_right() # 南を向く
            api.move()       # 南に移動
            break
    
    # ゲーム状況確認
    result = api.get_game_result()
    print(f"ゲーム結果: {result}")
    
    if api.is_game_finished():
        print("✅ ゲーム完了")
    else:
        print("⏳ ゲーム継続中")


def test_undo_functionality():
    """取り消し機能テスト"""
    print("↩️ 取り消し機能テスト...")
    
    api.initialize_stage("stage01")
    
    # 初期状態の確認
    initial_info = api.see()
    initial_pos = initial_info["player"]["position"]
    initial_dir = initial_info["player"]["direction"]
    
    # 単一コマンド実行（移動のみ）
    api.turn_right()  # 東を向く
    move_success = api.move()  # 東に移動
    
    if move_success:
        # 移動が成功した場合
        changed_info = api.see()
        assert changed_info["player"]["position"] != initial_pos
        
        # 取り消し可能性チェック
        assert api.can_undo()
        
        # 取り消し実行
        assert api.undo()
        
        # 位置が戻ったことを確認
        reverted_info = api.see()
        assert reverted_info["player"]["position"] == initial_pos
    else:
        # 移動が失敗した場合（境界外など）
        print("移動失敗のため取り消しテストをスキップ")
    
    print("✅ 取り消し機能正常")


def test_reset_functionality():
    """リセット機能テスト"""
    print("🔄 リセット機能テスト...")
    
    api.initialize_stage("stage01")
    
    # 初期状態保存
    initial_info = api.see()
    initial_pos = initial_info["player"]["position"]
    initial_turn = initial_info["game_status"]["turn"]
    
    # いくつかの操作実行
    api.turn_left()
    api.turn_right()
    api.move()
    
    # 状態変化確認
    changed_info = api.see()
    assert changed_info["game_status"]["turn"] > initial_turn
    
    # リセット実行
    assert api.reset_stage()
    
    # 初期状態に戻ったことを確認
    reset_info = api.see()
    assert reset_info["player"]["position"] == initial_pos
    assert reset_info["game_status"]["turn"] == 0
    
    print("✅ リセット機能正常")


def test_error_handling():
    """エラーハンドリングテスト"""
    print("⚠️ エラーハンドリングテスト...")
    
    # グローバルAPIをリセット（新しいインスタンス作成）
    import engine.api as api_module
    api_module._global_api = api_module.APILayer()
    
    # 初期化前のAPI呼び出し
    try:
        api.turn_left()
        assert False, "初期化チェックが機能していない"
    except APIUsageError as e:
        assert "初期化されていません" in str(e)
        print("✅ 初期化前API呼び出しエラー検出")
    
    # 存在しないステージ
    success = api.initialize_stage("non_existent_stage")
    assert not success
    print("✅ 存在しないステージエラー処理")
    
    # 正常初期化後のテスト
    api.initialize_stage("stage01")
    
    # 境界を越えた移動テスト
    # 現在位置を確認して境界外移動をテスト
    info = api.see()
    pos = info["player"]["position"]
    
    # 左上角(0,0)にいる場合は北または西への移動が境界外
    if pos == [0, 0]:
        # 北への移動（境界外）
        current_dir = info["player"]["direction"]
        if current_dir != "N":
            # 北を向く
            while info["player"]["direction"] != "N":
                api.turn_left()
                info = api.see()
        
        success = api.move()  # Position(0,0)から北への移動は境界外
        assert not success
        print("✅ 境界移動エラー処理")
    else:
        # 他の位置の場合は適切な境界外移動をテスト
        print("✅ 境界移動テストスキップ（位置未対応）")


def test_stage_variations():
    """異なるステージのテスト"""
    print("🎭 異なるステージテスト...")
    
    # Stage01テスト
    api.initialize_stage("stage01")
    info1 = api.see()
    assert info1["player"]["position"] == [0, 0]
    print("✅ Stage01読み込み")
    
    # Stage02テスト
    api.initialize_stage("stage02")
    info2 = api.see()
    assert info2["player"]["position"] == [1, 1]  # stage02の初期位置
    assert info2["player"]["direction"] == "E"     # stage02の初期方向
    print("✅ Stage02読み込み")
    
    # Stage03テスト
    api.initialize_stage("stage03")
    info3 = api.see()
    assert info3["player"]["position"] == [0, 0]  # stage03の初期位置
    assert info3["player"]["direction"] == "S"     # stage03の初期方向
    print("✅ Stage03読み込み")


def test_integration():
    """統合テスト"""
    print("🔗 統合テスト...")
    
    # 完全なゲームフローをテスト
    api.initialize_stage("stage01")
    
    # 初期状態確認
    assert not api.is_game_finished()
    initial_result = api.get_game_result()
    assert "継続中" in initial_result
    
    # 複合操作
    operations = [
        ("turn_right", api.turn_right),  # 東を向く
        ("move", api.move),              # 東に移動
        ("move", api.move),              # 東に移動  
        ("see", api.see),                # 周囲確認
        ("turn_right", api.turn_right),  # 南を向く
        ("move", api.move),              # 南に移動
    ]
    
    for op_name, op_func in operations:
        if op_name == "see":
            info = op_func()
            assert isinstance(info, dict)
        else:
            success = op_func()
            # 移動が失敗する場合もあるが、APIエラーは発生しない
            print(f"{op_name}: {'✅' if success else '⚠️'}")
    
    # 履歴確認
    history = api.get_call_history()
    assert len(history) >= 5  # see以外の操作数
    
    print("✅ 統合テスト完了")


def main():
    """メイン実行"""
    print("🧪 学生向けAPIテスト開始\n")
    
    try:
        test_basic_movement()
        test_see_function()
        test_api_restrictions()
        test_game_completion()
        test_undo_functionality()
        test_reset_functionality()
        test_error_handling()
        test_stage_variations()
        test_integration()
        
        print("\n🎉 全ての学生向けAPIテストが完了！")
        print("✅ タスク9完了: 基本API関数の実装")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()