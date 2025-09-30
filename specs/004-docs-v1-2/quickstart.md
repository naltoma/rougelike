# Quickstart: Detrimental Items and Item Management System

## Overview
Test the new bomb item system with is_available() and dispose() APIs through a complete development cycle.

## Prerequisites
- Existing rogue-like framework running
- Python 3.8+ with pytest installed
- Working stage generation and validation scripts

## Test Sequence

### Phase 1: Basic Item Management API Testing

#### Test 1: is_available() Function
```python
# Create test stage with beneficial item
stage_config = create_test_stage_with_item("key", position=(1, 1))
load_stage(stage_config)
move_to_position(1, 1)

# Test beneficial item detection
result = is_available()
assert result == True, "is_available() should return True for beneficial items"

# Test turn consumption
turn_before = get_turn_count()
is_available()
turn_after = get_turn_count()
assert turn_before == turn_after, "is_available() should not consume turns"
```

#### Test 2: dispose() Function with Bomb
```python
# Create test stage with bomb item
bomb_item = {
    "id": "test_bomb",
    "type": "bomb",
    "position": [2, 2],
    "damage": 50
}
stage_config = create_test_stage_with_item(bomb_item)
load_stage(stage_config)
move_to_position(2, 2)

# Test bomb detection
available = is_available()
assert available == False, "is_available() should return False for bomb items"

# Test disposal
result = dispose()
assert result.success == True, "dispose() should succeed for bomb items"

# Verify item removed
items_at_position = get_items_at_position(2, 2)
assert len(items_at_position) == 0, "Item should be removed after dispose()"
```

### Phase 2: HP System Integration Testing

#### Test 3: HP Damage from Bomb Collection
```python
# Setup bomb item
bomb_config = create_bomb_item(damage=30)
stage_config = create_test_stage_with_item(bomb_config)
load_stage(stage_config)
move_to_bomb_position()

# Record initial HP
initial_hp = get_player_hp()

# Collect bomb (should cause damage)
pickup()

# Verify HP reduction
current_hp = get_player_hp()
assert current_hp == initial_hp - 30, "HP should be reduced by bomb damage"
```

#### Test 4: Default Bomb Damage
```python
# Create bomb without explicit damage
bomb_config = {
    "id": "default_bomb",
    "type": "bomb",
    "position": [3, 3]
    # No damage field - should default to 100
}
stage_config = create_test_stage_with_item(bomb_config)
load_stage(stage_config)
move_to_position(3, 3)

initial_hp = get_player_hp()
pickup()
current_hp = get_player_hp()
assert current_hp == initial_hp - 100, "Default bomb damage should be 100"
```

### Phase 3: Stage Completion Integration Testing

#### Test 5: Stage Completion with Disposed Items
```python
# Create stage with bomb at goal approach
stage_config = create_stage_with_bomb_near_goal()
load_stage(stage_config)

# Move to bomb and dispose
navigate_to_bomb()
dispose()

# Move to goal
navigate_to_goal()

# Verify stage completion
assert is_stage_complete(), "Stage should complete with disposed bomb"
```

#### Test 6: Mixed Item Handling
```python
# Create stage with both beneficial and bomb items
stage_config = create_stage_with_mixed_items()
load_stage(stage_config)

# Handle beneficial item
move_to_beneficial_item()
assert is_available() == True
pickup()

# Handle bomb item
move_to_bomb_item()
assert is_available() == False
dispose()

# Complete stage
move_to_goal()
assert is_stage_complete(), "Stage should complete with mixed item handling"
```

### Phase 4: Stage Generation and Validation Testing

#### Test 7: Generate Stage with Bombs
```bash
# Generate new stage including bombs
python generate_stage.py --type attack --seed 789 --include-bombs

# Verify generated stage has bomb items
python -c "
import yaml
with open('stages/generated_attack_789.yml') as f:
    stage = yaml.safe_load(f)
bomb_items = [item for item in stage['items'] if item['type'] == 'bomb']
assert len(bomb_items) > 0, 'Generated stage should contain bomb items'
print('✓ Stage generation with bombs successful')
"
```

#### Test 8: Validate Bomb Stage
```bash
# Validate generated bomb stage
python validate_stage.py --file stages/generated_attack_789.yml --detailed

# Should output:
# ✓ Stage is solvable
# ✓ Bomb items properly handled with dispose()
# ✓ Stage completion achieved
```

### Phase 5: End-to-End Integration Test

#### Test 9: Complete Workflow
```python
def test_complete_bomb_workflow():
    """Test complete workflow from stage creation to completion"""

    # 1. Generate stage with bombs
    subprocess.run(["python", "generate_stage.py", "--type", "pickup",
                   "--seed", "999", "--include-bombs"], check=True)

    # 2. Load and play the generated stage
    stage_path = "stages/generated_pickup_999.yml"
    load_stage_from_file(stage_path)

    # 3. Use new APIs to complete stage
    while not is_stage_complete():
        current_pos = get_player_position()

        # Check for items at current position
        if has_item_at_position(current_pos):
            if is_available():
                pickup()  # Safe to collect
            else:
                dispose()  # Bomb item, dispose instead
        else:
            # Move toward goal or uncollected items
            next_move = plan_next_move()
            execute_move(next_move)

    # 4. Verify successful completion
    assert is_stage_complete()
    assert get_player_hp() > 0  # Should avoid bomb damage

    print("✓ Complete bomb workflow test passed")
```

## Success Criteria
- [ ] is_available() correctly identifies item types
- [ ] is_available() does not consume turns
- [ ] dispose() successfully removes bomb items
- [ ] dispose() consumes exactly one turn
- [ ] Bomb pickup causes appropriate HP damage
- [ ] Stage completion works with disposed items
- [ ] Generated stages include bomb items
- [ ] Validation handles bomb stages correctly
- [ ] All existing functionality remains unaffected

## Expected Output
```
Testing Item Management System v1.2.12
======================================

✓ is_available() basic functionality
✓ is_available() turn consumption
✓ dispose() bomb removal
✓ dispose() turn consumption
✓ HP damage from bomb pickup
✓ Default bomb damage (100)
✓ Stage completion with disposed items
✓ Mixed item handling
✓ Stage generation with bombs
✓ Stage validation with bombs
✓ Complete workflow integration

All tests passed! Bomb item system ready for deployment.
```

## Troubleshooting
- If is_available() always returns True: Check item type detection logic
- If dispose() fails: Verify item exists and is bomb type
- If HP doesn't change: Check HP system integration
- If stage won't complete: Verify disposed items count toward completion
- If generation fails: Check bomb item configuration format