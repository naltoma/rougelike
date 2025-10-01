"""
実ゲーム環境でのスタミナ消費テスト

ENABLE_STAMINA = True の状態で、
実際にゲームを実行してスタミナ消費が機能するか確認します。
"""
import sys
import os

# Add project root to path (3 levels up: stamina -> integration -> tests -> root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

def test_stamina_consumption_in_game():
    """実ゲーム環境でのスタミナ消費確認"""
    print("=" * 60)
    print("テスト: 実ゲーム環境でのスタミナ消費確認")
    print("=" * 60)

    # 1. ENABLE_STAMINAをTrueに設定
    import main
    main.ENABLE_STAMINA = True
    print(f"\n1. ENABLE_STAMINA = {main.ENABLE_STAMINA}")

    # 2. HyperParameterManagerを取得
    from engine.hyperparameter_manager import HyperParameterManager
    hyper_manager = HyperParameterManager()

    # 3. setup_stage()と同等の処理（簡易版）
    from engine.api import initialize_api
    from engine.stage_loader import StageLoader
    from engine.game_state import GameStateManager

    print(f"\n2. ゲーム環境初期化中...")

    # APIレイヤー初期化
    initialize_api("cui")

    # スタミナシステム有効化（main.pyのsetup_stage()と同じ処理）
    hyper_manager.data.enable_stamina = main.ENABLE_STAMINA
    print(f"   ⚡ スタミナシステム: {'有効' if main.ENABLE_STAMINA else '無効'}")

    # 4. ステージロード
    loader = StageLoader()
    stage = loader.load_stage("test_stamina_basic")
    print(f"\n3. ステージロード完了: {stage.id}")
    print(f"   初期スタミナ: {stage.player_stamina}/{stage.player_max_stamina}")

    # 5. ゲーム初期化
    from engine import Board
    board = Board(
        width=stage.board_size[0],
        height=stage.board_size[1],
        walls=stage.walls,
        forbidden_cells=stage.forbidden_cells
    )

    game_manager = GameStateManager()
    game_manager.initialize_game(
        player_start=stage.player_start,
        player_direction=stage.player_direction,
        board=board,
        enemies=stage.enemies,
        items=stage.items,
        goal_position=stage.goal_position,
        player_hp=stage.player_hp if stage.player_hp is not None else 100,
        player_max_hp=stage.player_max_hp if stage.player_max_hp is not None else 100,
        player_stamina=stage.player_stamina if stage.player_stamina is not None else 20,
        player_max_stamina=stage.player_max_stamina if stage.player_max_stamina is not None else 20
    )

    initial_state = game_manager.get_current_state()
    initial_stamina = initial_state.player.stamina
    print(f"\n4. ゲーム初期化完了")
    print(f"   プレイヤー位置: {initial_state.player.position}")
    print(f"   プレイヤースタミナ: {initial_stamina}/{initial_state.player.max_stamina}")

    # 6. アクション実行テスト
    print(f"\n5. アクション実行テスト:")
    from engine.commands import MoveCommand, TurnLeftCommand

    # アクション1: move
    print(f"   [アクション1] move実行前: スタミナ={initial_state.player.stamina}")
    move_cmd = MoveCommand()
    result1 = game_manager.execute_command(move_cmd)
    state_after_move = game_manager.get_current_state()
    stamina_after_move = state_after_move.player.stamina
    print(f"   [アクション1] move実行後: スタミナ={stamina_after_move} (消費: {initial_stamina - stamina_after_move})")

    # アクション2: turn_left
    print(f"   [アクション2] turn_left実行前: スタミナ={stamina_after_move}")
    turn_cmd = TurnLeftCommand()
    result2 = game_manager.execute_command(turn_cmd)
    state_after_turn = game_manager.get_current_state()
    stamina_after_turn = state_after_turn.player.stamina
    print(f"   [アクション2] turn_left実行後: スタミナ={stamina_after_turn} (消費: {stamina_after_move - stamina_after_turn})")

    # 7. 検証
    print(f"\n6. 検証結果:")
    success = True

    # 検証1: スタミナシステムが有効
    if not hyper_manager.data.enable_stamina:
        print("   ❌ スタミナシステムが有効になっていない")
        success = False
    else:
        print("   ✅ スタミナシステムが有効")

    # 検証2: 初期スタミナが正しい
    if initial_stamina != 5:
        print(f"   ❌ 初期スタミナが期待値(5)と異なる: {initial_stamina}")
        success = False
    else:
        print(f"   ✅ 初期スタミナが正しい: {initial_stamina}")

    # 検証3: moveでスタミナ消費
    move_consumption = initial_stamina - stamina_after_move
    if move_consumption != 1:
        print(f"   ❌ move のスタミナ消費が期待値(1)と異なる: {move_consumption}")
        success = False
    else:
        print(f"   ✅ move でスタミナ消費が正しい: {move_consumption}")

    # 検証4: turn_leftでスタミナ消費
    turn_consumption = stamina_after_move - stamina_after_turn
    if turn_consumption != 1:
        print(f"   ❌ turn_left のスタミナ消費が期待値(1)と異なる: {turn_consumption}")
        success = False
    else:
        print(f"   ✅ turn_left でスタミナ消費が正しい: {turn_consumption}")

    # 検証5: 合計消費量
    total_consumption = initial_stamina - stamina_after_turn
    if total_consumption != 2:
        print(f"   ❌ 合計スタミナ消費が期待値(2)と異なる: {total_consumption}")
        success = False
    else:
        print(f"   ✅ 合計スタミナ消費が正しい: {total_consumption}")

    print("\n" + "=" * 60)
    if success:
        print("✅ テスト成功: 実ゲーム環境でスタミナ消費が正しく機能しています")
        print("\n📝 確認された機能:")
        print("   • ENABLE_STAMINA フラグの有効化")
        print("   • ステージYAMLからのスタミナ読み込み")
        print("   • ゲーム初期化時のスタミナ設定")
        print("   • move, turn_left コマンドでのスタミナ消費 (-1)")
        print("\n🎮 ユーザーは main_hoge4.py で以下を設定するだけでOKです:")
        print("   ENABLE_STAMINA = True")
    else:
        print("❌ テスト失敗: スタミナ消費に問題があります")
    print("=" * 60)

    return success

if __name__ == "__main__":
    try:
        success = test_stamina_consumption_in_game()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)