# Implementation Tasks: Stamina System (v1.2.13)

**Branch**: `006-docs-v1-2`
**Input**: Design documents from `/specs/006-docs-v1-2/`
**Prerequisites**: plan.md, data-model.md, contracts/api-contract.md, quickstart.md

---

## Execution Flow (main)
```
✅ 1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, PyYAML, tkinter, pytest
   → Structure: Single project (engine/ library)
✅ 2. Load optional design documents:
   → data-model.md: Character, HyperParametersData, StatusChange entities
   → contracts/api-contract.md: get_stamina() API + modified actions
   → quickstart.md: 6 E2E validation scenarios
✅ 3. Generate tasks by category:
   → Setup: test stages, test utilities
   → Tests: contract tests (5 test files), integration tests (6 scenarios)
   → Core: Character model, HyperParameters, StageLoader, GameState, API
   → Integration: Commands, Renderer (CUI/GUI), StatusChange tracking
   → Polish: backward compatibility tests, performance tests
✅ 4. Apply task rules:
   → Different test files = [P] parallel
   → Model extensions = [P] parallel (different classes)
   → Command/Renderer integration = sequential (shared dependencies)
   → Tests before implementation (TDD enforced)
✅ 5. Number tasks sequentially (T001, T002...)
✅ 6. Generate dependency graph
✅ 7. Create parallel execution examples
✅ 8. Validate task completeness:
   ✅ All contracts have tests (get_stamina + modified actions)
   ✅ All entities have implementation tasks (Character, HyperParameters, StatusChange)
   ✅ All quickstart scenarios covered (6 integration tests)
✅ 9. Return: SUCCESS (27 tasks ready for execution)
```

---

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in task descriptions
- Follow TDD: Tests → RED → Implementation → GREEN → Refactor

---

## Phase 3.1: Setup & Test Infrastructure

### T001 [P] テスト用ステージファイル作成
**File**: `stages/test_stamina_basic.yml`
**Description**:
スタミナ消費テスト用のシンプルなステージを作成。壁なし10x10グリッド、初期スタミナ5/5（早期枯渇テスト用）、敵なし、アイテムなし。
```yaml
player:
  start: [5, 2]
  direction: N
  hp: 100
  max_hp: 100
  stamina: 5
  max_stamina: 5
```
**Dependencies**: None
**Estimated Time**: 15分

---

### T002 [P] テスト用ステージファイル作成（回復用）
**File**: `stages/test_stamina_recovery.yml`
**Description**:
スタミナ回復テスト用ステージ。10x10グリッド、初期スタミナ20/20、敵なし（安全なwait()回復テスト用）。
```yaml
player:
  stamina: 20
  max_stamina: 20
```
**Dependencies**: None
**Estimated Time**: 15分

---

### T003 [P] テスト用ステージファイル作成（敵警戒用）
**File**: `stages/test_stamina_no_recovery.yml`
**Description**:
敵警戒時のスタミナ回復なしテスト用ステージ。プレイヤー近くに敵配置（vision_range: 5）。
```yaml
enemies:
  - position: [5, 4]
    hp: 50
    max_hp: 50
    attack_power: 10
    direction: S
    vision_range: 5
```
**Dependencies**: None
**Estimated Time**: 15分

---

## Phase 3.2: Contract Tests (TDD - MUST FAIL FIRST)

**⚠️ CRITICAL**: These tests MUST be written and MUST FAIL before ANY implementation in Phase 3.3

### T004 [P] get_stamina() API契約テスト
**File**: `tests/contract/test_get_stamina_api.py`
**Description**:
`get_stamina()`の契約テストを実装:
- `test_get_stamina_returns_current_value()`: 現在スタミナ値を返すこと
- `test_get_stamina_no_turn_consumption()`: ターン消費しないこと（10回呼び出しでターン0維持）
- `test_get_stamina_no_stamina_consumption()`: スタミナ消費しないこと（100回呼び出しでスタミナ20維持）
- `test_get_stamina_works_when_stamina_disabled()`: ENABLE_STAMINA=Falseでも動作すること
- `test_get_stamina_raises_error_when_game_not_initialized()`: 未初期化時にRuntimeError

stages/test_stamina_basic.ymlを使用。**実行して全て失敗することを確認（RED phase）**。

**Dependencies**: T001
**Estimated Time**: 45分

---

### T005 [P] move()スタミナ消費契約テスト
**File**: `tests/contract/test_move_stamina_contract.py`
**Description**:
`move()`のスタミナ消費契約テストを実装:
- `test_move_consumes_stamina_when_enabled()`: ENABLE_STAMINA=Trueでスタミナ1消費
- `test_move_no_stamina_consumption_when_disabled()`: ENABLE_STAMINA=Falseで消費なし
- `test_move_fails_when_stamina_reaches_zero()`: スタミナ0でHP0（死亡）
- `test_move_consumes_stamina_even_on_failure()`: 移動失敗でもスタミナ消費

**実行して全て失敗することを確認（RED phase）**。

**Dependencies**: T001
**Estimated Time**: 45分

---

### T006 [P] wait()スタミナ回復契約テスト
**File**: `tests/contract/test_wait_stamina_contract.py`
**Description**:
`wait()`のスタミナ回復契約テストを実装:
- `test_wait_recovers_stamina_when_safe()`: 安全時に+10回復（上限チェック）
- `test_wait_no_recovery_when_enemy_alerted()`: 敵警戒時に回復なし
- `test_wait_no_recovery_when_attacked()`: 攻撃受け時に回復なし
- `test_wait_recovery_capped_at_max()`: max_staminaで上限
- `test_wait_no_recovery_when_stamina_disabled()`: ENABLE_STAMINA=Falseで回復ロジック無効

stages/test_stamina_recovery.yml（安全）とtest_stamina_no_recovery.yml（敵警戒）を使用。**実行して全て失敗することを確認（RED phase）**。

**Dependencies**: T002, T003
**Estimated Time**: 60分

---

### T007 [P] ステージ設定読み込み契約テスト
**File**: `tests/contract/test_stage_stamina_config.py`
**Description**:
ステージYAMLからのスタミナ設定読み込み契約テスト:
- `test_stage_load_with_stamina_fields()`: stamina/max_stamina指定時に値使用
- `test_stage_load_without_stamina_fields()`: 未指定時にデフォルト20/20
- `test_stage_load_validates_stamina_range()`: stamina > max_staminaでエラー
- `test_stage_load_validates_max_stamina_positive()`: max_stamina <= 0でエラー

stages/test_stamina_basic.yml（カスタム値）とstages/stage01.yml（既存ステージ）を使用。**実行して全て失敗することを確認（RED phase）**。

**Dependencies**: T001
**Estimated Time**: 45分

---

### T008 [P] GUI表示契約テスト
**File**: `tests/contract/test_gui_stamina_display.py`
**Description**:
GUI/CUIスタミナ表示契約テスト:
- `test_gui_displays_stamina()`: "スタミナ: 現在/最大"表示
- `test_gui_highlights_stamina_decrease()`: 減少時に赤ハイライト
- `test_gui_highlights_stamina_increase()`: 回復時に緑ハイライト
- `test_cui_displays_stamina()`: CUI版でもスタミナ表示

Rendererクラスのrender_game_info()出力をテスト。**実行して全て失敗することを確認（RED phase）**。

**Dependencies**: T001
**Estimated Time**: 45分

---

## Phase 3.3: Core Model Implementation (ONLY after contract tests are failing)

### T009 [P] Characterデータクラス拡張（スタミナフィールド追加）
**File**: `engine/__init__.py`
**Description**:
Characterデータクラスにスタミナフィールドを追加:
```python
@dataclass
class Character:
    # 既存フィールド（変更なし）
    position: Position
    direction: Direction
    hp: int = 100
    max_hp: int = 100
    attack_power: int = 30
    collected_items: List[str] = field(default_factory=list)
    disposed_items: List[str] = field(default_factory=list)

    # 新規フィールド (v1.2.13)
    stamina: int = 20
    max_stamina: int = 20
```
**既存テストへの影響**: 全テストが引き続き合格すること（デフォルト値で後方互換性維持）。

**Dependencies**: T004-T008（契約テスト失敗確認後）
**Estimated Time**: 15分

---

### T010 [P] Characterクラスにスタミナメソッド追加
**File**: `engine/__init__.py`
**Description**:
Characterクラスに3つのスタミナメソッドを実装:

1. `consume_stamina(self, amount: int = 1) -> bool`:
   - スタミナを減少（最小0）
   - スタミナ0になった場合、`self.hp = 0`（即死）
   - 戻り値: 死亡発生時True

2. `recover_stamina(self, amount: int) -> int`:
   - スタミナを増加（最大`max_stamina`）
   - 戻り値: 実際に回復した量

3. `stamina_percentage(self) -> float`:
   - 戻り値: `(stamina / max_stamina) * 100.0`

**Unit Test**: `tests/unit/test_character_stamina.py`で各メソッドをテスト（並行実装推奨）。

**Dependencies**: T009
**Estimated Time**: 45分

---

### T011 [P] HyperParametersData拡張（ENABLE_STAMINA追加）
**File**: `engine/hyperparameter_manager.py`
**Description**:
`HyperParametersData`データクラスに`enable_stamina`フィールドを追加:
```python
@dataclass
class HyperParametersData:
    delay_ms: int = 100
    speed_level: int = 4
    enable_stamina: bool = False  # 新規 (v1.2.13)
```

**既存テストへの影響**: 全テストが引き続き合格すること（デフォルトFalseで後方互換性維持）。

**Dependencies**: T004-T008（契約テスト失敗確認後）
**Estimated Time**: 15分

---

### T012 [P] StatusChange拡張（スタミナトラッキング追加）
**File**: `engine/renderer.py`
**Description**:
`StatusChange`データクラスにスタミナトラッキングフィールドを追加:
```python
@dataclass
class StatusChange:
    old_hp: Optional[int]
    new_hp: Optional[int]
    old_items: Optional[List[str]]
    new_items: Optional[List[str]]
    old_stamina: Optional[int] = None  # 新規 (v1.2.13)
    new_stamina: Optional[int] = None  # 新規 (v1.2.13)
```

`StatusChangeTracker.track_changes()`メソッドを更新し、`old_player.stamina`と`new_player.stamina`を記録。

**Dependencies**: T009, T010（Characterスタミナ実装後）
**Estimated Time**: 30分

---

## Phase 3.4: Stage Loading Integration

### T013 StageLoader拡張（YAMLスタミナパース対応）
**File**: `engine/stage_loader.py`
**Description**:
`StageLoader._validate_player()`メソッドを拡張し、YAMLからスタミナフィールドを読み込み:
```python
stamina = player_config.get("stamina", 20)  # デフォルト20
max_stamina = player_config.get("max_stamina", 20)  # デフォルト20

# バリデーション
if max_stamina <= 0:
    raise ValidationError("max_stamina must be positive")
if stamina < 0 or stamina > max_stamina:
    raise ValidationError("stamina must be 0 <= stamina <= max_stamina")
```

`_build_stage()`でCharacterインスタンス生成時に`stamina`と`max_stamina`を渡す。

**Contract Test**: T007が合格すること。

**Dependencies**: T009（Characterフィールド追加後）
**Estimated Time**: 45分

---

## Phase 3.5: Game State Integration (Stamina Consumption)

### T014 GameStateManagerにスタミナ消費ロジック統合
**File**: `engine/game_state.py`
**Description**:
`GameStateManager.execute_command()`メソッドを拡張:

1. コマンド実行**前**にスタミナチェック:
```python
if self._hyperparameter_manager.data.enable_stamina:
    if self._state.player.stamina <= 0:
        # Already dead, prevent action
        return
```

2. コマンド実行**後**にスタミナ消費（ターン消費系コマンドのみ）:
```python
if self._hyperparameter_manager.data.enable_stamina:
    if command.consumes_turn:  # TurnLeftCommand, MoveCommand, etc.
        player_died = self._state.player.consume_stamina(1)
        if player_died:
            # Handle death (log, update GUI state)
            pass
```

**ターン消費系コマンド判定**: `TurnLeftCommand`, `TurnRightCommand`, `MoveCommand`, `AttackCommand`, `PickupCommand`, `DisposeCommand`, `WaitCommand`は`consumes_turn=True`を持つ（既存Command基底クラスの属性を活用）。

**Contract Test**: T005が合格すること（move()スタミナ消費）。

**Dependencies**: T010（consume_stamina()メソッド実装後）, T011（ENABLE_STAMINAフラグ実装後）
**Estimated Time**: 60分

---

## Phase 3.6: Wait Command Integration (Stamina Recovery)

### T015 WaitCommandにスタミナ回復ロジック統合
**File**: `engine/commands.py`
**Description**:
`WaitCommand.execute()`メソッドを拡張し、安全条件下でスタミナ回復:

1. wait()実行後、安全条件チェック:
```python
if game_state._hyperparameter_manager.data.enable_stamina:
    # 条件1: 敵が非警戒
    enemies_not_alerted = all(not enemy.alerted for enemy in game_state._state.enemies)

    # 条件2: プレイヤーが攻撃を受けていない
    player_not_attacked = not game_state._player_attacked_this_turn

    if enemies_not_alerted and player_not_attacked:
        game_state._state.player.recover_stamina(10)
```

2. `_player_attacked_this_turn`フラグを`GameStateManager`に追加（敵AI処理後に更新）。

**Contract Test**: T006が合格すること（wait()回復）。

**Dependencies**: T010（recover_stamina()メソッド実装後）, T014（スタミナ消費統合後）
**Estimated Time**: 60分

---

## Phase 3.7: API Layer (get_stamina)

### T016 get_stamina() API実装
**File**: `engine/api.py`
**Description**:
新規API関数`get_stamina()`を実装:
```python
def get_stamina() -> int:
    """
    現在のプレイヤースタミナ値を取得

    ターン消費: なし
    スタミナ消費: なし

    Returns:
        int: 現在のスタミナ値

    Raises:
        RuntimeError: ゲーム未実行時
    """
    if GameContext.current_game is None:
        raise RuntimeError("Game is not running")

    return GameContext.current_game._state.player.stamina
```

**公開API**: `main.py`のAPIインポートリストに`get_stamina`を追加（ユーザーが利用可能に）。

**Contract Test**: T004が合格すること（get_stamina() API）。

**Dependencies**: T009（Characterスタミナフィールド実装後）
**Estimated Time**: 30分

---

## Phase 3.8: GUI/CUI Rendering Integration

### T017 CUIレンダラーにスタミナ表示追加
**File**: `engine/renderer.py`
**Description**:
`Renderer.render_game_info()`メソッドにスタミナ情報を追加:

CUI出力例:
```
=== ゲーム情報 ===
ステージ: stage01
ターン: 5
HP: 80/100
スタミナ: 15/20  # 新規
...
```

**表示条件**: `ENABLE_STAMINA=True`の場合のみ表示（オプション）。または常に表示してシステム無効時は"(無効)"マークを付ける。

**Contract Test**: T008が合格すること（CUI表示）。

**Dependencies**: T009（Characterスタミナフィールド実装後）
**Estimated Time**: 30分

---

### T018 GUIレンダラーにスタミナ表示追加
**File**: `engine/renderer.py`
**Description**:
`Renderer._draw_player_info()`メソッド（Tkinter GUI）にスタミナ情報を追加:

GUI表示例（サイドバー）:
```
プレイヤー情報
HP: 80/100 ████████░░
スタミナ: 15/20 ███████░░░  # 新規
方向: N
...
```

**Dependencies**: T009（Characterスタミナフィールド実装後）
**Estimated Time**: 30分

---

### T019 StatusChangeTrackerにスタミナハイライト対応
**File**: `engine/renderer.py`
**Description**:
`StatusChangeTracker`の変化検出ロジックを拡張し、スタミナ変化をハイライト表示:

1. `StatusChange`に`old_stamina`/`new_stamina`が記録されている場合:
   - 減少時: 赤色ハイライト（例: `スタミナ: 20 → 19`）
   - 増加時: 緑色ハイライト（例: `スタミナ: 10 → 20`）

2. GUI/CUI両対応の変化表示。

**Contract Test**: T008が合格すること（ハイライト表示）。

**Dependencies**: T012（StatusChange拡張後）, T017-T018（スタミナ表示実装後）
**Estimated Time**: 45分

---

## Phase 3.9: Integration Testing (E2E Scenarios)

### T020 [P] 統合テスト: 基本的なスタミナ消費
**File**: `tests/integration/test_stamina_consumption.py`
**Description**:
quickstart.mdのシナリオ1をpytestテストとして実装:
- 初期スタミナ5/5
- 5回アクション（turn_left, turn_right, move等）
- スタミナ0で死亡（`is_game_over() == True`）

stages/test_stamina_basic.ymlを使用。

**Dependencies**: T001, T009-T016（全コア実装完了後）
**Estimated Time**: 45分

---

### T021 [P] 統合テスト: スタミナ回復
**File**: `tests/integration/test_stamina_recovery.py`
**Description**:
quickstart.mdのシナリオ2をpytestテストとして実装:
- 5回move()でスタミナ15
- wait()で回復 → スタミナ20（上限）
- 再度wait() → スタミナ20維持（上限超えない）

stages/test_stamina_recovery.ymlを使用。

**Dependencies**: T002, T009-T016（全コア実装完了後）
**Estimated Time**: 45分

---

### T022 [P] 統合テスト: 敵警戒時の回復なし
**File**: `tests/integration/test_stamina_no_recovery.py`
**Description**:
quickstart.mdのシナリオ3をpytestテストとして実装:
- 敵に接近してalert状態にする
- wait()実行 → スタミナ回復**なし**（-1消費のみ）

stages/test_stamina_no_recovery.ymlを使用。

**Dependencies**: T003, T009-T016（全コア実装完了後）
**Estimated Time**: 45分

---

### T023 [P] 統合テスト: 後方互換性（ENABLE_STAMINA=False）
**File**: `tests/integration/test_stamina_disabled.py`
**Description**:
quickstart.mdのシナリオ4をpytestテストとして実装:
- ENABLE_STAMINA=False
- 100回アクション実行
- スタミナ変化なし、死亡なし

stages/stage01.yml（既存ステージ）を使用。

**Dependencies**: T009-T016（全コア実装完了後）
**Estimated Time**: 30分

---

### T024 [P] 統合テスト: GUI表示確認
**File**: `tests/integration/test_gui_stamina_display.py`
**Description**:
quickstart.mdのシナリオ5をpytestテストとして実装:
- Rendererのrender_game_info()出力に"スタミナ:"が含まれること
- move()後に値が更新されること
- wait()後に回復が反映されること

**Dependencies**: T017-T019（GUI実装完了後）
**Estimated Time**: 45分

---

### T025 [P] 統合テスト: ステージ設定読み込み
**File**: `tests/integration/test_stage_stamina_loading.py`
**Description**:
quickstart.mdのシナリオ6をpytestテストとして実装:
- カスタムスタミナ（5/5）のステージロード確認
- デフォルトスタミナ（20/20）のステージロード確認

stages/test_stamina_basic.yml（カスタム）とstages/stage01.yml（デフォルト）を使用。

**Dependencies**: T013（StageLoader実装完了後）
**Estimated Time**: 30分

---

## Phase 3.10: Backward Compatibility & Performance

### T026 既存テストスイート全実行（後方互換性確認）
**Command**: `pytest tests/`
**Description**:
ENABLE_STAMINA=False（デフォルト）で既存の全テストスイートを実行:
- 全テストが合格すること
- スタミナシステムが既存動作に影響しないこと

**期待結果**: 全既存テスト合格（v1.2.12と同じ挙動）

**Dependencies**: T009-T019（全実装完了後）
**Estimated Time**: 15分（実行のみ）

---

### T027 既存13ステージ動作確認
**Command**: 各ステージをmain.pyで実行
**Description**:
stages/stage01.yml～stage13.ymlの各ステージが正常動作すること:
- ENABLE_STAMINA=False（デフォルト）で動作確認
- エラーなくゲーム開始・終了できること

**期待結果**: 全13ステージがv1.2.12と同じ挙動

**Dependencies**: T013（StageLoader実装完了後）
**Estimated Time**: 30分（手動確認）

---

## Dependencies Graph

```
Setup Phase:
T001 (test_stamina_basic.yml)
T002 (test_stamina_recovery.yml)
T003 (test_stamina_no_recovery.yml)
  ↓
Contract Tests Phase (RED):
T004 (get_stamina API) ← T001
T005 (move stamina) ← T001
T006 (wait recovery) ← T002, T003
T007 (stage config) ← T001
T008 (GUI display) ← T001
  ↓
Core Implementation Phase (GREEN):
T009 (Character fields)
T010 (Character methods) ← T009
T011 (HyperParameters)
T012 (StatusChange) ← T009, T010
  ↓
Integration Phase:
T013 (StageLoader) ← T009
T014 (GameState consumption) ← T010, T011
T015 (WaitCommand recovery) ← T010, T014
T016 (API layer) ← T009
  ↓
Rendering Phase:
T017 (CUI display) ← T009
T018 (GUI display) ← T009
T019 (StatusChange tracking) ← T012, T017, T018
  ↓
Integration Testing Phase:
T020-T025 (E2E tests) ← T009-T019 (all core implementation)
  ↓
Validation Phase:
T026 (existing tests) ← T009-T019
T027 (existing stages) ← T013
```

---

## Parallel Execution Examples

### Batch 1: Setup (all parallel)
```bash
# T001-T003を並列実行
Task: "Create test stage stages/test_stamina_basic.yml"
Task: "Create test stage stages/test_stamina_recovery.yml"
Task: "Create test stage stages/test_stamina_no_recovery.yml"
```

### Batch 2: Contract Tests (all parallel, after Batch 1)
```bash
# T004-T008を並列実行
Task: "Contract test get_stamina() in tests/contract/test_get_stamina_api.py"
Task: "Contract test move() in tests/contract/test_move_stamina_contract.py"
Task: "Contract test wait() in tests/contract/test_wait_stamina_contract.py"
Task: "Contract test stage config in tests/contract/test_stage_stamina_config.py"
Task: "Contract test GUI display in tests/contract/test_gui_stamina_display.py"
```

### Batch 3: Core Models (all parallel, after verifying RED phase)
```bash
# T009-T012を並列実行
Task: "Add stamina fields to Character in engine/__init__.py"
Task: "Add stamina methods to Character in engine/__init__.py"
Task: "Add enable_stamina to HyperParametersData in engine/hyperparameter_manager.py"
Task: "Add stamina tracking to StatusChange in engine/renderer.py"
```

### Batch 4: Integration Tests (all parallel, after all implementation)
```bash
# T020-T025を並列実行
Task: "Integration test basic consumption in tests/integration/test_stamina_consumption.py"
Task: "Integration test recovery in tests/integration/test_stamina_recovery.py"
Task: "Integration test no recovery in tests/integration/test_stamina_no_recovery.py"
Task: "Integration test disabled in tests/integration/test_stamina_disabled.py"
Task: "Integration test GUI display in tests/integration/test_gui_stamina_display.py"
Task: "Integration test stage loading in tests/integration/test_stage_stamina_loading.py"
```

---

## Validation Checklist

**Before Starting Implementation**:
- [x] All contract tests defined (T004-T008)
- [x] All entities have model tasks (Character, HyperParameters, StatusChange)
- [x] All tests come before implementation (Phase 3.2 → 3.3)
- [x] Parallel tasks truly independent ([P] marked correctly)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task

**After Completing All Tasks**:
- [ ] All contract tests pass (T004-T008 GREEN)
- [ ] All integration tests pass (T020-T025 GREEN)
- [ ] All existing tests pass (T026 GREEN)
- [ ] All 13 stages work (T027 GREEN)
- [ ] Performance overhead <1% (スタミナチェックは単純なif文のみ)
- [ ] Backward compatibility maintained (ENABLE_STAMINA=False)

---

## Notes

- **[P]マークのタスク**: 異なるファイルで依存関係なし、並列実行可能
- **TDD厳守**: T004-T008が失敗することを確認してからT009以降を実装
- **後方互換性**: デフォルトENABLE_STAMINA=Falseで既存動作維持
- **ユーザーファイル保護**: main_*.pyは一切変更しない
- **コミット推奨**: 各タスク完了後にコミット（特にT009-T019の実装フェーズ）

---

## Implementation Strategy Summary

1. **Setup (15分 x 3)**: テストステージ3つ作成
2. **Contract Tests (45分 x 5)**: 契約テスト作成 → RED確認
3. **Core Models (15-45分 x 4)**: Character/HyperParameters/StatusChange拡張 → 契約テスト一部GREEN
4. **Integration (30-60分 x 4)**: StageLoader/GameState/WaitCommand/API統合 → 残り契約テストGREEN
5. **Rendering (30-45分 x 3)**: CUI/GUI表示＋ハイライト → GUI契約テストGREEN
6. **E2E Tests (30-45分 x 6)**: 統合テスト実装＋実行 → 全GREEN確認
7. **Validation (15-30分 x 2)**: 既存テスト＋既存ステージ確認 → 後方互換性確認

**推定総時間**: 約18-22時間（1-2日の集中実装、または1週間のペースで分散実装）

**並列実行効果**: Batch実行で約30-40%時間短縮可能（特にテスト作成フェーズ）

---

**実装準備完了！次のステップ**: T001からタスクを順次実行し、TDD原則に従ってRED → GREEN → Refactorサイクルを回してください。