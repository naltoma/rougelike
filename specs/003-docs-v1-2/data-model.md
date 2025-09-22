# Data Model: GUI Dynamic Display Enhancement v1.2.11

## Core Entities

### StatusChangeTracker
**Purpose**: Tracks status value changes between game turns and calculates deltas for visual emphasis.

**Attributes**:
- `previous_states: Dict[str, Dict[str, int]]` - Previous turn status values by entity ID
- `current_states: Dict[str, Dict[str, int]]` - Current turn status values by entity ID
- `change_deltas: Dict[str, Dict[str, int]]` - Calculated changes per entity per status type

**Key Methods**:
- `track_changes(entity_id: str, current_status: Dict[str, int]) -> Dict[str, int]`
- `has_changes(entity_id: str) -> bool`
- `get_change_delta(entity_id: str, status_key: str) -> int`
- `reset_entity_tracking(entity_id: str) -> None`

**Validation Rules**:
- entity_id must be non-empty string
- status values must be integers
- delta calculation: current_value - previous_value
- Supports negative deltas (decreases) and positive deltas (increases)

**State Transitions**:
1. Initial state: No previous values recorded
2. First update: Previous = Current, no changes detected
3. Subsequent updates: Changes = Current - Previous
4. Reset: Clear previous state for entity

### StageNameResolver
**Purpose**: Dynamically reads STAGE_ID variable from main_*.py files for accurate stage name display.

**Attributes**:
- `stage_id: str` - Resolved stage identifier from file
- `file_path: Path` - Path to the main_*.py file being analyzed
- `resolved_name: str` - Human-readable stage name for display
- `cache: Dict[str, str]` - Cached resolutions by file path

**Key Methods**:
- `resolve_stage_name(file_path: str) -> str`
- `validate_stage_id(stage_id: str) -> bool`
- `get_display_name(stage_id: str) -> str`
- `clear_cache() -> None`

**Validation Rules**:
- file_path must exist and be readable
- STAGE_ID variable must be string type
- stage_id format: "stage" + 2-digit number (e.g., "stage09")
- Fallback to "unknown_stage" if resolution fails

**State Transitions**:
1. Initial: No cached values
2. Resolution request: Load file, extract STAGE_ID, cache result
3. Cache hit: Return cached value
4. Error state: Return fallback value and log error

### DisplayStateManager
**Purpose**: Manages visual formatting states for status values based on change detection.

**Attributes**:
- `emphasis_state: Dict[str, Dict[str, EmphasisType]]` - Current emphasis per entity per status
- `color_config: ColorConfig` - Color definitions for different states
- `text_formatting: TextFormatConfig` - Font and style configurations

**Key Methods**:
- `format_status_text(entity_id: str, status_key: str, value: int, change: int) -> FormattedText`
- `get_emphasis_type(change_delta: int) -> EmphasisType`
- `apply_color_formatting(text: str, emphasis: EmphasisType) -> pygame.Surface`
- `reset_emphasis(entity_id: str) -> None`

**Validation Rules**:
- EmphasisType enum: DEFAULT, DECREASED, INCREASED
- Color values must be valid RGB tuples (0-255)
- Font sizes must be positive integers
- Change delta: negative = DECREASED, positive = INCREASED, zero = DEFAULT

**State Transitions**:
1. DEFAULT: No changes detected, normal text formatting
2. DECREASED: Negative change delta, red bold text with ↓ symbol
3. INCREASED: Positive change delta, green bold text with ↑ symbol
4. Back to DEFAULT: Next turn with no changes

## Supporting Types

### EmphasisType (Enum)
```python
class EmphasisType(Enum):
    DEFAULT = "default"
    DECREASED = "decreased"
    INCREASED = "increased"
```

### ColorConfig
```python
@dataclass
class ColorConfig:
    default_color: Tuple[int, int, int] = (255, 255, 255)  # White
    decreased_color: Tuple[int, int, int] = (255, 0, 0)    # Red
    increased_color: Tuple[int, int, int] = (0, 255, 0)    # Green
```

### TextFormatConfig
```python
@dataclass
class TextFormatConfig:
    normal_font_size: int = 24
    bold_font_size: int = 24
    font_family: Optional[str] = None
    decrease_symbol: str = "↓"
    increase_symbol: str = "↑"
```

### FormattedText
```python
@dataclass
class FormattedText:
    content: str
    color: Tuple[int, int, int]
    is_bold: bool
    emphasis_type: EmphasisType
```

### ChangeResult
```python
@dataclass
class ChangeResult:
    entity_id: str
    status_changes: Dict[str, int]
    has_any_changes: bool
    emphasis_map: Dict[str, EmphasisType]
```

## Entity Relationships

```
StatusChangeTracker ──┐
                      ├──> DisplayStateManager ──> FormattedText
StageNameResolver ────┘

Game Loop:
GameState → StatusChangeTracker → ChangeResult → DisplayStateManager → GUI Rendering
```

## Persistence

**Session-based**: All data models are session-scoped and reset between game runs.
**No permanent storage**: Changes and states are tracked only during active gameplay.
**Cache strategy**: StageNameResolver caches file resolutions for performance.

## Performance Characteristics

- **StatusChangeTracker**: O(n) per update where n = number of status values
- **StageNameResolver**: O(1) cache lookups after initial O(k) file parsing
- **DisplayStateManager**: O(1) formatting operations per status value
- **Memory usage**: Minimal - single previous state per entity + small caches