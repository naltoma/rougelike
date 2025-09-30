# Tasks: Detrimental Items and Item Management System

**Input**: Design documents from `/specs/004-docs-v1-2/`
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Extract: Python 3.8+, pygame, pytest, educational framework
   → Structure: Single project with engine/ modules
2. Load optional design documents ✓:
   → data-model.md: Item extension, Player HP, Stage completion
   → contracts/: item_management_api.py, stage_generation_api.py
   → research.md: Technical decisions for bomb system
3. Generate tasks by category:
   → Setup: Dependencies already met, linting configuration
   → Tests: Contract tests for APIs, integration tests for workflows
   → Core: Item model extension, HP system, API functions, commands
   → Integration: Stage completion logic, script updates
   → Polish: End-to-end tests, performance validation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Tests before implementation (TDD enforced)
   → Educational constraint: Preserve main_*.py files
5. Number tasks sequentially (T001-T024)
6. Dependencies: Models → Commands → APIs → Integration → Scripts
7. SUCCESS: 24 tasks ready for TDD execution
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup
- [ ] T001 [P] Configure pytest coverage for bomb item system in pytest.ini
- [ ] T002 [P] Update requirements.txt if needed for v1.2.12 dependencies

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] T003 [P] Contract test is_available() function in tests/contract/test_item_management_api.py
- [ ] T004 [P] Contract test dispose() function in tests/contract/test_item_management_api.py
- [ ] T005 [P] Contract test stage generation with bombs in tests/contract/test_stage_generation_api.py
- [ ] T006 [P] Contract test stage validation with bombs in tests/contract/test_stage_generation_api.py

### Model Extension Tests
- [ ] T007 [P] Item model damage attribute tests in tests/unit/test_item_model.py
- [ ] T008 [P] Player HP system tests in tests/unit/test_player_hp.py
- [ ] T009 [P] DisposeCommand tests in tests/unit/test_dispose_command.py

### Integration Tests
- [ ] T010 [P] Stage completion with disposed items tests in tests/integration/test_stage_completion.py
- [ ] T011 [P] HP damage from bomb pickup tests in tests/integration/test_bomb_damage.py
- [ ] T012 [P] End-to-end bomb workflow tests in tests/integration/test_bomb_workflow.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Model Extensions
- [ ] T013 [P] Extend Item class with damage attribute in engine/__init__.py
- [ ] T014 [P] Add HP tracking to Player/GameState in engine/game_state.py
- [ ] T015 [P] Create DisposeCommand class in engine/commands.py

### API Layer Implementation
- [ ] T016 Add is_available() function to API layer in engine/api.py
- [ ] T017 Add dispose() function to API layer in engine/api.py
- [ ] T018 Update global API exports for new functions in engine/api.py

### Core Logic Implementation
- [ ] T019 Implement bomb damage logic in pickup command in engine/commands.py
- [ ] T020 Update stage completion logic for disposed items in engine/validator.py

## Phase 3.4: Integration & Scripts
- [ ] T021 [P] Update generate_stage.py to include bomb items in scripts/generate_stage.py
- [ ] T022 [P] Update validate_stage.py to use is_available() and dispose() in scripts/validate_stage.py

## Phase 3.5: Validation & Polish
- [ ] T023 Create test bomb stage file in stages/test_bomb_stage.yml
- [ ] T024 Run complete quickstart validation sequence per quickstart.md

## Dependencies
- Tests (T003-T012) before implementation (T013-T022)
- T013 (Item extension) blocks T016, T017, T019
- T014 (HP system) blocks T011, T019
- T015 (DisposeCommand) blocks T017
- T016, T017 (API functions) block T018
- T020 (completion logic) requires T013, T014
- Scripts (T021, T022) require T016, T017
- Validation (T023, T024) requires all implementation complete

## Parallel Example
```
# Launch contract tests together (Phase 3.2):
Task: "Contract test is_available() function in tests/contract/test_item_management_api.py"
Task: "Contract test dispose() function in tests/contract/test_item_management_api.py"
Task: "Contract test stage generation with bombs in tests/contract/test_stage_generation_api.py"
Task: "Contract test stage validation with bombs in tests/contract/test_stage_generation_api.py"

# Launch model tests together:
Task: "Item model damage attribute tests in tests/unit/test_item_model.py"
Task: "Player HP system tests in tests/unit/test_player_hp.py"
Task: "DisposeCommand tests in tests/unit/test_dispose_command.py"

# Launch model implementations together (after tests fail):
Task: "Extend Item class with damage attribute in engine/__init__.py"
Task: "Add HP tracking to Player/GameState in engine/game_state.py"
Task: "Create DisposeCommand class in engine/commands.py"

# Launch script updates together:
Task: "Update generate_stage.py to include bomb items in scripts/generate_stage.py"
Task: "Update validate_stage.py to use is_available() and dispose() in scripts/validate_stage.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing (TDD)
- Preserve existing main_*.py files (educational constraint)
- Follow existing code patterns and conventions
- Commit after each task completion
- HP system default: 100 HP, bomb default damage: 100

## File Path Map
```
Core Files (Sequential - same file modifications):
├── engine/__init__.py        # T013 (Item extension)
├── engine/game_state.py      # T014 (HP system)
├── engine/commands.py        # T015 (DisposeCommand), T019 (bomb damage)
├── engine/api.py            # T016, T017, T018 (API functions)
└── engine/validator.py      # T020 (completion logic)

Test Files (Parallel - different files):
├── tests/contract/test_item_management_api.py     # T003, T004
├── tests/contract/test_stage_generation_api.py    # T005, T006
├── tests/unit/test_item_model.py                  # T007
├── tests/unit/test_player_hp.py                   # T008
├── tests/unit/test_dispose_command.py              # T009
├── tests/integration/test_stage_completion.py     # T010
├── tests/integration/test_bomb_damage.py           # T011
└── tests/integration/test_bomb_workflow.py         # T012

Script Files (Parallel - different files):
├── scripts/generate_stage.py                      # T021
└── scripts/validate_stage.py                      # T022

Configuration/Data Files (Parallel):
├── pytest.ini                                     # T001
├── requirements.txt                                # T002
└── stages/test_bomb_stage.yml                     # T023
```

## Task Generation Rules Applied
1. **From Contracts**: item_management_api.py → T003, T004, T016, T017; stage_generation_api.py → T005, T006, T021, T022
2. **From Data Model**: Item extension → T007, T013; Player HP → T008, T014; Stage completion → T010, T020
3. **From User Stories**: quickstart.md scenarios → T011, T012, T024
4. **Ordering**: Setup → Tests → Models → Services → APIs → Integration → Validation

## Validation Checklist
- [x] All contracts have corresponding tests (T003-T006)
- [x] All entities have model tasks (T007-T009, T013-T015)
- [x] All tests come before implementation (Phase 3.2 → 3.3)
- [x] Parallel tasks truly independent ([P] tasks use different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task