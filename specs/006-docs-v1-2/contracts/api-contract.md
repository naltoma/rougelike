# API Contract: Stamina System (v1.2.13)

**Date**: 2025-09-30
**Status**: Design Phase
**Type**: Python API Contract (Internal Library API)

---

## 1. New API Function

### 1.1 get_stamina()

**Signature**:
```python
def get_stamina() -> int
```

**Description**:
現在のプレイヤースタミナ値を取得する。ターンもスタミナも消費しない調査系API。

**Parameters**: None

**Returns**:
- `int`: 現在のスタミナ値 (0以上)

**Raises**:
- `RuntimeError`: ゲームが実行されていない場合（`GameContext.current_game`が未初期化）

**Side Effects**:
- None (non-turn-consuming, non-stamina-consuming)

**Preconditions**:
- Game must be initialized via `GameContext.initialize()`

**Postconditions**:
- Game state unchanged
- Turn counter unchanged
- Player stamina unchanged

**Contract Tests**:
```python
def test_get_stamina_returns_current_value():
    """get_stamina()が現在のスタミナ値を返すこと"""
    # Given: プレイヤーのスタミナが20
    # When: get_stamina()を呼び出す
    # Then: 20が返される

def test_get_stamina_no_turn_consumption():
    """get_stamina()がターンを消費しないこと"""
    # Given: ゲーム開始時（ターン0）
    # When: get_stamina()を10回連続で呼び出す
    # Then: ターンカウントが0のまま変化しない

def test_get_stamina_no_stamina_consumption():
    """get_stamina()がスタミナを消費しないこと"""
    # Given: ENABLE_STAMINA=True、初期スタミナ20
    # When: get_stamina()を100回連続で呼び出す
    # Then: スタミナが20のまま変化しない

def test_get_stamina_works_when_stamina_disabled():
    """ENABLE_STAMINA=Falseでもget_stamina()が動作すること"""
    # Given: ENABLE_STAMINA=False
    # When: get_stamina()を呼び出す
    # Then: 現在のスタミナ値が返される（エラーなし）

def test_get_stamina_raises_error_when_game_not_initialized():
    """ゲーム未初期化時にRuntimeErrorを発生すること"""
    # Given: GameContextが初期化されていない
    # When: get_stamina()を呼び出す
    # Then: RuntimeErrorが発生する
```

---

## 2. Modified API Functions

### 2.1 Existing Turn-Consuming Actions

**Functions**:
- `turn_left()`
- `turn_right()`
- `move()`
- `attack()`
- `pickup()`
- `dispose()`
- `wait()`

**Contract Change**:
When `ENABLE_STAMINA = True`, these functions now:
1. Consume 1 stamina before execution
2. Check for stamina depletion (0 stamina → player death)

**Backward Compatibility**:
When `ENABLE_STAMINA = False` (default), behavior is identical to v1.2.12

**Contract Tests (Example: move())**:
```python
def test_move_consumes_stamina_when_enabled():
    """ENABLE_STAMINA=Trueの時、move()がスタミナを1消費すること"""
    # Given: ENABLE_STAMINA=True、初期スタミナ20
    # When: move()を1回実行
    # Then: スタミナが19になる

def test_move_no_stamina_consumption_when_disabled():
    """ENABLE_STAMINA=Falseの時、move()がスタミナを消費しないこと"""
    # Given: ENABLE_STAMINA=False、初期スタミナ20
    # When: move()を10回実行
    # Then: スタミナが20のまま（システム無効）

def test_move_fails_when_stamina_reaches_zero():
    """スタミナ消費でスタミナが0になった時、プレイヤーが死亡すること"""
    # Given: ENABLE_STAMINA=True、スタミナ1
    # When: move()を実行（スタミナ1→0）
    # Then: プレイヤーのHPが0になる（死亡）

def test_move_consumes_stamina_even_on_failure():
    """move()が失敗した場合でもスタミナを消費すること"""
    # Given: ENABLE_STAMINA=True、壁に向かって移動不可
    # When: move()を実行（移動失敗）
    # Then: スタミナが1減少する
```

---

### 2.2 wait() - Stamina Recovery

**Contract Change**:
When `ENABLE_STAMINA = True` and safe conditions met:
- Recover +10 stamina (capped at `max_stamina`)

**Safe Conditions**:
1. No enemy is in alert state
2. Player did not take damage this turn

**Contract Tests**:
```python
def test_wait_recovers_stamina_when_safe():
    """安全な状態でwait()を実行するとスタミナが10回復すること"""
    # Given: ENABLE_STAMINA=True、スタミナ10、敵非警戒
    # When: wait()を実行
    # Then: スタミナが20になる

def test_wait_no_recovery_when_enemy_alerted():
    """敵が警戒状態の時、wait()でスタミナが回復しないこと"""
    # Given: ENABLE_STAMINA=True、スタミナ10、敵警戒中
    # When: wait()を実行
    # Then: スタミナが9になる（-1消費のみ、回復なし）

def test_wait_no_recovery_when_attacked():
    """wait()中に攻撃を受けた場合、スタミナが回復しないこと"""
    # Given: ENABLE_STAMINA=True、スタミナ10、敵が隣接
    # When: wait()を実行（敵の攻撃を受ける）
    # Then: スタミナが9になる（-1消費のみ、回復なし）

def test_wait_recovery_capped_at_max():
    """wait()回復がmax_staminaで上限されること"""
    # Given: ENABLE_STAMINA=True、スタミナ18/20、敵非警戒
    # When: wait()を実行（+10回復）
    # Then: スタミナが20になる（28ではない）

def test_wait_no_recovery_when_stamina_disabled():
    """ENABLE_STAMINA=Falseの時、wait()でスタミナ回復ロジックが動作しないこと"""
    # Given: ENABLE_STAMINA=False
    # When: wait()を実行
    # Then: スタミナが変化しない（システム無効）
```

---

## 3. Configuration Contract

### 3.1 Hyperparameter: ENABLE_STAMINA

**Location**: `main.py` (user configuration section)

**Type**: `bool`

**Default**: `False`

**Values**:
- `True`: Stamina system enabled
- `False`: Stamina system disabled (backward compatible)

**Contract**:
```python
def test_enable_stamina_default_false():
    """ENABLE_STAMINAのデフォルト値がFalseであること"""
    # Given: main.pyのデフォルト設定
    # Then: ENABLE_STAMINA = False

def test_enable_stamina_true_activates_system():
    """ENABLE_STAMINA=Trueの時、スタミナシステムが動作すること"""
    # Given: ENABLE_STAMINA = True
    # When: move()を実行
    # Then: スタミナが消費される

def test_enable_stamina_false_disables_system():
    """ENABLE_STAMINA=Falseの時、スタミナシステムが動作しないこと"""
    # Given: ENABLE_STAMINA = False
    # When: move()を20回実行
    # Then: スタミナが変化しない、死亡しない
```

---

### 3.2 Stage Configuration: stamina fields

**Location**: `stages/*.yml` → `player` section

**Fields**:
- `stamina`: `int` (optional, default: 20)
- `max_stamina`: `int` (optional, default: 20)

**Contract**:
```python
def test_stage_load_with_stamina_fields():
    """YAMLにstamina/max_staminaが記載されている場合、その値を使用すること"""
    # Given: stage.yml with stamina=30, max_stamina=30
    # When: ステージをロード
    # Then: プレイヤーのスタミナが30/30で初期化される

def test_stage_load_without_stamina_fields():
    """YAMLにstamina/max_staminaが記載されていない場合、デフォルト20/20を使用すること"""
    # Given: stage.yml without stamina fields (既存ステージ)
    # When: ステージをロード
    # Then: プレイヤーのスタミナが20/20で初期化される

def test_stage_load_validates_stamina_range():
    """YAMLのstamina値がmax_staminaを超える場合、エラーを発生すること"""
    # Given: stage.yml with stamina=50, max_stamina=20
    # When: ステージをロード
    # Then: ValidationErrorが発生する

def test_stage_load_validates_max_stamina_positive():
    """YAMLのmax_staminaが0以下の場合、エラーを発生すること"""
    # Given: stage.yml with max_stamina=-10
    # When: ステージをロード
    # Then: ValidationErrorが発生する
```

---

## 4. GUI Display Contract

### 4.1 Player Info Display

**Requirement**: Display stamina in player info section (both CUI and GUI)

**Format**: `スタミナ: {current}/{max}`

**Contract**:
```python
def test_gui_displays_stamina():
    """GUI画面にスタミナが表示されること"""
    # Given: ENABLE_STAMINA=True、スタミナ15/20
    # When: GUI画面を描画
    # Then: "スタミナ: 15/20"が表示される

def test_gui_highlights_stamina_decrease():
    """スタミナ減少時に赤色でハイライト表示されること"""
    # Given: スタミナが20→19に減少
    # When: GUI画面を描画
    # Then: スタミナ表示が赤色でハイライトされる

def test_gui_highlights_stamina_increase():
    """スタミナ回復時に緑色でハイライト表示されること"""
    # Given: スタミナが10→20に回復
    # When: GUI画面を描画
    # Then: スタミナ表示が緑色でハイライトされる

def test_gui_stamina_display_when_disabled():
    """ENABLE_STAMINA=Falseの時、スタミナ表示がどうなるか"""
    # Option 1: 表示しない
    # Option 2: 表示するが"(無効)"マーク付き
    # [要決定]
```

---

## 5. Backward Compatibility Contract

### 5.1 Existing Tests Must Pass

**Contract**:
```python
def test_all_existing_tests_pass_with_default_config():
    """ENABLE_STAMINA=False（デフォルト）で既存テストが全て通ること"""
    # Given: ENABLE_STAMINA=False（デフォルト設定）
    # When: 既存の全テストスイートを実行
    # Then: 全テスト合格（v1.2.12と同じ挙動）
```

### 5.2 Existing Stages Work

**Contract**:
```python
def test_existing_stages_load_without_error():
    """既存ステージ（stamina設定なし）がエラーなくロードできること"""
    # Given: stages/stage01.yml～stage13.yml（v1.2.12）
    # When: 各ステージをロード
    # Then: エラーなし、デフォルトスタミナ20/20で動作
```

### 5.3 User Files Unchanged

**Contract**:
```python
def test_main_template_files_not_modified():
    """main_*.pyファイル（ユーザー演習用）が変更されていないこと"""
    # Given: main_stage01.py～main_stage13.py
    # When: v1.2.12とv1.2.13を比較
    # Then: ファイル内容が完全一致（変更なし）
```

---

## 6. Error Handling Contract

### 6.1 Stamina Depletion Death

**Contract**:
```python
def test_stamina_depletion_triggers_death():
    """スタミナが0になった瞬間にHPが0になること"""
    # Given: ENABLE_STAMINA=True、スタミナ1、HP100
    # When: move()を実行（スタミナ1→0）
    # Then: プレイヤーのHPが0になる（即死）

def test_stamina_depletion_ends_game():
    """スタミナ枯渇死後、ゲームが終了すること"""
    # Given: スタミナ枯渇でHP=0
    # When: 次のアクションを実行しようとする
    # Then: ゲームオーバー状態で新アクション不可
```

### 6.2 API Error Handling

**Contract**:
```python
def test_api_raises_error_when_game_not_running():
    """ゲーム未実行時にget_stamina()がRuntimeErrorを発生すること"""
    # Given: GameContextが未初期化
    # When: get_stamina()を呼び出す
    # Then: RuntimeError("Game is not running")

def test_api_returns_valid_value_when_game_running():
    """ゲーム実行中はget_stamina()が常に有効な値を返すこと"""
    # Given: ゲーム実行中
    # When: get_stamina()を呼び出す
    # Then: 0以上の整数が返される
```

---

## 7. Performance Contract

### 7.1 Stamina Check Overhead

**Requirement**: Stamina system should add <1% overhead to action execution

**Contract**:
```python
def test_stamina_system_performance_overhead():
    """スタミナシステム有効時のオーバーヘッドが1%未満であること"""
    # Given: ENABLE_STAMINA=True
    # When: move()を1000回実行
    # Then: ENABLE_STAMINA=Falseと比較して実行時間が1%未満の増加
```

---

## 8. Summary

### 8.1 New API

| Function | Signature | Turn Cost | Stamina Cost | Returns |
|----------|-----------|-----------|--------------|---------|
| `get_stamina()` | `() -> int` | 0 | 0 | Current stamina |

### 8.2 Modified API Behavior

| Function | Stamina Cost (if enabled) | Recovery (if safe) | Death Condition |
|----------|---------------------------|--------------------|--------------------|
| `turn_left()` | -1 | - | stamina=0 → hp=0 |
| `turn_right()` | -1 | - | stamina=0 → hp=0 |
| `move()` | -1 | - | stamina=0 → hp=0 |
| `attack()` | -1 | - | stamina=0 → hp=0 |
| `pickup()` | -1 | - | stamina=0 → hp=0 |
| `dispose()` | -1 | - | stamina=0 → hp=0 |
| `wait()` | -1 | +10 (if safe) | stamina=0 → hp=0 |

### 8.3 Configuration

| Parameter | Type | Default | Location |
|-----------|------|---------|----------|
| `ENABLE_STAMINA` | `bool` | `False` | `main.py` |
| `player.stamina` | `int` | 20 | `stages/*.yml` |
| `player.max_stamina` | `int` | 20 | `stages/*.yml` |

---

**Next Steps**:
1. Generate contract test files from this specification
2. Ensure all tests fail (RED phase of TDD)
3. Proceed to implementation phase