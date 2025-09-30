# Tasks: A*アルゴリズムとゲームエンジン動作差異修正

**Input**: Design documents from `/specs/005-docs-v1-2/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

## Phase 3.1: Setup
- [ ] T001 Create src/stage_validator/ directory structure for state comparison library
- [ ] T002 Initialize Python module with __init__.py files in src/stage_validator/ and tests/ directories
- [ ] T003 [P] Configure pytest for test discovery in existing framework

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Contract test for StateValidator interface in tests/contract/test_state_validator_contract.py
- [ ] T005 [P] Contract test for ExecutionEngine interface in tests/contract/test_execution_engine_contract.py
- [ ] T006 [P] Contract test for UnifiedEnemyAI interface in tests/contract/test_unified_enemy_ai_contract.py
- [ ] T007 [P] Integration test for A* vs game engine comparison in tests/integration/test_engine_comparison.py
- [ ] T008 [P] Integration test for enemy behavior synchronization in tests/integration/test_enemy_ai_sync.py
- [ ] T009 [P] Integration test for solution validation workflow in tests/integration/test_solution_validation.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T010 [P] ExecutionLog data model in src/stage_validator/models/execution_log.py
- [ ] T011 [P] EnemyState data model in src/stage_validator/models/enemy_state.py
- [ ] T012 [P] SolutionPath data model in src/stage_validator/models/solution_path.py
- [ ] T013 [P] StateDifference data model in src/stage_validator/models/state_difference.py
- [ ] T014 [P] ValidationConfig data model in src/stage_validator/models/validation_config.py
- [ ] T015 StateValidator implementation in src/stage_validator/state_validator.py
- [ ] T016 ExecutionEngine base implementation in src/stage_validator/execution_engine.py
- [ ] T017 AStarEngine wrapper implementation in src/stage_validator/astar_engine.py
- [ ] T018 GameEngineWrapper implementation in src/stage_validator/game_engine_wrapper.py
- [ ] T019 UnifiedEnemyAI implementation in src/stage_validator/unified_enemy_ai.py

## Phase 3.4: Integration
- [ ] T020 State comparison logic integration in src/stage_validator/state_validator.py
- [ ] T021 Enemy behavior synchronization integration in src/stage_validator/unified_enemy_ai.py
- [ ] T022 CLI extension for validate_stage.py --compare-engines flag
- [ ] T023 Debug logging and difference reporting in src/stage_validator/debug_logger.py
- [ ] T024 Configuration management for unified settings in src/stage_validator/config_manager.py

## Phase 3.5: Polish
- [ ] T025 [P] Unit tests for ExecutionLog validation in tests/unit/test_execution_log.py
- [ ] T026 [P] Unit tests for EnemyState transitions in tests/unit/test_enemy_state.py
- [ ] T027 [P] Unit tests for state comparison logic in tests/unit/test_state_comparison.py
- [ ] T028 [P] Performance test for large stage validation (<1 second) in tests/performance/test_validation_speed.py
- [ ] T029 [P] Update quickstart.md with actual CLI commands and examples
- [ ] T030 [P] Add error handling and edge case coverage in existing modules
- [ ] T031 Run quickstart.md validation workflow end-to-end
- [ ] T032 Clean up code duplication and refactor shared utilities

## Dependencies
- Tests (T004-T009) before implementation (T010-T024)
- Models (T010-T014) before services (T015-T019)
- Core services before integration (T020-T024)
- Implementation before polish (T025-T032)

## Parallel Example
```
# Launch T004-T006 together (contract tests):
Task: "Contract test for StateValidator interface in tests/contract/test_state_validator_contract.py"
Task: "Contract test for ExecutionEngine interface in tests/contract/test_execution_engine_contract.py"
Task: "Contract test for UnifiedEnemyAI interface in tests/contract/test_unified_enemy_ai_contract.py"

# Launch T007-T009 together (integration tests):
Task: "Integration test for A* vs game engine comparison in tests/integration/test_engine_comparison.py"
Task: "Integration test for enemy behavior synchronization in tests/integration/test_enemy_ai_sync.py"
Task: "Integration test for solution validation workflow in tests/integration/test_solution_validation.py"

# Launch T010-T014 together (data models):
Task: "ExecutionLog data model in src/stage_validator/models/execution_log.py"
Task: "EnemyState data model in src/stage_validator/models/enemy_state.py"
Task: "SolutionPath data model in src/stage_validator/models/solution_path.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- main_*.py files are protected - do not modify
- All settings must be centralized in ValidationConfig
- Preserve existing API compatibility

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - StateValidator contract → T004 contract test + T015 implementation
   - ExecutionEngine contract → T005 contract test + T016-T018 implementations
   - UnifiedEnemyAI contract → T006 contract test + T019 implementation

2. **From Data Model**:
   - ExecutionLog entity → T010 model creation task [P]
   - EnemyState entity → T011 model creation task [P]
   - SolutionPath entity → T012 model creation task [P]
   - StateDifference entity → T013 model creation task [P]
   - ValidationConfig entity → T014 model creation task [P]

3. **From User Stories**:
   - State comparison story → T007 integration test [P]
   - Enemy AI sync story → T008 integration test [P]
   - Solution validation story → T009 integration test [P]
   - Quickstart scenarios → T031 validation task

4. **Ordering**:
   - Setup → Tests → Models → Services → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T004-T006)
- [x] All entities have model tasks (T010-T014)
- [x] All tests come before implementation (T004-T009 before T010+)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Main constraint respected (no main_*.py modifications)
- [x] Configuration centralization enforced