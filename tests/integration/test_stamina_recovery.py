"""
T021: 統合テスト - スタミナ回復
quickstart.mdのシナリオ2を実装
"""

import pytest
from engine.api import initialize_api, initialize_stage, get_stamina, move, wait
from engine.hyperparameter_manager import HyperParameterManager


@pytest.fixture
def setup_stamina_system():
    """スタミナシステムを有効化"""
    hyper_manager = HyperParameterManager()
    hyper_manager.data.enable_stamina = True

    initialize_api(renderer_type="cui", enable_progression=False, enable_session_logging=False)

    yield

    hyper_manager.data.enable_stamina = False


def test_stamina_recovery_with_wait(setup_stamina_system):
    """wait()でのスタミナ回復（敵なし・安全な状況）"""
    # 敵のいないステージ（初期スタミナ20/20）
    initialize_stage("test_stamina_recovery")

    initial_stamina = get_stamina()
    assert initial_stamina == 20, f"初期スタミナは20であるべき: {initial_stamina}"

    # 5回move()でスタミナ消費
    for _ in range(5):
        move()

    after_moves = get_stamina()
    assert after_moves == 15, f"5回move()後のスタミナは15であるべき: {after_moves}"

    # wait()で回復（敵なし → 安全 → +10回復だが、wait自体も-1消費するので net +9）
    # 実際: 15 - 1(wait消費) + 10(回復) = 24だが、max_stamina=20なので20
    wait()

    after_wait = get_stamina()
    assert after_wait == 20, f"wait()後のスタミナは20（上限）であるべき: {after_wait}"


def test_stamina_recovery_cap_at_max(setup_stamina_system):
    """スタミナ回復は最大値を超えない"""
    initialize_stage("test_stamina_recovery")

    # 既に満タン（20/20）
    initial = get_stamina()
    assert initial == 20

    # wait()しても20のまま
    wait()
    after_wait = get_stamina()
    # wait()自体が-1消費、その後+10回復で19になる
    # ただし、満タン時のwait()の挙動によっては変わる可能性があるため確認
    # 実装仕様: wait()はまずターン消費でスタミナ-1、その後安全なら+10回復
    # 20 - 1 = 19、その後 19 + 10 = 29だが上限20なので20
    assert after_wait == 20, f"満タン時のwait()後も20であるべき: {after_wait}"


def test_multiple_wait_recovery(setup_stamina_system):
    """複数回wait()での段階的回復"""
    initialize_stage("test_stamina_recovery")

    # 10回move()でスタミナ消費
    for _ in range(10):
        move()

    after_moves = get_stamina()
    assert after_moves == 10, f"10回move()後のスタミナは10であるべき: {after_moves}"

    # 1回目のwait(): 10 - 1 + 10 = 19
    wait()
    assert get_stamina() == 19, "1回目wait()後は19"

    # 2回目のwait(): 19 - 1 + 10 = 28 → 上限20
    wait()
    assert get_stamina() == 20, "2回目wait()後は20（上限）"

    # 3回目のwait(): 20 - 1 + 10 = 29 → 上限20
    wait()
    assert get_stamina() == 20, "3回目wait()後も20（上限維持）"


def test_stamina_recovery_after_near_depletion(setup_stamina_system):
    """スタミナほぼ枯渇後の回復"""
    initialize_stage("test_stamina_recovery")

    # 19回move()でスタミナ1まで消費
    for _ in range(19):
        move()

    assert get_stamina() == 1, "スタミナは1"

    # wait()で回復: 1 - 1 + 10 = 10
    wait()
    assert get_stamina() == 10, "wait()後はスタミナ10"

    # さらに回復確認
    wait()
    assert get_stamina() == 19, "2回目wait()後はスタミナ19"