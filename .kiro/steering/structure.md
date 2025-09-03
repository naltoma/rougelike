# Project Structure

## Root Directory Organization
```
rougelike/
├── .kiro/              # Spec-driven development
│   ├── steering/       # Project steering documents
│   └── specs/          # Feature specifications
│       ├── gui-enhancements-v1.1/  # 🆕 v1.1 GUI enhancement spec
│       └── gui-critical-fixes-v1.2.1/  # 🆕 v1.2.1 Critical button fixes spec
├── .claude/            # Claude Code commands
├── docs/               # Project documentation
│   ├── v1.2.1.md       # 🆕 v1.2.1 Critical Fixes documentation
│   ├── v1.1.md         # v1.1 Enhancement documentation
│   └── v0_1st_plan.md  # Original planning documents
├── engine/             # Core game engine (21 files + v1.2.1 critical fixes)
├── stages/             # YAML stage definitions
├── tests/              # Comprehensive test suite (26+ files)
├── temp/               # Temporary files and screenshots
├── main.py             # Entry point (v1.2.1 GUI loop fixes)
├── student_example.py  # Student sample code
├── run_tests.py        # Pytest integration runner
├── conftest.py         # Pytest configuration
├── config.py           # Project configuration
├── requirements.txt    # pip dependencies (pytest integrated)
├── Makefile            # Test automation
└── README.md           # Setup instructions (v1.1 updated)
```

## Subdirectory Structures

### `/engine/` - Core Game Engine (v1.2.1 - GUI Critical Fixes Complete)
```
engine/
├── __init__.py                 # Core data models (9,705 bytes)
├── api.py                      # Student API (61,365 bytes - comprehensive)
├── game_state.py              # Basic game state (8,282 bytes)
├── advanced_game_state.py     # Extended state management (16,151 bytes)
├── main_game_loop.py          # Main loop controller (23,371 bytes)
├── renderer.py                # GUI/CUI rendering (27,533 bytes + v1.1 enhancements)
├── stage_loader.py            # YAML parsing (15,977 bytes)
├── validator.py               # Validation logic (9,446 bytes)
├── commands.py                # Command pattern (12,605 bytes)
├── enemy_system.py            # Enemy AI (20,059 bytes)
├── item_system.py             # Item mechanics (20,535 bytes)
├── educational_errors.py      # Error handling (37,254 bytes)
├── educational_feedback.py    # Learning feedback (31,496 bytes)
├── progress_analytics.py      # Analytics (31,970 bytes)
├── progression.py             # Progress tracking (24,219 bytes)
├── session_logging.py         # Session logs (23,796 bytes)
├── quality_assurance.py       # QA system (28,750 bytes)
├── data_uploader.py           # Google Sheets (24,052 bytes)
├── 🆕 execution_controller.py  # v1.1: Step execution control system
├── 🆕 hyperparameter_manager.py # v1.1: Parameter validation & management
├── 🆕 session_log_manager.py   # v1.1: Enhanced session logging
└── 🆕 action_history_tracker.py # v1.1: Detailed action tracking
```

### `/tests/` - Comprehensive Test Suite (pytest v1.0.1)
```
tests/
├── __init__.py                    # Test package init
├── conftest.py                    # Pytest fixtures (in root)
├── run_tests.py                   # Legacy test runner
├── test_api.py                    # API testing (11,004 bytes)
├── test_commands.py               # Command pattern tests (8,640 bytes)
├── test_comprehensive_integration.py  # Full integration (21,365 bytes)
├── test_data_models.py           # Data model tests (8,464 bytes)
├── test_educational_errors.py    # Error system tests (6,545 bytes)
├── test_educational_feedback.py  # Feedback tests (10,873 bytes)
├── test_enemy_item_systems.py    # Game systems (14,521 bytes)
├── test_game_state_manager.py    # State management (10,531 bytes)
├── test_google_sheets*.py        # Sheets integration tests
├── test_gui_*.py                  # GUI testing suite
├── test_main_game_loop*.py        # Main loop tests
├── test_progress_analytics.py    # Analytics tests (12,287 bytes)
├── test_progression.py           # Progress tests (9,856 bytes)
├── test_quality_assurance.py     # QA tests (10,624 bytes)
├── test_renderer*.py             # Rendering tests
├── test_session_*.py             # Session testing
├── test_stage_loader.py          # Stage loading tests (12,357 bytes)
├── test_validator.py             # Validation tests (10,815 bytes)
├── config/                       # Test configurations
├── data/                         # Test data files
└── test_data/                    # Additional test assets
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
                    ↓                           ↑
                Logger -> Local Files -> [Manual] -> Google Sheets
                
🆕 v1.1 Execution Control Flow:
GUI Events -> ExecutionController -> solve() Function Control -> Step Execution
     ↓              ↓                       ↓
Pause/Resume -> Action History -> Enhanced Session Logging
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

### 🆕 6. v1.1 Interactive Learning (NEW)
- **Step-by-step execution**: GUI-controlled solve() function execution
- **Pre-execution pause**: Learning preparation and code review
- **Visual feedback loop**: Real-time GUI updates during execution
- **Progressive disclosure**: Execution control complexity introduced gradually
- **Error isolation**: Execution problems don't crash the learning environment

### 🔧 7. v1.2.1 GUI Stability & Reliability (CRITICAL FIXES)
- **Button reliability**: Step/Pause/Reset buttons with guaranteed functionality
- **State consistency**: Accurate step counting and action history management
- **System integrity**: Complete reset functionality for learning session restart
- **Execution stability**: Robust continuous and step execution modes
- **Error resilience**: Improved error handling and recovery mechanisms

## Development Workflow
1. **Stage Design**: Create YAML in `/stages/`
2. **Engine Updates**: Modify `/engine/` for new features  
3. **Testing**: Validate with `/tests/` suite
4. **Student API**: Update `/engine/api.py` if needed
5. **Documentation**: Update README.md and `/docs/`

## Testing Strategy (v1.2.1 - pytest + GUI Critical Fixes Validated)
- **Comprehensive Coverage**: 26+ test files covering all 21 engine components (including v1.2.1)
- **Test Success Rate**: 88.9% (23/26 tests passing) - maintained through v1.2.1 fixes
- **pytest Integration**: Full pytest framework with markers and plugins
- **Test Categories**:
  - Unit tests: Isolated component testing
  - Integration tests: Full game flow testing (test_comprehensive_integration.py)
  - GUI tests: pygame rendering tests (marked with @pytest.mark.gui)
  - Session tests: Learning session workflows
  - Google Sheets tests: API integration tests
  - **🔧 v1.2.1 tests**: GUI critical fixes validation, button functionality testing
- **Advanced Features**:
  - Test markers: unit/integration/gui classification
  - Failed test analysis and re-run commands
  - Parallel execution with pytest-xdist
  - Coverage reporting with pytest-cov
  - HTML/JSON test reports
- **Quality Assurance**: Automated quality metrics and test-driven development
- **🔧 v1.2.1 Test Coverage**: Step/Pause/Reset button functionality, execution controller stability