# Quickstart Guide: Random Stage Generation System

## Overview
This guide demonstrates how to generate and validate random stages for the Python roguelike framework. All generated stages maintain compatibility with the existing YAML format and require no changes to main_*.py files.

## Prerequisites
- Python 3.8+ with PyYAML installed
- Existing roguelike framework (v1.2.8+)
- Write access to the stages/ directory

## Quick Start Commands

### 1. Generate a Basic Movement Stage
```bash
# Generate a simple movement stage (equivalent to stages 01-03)
python generate_stage.py --type move --seed 123

# Output:
# ✅ Generated move stage with seed 123
#    File: stages/generated_move_123.yml
#    Size: 7x7, Walls: 12, Path length: ~15 steps
```

### 2. Generate and Validate an Attack Stage
```bash
# Generate an attack stage and validate it immediately
python generate_stage.py --type attack --seed 456 --validate

# Output:
# ✅ Generated attack stage with seed 456
#    File: stages/generated_attack_456.yml
#    Size: 8x8, Enemies: 2, Items: 0
# ✅ Validation passed: Solvable in 23 steps using [turn_left, turn_right, move, attack, see]
```

### 3. Generate All Stage Types
```bash
# Generate one of each type with predictable seeds
python generate_stage.py --type move --seed 100
python generate_stage.py --type attack --seed 200
python generate_stage.py --type pickup --seed 300
python generate_stage.py --type patrol --seed 400
python generate_stage.py --type special --seed 500
```

### 4. Validate an Existing Stage
```bash
# Validate a hand-crafted stage
python validate_stage.py --file stages/stage01.yml

# Validate with detailed analysis
python validate_stage.py --file stages/generated_special_500.yml --detailed
```

## Generated Stage Structure

All generated stages follow the existing YAML format:

```yaml
id: generated_move_123
title: Generated Movement Stage
description: Randomly generated stage focusing on basic movement and navigation skills.
board:
  size: [7, 7]
  grid:
    - "......."
    - ".#..#.."
    - "......#"
    - "..#...."
    - "#......"
    - "...#..."
    - "......."
  legend:
    ".": "empty"
    "#": "wall"
    "P": "player"
    "G": "goal"
player:
  start: [0, 0]
  direction: "E"
  hp: 100
  max_hp: 100
goal:
  position: [6, 6]
enemies: []
items: []
constraints:
  max_turns: 50
  allowed_apis: ["turn_left", "turn_right", "move", "see"]
```

## Stage Types and Characteristics

### Move Stages (Type: move)
- **Equivalent to**: stages 01-03
- **Focus**: Basic navigation and pathfinding
- **Features**: Simple walls, no enemies or items
- **APIs**: turn_left, turn_right, move, see
- **Difficulty**: Progressive path complexity

### Attack Stages (Type: attack)
- **Equivalent to**: stages 04-06
- **Focus**: Combat mechanics and enemy elimination
- **Features**: Static enemies with varying HP
- **APIs**: + attack
- **Difficulty**: Multiple enemies, tactical positioning

### Pickup Stages (Type: pickup)
- **Equivalent to**: stages 07-09
- **Focus**: Item collection and resource management
- **Features**: Items scattered across map, some enemies
- **APIs**: + pickup
- **Difficulty**: Multiple collection points, mixed obstacles

### Patrol Stages (Type: patrol)
- **Equivalent to**: stage 10
- **Focus**: Stealth and timing mechanics
- **Features**: Moving enemies with patrol patterns
- **APIs**: + wait
- **Difficulty**: Timing-based puzzles, moving obstacles

### Special Stages (Type: special)
- **Equivalent to**: stages 11-13
- **Focus**: Advanced mechanics and complex scenarios
- **Features**: Large enemies (2x2, 3x3, 2x3), special conditions
- **APIs**: All available
- **Difficulty**: Multi-phase challenges, complex elimination rules

## Using Generated Stages in Practice

### 1. Integration with Existing Framework
```python
# Generated stages work exactly like hand-crafted ones
from engine.game_state import GameState

# Load and play a generated stage
game = GameState()
game.initialize_stage("generated_attack_456")  # Works seamlessly
game.set_student_id("student123")

# All existing APIs work normally
result = game.see()
game.move()
game.attack()
```

### 2. Batch Generation for Course Content
```bash
# Create a complete set of varied stages for students
for seed in {1..10}; do
  python generate_stage.py --type move --seed $seed
  python generate_stage.py --type attack --seed $((seed + 100))
done
```

### 3. Quality Assurance Workflow
```bash
# Generate and validate in one step
python generate_stage.py --type special --seed 999 --validate

# Separate validation for detailed analysis
python validate_stage.py --file stages/generated/generated_special_999.yml --detailed
```

## Validation Output Examples

### Successful Validation
```
✅ Stage stages/generated_attack_456.yml is solvable

Solution Analysis:
  Steps: 23
  APIs used: turn_left, turn_right, move, attack, see
  Path: [0,0] → [1,0] → [1,1] → [2,1] → [3,1] → ... → [7,7]

Combat Analysis:
  Enemies defeated: 2
  - Enemy at [3,3]: 3 attacks (90 HP)
  - Enemy at [5,5]: 1 attack (10 HP)

Efficiency Rating: Good (optimal path +5 steps for combat)
```

### Failed Validation
```
❌ Stage stages/generated_test_impossible.yml is not solvable

Analysis:
  Issue: No path to goal
  Cause: Goal position [9,9] unreachable from start [0,0]
  Blocked by: Walls form complete barrier at row 5

Suggestions:
  - Regenerate with different seed
  - Check stage type constraints
  - Report as generation bug if consistently failing
```

## Advanced Usage

### Custom Output Directory
```bash
# Generate stages in a custom location (files still named generated_[type]_[seed].yml)
python generate_stage.py --type move --seed 123 --output custom_stages/
```

### Quiet Mode for Scripting
```bash
# Suppress verbose output for batch processing
python generate_stage.py --type attack --seed 456 --quiet
echo "Exit code: $?"  # 0 = success, non-zero = failure
```

### JSON Format for Analysis
```bash
# Output validation results in JSON for programmatic processing
python validate_stage.py --file stages/stage01.yml --format json
```

## Testing Generated Stages

### Manual Testing
1. Generate a stage with known seed
2. Load in the framework
3. Attempt to solve manually
4. Verify solution matches validation results

### Automated Testing
```python
# Example test case
def test_generated_stage_solvability():
    # Generate stage
    params = GenerationParameters(StageType.ATTACK, seed=456)
    config = generate_stage(params)

    # Validate
    result = validate_stage_solvability(config)
    assert result.success, f"Generated stage should be solvable: {result.error_details}"

    # Test in actual game engine
    game = GameState()
    game.load_stage_config(config)
    # ... run solution steps ...
    assert game.is_complete(), "Validation solution should work in practice"
```

## Troubleshooting

### Common Issues

**Generation Fails**:
- Check seed value (must be 0 to 2^32-1)
- Verify stage type spelling
- Ensure write permissions to output directory

**Validation Fails**:
- Some seeds may produce unsolvable stages (this is expected)
- Try different seed values
- Check that stage type constraints are appropriate

**Integration Issues**:
- Generated stages follow exact same format as hand-crafted stages
- No changes to main_*.py files are needed
- Existing game engine should load generated stages seamlessly

### Performance Notes

- **Generation**: <1 second for simple stages, <5 seconds for special stages
- **Validation**: <5 seconds for most stages, up to 60 seconds for complex special stages
- **Memory**: Minimal - all operations use existing framework patterns

## Next Steps

After generating stages:
1. Test them manually in the framework
2. Add them to student exercise sets
3. Use validation reports to understand difficulty levels
4. Generate variations by changing seeds
5. Create custom stage collections for different learning objectives

---
*Ready to generate and validate stages - see contracts/ for detailed API specifications*