# Data Model: Detrimental Items and Item Management System

## Entity Definitions

### Item (Extended)
**Purpose**: Represents game items including detrimental bomb items
**Existing attributes**: id, type, position, name, description, value
**New attributes**:
- `damage: Optional[int]` - HP damage dealt when collected (default: 100 for bomb type)

**Validation Rules**:
- damage must be positive integer when specified
- damage is required for bomb type items
- damage is ignored for non-bomb type items

**State Transitions**:
- Item can be: placed → collected (beneficial) / placed → disposed (detrimental)
- Collected/disposed items are removed from game map
- Items cannot be uncollected or undisposed

### Player State (Extended)
**Purpose**: Tracks player status including health points
**Existing attributes**: position, direction, inventory, collected_items
**New attributes**:
- `hp: int` - Current hit points (default: 100)
- `max_hp: int` - Maximum hit points (default: 100)
- `disposed_items: List[str]` - IDs of items that were disposed

**Validation Rules**:
- hp cannot exceed max_hp
- hp cannot be negative (minimum 0)
- disposed_items contains unique item IDs only

**State Transitions**:
- HP: max_hp → damaged (pickup bomb) → healed (future healing items)
- disposed_items: empty → accumulates disposed item IDs

### Stage Completion (Modified)
**Purpose**: Determines when a stage is successfully completed
**Existing logic**: collect_all_items checks if all items collected
**Modified logic**:
- collect_all_items satisfied when: (collected_items ∪ disposed_items) contains all item IDs
- Disposed bomb items count as "collected" for completion purposes

**Validation Rules**:
- No item can be both collected and disposed
- All items must be either collected or disposed for completion
- Goal position must still be reached

## API Interface Definitions

### is_available() Function
**Purpose**: Check if item at current position should be collected
**Parameters**: None (uses current player position)
**Returns**:
- `True` - if beneficial item at position (safe to pickup)
- `False` - if detrimental item at position (should dispose)
- `False` - if no item at position

**Behavior**:
- Non-turn-consuming operation
- Checks item at player's current position only
- Returns False for bomb-type items
- Returns True for all other item types

### dispose() Function
**Purpose**: Remove detrimental item from current position
**Parameters**: None (uses current player position)
**Returns**: `ExecutionResult` object with success/failure status
**Side Effects**:
- Consumes one turn
- Removes item from game map
- Adds item ID to player's disposed_items list
- Updates stage completion status

**Error Conditions**:
- No item at current position → failure
- Item is not detrimental type → failure (beneficial items should be collected)
- Item already collected/disposed → failure

## Relationships

### Item ↔ Player
- Player can collect beneficial items (existing)
- Player can dispose detrimental items (new)
- Items affect player HP when collected (new for bomb type)

### Item ↔ Stage Completion
- Collected items contribute to completion (existing)
- Disposed items contribute to completion (new)
- All items must be handled for completion

### API ↔ Game State
- is_available() reads game state, no modifications
- dispose() modifies game state (removes item, updates player)
- Both follow existing API patterns and error handling

## Data Flow

### Item Checking Flow
1. Player calls is_available()
2. Game checks item at current position
3. Return True/False based on item type
4. No state changes, no turn consumption

### Item Disposal Flow
1. Player calls dispose()
2. Validate item exists and is detrimental
3. Remove item from map
4. Add to player's disposed_items
5. Consume turn, update stage status
6. Return execution result

### Stage Completion Flow
1. Check if player at goal position
2. Calculate total_handled_items = collected_items ∪ disposed_items
3. Compare with total_items_on_stage
4. Stage complete if all items handled + at goal

## Persistence

### YAML Stage Files (Extended)
```yaml
items:
  - id: bomb_1
    type: bomb
    position: [4, 6]
    name: 爆弾
    description: An item must be disposed
    damage: 50  # New field for bomb items
```

### Session Logs (Extended)
- Log is_available() calls with results
- Log dispose() actions with item details
- Log HP changes from bomb collection
- Track completion via disposed items