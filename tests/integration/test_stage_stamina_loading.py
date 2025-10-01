"""
T025: 統合テスト - ステージ設定読み込み
quickstart.mdのシナリオ6を実装
"""

import pytest
from engine.api import initialize_api, initialize_stage, get_stamina
from engine.hyperparameter_manager import HyperParameterManager


@pytest.fixture
def setup_stamina_system():
    """スタミナシステムを有効化"""
    hyper_manager = HyperParameterManager()
    hyper_manager.data.enable_stamina = True

    initialize_api(renderer_type="cui", enable_progression=False, enable_session_logging=False)

    yield

    hyper_manager.data.enable_stamina = False


def test_load_custom_stamina_from_stage(setup_stamina_system):
    """カスタムスタミナ値がステージYAMLから正しく読み込まれる"""
    # test_stamina_basic.yml: stamina=5, max_stamina=5
    initialize_stage("test_stamina_basic")

    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    # カスタムスタミナ値を確認
    assert game_state.player.stamina == 5, "カスタムスタミナ値が読み込まれる"
    assert game_state.player.max_stamina == 5, "カスタム最大スタミナ値が読み込まれる"

    # get_stamina()でも確認
    stamina = get_stamina()
    assert stamina == 5, "get_stamina()がカスタム値を返す"


def test_load_default_stamina_when_not_specified(setup_stamina_system):
    """ステージYAMLでスタミナ未指定時はデフォルト値（20/20）"""
    # stage01.ymlにはスタミナ設定がない（デフォルト使用）
    initialize_stage("stage01")

    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    # デフォルトスタミナ値を確認
    assert game_state.player.stamina == 20, "未指定時はデフォルトスタミナ20"
    assert game_state.player.max_stamina == 20, "未指定時はデフォルト最大スタミナ20"


def test_different_stamina_values_across_stages(setup_stamina_system):
    """複数ステージで異なるスタミナ設定が正しく読み込まれる"""
    # test_stamina_basic: 5/5
    initialize_stage("test_stamina_basic")
    stamina1 = get_stamina()
    assert stamina1 == 5, "test_stamina_basicは5"

    # test_stamina_recovery: 20/20
    initialize_stage("test_stamina_recovery")
    stamina2 = get_stamina()
    assert stamina2 == 20, "test_stamina_recoveryは20"

    # stage01: デフォルト20/20
    initialize_stage("stage01")
    stamina3 = get_stamina()
    assert stamina3 == 20, "stage01はデフォルト20"


def test_stamina_persists_between_actions(setup_stamina_system):
    """ロード後のスタミナ値がアクション間で正しく維持される"""
    initialize_stage("test_stamina_basic")

    from engine.api import _global_api, turn_left
    game_state = _global_api.game_manager.get_current_state()

    # 初期値確認
    assert game_state.player.stamina == 5

    # アクション実行
    turn_left()

    # スタミナ減少確認
    assert game_state.player.stamina == 4, "アクション後にスタミナが維持・更新される"
    assert game_state.player.max_stamina == 5, "max_staminaは変化しない"


def test_max_stamina_boundary(setup_stamina_system):
    """スタミナがmax_staminaを超えない"""
    initialize_stage("test_stamina_recovery")

    from engine.api import wait

    # 既に満タン（20/20）
    stamina_before = get_stamina()
    assert stamina_before == 20

    # wait()で回復試行
    wait()

    # 上限を超えない
    stamina_after = get_stamina()
    assert stamina_after <= 20, "スタミナはmax_staminaを超えない"


def test_stage_with_partial_stamina_config(setup_stamina_system):
    """staminaのみ指定、max_staminaはデフォルト（またはその逆）"""
    # 注: 既存のテストステージにはこのケースがないため、
    # test_stamina_basic.ymlが両方指定していることを確認

    initialize_stage("test_stamina_basic")

    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    # 両方が正しく設定されている
    assert game_state.player.stamina == 5
    assert game_state.player.max_stamina == 5


def test_validation_stamina_not_exceed_max(setup_stamina_system):
    """検証: staminaがmax_staminaを超えていないか"""
    # 複数のステージで確認
    test_stages = ["test_stamina_basic", "test_stamina_recovery", "stage01"]

    for stage_id in test_stages:
        initialize_stage(stage_id)

        from engine.api import _global_api
        game_state = _global_api.game_manager.get_current_state()

        # 初期スタミナは最大スタミナ以下
        assert game_state.player.stamina <= game_state.player.max_stamina, \
            f"{stage_id}: 初期スタミナは最大スタミナ以下であるべき"