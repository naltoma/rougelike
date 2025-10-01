"""
T020: 統合テスト - 基本的なスタミナ消費
quickstart.mdのシナリオ1を実装
"""

import pytest
from engine.api import initialize_api, initialize_stage, get_stamina, move, turn_left
from engine.hyperparameter_manager import HyperParameterManager


@pytest.fixture
def setup_stamina_system():
    """スタミナシステムを有効化"""
    hyper_manager = HyperParameterManager()
    hyper_manager.data.enable_stamina = True

    # APIを初期化（プログレス・ログ無効化）
    initialize_api(renderer_type="cui", enable_progression=False, enable_session_logging=False)

    yield

    # クリーンアップ
    hyper_manager.data.enable_stamina = False


def test_basic_stamina_consumption(setup_stamina_system):
    """基本的なスタミナ消費: 5回アクションでスタミナ0、死亡"""
    # ステージ初期化（初期スタミナ5/5）
    initialize_stage("test_stamina_basic")

    # 初期スタミナ確認
    initial_stamina = get_stamina()
    assert initial_stamina == 5, f"初期スタミナは5であるべき: {initial_stamina}"

    # 5回アクション実行
    actions = [turn_left, turn_left, turn_left, turn_left, turn_left]

    for i, action in enumerate(actions, start=1):
        action()
        current_stamina = get_stamina()
        expected = 5 - i
        assert current_stamina == expected, f"アクション{i}回後のスタミナは{expected}であるべき: {current_stamina}"

    # スタミナ0確認
    final_stamina = get_stamina()
    assert final_stamina == 0, f"最終スタミナは0であるべき: {final_stamina}"

    # 死亡確認
    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()
    assert game_state.player.hp == 0, f"スタミナ枯渇時はHP=0であるべき: {game_state.player.hp}"
    assert game_state.is_game_over(), "スタミナ枯渇時はゲームオーバーであるべき"


def test_stamina_consumption_on_failed_action(setup_stamina_system):
    """失敗したアクションでもスタミナを消費"""
    initialize_stage("test_stamina_basic")

    initial_stamina = get_stamina()

    # 壁に向かって移動（失敗するが、スタミナは消費される）
    # test_stamina_basicは10x10の空グリッドなので、端まで移動
    for _ in range(10):
        move()

    # さらに移動試行（ボード外なので失敗）
    move()

    # スタミナは消費されている
    current_stamina = get_stamina()
    assert current_stamina < initial_stamina, "失敗したアクションでもスタミナは消費されるべき"


def test_stamina_depletion_instant_death(setup_stamina_system):
    """スタミナ枯渇時の即死確認"""
    initialize_stage("test_stamina_basic")

    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    # スタミナが1以上ある間はHPが維持される
    for i in range(4):
        turn_left()
        assert game_state.player.hp == 100, f"{i+1}回目: HPは100のまま"
        assert game_state.player.stamina > 0, f"{i+1}回目: スタミナは1以上"

    # 最後のアクションでスタミナ0 → HP=0
    turn_left()
    assert game_state.player.stamina == 0, "スタミナは0"
    assert game_state.player.hp == 0, "HPは0（即死）"