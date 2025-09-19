# Research: Random Stage Generation System

## Overview
Research conducted to resolve NEEDS CLARIFICATION items from the feature specification and understand technical requirements for implementing a random stage generation system.

## Research Questions Resolved

### 1. Stage Storage Format
**Question**: どの形式で保存するか？JSON、Python、独自形式？

**Decision**: YAML format (.yml extension)
**Rationale**:
- User explicitly specified "ステージファイルは既存のYAML形式に則ってください"
- Existing stages use .yml format (stages/stage01.yml through stage13.yml)
- Maintains consistency with hand-crafted stages
- PyYAML library provides robust parsing and generation
**Alternatives considered**:
- JSON: Rejected - breaks consistency with existing stages
- Python: Rejected - not suitable for configuration data
- Custom format: Rejected - adds unnecessary complexity

### 2. Validation Script Execution Method
**Question**: 自動実行か手動実行か？生成と同時に実行されるか？

**Decision**: Flexible approach with both options
**Rationale**:
- `--validate` flag in generate_stage.py for integrated validation
- Separate `validate_stage.py` script for standalone validation
- Supports both developer workflows (quick generation + validation, detailed analysis)
**Alternatives considered**:
- Auto-only: Rejected - reduces flexibility for debugging
- Manual-only: Rejected - slows down typical workflow

### 3. File Naming and Storage Location
**Question**: ファイル名規則や保存場所は？

**Decision**: `stages/generated/generated_[type]_[seed].yml`
**Rationale**:
- Separate subdirectory avoids conflicts with hand-crafted stages
- Clear naming convention indicates generated nature
- Type and seed in filename enables easy identification
- Follows existing project structure patterns
**Alternatives considered**:
- Direct to stages/: Rejected - potential filename conflicts
- Timestamped names: Rejected - seed reproducibility is more important

### 4. Unsolvable Stage Handling
**Question**: 再生成するか、エラーとするか、ログのみか？

**Decision**: Log detailed warning, continue (don't fail)
**Rationale**:
- Educational context - teachers may want to analyze why stage is unsolvable
- Provides detailed report about failed pathfinding attempts
- Allows manual inspection and learning from generation issues
- Non-blocking workflow for batch generation
**Alternatives considered**:
- Auto-regenerate: Rejected - may hide fundamental generation issues
- Hard error: Rejected - breaks batch processing workflows

## Technical Analysis

### Existing YAML Structure Analysis
Based on stages/stage01.yml and stages/stage13.yml analysis:

**Core Structure**:
```yaml
id: stage_id
title: Display title
description: Learning objectives
board:
  size: [width, height]
  grid: [row_strings]
  legend: {char: meaning}
player:
  start: [x, y]
  direction: N/S/E/W
  hp: integer (optional, defaults to 100)
  max_hp: integer (optional)
  attack_power: integer (optional, defaults to 30)
goal:
  position: [x, y]
enemies: [list_of_enemy_objects]
items: [list_of_item_objects]
constraints:
  max_turns: integer
  allowed_apis: [api_list]
```

**Advanced Features** (from stage13.yml):
- Large enemies (2x2, 3x3, 2x3)
- Special behaviors and conditions
- Learning objectives and hints
- Victory conditions
- Error handling configurations

### Stage Type Requirements

**move** (stages 01-03 equivalent):
- Basic navigation with walls
- Simple grid layouts (5x5 to 8x8)
- APIs: turn_left, turn_right, move, see
- No enemies or items

**attack** (stages 04-06 equivalent):
- Enemy combat scenarios
- Enemies with varying HP levels
- APIs: + attack
- Strategic positioning elements

**pickup** (stages 07-09 equivalent):
- Item collection mechanics
- Mixed combat and collection
- APIs: + pickup
- Resource management scenarios

**patrol** (stage 10 equivalent):
- Moving enemies with patrol patterns
- Stealth and avoidance mechanics
- APIs: + wait
- AI behavior prediction

**special** (stages 11-13 equivalent):
- Large enemies (2x2, 3x3, 2x3)
- Complex special conditions
- Advanced AI behaviors
- All APIs available

### Generation Algorithm Requirements

**Core Principles**:
1. **Seeded Randomness**: Same seed + type = identical stage
2. **Solvability**: Must be completable with allowed APIs
3. **Progressive Difficulty**: Each type builds on previous capabilities
4. **Format Compliance**: No new YAML attributes, existing structure only

**Pathfinding Validation**:
- A* or BFS pathfinding from start to goal
- Respect wall obstacles and enemy positions
- Validate required API usage (e.g., attack for enemy stages)
- Report detailed failure reasons

### Dependencies and Integration

**Required Libraries**:
- `pyyaml`: YAML parsing and generation (existing dependency)
- `argparse`: CLI interface (Python standard library)
- `random`: Seeded random generation (Python standard library)
- `pathlib`: File path operations (Python standard library)

**Integration Points**:
- Existing stage loading system in `engine/stage_loader.py`
- Test framework integration with pytest
- No modifications to main_*.py files (user exercise files)

## Implementation Strategy

### Library Architecture
```
stage_generator/
├── __init__.py           # Public API
├── core.py              # Base generation logic
├── types/               # Type-specific generators
│   ├── move_generator.py
│   ├── attack_generator.py
│   ├── pickup_generator.py
│   ├── patrol_generator.py
│   └── special_generator.py
└── utils.py            # Helper functions

stage_validator/
├── __init__.py         # Public API
├── pathfinder.py      # A* pathfinding algorithm
├── analyzer.py        # Solution analysis
└── reporter.py        # Validation reporting

yaml_manager/
├── __init__.py        # Public API
├── loader.py          # YAML loading utilities
├── saver.py           # YAML saving utilities
└── validator.py       # Schema validation
```

### CLI Interface Design
```bash
# Primary generation command
generate_stage.py --type move --seed 123
generate_stage.py --type attack --seed 456 --validate
generate_stage.py --type special --seed 789 --output custom/path/

# Standalone validation
validate_stage.py --file stages/stage01.yml
validate_stage.py --file stages/generated/generated_move_123.yml --detailed
```

## Risk Analysis

**Low Risk**:
- YAML format compliance (well-defined existing structure)
- Seeded randomness (standard library support)
- File I/O operations (existing patterns in project)

**Medium Risk**:
- Pathfinding validation complexity (A* implementation needed)
- Large enemy generation logic (complex spatial constraints)
- Ensuring solvability across all generated stages

**Mitigation Strategies**:
- Start with simple stage types (move) and progressively add complexity
- Comprehensive test coverage for each stage type
- Detailed validation reporting for debugging generation issues
- Reference existing hand-crafted stages as templates

## Success Criteria

**Functional Success**:
- Generate 5 stage types with seed reproducibility
- 100% format compliance with existing YAML structure
- Solvability validation with detailed reporting
- CLI interface matching specified command patterns

**Quality Success**:
- Test coverage >90% for generation and validation logic
- Performance <1s generation, <5s validation
- No modifications to existing main_*.py files
- Integration with existing pytest framework

---
*Research complete - ready for Phase 1 design and contracts*