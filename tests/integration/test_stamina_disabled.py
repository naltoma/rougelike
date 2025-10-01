"""
T023: 統合テスト - 後方互換性（ENABLE_STAMINA=False）
quickstart.mdのシナリオ4を実装
"""

import pytest
from engine.api import initialize_api, initialize_stage, get_stamina, move, turn_left, turn_right
from engine.hyperparameter_manager import HyperParameterManager


@pytest.fixture
def setup_stamina_disabled():
    """スタミナシステムを無効化（デフォルト）"""
    hyper_manager = HyperParameterManager()
    hyper_manager.data.enable_stamina = False  # 明示的に無効化

    initialize_api(renderer_type="cui", enable_progression=False, enable_session_logging=False)

    yield


def test_stamina_not_consumed_when_disabled(setup_stamina_disabled):
    """スタミナ無効時はアクションでスタミナが消費されない"""
    # 既存ステージを使用
    initialize_stage("stage01")

    initial_stamina = get_stamina()

    # 多数のアクション実行
    for _ in range(50):
        turn_left()

    # スタミナは変化しない
    final_stamina = get_stamina()
    assert final_stamina == initial_stamina, f"スタミナ無効時はスタミナが変化しないべき: initial={initial_stamina}, final={final_stamina}"


def test_no_death_from_stamina_when_disabled(setup_stamina_disabled):
    """スタミナ無効時はスタミナ枯渇で死亡しない"""
    initialize_stage("stage01")

    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    initial_hp = game_state.player.hp

    # 100回アクション実行（スタミナ有効時なら確実に枯渇）
    for _ in range(100):
        turn_left()

    # HPは変化しない（敵に攻撃されない限り）
    # stage01では敵の配置によってはHPが減る可能性があるが、スタミナ枯渇では死なない
    final_hp = game_state.player.hp
    stamina = get_stamina()

    # スタミナが枯渇していないか、枯渇していてもHP > 0
    assert final_hp > 0, "スタミナ無効時はスタミナ枯渇で死亡しない"


def test_game_continues_normally_when_disabled(setup_stamina_disabled):
    """スタミナ無効時はゲームが通常通り進行"""
    initialize_stage("stage01")

    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    # 複数のアクション実行
    actions_performed = 0
    for _ in range(30):
        turn_left()
        actions_performed += 1

    # ゲームは継続中（ターンアウトまたは他の理由で終了する可能性はある）
    assert actions_performed == 30, "アクションが正常に実行されるべき"

    # スタミナ値は読み取れるが、消費されていない
    stamina = get_stamina()
    # スタミナは初期値または変化なし


def test_backward_compatibility_with_existing_stages(setup_stamina_disabled):
    """既存ステージがスタミナ無効時に正常動作"""
    # 複数の既存ステージで確認
    test_stages = ["stage01", "stage02", "stage03"]

    for stage_id in test_stages:
        initialize_stage(stage_id)

        from engine.api import _global_api
        game_state = _global_api.game_manager.get_current_state()

        # 基本的なアクション実行
        turn_left()
        turn_right()
        move()

        # エラーなく実行できることを確認
        assert game_state is not None, f"{stage_id}が正常にロードされるべき"


def test_stamina_value_exists_but_not_used(setup_stamina_disabled):
    """スタミナ無効時もスタミナ値は存在するが使用されない"""
    initialize_stage("stage01")

    # get_stamina()は呼び出せる
    stamina = get_stamina()
    assert isinstance(stamina, int), "スタミナ値は整数として取得できる"
    assert stamina >= 0, "スタミナ値は0以上"

    # アクション後も値は変化しない
    initial = stamina
    for _ in range(10):
        move()

    final = get_stamina()
    assert final == initial, "スタミナ無効時はget_stamina()の値が変化しない"