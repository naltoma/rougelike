# Data Model: Random Stage Generation System

## Core Data Models

### StageType Enumeration
```python
from enum import Enum

class StageType(Enum):
    MOVE = "move"        # Basic movement (stages 01-03 equivalent)
    ATTACK = "attack"    # Combat scenarios (stages 04-06 equivalent)
    PICKUP = "pickup"    # Item collection (stages 07-09 equivalent)
    PATROL = "patrol"    # Moving enemies (stage 10 equivalent)
    SPECIAL = "special"  # Large enemies, complex conditions (stages 11-13 equivalent)
```

### GenerationParameters
```python
@dataclass
class GenerationParameters:
    stage_type: StageType
    seed: int
    output_path: Optional[str] = None
    validate: bool = False

    def get_filename(self) -> str:
        """Generate filename: generated_[type]_[seed].yml"""
        return f"generated_{self.stage_type.value}_{self.seed}.yml"

    def get_stage_id(self) -> str:
        """Generate stage ID: generated_[type]_[seed]"""
        return f"generated_{self.stage_type.value}_{self.seed}"
```

### StageConfiguration
```python
@dataclass
class StageConfiguration:
    """Complete YAML stage structure matching existing format"""
    id: str
    title: str
    description: str
    board: BoardConfiguration
    player: PlayerConfiguration
    goal: GoalConfiguration
    enemies: List[EnemyConfiguration]
    items: List[ItemConfiguration]
    constraints: ConstraintConfiguration

    # Optional advanced features (for special stages)
    victory_conditions: Optional[List[Dict]] = None
    learning_objectives: Optional[List[str]] = None
    hints: Optional[List[str]] = None
    error_handling: Optional[Dict] = None

@dataclass
class BoardConfiguration:
    size: Tuple[int, int]  # [width, height]
    grid: List[str]        # List of row strings
    legend: Dict[str, str] # Character to meaning mapping

@dataclass
class PlayerConfiguration:
    start: Tuple[int, int]     # [x, y] starting position
    direction: str             # N, S, E, W
    hp: int = 100             # Default HP
    max_hp: int = 100         # Default max HP
    attack_power: int = 30    # Default attack power

@dataclass
class GoalConfiguration:
    position: Tuple[int, int]  # [x, y] goal position

@dataclass
class EnemyConfiguration:
    id: str
    type: str              # normal, large_2x2, large_3x3, special_2x3
    position: Tuple[int, int]
    direction: str
    hp: int
    max_hp: int
    attack_power: int
    behavior: str = "normal"

    # Optional advanced features
    rage_threshold: Optional[float] = None
    area_attack_range: Optional[int] = None
    stage11_special: Optional[bool] = None
    special_conditions: Optional[Dict] = None

@dataclass
class ItemConfiguration:
    id: str
    type: str
    position: Tuple[int, int]
    value: Optional[int] = None

@dataclass
class ConstraintConfiguration:
    max_turns: int
    allowed_apis: List[str]
```

### ValidationResult
```python
@dataclass
class ValidationResult:
    success: bool
    stage_path: str
    path_found: bool
    required_apis: List[str]
    solution_length: Optional[int] = None
    error_details: Optional[str] = None
    detailed_analysis: Optional[Dict] = None

    def to_report(self) -> str:
        """Generate human-readable validation report"""
        if self.success:
            return f"✅ Stage {self.stage_path} is solvable in {self.solution_length} steps"
        else:
            return f"❌ Stage {self.stage_path} validation failed: {self.error_details}"

@dataclass
class SolutionPath:
    actions: List[str]      # Sequence of API calls
    positions: List[Tuple[int, int]]  # Player positions
    total_steps: int
    apis_used: Set[str]     # APIs required for solution
```

## Type-Specific Generation Rules

### Move Stage Generation
- **Board Size**: 5x5 to 8x8
- **Wall Density**: 10-25% of tiles
- **Complexity**: Simple paths, 1-2 direction changes minimum
- **APIs**: turn_left, turn_right, move, see
- **Validation**: Basic A* pathfinding from start to goal

### Attack Stage Generation
- **Board Size**: 6x6 to 10x10
- **Enemy Count**: 1-3 static enemies
- **Enemy HP**: 10-300 (progressive difficulty)
- **Wall Integration**: Use walls for tactical positioning
- **APIs**: + attack
- **Validation**: Pathfinding + enemy elimination requirements

### Pickup Stage Generation
- **Board Size**: 7x7 to 12x12
- **Item Count**: 2-5 items
- **Enemy Integration**: Mix of enemies and items
- **Collection Strategy**: Multiple pickup locations
- **APIs**: + pickup
- **Validation**: Path through all required items + enemies

### Patrol Stage Generation
- **Board Size**: 8x8 to 14x14
- **Moving Enemies**: 1-3 with patrol patterns
- **Stealth Elements**: Cover positions, timing requirements
- **Wait Strategy**: Timing-based puzzle elements
- **APIs**: + wait
- **Validation**: Complex pathfinding with moving obstacles

### Special Stage Generation
- **Board Size**: 10x10 to 15x15
- **Large Enemies**: 2x2, 3x3, 2x3 configurations
- **Special Conditions**: Complex elimination rules
- **All Features**: Items, multiple enemy types, conditions
- **APIs**: All available
- **Validation**: Multi-phase solution validation

## Data Relationships

```
StageType (1) → (N) StageConfiguration
GenerationParameters (1) → (1) StageConfiguration
StageConfiguration (1) → (1) ValidationResult
StageConfiguration (1) → (N) EnemyConfiguration
StageConfiguration (1) → (N) ItemConfiguration
StageConfiguration (1) → (1) BoardConfiguration
StageConfiguration (1) → (1) PlayerConfiguration
StageConfiguration (1) → (1) GoalConfiguration
StageConfiguration (1) → (1) ConstraintConfiguration
```

## State Transitions

```
GenerationParameters
    ↓ (generate_stage)
StageConfiguration
    ↓ (save_stage)
YAML File
    ↓ (validate_stage)
ValidationResult
```

## Validation Rules

### Board Validation
- Grid dimensions must match size specification
- All grid characters must be in legend
- Player start position must be valid (not wall/obstacle)
- Goal position must be valid and different from start

### Enemy Validation
- Positions must not overlap with walls or other entities
- Large enemies (2x2, 3x3, 2x3) must fit within board boundaries
- HP and attack values must be positive integers
- Behavior types must match allowed patterns

### Pathfinding Validation
- Must exist path from start to goal using allowed APIs
- Enemy positions must be reachable if attack required
- Item positions must be accessible if pickup required
- Solution path must use only constraint-allowed APIs

### Seed Reproducibility Validation
- Same seed + stage type must produce identical configuration
- Random state must be properly seeded and isolated
- Generated stage must pass validation consistently

## File Format Mapping

The StageConfiguration dataclass maps directly to YAML structure:

```yaml
# Generated from StageConfiguration
id: {stage_id}
title: {title}
description: {description}
board:
  size: {board.size}
  grid: {board.grid}
  legend: {board.legend}
player:
  start: {player.start}
  direction: {player.direction}
  hp: {player.hp}
  max_hp: {player.max_hp}
  attack_power: {player.attack_power}
goal:
  position: {goal.position}
enemies: {enemies}
items: {items}
constraints:
  max_turns: {constraints.max_turns}
  allowed_apis: {constraints.allowed_apis}
```

## Error Handling

### Generation Errors
- **InvalidSeedError**: Seed value out of acceptable range
- **UnsupportedStageTypeError**: Unknown or invalid stage type
- **GenerationTimeoutError**: Generation takes too long (>30s)
- **InvalidBoardConfigurationError**: Generated board violates constraints

### Validation Errors
- **FileNotFoundError**: Stage file doesn't exist
- **YAMLParseError**: Invalid YAML structure
- **SchemaValidationError**: Missing required fields or invalid types
- **PathfindingTimeoutError**: Validation takes too long (>60s)
- **UnsolvableStageError**: No valid solution path exists

---
*Data model complete - ready for contract generation*