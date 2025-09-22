# Tasks: GUI Dynamic Display Enhancement v1.2.11

**Input**: Design documents from `/specs/003-docs-v1-2/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → ✅ Implementation plan loaded: Python 3.11, pygame, educational framework enhancement
   → ✅ Extract: tech stack (pygame, pathlib, typing), structure (single project)
2. Load optional design documents:
   → ✅ data-model.md: Extract entities (StatusChangeTracker, StageNameResolver, DisplayStateManager)
   → ✅ contracts/: 3 contract files → 3 contract test tasks
   → ✅ research.md: Extract decisions → pygame rendering, importlib module loading
3. Generate tasks by category:
   → Setup: project structure, dependencies, linting
   → Tests: contract tests, integration tests from quickstart scenarios
   → Core: models (3 entities), services, CLI commands
   → Integration: renderer enhancement, logging
   → Polish: unit tests, performance, validation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → ✅ All contracts have tests
   → ✅ All entities have models
   → ✅ All quickstart scenarios covered
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `engine/`, `tests/` at repository root (following existing structure)
- Paths shown below follow existing codebase structure under `/Users/tnal/2025/lecture/prog1-exe/rougelike/`

## Phase 3.1: Setup
- [ ] T001 Create project structure for GUI enhancement libraries in engine/gui_enhancement/
- [ ] T002 Initialize Python modules with proper imports for pygame and typing dependencies
- [ ] T003 [P] Configure linting validation for new modules (if not already configured)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (Parallel - Different Files)
- [ ] T004 [P] Contract test StatusChangeTracker.track_changes() in tests/contract/test_status_change_tracker_contract.py
- [ ] T005 [P] Contract test StageNameResolver.resolve_stage_name() in tests/contract/test_stage_name_resolver_contract.py
- [ ] T006 [P] Contract test DisplayStateManager.format_status_text() in tests/contract/test_display_state_manager_contract.py

### Integration Tests from Quickstart Scenarios (Parallel - Different Files)
- [ ] T007 [P] Integration test dynamic stage name display in tests/integration/test_stage_name_display.py
- [ ] T008 [P] Integration test status decrease highlighting (red bold ↓) in tests/integration/test_status_decrease_highlighting.py
- [ ] T009 [P] Integration test status increase highlighting (green bold ↑) in tests/integration/test_status_increase_highlighting.py
- [ ] T010 [P] Integration test multiple entity status tracking in tests/integration/test_multiple_entity_status.py
- [ ] T011 [P] Integration test no change default formatting in tests/integration/test_no_change_formatting.py

### GUI Integration Tests (Parallel - Different Files)
- [ ] T012 [P] Integration test renderer enhancement with status highlighting in tests/integration/test_gui_renderer_enhancement.py
- [ ] T013 [P] Integration test pygame text rendering with colors/bold in tests/integration/test_pygame_text_rendering.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Core Entities (Parallel - Different Files)
- [ ] T014 [P] StatusChangeTracker model in engine/gui_enhancement/status_change_tracker.py
- [ ] T015 [P] StageNameResolver model in engine/gui_enhancement/stage_name_resolver.py
- [ ] T016 [P] DisplayStateManager model in engine/gui_enhancement/display_state_manager.py

### Supporting Types and Configs (Parallel - Different Files)
- [ ] T017 [P] EmphasisType enum and ColorConfig dataclass in engine/gui_enhancement/display_types.py
- [ ] T018 [P] FormattedText and ChangeResult dataclasses in engine/gui_enhancement/data_types.py

### CLI Commands for Libraries (Parallel - Different Files)
- [ ] T019 [P] CLI command for status_tracker --format json in engine/gui_enhancement/cli/status_tracker_cli.py
- [ ] T020 [P] CLI command for stage_name_resolver --validate in engine/gui_enhancement/cli/stage_name_resolver_cli.py

### Renderer Integration (Sequential - Same File Modifications)
- [ ] T021 Extend GuiRenderer class in engine/renderer.py to integrate StatusChangeTracker
- [ ] T022 Add stage name resolution to GuiRenderer class in engine/renderer.py
- [ ] T023 Add status change highlighting to GuiRenderer class in engine/renderer.py

### Error Handling and Logging
- [ ] T024 Add structured logging for status change events and stage name resolution in engine/gui_enhancement/logging.py
- [ ] T025 Add error handling for missing STAGE_ID and file reading errors in existing modules

## Phase 3.4: Integration

### Module Integration
- [ ] T026 Integrate StatusChangeTracker with existing GameState in engine/main_game_loop.py
- [ ] T027 Integrate StageNameResolver with stage loading system in engine/stage_loader.py
- [ ] T028 Update GUI initialization to include enhancement modules in main.py

### Performance Optimization
- [ ] T029 Add caching for stage name resolution to maintain 60 FPS performance
- [ ] T030 Optimize status change detection for <50ms response time requirement

## Phase 3.5: Polish

### Unit Tests (Parallel - Different Files)
- [ ] T031 [P] Unit tests for EmphasisType logic in tests/unit/test_emphasis_type.py
- [ ] T032 [P] Unit tests for color configuration validation in tests/unit/test_color_config.py
- [ ] T033 [P] Unit tests for stage ID validation patterns in tests/unit/test_stage_id_validation.py

### Performance and Edge Case Tests (Parallel - Different Files)
- [ ] T034 [P] Performance tests for 60 FPS rendering with status changes in tests/performance/test_rendering_performance.py
- [ ] T035 [P] Edge case tests for missing STAGE_ID handling in tests/edge_cases/test_missing_stage_id.py
- [ ] T036 [P] Edge case tests for invalid status values in tests/edge_cases/test_invalid_status_values.py

### Documentation and Validation
- [ ] T037 [P] Update library documentation in llms.txt format for status_tracker and stage_name_resolver
- [ ] T038 Execute quickstart.md validation scenarios manually
- [ ] T039 Remove any code duplication and refactor for maintainability

## Dependencies

### Critical TDD Dependencies
- Tests (T004-T013) MUST complete and FAIL before implementation (T014-T030)
- T014 (StatusChangeTracker) blocks T021, T026
- T015 (StageNameResolver) blocks T022, T027
- T016 (DisplayStateManager) blocks T023
- T017-T018 (Supporting types) blocks T014-T016
- T021-T023 (Renderer integration) blocks T028
- Implementation before polish (T031-T039)

### File Dependencies
- T021, T022, T023 are sequential (same file: engine/renderer.py)
- T026, T027, T028 require T014-T016 completion
- T029, T030 require T021-T023 completion

## Parallel Execution Examples

### Contract Tests Phase (T004-T006)
```bash
# Launch T004-T006 together:
Task: "Contract test StatusChangeTracker.track_changes() in tests/contract/test_status_change_tracker_contract.py"
Task: "Contract test StageNameResolver.resolve_stage_name() in tests/contract/test_stage_name_resolver_contract.py"
Task: "Contract test DisplayStateManager.format_status_text() in tests/contract/test_display_state_manager_contract.py"
```

### Integration Tests Phase (T007-T013)
```bash
# Launch T007-T013 together:
Task: "Integration test dynamic stage name display in tests/integration/test_stage_name_display.py"
Task: "Integration test status decrease highlighting in tests/integration/test_status_decrease_highlighting.py"
Task: "Integration test status increase highlighting in tests/integration/test_status_increase_highlighting.py"
Task: "Integration test multiple entity status tracking in tests/integration/test_multiple_entity_status.py"
Task: "Integration test no change default formatting in tests/integration/test_no_change_formatting.py"
Task: "Integration test renderer enhancement with status highlighting in tests/integration/test_gui_renderer_enhancement.py"
Task: "Integration test pygame text rendering with colors/bold in tests/integration/test_pygame_text_rendering.py"
```

### Core Entities Phase (T014-T018)
```bash
# Launch T014-T018 together:
Task: "StatusChangeTracker model in engine/gui_enhancement/status_change_tracker.py"
Task: "StageNameResolver model in engine/gui_enhancement/stage_name_resolver.py"
Task: "DisplayStateManager model in engine/gui_enhancement/display_state_manager.py"
Task: "EmphasisType enum and ColorConfig dataclass in engine/gui_enhancement/display_types.py"
Task: "FormattedText and ChangeResult dataclasses in engine/gui_enhancement/data_types.py"
```

### CLI Commands Phase (T019-T020)
```bash
# Launch T019-T020 together:
Task: "CLI command for status_tracker --format json in engine/gui_enhancement/cli/status_tracker_cli.py"
Task: "CLI command for stage_name_resolver --validate in engine/gui_enhancement/cli/stage_name_resolver_cli.py"
```

### Unit Tests Phase (T031-T036)
```bash
# Launch T031-T036 together:
Task: "Unit tests for EmphasisType logic in tests/unit/test_emphasis_type.py"
Task: "Unit tests for color configuration validation in tests/unit/test_color_config.py"
Task: "Unit tests for stage ID validation patterns in tests/unit/test_stage_id_validation.py"
Task: "Performance tests for 60 FPS rendering in tests/performance/test_rendering_performance.py"
Task: "Edge case tests for missing STAGE_ID in tests/edge_cases/test_missing_stage_id.py"
Task: "Edge case tests for invalid status values in tests/edge_cases/test_invalid_status_values.py"
```

## Notes
- [P] tasks = different files, no dependencies between them
- Verify ALL tests fail before implementing ANY code (TDD requirement)
- Commit after each task completion
- No modifications to main_*.py files (user exercise files)
- Maintain 60 FPS performance and <50ms response times

## Task Generation Rules Applied

1. **From Contracts**: 3 contract files → 3 contract test tasks [P] (T004-T006)
2. **From Data Model**: 3 entities → 3 model creation tasks [P] (T014-T016)
3. **From Quickstart Scenarios**: 5 scenarios → 7 integration tests [P] (T007-T013)
4. **Ordering**: Setup → Tests → Models → Services → Integration → Polish
5. **Dependencies**: Tests before implementation, models before services

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T004-T006)
- [x] All entities have model tasks (T014-T016)
- [x] All tests come before implementation (T004-T013 before T014+)
- [x] Parallel tasks truly independent (different files marked [P])
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Quickstart scenarios covered (T007-T013, T038)
- [x] CLI commands for libraries included (T019-T020)
- [x] Performance requirements addressed (T029-T030, T034)
- [x] Error handling and edge cases covered (T024-T025, T035-T036)