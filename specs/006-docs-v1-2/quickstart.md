# Quickstart: Stamina System (v1.2.13)

**Date**: 2025-09-30
**Purpose**: End-to-end validation of stamina system functionality
**Target User**: Developers testing the implementation

---

## Prerequisites

1. Python 3.11+ installed
2. Repository cloned and dependencies installed
3. All tests passing (contract + integration + unit)

---

## Quickstart Scenario 1: Basic Stamina Consumption

**Goal**: Verify stamina decreases on actions and player dies when stamina reaches 0

### Setup

1. Create test stage: `stages/test_stamina_basic.yml`
```yaml
name: "Stamina Test - Basic"
width: 10
height: 10
max_turns: 100

cells:
  - [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

player:
  start: [5, 2]
  direction: N
  hp: 100
  max_hp: 100
  stamina: 5        # Low stamina for quick test
  max_stamina: 5

items: []
enemies: []
```

2. Create test script: `test_quickstart_stamina.py`
```python
from engine.api import (
    initialize, move, turn_left, turn_right, get_stamina,
    get_stage_info, is_game_over
)
from engine.hyperparameter_manager import HyperParameterManager

def test_basic_stamina_consumption():
    """基本的なスタミナ消費テスト"""
    # Enable stamina system
    hyperparameters = HyperParameterManager()
    hyperparameters.data.enable_stamina = True

    # Initialize game
    initialize("stages/test_stamina_basic.yml", hyperparameters)

    # Step 1: Check initial stamina
    stamina = get_stamina()
    assert stamina == 5, f"Expected stamina 5, got {stamina}"
    print(f"✓ Initial stamina: {stamina}")

    # Step 2: Perform action and check consumption
    turn_left()
    stamina = get_stamina()
    assert stamina == 4, f"Expected stamina 4, got {stamina}"
    print(f"✓ After turn_left: {stamina}")

    # Step 3: Perform multiple actions
    turn_right()
    move()
    turn_left()
    stamina = get_stamina()
    assert stamina == 1, f"Expected stamina 1, got {stamina}"
    print(f"✓ After 3 more actions: {stamina}")

    # Step 4: Final action triggers death
    move()
    assert is_game_over(), "Game should be over (stamina depleted)"
    print("✓ Player died when stamina reached 0")

    print("\n✅ Test passed: Basic stamina consumption works!")

if __name__ == "__main__":
    test_basic_stamina_consumption()
```

### Execution

```bash
python test_quickstart_stamina.py
```

### Expected Output

```
✓ Initial stamina: 5
✓ After turn_left: 4
✓ After 3 more actions: 1
✓ Player died when stamina reached 0

✅ Test passed: Basic stamina consumption works!
```

---

## Quickstart Scenario 2: Stamina Recovery with wait()

**Goal**: Verify stamina recovers when using wait() in safe conditions

### Setup

1. Create test stage: `stages/test_stamina_recovery.yml`
```yaml
name: "Stamina Test - Recovery"
width: 10
height: 10
max_turns: 100

cells:
  - [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

player:
  start: [5, 2]
  direction: N
  hp: 100
  max_hp: 100
  stamina: 20
  max_stamina: 20

items: []
enemies: []  # No enemies = safe for recovery
```

2. Create test script:
```python
from engine.api import (
    initialize, move, wait, get_stamina
)
from engine.hyperparameter_manager import HyperParameterManager

def test_stamina_recovery():
    """スタミナ回復テスト"""
    hyperparameters = HyperParameterManager()
    hyperparameters.data.enable_stamina = True

    initialize("stages/test_stamina_recovery.yml", hyperparameters)

    # Step 1: Consume some stamina
    for _ in range(5):
        move()

    stamina = get_stamina()
    assert stamina == 15, f"Expected stamina 15, got {stamina}"
    print(f"✓ After 5 moves: {stamina}")

    # Step 2: Wait in safe area (no enemies)
    wait()

    stamina = get_stamina()
    # wait() consumes 1, then recovers 10 → 15-1+10=24, capped at 20
    assert stamina == 20, f"Expected stamina 20 (capped), got {stamina}"
    print(f"✓ After wait (safe): {stamina} (recovered to max)")

    # Step 3: Verify capping at max_stamina
    wait()
    stamina = get_stamina()
    assert stamina == 20, f"Expected stamina 20 (still capped), got {stamina}"
    print(f"✓ After another wait: {stamina} (still at max)")

    print("\n✅ Test passed: Stamina recovery works!")

if __name__ == "__main__":
    test_stamina_recovery()
```

### Execution

```bash
python test_quickstart_stamina.py
```

### Expected Output

```
✓ After 5 moves: 15
✓ After wait (safe): 20 (recovered to max)
✓ After another wait: 20 (still at max)

✅ Test passed: Stamina recovery works!
```

---

## Quickstart Scenario 3: No Recovery When Enemy Alerted

**Goal**: Verify stamina does NOT recover when enemy is alert

### Setup

1. Create test stage: `stages/test_stamina_no_recovery.yml`
```yaml
name: "Stamina Test - No Recovery"
width: 10
height: 10
max_turns: 100

cells:
  - [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
  - [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

player:
  start: [5, 2]
  direction: N
  hp: 100
  max_hp: 100
  stamina: 20
  max_stamina: 20

items: []
enemies:
  - position: [5, 4]  # Close to player
    hp: 50
    max_hp: 50
    attack_power: 10
    direction: S
    vision_range: 5
    patrol_points: []
```

2. Create test script:
```python
from engine.api import (
    initialize, move, wait, get_stamina, see
)
from engine.hyperparameter_manager import HyperParameterManager

def test_no_recovery_when_alerted():
    """敵警戒時にスタミナが回復しないテスト"""
    hyperparameters = HyperParameterManager()
    hyperparameters.data.enable_stamina = True

    initialize("stages/test_stamina_no_recovery.yml", hyperparameters)

    # Step 1: Move to trigger enemy alert
    move()  # Move toward enemy
    move()

    stamina = get_stamina()
    assert stamina == 18, f"Expected stamina 18, got {stamina}"
    print(f"✓ After 2 moves (enemy alerted): {stamina}")

    # Step 2: Try to wait (should NOT recover because enemy is alert)
    wait()

    stamina = get_stamina()
    # wait() consumes 1, NO recovery → 18-1=17
    assert stamina == 17, f"Expected stamina 17 (no recovery), got {stamina}"
    print(f"✓ After wait (enemy alerted): {stamina} (no recovery)")

    print("\n✅ Test passed: No stamina recovery when enemy alerted!")

if __name__ == "__main__":
    test_no_recovery_when_alerted()
```

### Expected Output

```
✓ After 2 moves (enemy alerted): 18
✓ After wait (enemy alerted): 17 (no recovery)

✅ Test passed: No stamina recovery when enemy alerted!
```

---

## Quickstart Scenario 4: Backward Compatibility (Stamina Disabled)

**Goal**: Verify existing behavior when ENABLE_STAMINA = False

### Setup

```python
from engine.api import (
    initialize, move, turn_left, get_stamina, is_game_over
)
from engine.hyperparameter_manager import HyperParameterManager

def test_stamina_disabled():
    """スタミナシステム無効時の後方互換性テスト"""
    hyperparameters = HyperParameterManager()
    hyperparameters.data.enable_stamina = False  # Disabled (default)

    initialize("stages/stage01.yml", hyperparameters)

    # Step 1: Check stamina exists but is not consumed
    initial_stamina = get_stamina()
    print(f"✓ Initial stamina: {initial_stamina}")

    # Step 2: Perform many actions
    for _ in range(100):
        turn_left()

    stamina = get_stamina()
    assert stamina == initial_stamina, f"Stamina should not change when disabled"
    print(f"✓ After 100 actions: {stamina} (unchanged)")

    # Step 3: Game should still be running
    assert not is_game_over(), "Game should not be over (stamina system disabled)"
    print("✓ Game still running (no stamina death)")

    print("\n✅ Test passed: Backward compatibility maintained!")

if __name__ == "__main__":
    test_stamina_disabled()
```

### Expected Output

```
✓ Initial stamina: 20
✓ After 100 actions: 20 (unchanged)
✓ Game still running (no stamina death)

✅ Test passed: Backward compatibility maintained!
```

---

## Quickstart Scenario 5: GUI Display Verification

**Goal**: Verify stamina is displayed in GUI

### Setup

```python
from engine.api import initialize, move, wait
from engine.renderer import Renderer
from engine.hyperparameter_manager import HyperParameterManager
from engine import GameContext

def test_gui_stamina_display():
    """GUI表示テスト"""
    hyperparameters = HyperParameterManager()
    hyperparameters.data.enable_stamina = True

    initialize("stages/stage01.yml", hyperparameters)

    # Step 1: Render initial state
    renderer = Renderer()
    game_state = GameContext.current_game
    output = renderer.render_game_info(game_state._state, game_state._hyperparameter_manager)

    assert "スタミナ:" in output or "stamina:" in output.lower(), \
        "GUI should display stamina info"
    print("✓ Initial GUI displays stamina")

    # Step 2: Perform action and check display update
    move()
    output = renderer.render_game_info(game_state._state, game_state._hyperparameter_manager)

    assert "19" in output, "GUI should show stamina decreased to 19"
    print("✓ GUI updates stamina after action")

    # Step 3: Wait and check recovery display
    wait()
    output = renderer.render_game_info(game_state._state, game_state._hyperparameter_manager)

    # Should show recovery (depends on enemy presence)
    print(f"✓ GUI shows stamina after wait: {output}")

    print("\n✅ Test passed: GUI displays stamina correctly!")

if __name__ == "__main__":
    test_gui_stamina_display()
```

---

## Quickstart Scenario 6: Stage Config Loading

**Goal**: Verify YAML stamina config loads correctly

### Setup

1. Test with custom stamina values:
```python
from engine.stage_loader import StageLoader

def test_stage_stamina_config():
    """ステージ設定読み込みテスト"""
    # Test 1: Stage with custom stamina
    loader = StageLoader()
    stage = loader.load("stages/test_stamina_basic.yml")

    assert stage.player.stamina == 5, f"Expected stamina 5, got {stage.player.stamina}"
    assert stage.player.max_stamina == 5, f"Expected max 5, got {stage.player.max_stamina}"
    print("✓ Custom stamina values loaded correctly")

    # Test 2: Stage without stamina (default values)
    stage = loader.load("stages/stage01.yml")

    assert stage.player.stamina == 20, f"Expected default stamina 20, got {stage.player.stamina}"
    assert stage.player.max_stamina == 20, f"Expected default max 20, got {stage.player.max_stamina}"
    print("✓ Default stamina values applied correctly")

    print("\n✅ Test passed: Stage config loading works!")

if __name__ == "__main__":
    test_stage_stamina_config()
```

---

## Running All Quickstart Tests

```bash
# Run individual scenarios
python test_quickstart_stamina.py
python test_quickstart_recovery.py
python test_quickstart_no_recovery.py
python test_stamina_disabled.py
python test_gui_stamina.py
python test_stage_config.py

# Or run all at once (if combined into single file)
python quickstart_all.py
```

---

## Success Criteria

All quickstart scenarios should:
- ✅ Execute without errors
- ✅ Pass all assertions
- ✅ Display expected console output
- ✅ Demonstrate stamina system working correctly
- ✅ Confirm backward compatibility

---

## Troubleshooting

### Issue: "RuntimeError: Game is not running"
**Solution**: Ensure `initialize()` is called before any API calls

### Issue: Stamina not decreasing
**Solution**: Check `ENABLE_STAMINA = True` in hyperparameters

### Issue: Player not dying at stamina=0
**Solution**: Verify stamina depletion logic in `consume_stamina()` method

### Issue: Recovery not working
**Solution**: Check enemy alert status and attack conditions

---

## Next Steps

After all quickstart scenarios pass:
1. Run full test suite: `pytest tests/`
2. Run existing stage tests to verify backward compatibility
3. Test with GUI: `python main.py` with `ENABLE_STAMINA = True`
4. Test all 13 existing stages with stamina enabled
5. Update documentation: `docs/v1.2.13.md`

---

**Validation Complete**: If all scenarios pass, stamina system (v1.2.13) is ready for production!