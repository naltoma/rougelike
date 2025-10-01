# Phase 0 Research: Stamina System (v1.2.13)

**Research Date**: 2025-09-30
**Target Feature**: Stamina system with toggle ON/OFF, turn consumption, wait recovery, GUI display
**Constraint**: DO NOT modify main_*.py files (user exercise files)

---

## Executive Summary

This research document provides comprehensive technical information for implementing a stamina system in the Python roguelike framework. The stamina system will:
- Track player stamina (default 20/20)
- Consume 1 stamina per turn-consuming action
- Recover +10 stamina on wait() under safe conditions
- Display stamina in GUI player info
- Support toggle via ENABLE_STAMINA hyperparameter (default: OFF)
- Be configurable per-stage via YAML

---

## 1. Player Class/Model

### Location
**File**: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/__init__.py`
**Class**: `Character` (lines 146-227)

### Current Player Structure
```python
@dataclass
class Character:
    """キャラクター（プレイヤー・敵共通）"""
    position: Position
    direction: Direction
    hp: int = 100
    max_hp: int = 100
    attack_power: int = 30
    # v1.2.12: プレイヤー専用フィールド
    collected_items: List[str] = field(default_factory=list)
    disposed_items: List[str] = field(default_factory=list)
```

### Key Methods
- `is_alive()`: Returns `self.hp > 0`
- `take_damage(damage, attacker_position)`: Reduces HP, returns actual damage taken
- `heal(amount)`: Restores HP, returns actual heal amount
- `hp_percentage()`: Returns HP% (0-100)

### Integration Points for Stamina
1. **Add stamina attributes** to `Character` dataclass:
   - `stamina: int = 20`
   - `max_stamina: int = 20`

2. **Add stamina methods**:
   - `consume_stamina(amount)`: Reduce stamina, check for depletion → death
   - `recover_stamina(amount)`: Restore stamina (capped at max_stamina)
   - `stamina_percentage()`: Return stamina% for GUI display

3. **Death condition**: When `stamina <= 0`, set `hp = 0` (instant death)

---

## 2. Action System

### Location
**Files**:
- Command Pattern: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/commands.py`
- API Layer: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/api.py`

### Turn-Consuming Actions (Stamina -1)
**Command Classes** (all in `commands.py`):
1. `TurnLeftCommand` (lines 130-168)
2. `TurnRightCommand` (lines 171-209)
3. `MoveCommand` (lines 212-266)
4. `AttackCommand` (lines 269-337)
5. `PickupCommand` (lines 340-430)
6. `DisposeCommand` (lines 463-539) - v1.2.12
7. `WaitCommand` (lines 433-460)

### Non-Turn-Consuming Actions (No Stamina Cost)
- `see()`: Returns vision data without consuming turn
- `get_stage_info()`: Returns stage metadata
- `get_stamina()`: **NEW API** - returns current stamina, no turn/stamina cost
- `is_available()`: Checks item availability

### Command Execution Flow
```
APILayer.turn_left()
  → ExecutionController.wait_for_action()  # GUI control
  → TurnLeftCommand.execute(game_state)
  → GameStateManager.execute_command(command)
  → _update_game_state()  # Turn increment + enemy processing
```

### Integration Points for Stamina
1. **Before command execution** in `GameStateManager.execute_command()` (game_state.py:85-126):
   - Check if ENABLE_STAMINA is ON
   - If stamina <= 0, prevent action and set player death

2. **After successful command execution**:
   - Consume 1 stamina for turn-consuming commands
   - Check stamina depletion → trigger death if stamina = 0

3. **WaitCommand special case**:
   - Check if safe conditions met (no alerted enemies + not attacked this turn)
   - If safe: recover +10 stamina (capped at max_stamina)
   - If unsafe: normal stamina consumption (-1)

---

## 3. Stage Loading System

### Location
**File**: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/stage_loader.py`

### Current Stage YAML Structure
**Example**: `/Users/tnal/2025/lecture/prog1-exe/rougelike/stages/stage01.yml`
```yaml
player:
  start: [0, 0]
  direction: "N"
  hp: 100
  max_hp: 100
  # Optional fields parsed by StageLoader:
  # attack_power: 30
```

### Stage Loading Flow
1. `StageLoader.load_stage(stage_id)` → reads YAML
2. `_validate_player()` (lines 121-165) → validates player config
3. `_build_stage()` (lines 358-470) → extracts player HP/max_HP/attack_power
4. `APILayer.initialize_stage()` (api.py:117-216) → passes to GameStateManager
5. `GameStateManager.initialize_game()` (game_state.py:22-83) → creates Character with stats

### Current Player Config Parsing (stage_loader.py:397-400)
```python
# プレイヤーのステータス情報の抽出（オプション）
player_hp = player_data.get("hp")
player_max_hp = player_data.get("max_hp")
player_attack_power = player_data.get("attack_power")
```

### Integration Points for Stamina
1. **Add stamina validation** in `_validate_player()`:
   ```python
   if "stamina" in player_data:
       if not isinstance(player_data["stamina"], int) or player_data["stamina"] <= 0:
           raise StageValidationError("player.stamina must be positive integer")

   if "max_stamina" in player_data:
       if not isinstance(player_data["max_stamina"], int) or player_data["max_stamina"] <= 0:
           raise StageValidationError("player.max_stamina must be positive integer")
   ```

2. **Add stamina extraction** in `_build_stage()`:
   ```python
   player_stamina = player_data.get("stamina")
   player_max_stamina = player_data.get("max_stamina")
   ```

3. **Pass stamina to Stage dataclass** (add to Stage.__init__):
   ```python
   player_stamina: Optional[int] = None
   player_max_stamina: Optional[int] = None
   ```

4. **Apply defaults** in `GameStateManager.initialize_game()`:
   ```python
   final_stamina = player_stamina if player_stamina is not None else 20
   final_max_stamina = player_max_stamina if player_max_stamina is not None else final_stamina
   ```

---

## 4. GUI Rendering System

### Location
**File**: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/renderer.py`

### Current Player Info Display
**CUI Renderer** (lines 158-173):
```python
def render_game_info(self, game_state: GameState) -> None:
    print(f"🎮 ターン: {game_state.turn_count}/{game_state.max_turns}")
    print(f"📍 位置: ({game_state.player.position.x}, {game_state.player.position.y})")
    print(f"🧭 向き: {game_state.player.direction.value}")
    print(f"❤️  HP: {game_state.player.hp}/{game_state.player.max_hp}")
    print(f"⚔️ 攻撃力: {game_state.player.attack_power}")
    print(f"🎯 状態: {game_state.status.value}")
```

**GUI Renderer** (lines 829-879):
```python
# HP display with change highlighting
if should_highlight:
    hp_change = self.status_tracker.get_change_delta("player", "hp")
    if hp_change != 0:
        # Highlighted display with change delta
        value_text = str(game_state.player.hp)
        suffix_text = f"/{game_state.player.max_hp} "
        change_text = f"({change_symbol}{abs(hp_change)})"
    else:
        # Default display
        self._draw_text(f"HP: {game_state.player.hp}/{game_state.player.max_hp}", ...)
```

### GUI Enhancement System (v1.2.11)
**Status Change Tracking** (`gui_enhancement/status_change_tracker.py`):
- Tracks changes in player/enemy status values
- Provides highlighting for HP/Attack changes
- Used by `DisplayStateManager` for visual emphasis

### Integration Points for Stamina
1. **Add stamina to CUI display** (after HP line):
   ```python
   if ENABLE_STAMINA:  # Check hyperparameter
       print(f"💨 スタミナ: {game_state.player.stamina}/{game_state.player.max_stamina}")
   ```

2. **Add stamina to GUI display** (in sidebar after HP):
   ```python
   # Stamina display with change highlighting
   if ENABLE_STAMINA:
       stamina_change = self.status_tracker.get_change_delta("player", "stamina")
       if stamina_change != 0:
           # Highlighted display (green for +, red for -)
           self._draw_text_highlighted(f"Stamina: {player.stamina}/{player.max_stamina} ({change})", ...)
       else:
           self._draw_text(f"Stamina: {player.stamina}/{player.max_stamina}", ...)
   ```

3. **Update StatusChangeTracker** to include stamina:
   ```python
   player_status = {
       "hp": game_state.player.hp,
       "attack": game_state.player.attack_power,
       "stamina": game_state.player.stamina  # NEW
   }
   ```

---

## 5. Main.py Structure & Hyperparameters

### Location
**File**: `/Users/tnal/2025/lecture/prog1-exe/rougelike/main.py`

### Main.py User Section (NOT TO BE MODIFIED)
**Pattern**: All `main_*.py` files (e.g., `main_stage01.py`, `main_stage02.py`)
- These are **user exercise files** for students
- **CONSTRAINT**: Cannot modify these files
- Students write their solve() function here

### Hyperparameter Management
**Manager**: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/hyperparameter_manager.py`

**Current Hyperparameters** (lines 13-21):
```python
@dataclass
class HyperParametersData:
    stage_id: str = "stage01"
    student_id: Optional[str] = None
    log_enabled: bool = True
    initial_confirmation_mode: bool = False  # v1.2.4
    stage_intro_displayed: Dict[str, bool] = field(default_factory=dict)
```

**Config Source**: `/Users/tnal/2025/lecture/prog1-exe/rougelike/config.py`

### Integration Points for Stamina
1. **Add ENABLE_STAMINA to HyperParametersData**:
   ```python
   @dataclass
   class HyperParametersData:
       # ... existing fields ...
       enable_stamina: bool = False  # v1.2.13: Stamina system toggle (default OFF)
   ```

2. **Add config loader support** in `load_from_config()`:
   ```python
   if hasattr(config_module, 'ENABLE_STAMINA'):
       self.data.enable_stamina = config_module.ENABLE_STAMINA
   ```

3. **Expose global flag** in config.py:
   ```python
   # v1.2.13: Stamina system toggle
   ENABLE_STAMINA = False  # Default OFF for backward compatibility
   ```

4. **Access in engine code**:
   ```python
   from engine.hyperparameter_manager import hyperparameter_manager
   if hyperparameter_manager.data.enable_stamina:
       # Apply stamina logic
   ```

---

## 6. Enemy AI System

### Location
**Files**:
- Enemy AI: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/game_state.py` (GameStateManager)
- Enemy Class: `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/__init__.py` (Enemy)

### Enemy Turn Processing
**Method**: `GameStateManager._process_enemy_turns()` (game_state.py:200-303)

**Enemy Alert System**:
```python
for enemy in self.current_state.enemies:
    # Vision check
    can_see = enemy.can_see_player(player.position, board)

    if can_see:
        enemy.alerted = True  # Alert on player detection
        enemy.alert_cooldown = 10  # 10-turn tracking
    elif enemy.alert_cooldown > 0:
        enemy.alert_cooldown -= 1  # Decay tracking
        if enemy.alert_cooldown <= 0:
            enemy.alerted = False  # Return to patrol
```

**Enemy Attack Flow** (game_state.py:317-346):
```python
if distance == 1:  # Adjacent
    damage = enemy.attack_power
    actual_damage = player.take_damage(damage)
    if not player.is_alive():
        self.current_state.status = GameStatus.FAILED
```

### Wait() Safety Conditions
For stamina recovery on wait(), check:
1. **No alerted enemies**: `all(not enemy.alerted for enemy in enemies)`
2. **No damage this turn**: Track if player received attack damage

### Integration Points for Stamina
1. **Track attack status** during enemy turn:
   ```python
   self.current_state.player_attacked_this_turn = False  # Reset at turn start

   # In enemy attack section:
   if distance == 1 and attack_success:
       self.current_state.player_attacked_this_turn = True
   ```

2. **WaitCommand stamina recovery logic**:
   ```python
   # In WaitCommand.execute()
   if ENABLE_STAMINA:
       no_alerted_enemies = all(not e.alerted for e in game_state.enemies)
       not_attacked = not getattr(game_state, 'player_attacked_this_turn', False)

       if no_alerted_enemies and not_attacked:
           # Safe wait: recover stamina
           recovered = game_state.player.recover_stamina(10)
           result.message += f" - スタミナ回復: +{recovered}"
       else:
           # Unsafe wait: normal stamina consumption
           game_state.player.consume_stamina(1)
   ```

---

## 7. Technical Decisions & Dependencies

### Python Version
- **Python 3.9+** (confirmed by dataclass usage and type hints)

### Key Dependencies
- **pygame**: GUI rendering (optional, graceful fallback to CUI)
- **PyYAML**: Stage configuration loading
- **dataclasses**: Core data models

### Testing Framework
- **pytest**: Standard testing (found in `/Users/tnal/2025/lecture/prog1-exe/rougelike/tests/`)
- Test patterns: Unit tests, integration tests, contract tests

### Architecture Patterns
1. **Command Pattern**: All player actions are Command objects
2. **Data Classes**: Immutable Position, mutable Character/Enemy/GameState
3. **Observer Pattern**: Renderer observers for state changes
4. **Factory Pattern**: RendererFactory for CUI/GUI creation
5. **Manager Pattern**: GameStateManager, HyperParameterManager, SessionLogManager

---

## 8. Implementation Strategy

### Phase 1: Core Data Model
1. Add stamina/max_stamina to Character dataclass
2. Add stamina methods (consume, recover, percentage)
3. Add death condition when stamina = 0

### Phase 2: Hyperparameter System
1. Add ENABLE_STAMINA to HyperParametersData
2. Add config loader support
3. Expose in config.py (default: False)

### Phase 3: Stage Configuration
1. Add stamina validation to StageLoader
2. Add stamina parsing in _build_stage()
3. Add stamina fields to Stage dataclass
4. Apply defaults in GameStateManager.initialize_game()

### Phase 4: Action System Integration
1. Add stamina consumption in GameStateManager.execute_command()
2. Track player_attacked_this_turn in _process_enemy_turns()
3. Implement wait() recovery logic in WaitCommand
4. Add death check after stamina depletion

### Phase 5: API Layer
1. Implement get_stamina() in APILayer (no turn/stamina cost)
2. Export get_stamina to global API

### Phase 6: GUI Display
1. Add stamina to CUI renderer (render_game_info)
2. Add stamina to GUI renderer (sidebar player info)
3. Update StatusChangeTracker to track stamina changes
4. Add stamina highlighting (green for +, red for -)

### Phase 7: Testing & Validation
1. Unit tests: stamina consumption/recovery
2. Integration tests: wait() recovery conditions
3. Stage loading tests: YAML stamina config
4. GUI tests: stamina display and highlighting
5. E2E tests: full stamina system workflow

---

## 9. Special Considerations

### Backward Compatibility
- **Default**: ENABLE_STAMINA = False (system OFF)
- **Existing stages**: Work unchanged without stamina config
- **Existing tests**: Pass without modification
- **User code**: main_*.py files remain untouched

### Performance Impact
- **Negligible**: Single integer check per action
- **No allocation**: Stamina values stored in existing Character object
- **No new loops**: Integrates into existing command execution flow

### Edge Cases
1. **Stamina exactly 0**: Player dies immediately (hp = 0)
2. **Wait recovery overflow**: Cap at max_stamina
3. **YAML stamina omitted**: Default to 20/20
4. **YAML stamina = 0**: Validation error (must be positive)
5. **Mixed safe/unsafe wait**: If any enemy alerted OR player attacked → unsafe

### Design Constraints
**CRITICAL**: Cannot modify main_*.py files
- Stamina logic must be in engine/ directory only
- API changes must be backward-compatible
- GUI changes must not break existing rendering
- Stage YAML changes must be optional

---

## 10. File Change Checklist

### Core Engine Files (MODIFY)
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/__init__.py`
  - Add stamina/max_stamina to Character
  - Add stamina methods

- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/game_state.py`
  - Add stamina consumption in execute_command()
  - Track player_attacked_this_turn
  - Add stamina death check

- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/commands.py`
  - Update WaitCommand with stamina recovery logic

- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/api.py`
  - Implement get_stamina() API

- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/stage_loader.py`
  - Add stamina validation and parsing

- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/renderer.py`
  - Add stamina display (CUI + GUI)

- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/hyperparameter_manager.py`
  - Add ENABLE_STAMINA hyperparameter

### Configuration Files (MODIFY)
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/config.py`
  - Add ENABLE_STAMINA = False

### GUI Enhancement Files (MODIFY)
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/engine/gui_enhancement/status_change_tracker.py`
  - Add stamina tracking

### Test Files (CREATE NEW)
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/tests/unit/test_stamina.py`
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/tests/integration/test_stamina_system.py`
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/tests/contract/test_stamina_api.py`

### Documentation Files (CREATE NEW)
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/docs/v1.2.13.md`
- [ ] `/Users/tnal/2025/lecture/prog1-exe/rougelike/docs/stamina_system_guide.md`

### User Files (DO NOT MODIFY)
- [ ] ❌ `main_*.py` files (student exercise files)

---

## 11. Reference Implementations

### Similar Systems in Codebase
1. **HP System**: Character.hp, max_hp, take_damage(), heal()
   - Stamina follows same pattern

2. **Attack Power System**: Character.attack_power
   - GUI display with highlighting (v1.2.11)
   - Stamina uses same display pattern

3. **Item System** (v1.2.12): collected_items, disposed_items
   - Optional YAML config with defaults
   - Stamina uses same config pattern

4. **Wait System**: WaitCommand with conditional behavior
   - Stamina recovery extends wait() logic

### Version History Pattern
- **v1.2.1**: GUI critical fixes
- **v1.2.2**: Session logging
- **v1.2.3**: Google Sheets integration
- **v1.2.4**: Initial execution behavior
- **v1.2.5**: Speed control (7-stage)
- **v1.2.6**: Attack system
- **v1.2.7**: Wait/pickup system
- **v1.2.8**: Special conditional stages
- **v1.2.9**: Random stage generation
- **v1.2.10**: Documentation (see tutorial)
- **v1.2.11**: GUI enhancements (status highlighting)
- **v1.2.12**: Advanced item system (bomb, dispose)
- **v1.2.13**: **Stamina system** (THIS VERSION)

---

## 12. Implementation Notes

### Critical Success Factors
1. **Toggle System**: ENABLE_STAMINA must work cleanly (ON/OFF)
2. **Default OFF**: Backward compatibility is paramount
3. **No main_*.py changes**: All logic in engine/ directory
4. **Wait() recovery**: Conditional logic must be precise
5. **Death on depletion**: Stamina = 0 → hp = 0 (instant death)
6. **GUI integration**: Stamina display with highlighting

### Testing Priority
1. **High**: Stamina consumption on actions
2. **High**: Wait() recovery conditions (safe vs unsafe)
3. **High**: Death on stamina depletion
4. **Medium**: YAML config parsing
5. **Medium**: GUI display and highlighting
6. **Low**: Performance benchmarks

### Documentation Requirements
1. User guide: How to enable stamina system
2. Developer guide: How stamina system works internally
3. YAML guide: How to configure stamina in stages
4. API reference: get_stamina() documentation

---

## Research Completed: 2025-09-30

All necessary information has been gathered for implementing the stamina system (v1.2.13). This research provides:
- Complete file locations for all integration points
- Detailed current architecture understanding
- Clear implementation strategy
- Comprehensive edge case analysis
- File change checklist
- Testing strategy

**Next Phase**: Proceed to specification creation using kiro workflow.