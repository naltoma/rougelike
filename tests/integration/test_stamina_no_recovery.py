"""
T022: 統合テスト - 敵警戒時の回復なし
quickstart.mdのシナリオ3を実装
"""

import pytest
from engine.api import initialize_api, initialize_stage, get_stamina, move, wait, attack
from engine.hyperparameter_manager import HyperParameterManager


@pytest.fixture
def setup_stamina_system():
    """スタミナシステムを有効化"""
    hyper_manager = HyperParameterManager()
    hyper_manager.data.enable_stamina = True

    initialize_api(renderer_type="cui", enable_progression=False, enable_session_logging=False)

    yield

    hyper_manager.data.enable_stamina = False


def test_no_recovery_when_enemy_alerted(setup_stamina_system):
    """敵がアラート状態の時はwait()してもスタミナ回復なし"""
    # 敵がいるステージ
    initialize_stage("test_stamina_no_recovery")

    # 初期スタミナ確認
    initial = get_stamina()
    assert initial == 20

    # スタミナを少し消費
    for _ in range(3):
        move()

    after_moves = get_stamina()
    assert after_moves == 17, f"3回move()後のスタミナは17: {after_moves}"

    # 敵に接近して攻撃（敵をアラート状態にする）
    # test_stamina_no_recovery.ymlでは敵がvision_range=5で配置されているため
    # プレイヤーが視界内に入ると敵がアラート状態になる
    # または攻撃を受けるとアラート状態になる

    # wait()を実行（敵がアラート状態なので回復なし）
    # wait()はターン消費するので-1のみ
    wait()

    after_wait = get_stamina()
    # 敵がアラート状態の場合: 17 - 1(wait消費) + 0(回復なし) = 16
    assert after_wait == 16, f"敵アラート時のwait()後は16（回復なし）: {after_wait}"


def test_recovery_resumes_after_enemy_defeat(setup_stamina_system):
    """敵を倒した後は再びwait()で回復可能"""
    initialize_stage("test_stamina_no_recovery")

    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    # スタミナを消費
    for _ in range(5):
        move()

    assert get_stamina() == 15

    # 敵を倒す（複数回攻撃が必要な場合がある）
    # test_stamina_no_recovery.ymlの敵はhp=50なので複数回攻撃
    initial_enemy_count = len([e for e in game_state.enemies if e.is_alive()])

    # 敵を倒すまで攻撃（最大10回）
    for _ in range(10):
        attack()
        alive_enemies = [e for e in game_state.enemies if e.is_alive()]
        if len(alive_enemies) == 0:
            break

    # 敵が全滅したことを確認
    assert len([e for e in game_state.enemies if e.is_alive()]) == 0, "敵が全滅しているべき"

    # 敵がいなくなったので、wait()で回復可能
    current_stamina = get_stamina()
    wait()
    after_wait = get_stamina()

    # 敵がいない → 安全 → 回復あり
    # current_stamina - 1 + 10 (ただし上限20)
    expected = min(current_stamina - 1 + 10, 20)
    assert after_wait == expected, f"敵撃破後のwait()は回復するべき: expected={expected}, actual={after_wait}"


def test_no_recovery_during_combat(setup_stamina_system):
    """戦闘中（敵がアラート状態）はwait()で回復しない"""
    initialize_stage("test_stamina_no_recovery")

    # スタミナを消費
    for _ in range(8):
        move()

    stamina_before_wait = get_stamina()
    assert stamina_before_wait == 12

    # 敵がvision_range内にいる（アラート状態）
    from engine.api import _global_api
    game_state = _global_api.game_manager.get_current_state()

    # 敵のアラート状態を確認（実装によっては最初からアラート）
    # test_stamina_no_recovery.ymlでは敵のvision_range=5なので、
    # プレイヤーが範囲内に入ると敵がアラート状態になる

    # wait()実行（回復なし）
    wait()
    after_wait = get_stamina()

    # アラート時: 12 - 1 = 11（回復なし）
    assert after_wait == 11, f"戦闘中のwait()は回復なし: {after_wait}"