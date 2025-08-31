# Project Structure

## Root Directory Organization
```
rougelike/
├── .kiro/              # Spec-driven development
│   ├── steering/       # Project steering documents
│   └── specs/          # Feature specifications
├── .claude/            # Claude Code commands
├── docs/               # Project documentation
├── engine/             # Core game engine
├── stages/             # YAML stage definitions
├── assets/             # Game assets (sprites, sounds)
├── logs/               # Student progress logs
├── scripts/            # Utility scripts
├── tests/              # Test suite
├── main.py             # Entry point
├── env.yml             # Conda environment
├── requirements.txt    # pip dependencies
└── README.md           # Setup instructions
```

## Subdirectory Structures

### `/engine/` - Core Game Engine
```
engine/
├── __init__.py
├── api.py              # Student-facing API (turn_left, move, etc.)
├── game_state.py       # Game state management
├── renderer.py         # GUI/CUI rendering
├── stage_loader.py     # YAML stage parsing
├── validator.py        # Move validation, collision detection
└── logger.py           # Progress logging
```

### `/stages/` - Stage Definitions
```
stages/
├── stage01.yml         # Move-only (2-3 steps)
├── stage02.yml         # Turn/move (3-4 turns)
├── stage03.yml         # Turn/move + walls (5-10 turns)
├── stage04-08.yml      # Attack + pickup phases
├── stage09-16.yml      # Advanced stages (10x10, enemies, items)
└── random/             # Random generation templates
    ├── R1-movement.yml
    ├── R2-attack.yml
    └── R3-pickup.yml
```

### `/scripts/` - Utility Scripts
```
scripts/
├── upload_logs.py      # Google Sheets upload
├── validate_stages.py  # YAML validation
├── generate_random.py  # Random stage generation
└── analyze_progress.py # Progress analysis
```

## Code Organization Patterns

### Student Interface Pattern
- **Single entry point**: `solve()` function in main.py
- **Immutable API**: Core functions never change signature
- **Progressive disclosure**: New functions introduced by stage
- **Error isolation**: Runtime errors don't crash system

### Engine Architecture Pattern  
- **State machine**: Clear game states (playing, won, failed)
- **Command pattern**: All actions as commands (undo support)
- **Observer pattern**: GUI/CUI both observe game state
- **Strategy pattern**: Different renderers, validators

### Data Flow Pattern
```
Student Code -> API Layer -> Game Engine -> State Update -> Renderer -> Display
                    ↓
                Logger -> Local Files -> [Manual] -> Google Sheets
```

## File Naming Conventions
- **Python modules**: snake_case.py
- **Stage files**: stageNN.yml (zero-padded)
- **Random stages**: R[N]-[theme].yml
- **Log files**: YYYYMMDD_HHMMSS_[student_id].jsonl
- **Asset files**: [category]_[name].[ext] (e.g., enemy_goblin.png)

## Import Organization
```python
# Standard library
import json
import logging
from pathlib import Path

# Third-party
import pygame
import yaml

# Local engine
from engine.api import turn_left, move
from engine.game_state import GameState
from engine.renderer import GuiRenderer, CuiRenderer
```

## Key Architectural Principles

### 1. Educational Focus
- **Simplicity over performance**: Clear code > optimized code
- **Error messages**: Plain Japanese, specific guidance
- **Gradual complexity**: New concepts introduced incrementally

### 2. Dual Interface Support
- **Renderer abstraction**: Same game logic, different displays
- **API consistency**: Identical function calls for GUI/CUI
- **Switch mechanism**: Command line flag or config

### 3. Data-Driven Design
- **YAML configuration**: All stages as external data
- **Validation layers**: Schema validation for YAML
- **Hot reloading**: Stage changes without restart (dev mode)

### 4. Robust Logging
- **Comprehensive tracking**: Every action, attempt, outcome
- **Structured data**: JSON format for analysis
- **Privacy aware**: Configurable anonymization
- **Offline first**: Local storage, optional upload

### 5. Extensible Framework
- **Plugin architecture**: Easy addition of new stage types
- **API versioning**: Backward compatibility for students
- **Modular enemies**: Component-based enemy behaviors
- **Theme support**: Visual customization for different courses

## Development Workflow
1. **Stage Design**: Create YAML in `/stages/`
2. **Engine Updates**: Modify `/engine/` for new features  
3. **Testing**: Validate with `/tests/` suite
4. **Student API**: Update `/engine/api.py` if needed
5. **Documentation**: Update README.md and `/docs/`

## Testing Strategy
- **Unit tests**: Each engine component isolated
- **Integration tests**: Full stage play-through
- **Student code tests**: Common mistake scenarios
- **Performance tests**: Large stage handling
- **API stability tests**: Backward compatibility