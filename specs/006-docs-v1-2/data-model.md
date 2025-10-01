# Data Model: Stamina System (v1.2.13)

**Date**: 2025-09-30
**Status**: Design Phase
**Source**: Derived from spec.md requirements and research.md findings

---

## 1. Core Data Models

### 1.1 Character (Player/Enemy) - Extended

**Location**: `engine/__init__.py`

```python
@dataclass
class Character:
    """キャラクター（プレイヤー・敵共通）"""
    # 既存フィールド
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

**Field Specifications**:

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `stamina` | `int` | 20 | `0 <= stamina <= max_stamina` | 現在のスタミナ値 |
| `max_stamina` | `int` | 20 | `max_stamina > 0` | 最大スタミナ値 |

**State Transitions**:
- `stamina` decreases by 1 on turn-consuming actions
- `stamina` increases by 10 on safe wait() (capped at `max_stamina`)
- When `stamina <= 0` → `hp = 0` (death condition)

**New Methods**:

```python
def consume_stamina(self, amount: int = 1) -> bool:
    """
    スタミナを消費する

    Args:
        amount: 消費量（デフォルト1）

    Returns:
        bool: スタミナ枯渇による死亡が発生した場合True
    """

def recover_stamina(self, amount: int) -> int:
    """
    スタミナを回復する（最大値を上限とする）

    Args:
        amount: 回復量

    Returns:
        int: 実際に回復した量
    """

def stamina_percentage(self) -> float:
    """
    スタミナ残量を百分率で返す

    Returns:
        float: 0.0～100.0のスタミナ残量パーセンテージ
    """
```

---

## 2. Configuration Models

### 2.1 HyperParametersData - Extended

**Location**: `engine/hyperparameter_manager.py`

```python
@dataclass
class HyperParametersData:
    """ハイパーパラメータデータクラス"""
    # 既存フィールド
    delay_ms: int = 100
    speed_level: int = 4

    # 新規フィールド (v1.2.13)
    enable_stamina: bool = False
```

**Field Specifications**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable_stamina` | `bool` | `False` | スタミナシステムの有効/無効切り替え |

**Default Behavior**:
- `False`: スタミナシステム無効（後方互換性維持）
- `True`: スタミナシステム有効

**Configuration Source**:
- `main.py`の`ENABLE_STAMINA`定数（ユーザー設定）
- デフォルト値: `False`

---

### 2.2 Stage Configuration (YAML) - Extended

**Location**: `stages/*.yml`

**Existing Structure**:
```yaml
player:
  start: [5, 6]
  direction: W
  hp: 100
  max_hp: 100
```

**New Structure (v1.2.13)**:
```yaml
player:
  start: [5, 6]
  direction: W
  hp: 100
  max_hp: 100
  stamina: 20        # オプション（省略時デフォルト: 20）
  max_stamina: 20    # オプション（省略時デフォルト: 20）
```

**Validation Rules**:
1. `stamina` and `max_stamina` are optional fields
2. If omitted, use defaults: `stamina = 20`, `max_stamina = 20`
3. If present: `0 <= stamina <= max_stamina`
4. If present: `max_stamina > 0`
5. Backward compatibility: Existing stage files without stamina fields must work

---

## 3. State Models

### 3.1 GameState - Stamina Tracking

**Location**: `engine/game_state.py`

**New State Tracking**:
```python
class GameStateManager:
    # 既存フィールド
    _state: Stage
    _hyperparameter_manager: HyperParameterManager
    _status_change_tracker: StatusChangeTracker

    # スタミナ関連の状態追跡
    # （既存のCharacterモデルで管理、追加フィールド不要）
```

**State Changes to Track**:
1. **Stamina consumption** (-1 per action)
2. **Stamina recovery** (+10 on safe wait)
3. **Stamina depletion** (stamina = 0 → hp = 0)

**Integration with StatusChangeTracker**:
- Track stamina changes for GUI highlighting
- Format: `stamina: 20 → 19` (red highlight for decrease)
- Format: `stamina: 10 → 20` (green highlight for increase)

---

### 3.2 StatusChangeTracker - Stamina Support

**Location**: `engine/renderer.py` (lines 40-121)

**New Change Type**:
```python
@dataclass
class StatusChange:
    # 既存フィールド
    old_hp: Optional[int]
    new_hp: Optional[int]
    old_items: Optional[List[str]]
    new_items: Optional[List[str]]

    # 新規フィールド (v1.2.13)
    old_stamina: Optional[int] = None
    new_stamina: Optional[int] = None
```

**Change Detection Logic**:
```python
def track_changes(old_player: Character, new_player: Character):
    changes = StatusChange(
        old_hp=old_player.hp,
        new_hp=new_player.hp,
        old_items=old_player.collected_items.copy(),
        new_items=new_player.collected_items.copy(),
        old_stamina=old_player.stamina,  # NEW
        new_stamina=new_player.stamina,  # NEW
    )
```

---

## 4. API Models

### 4.1 New API Function

**Location**: `engine/api.py`

```python
def get_stamina() -> int:
    """
    現在のスタミナ値を取得

    ターン消費: なし
    スタミナ消費: なし

    Returns:
        int: 現在のスタミナ値

    Raises:
        RuntimeError: ゲーム未実行時
    """
```

**API Characteristics**:
- Non-turn-consuming (no turn increment)
- Non-stamina-consuming (free query)
- Returns current player stamina value
- Available even when `ENABLE_STAMINA = False` (returns current value)

---

## 5. Relationships

### 5.1 Entity Relationships

```
HyperParametersData
  └─ enable_stamina: bool
       ↓ (controls)
GameStateManager
  └─ execute_command()
       ↓ (checks flag)
       ├─ IF enable_stamina == True:
       │    ├─ player.consume_stamina(1)
       │    └─ IF stamina <= 0: player.hp = 0
       └─ IF enable_stamina == False:
            └─ (no stamina logic)

Character (player)
  ├─ stamina: int
  ├─ max_stamina: int
  ├─ consume_stamina()
  ├─ recover_stamina()
  └─ stamina_percentage()
       ↑ (used by)
Renderer
  └─ render_game_info()
       └─ display: "スタミナ: 15/20"
```

### 5.2 Data Flow

```
1. Stage Load:
   YAML → StageLoader._validate_player() → Character(stamina=20, max_stamina=20)

2. Action Execution:
   user_code → api.move() → TurnLeftCommand.execute()
   → GameStateManager.execute_command()
   → IF enable_stamina: player.consume_stamina(1)

3. Wait Recovery:
   user_code → api.wait() → WaitCommand.execute()
   → IF safe_conditions: player.recover_stamina(10)

4. Stamina Query:
   user_code → api.get_stamina() → return player.stamina

5. GUI Display:
   Renderer.render_game_info() → f"スタミナ: {stamina}/{max_stamina}"
```

---

## 6. Validation Rules

### 6.1 Runtime Validation

| Validation | Rule | Error Handling |
|------------|------|----------------|
| Stamina bounds | `0 <= stamina <= max_stamina` | Clamp to valid range |
| Max stamina positive | `max_stamina > 0` | Stage load error |
| Stamina depletion | `stamina <= 0` | Set `hp = 0` (death) |
| Recovery cap | `stamina + recovery <= max_stamina` | Cap at `max_stamina` |

### 6.2 Configuration Validation

| Validation | Rule | Default Behavior |
|------------|------|------------------|
| YAML stamina field | Optional | Default: 20 |
| YAML max_stamina field | Optional | Default: 20 |
| ENABLE_STAMINA flag | Must be bool | Default: False |

---

## 7. Backward Compatibility

### 7.1 Existing Stage Files

**Requirement**: Existing stage YAML files without `stamina`/`max_stamina` must work

**Solution**:
```python
# In StageLoader._validate_player()
stamina = player_config.get("stamina", 20)        # Default 20
max_stamina = player_config.get("max_stamina", 20)  # Default 20
```

### 7.2 Existing Tests

**Requirement**: All existing tests must pass without modification

**Solution**: Default `ENABLE_STAMINA = False` ensures:
- No stamina consumption logic runs
- No stamina death condition triggers
- Tests see identical behavior to v1.2.12

---

## 8. Design Constraints

### 8.1 User File Protection

**Constraint**: DO NOT modify `main_*.py` files (user exercise files)

**Impact on Design**:
- API changes only in `engine/api.py` (add `get_stamina()`)
- Hyperparameter in `main.py` (template for user copying)
- No changes to user-facing action signatures

### 8.2 Performance Considerations

**Stamina Check Overhead**:
- Single boolean check per action: `if enable_stamina:`
- Negligible performance impact (<1μs per action)

**Memory Overhead**:
- 2 additional integers per Character: `stamina`, `max_stamina`
- Total: 16 bytes per character (negligible)

---

## 9. Summary

### 9.1 New Fields

| Entity | New Fields | Type | Default |
|--------|------------|------|---------|
| `Character` | `stamina` | `int` | 20 |
| `Character` | `max_stamina` | `int` | 20 |
| `HyperParametersData` | `enable_stamina` | `bool` | False |
| `StatusChange` | `old_stamina` | `Optional[int]` | None |
| `StatusChange` | `new_stamina` | `Optional[int]` | None |

### 9.2 New Methods

| Class | Method | Purpose |
|-------|--------|---------|
| `Character` | `consume_stamina(amount)` | スタミナ消費＋枯渇死判定 |
| `Character` | `recover_stamina(amount)` | スタミナ回復（上限付き） |
| `Character` | `stamina_percentage()` | GUI表示用パーセンテージ |
| `APILayer` | `get_stamina()` | 現在スタミナ取得API |

### 9.3 Modified Systems

| System | Modification |
|--------|--------------|
| Stage Loader | Parse optional `stamina`/`max_stamina` from YAML |
| Command Execution | Add stamina consumption logic (if enabled) |
| Wait Command | Add stamina recovery logic (if safe) |
| Renderer (CUI) | Display stamina in game info |
| Renderer (GUI) | Display stamina in sidebar + highlight changes |
| Hyperparameter Manager | Add `enable_stamina` flag |

---

**Next Steps**:
1. Generate contract tests for new API (`get_stamina()`)
2. Create integration test scenarios from acceptance criteria
3. Write quickstart.md with example usage
4. Update CLAUDE.md with stamina system context