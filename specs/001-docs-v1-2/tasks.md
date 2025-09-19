# Tasks: Random Stage Generation System

**Input**: Design documents from `/specs/001-docs-v1-2/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extracted: Python 3.8+, PyYAML, CLI tool with libraries
   → Structure: Single project with src/ and tests/
2. Load optional design documents:
   → data-model.md: StageType, GenerationParameters, StageConfiguration, ValidationResult
   → contracts/: CLI interface, library API contracts
   → research.md: YAML format, pathfinding validation, type-specific generation
3. Generate tasks by category:
   → Setup: project structure, dependencies, linting
   → Tests: contract tests for CLI and library APIs
   → Core: data models, generators, validators, CLI
   → Integration: YAML loading, type-specific generation
   → Polish: unit tests, performance validation, docs
4. Apply task rules:
   → Type-specific generators = mark [P] (different files)
   → CLI commands = sequential (shared argument parsing)
   → Tests before implementation (TDD enforced)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph based on library architecture
7. Create parallel execution examples for generator types
8. Validate task completeness:
   → CLI contracts have tests? YES
   → All entities have models? YES (4 main data classes)
   → All stage types implemented? YES (5 types)
9. Return: SUCCESS (24 tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root (per plan.md)
- CLI scripts at repository root: `generate_stage.py`, `validate_stage.py`
- Generated stages: `stages/generated_[type]_[seed].yml`

## Phase 3.1: Setup

- [ ] T001 Create project structure with src/stage_generator/, src/stage_validator/, src/yaml_manager/, and tests/ directories
- [ ] T002 Add PyYAML dependency to requirements.txt and verify Python 3.8+ compatibility
- [ ] T003 [P] Configure pytest and linting tools (flake8, black) for stage generation system

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### CLI Contract Tests
- [ ] T004 [P] Contract test generate_stage.py CLI arguments in tests/contract/test_generate_stage_cli.py
- [ ] T005 [P] Contract test validate_stage.py CLI arguments in tests/contract/test_validate_stage_cli.py
- [ ] T006 [P] Contract test generate_stage.py output format and file creation in tests/contract/test_generate_output.py
- [ ] T007 [P] Contract test validate_stage.py validation reporting in tests/contract/test_validate_output.py

### Library Contract Tests
- [ ] T008 [P] Contract test stage_generator API in tests/contract/test_generator_api.py
- [ ] T009 [P] Contract test stage_validator API in tests/contract/test_validator_api.py
- [ ] T010 [P] Contract test yaml_manager API in tests/contract/test_yaml_api.py

### Integration Tests
- [ ] T011 [P] Integration test move stage generation and validation in tests/integration/test_move_stages.py
- [ ] T012 [P] Integration test attack stage generation and validation in tests/integration/test_attack_stages.py
- [ ] T013 [P] Integration test pickup stage generation and validation in tests/integration/test_pickup_stages.py
- [ ] T014 [P] Integration test patrol stage generation and validation in tests/integration/test_patrol_stages.py
- [ ] T015 [P] Integration test special stage generation and validation in tests/integration/test_special_stages.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [ ] T016 [P] StageType enumeration and GenerationParameters in src/stage_generator/data_models.py
- [ ] T017 [P] StageConfiguration and related config classes in src/stage_generator/stage_config.py
- [ ] T018 [P] ValidationResult and SolutionPath in src/stage_validator/validation_models.py

### Core Libraries
- [ ] T019 [P] YAML manager with load/save utilities in src/yaml_manager/core.py
- [ ] T020 [P] Move stage generator in src/stage_generator/types/move_generator.py
- [ ] T021 [P] Attack stage generator in src/stage_generator/types/attack_generator.py
- [ ] T022 [P] Pickup stage generator in src/stage_generator/types/pickup_generator.py
- [ ] T023 [P] Patrol stage generator in src/stage_generator/types/patrol_generator.py
- [ ] T024 [P] Special stage generator in src/stage_generator/types/special_generator.py

### Validation System
- [ ] T025 [P] A* pathfinding algorithm in src/stage_validator/pathfinder.py
- [ ] T026 [P] Stage solution analyzer in src/stage_validator/analyzer.py
- [ ] T027 [P] Validation reporter with human-readable output in src/stage_validator/reporter.py

### CLI Implementation
- [ ] T028 generate_stage.py main CLI script with argparse and type selection
- [ ] T029 validate_stage.py main CLI script with file validation and reporting

## Phase 3.4: Integration

- [ ] T030 Stage generator core with type dispatcher in src/stage_generator/core.py
- [ ] T031 Stage validator integration with YAML loading in src/stage_validator/core.py
- [ ] T032 Seed reproducibility validation across all stage types
- [ ] T033 Error handling and logging integration for CLI tools

## Phase 3.5: Polish

- [ ] T034 [P] Unit tests for data model validation in tests/unit/test_data_models.py
- [ ] T035 [P] Unit tests for pathfinding algorithms in tests/unit/test_pathfinding.py
- [ ] T036 [P] Unit tests for YAML serialization in tests/unit/test_yaml_operations.py
- [ ] T037 Performance tests ensuring <1s generation, <5s validation in tests/performance/test_generation_speed.py
- [ ] T038 [P] Update CLAUDE.md with final usage patterns and examples
- [ ] T039 [P] Create llms.txt documentation for stage generator libraries
- [ ] T040 End-to-end test running quickstart.md scenarios in tests/e2e/test_quickstart_scenarios.py

## Dependencies

**Critical Path**:
- Setup (T001-T003) before everything
- Contract tests (T004-T015) before implementation (T016+)
- Data models (T016-T018) before generators/validators (T019+)
- Core libraries (T019-T027) before CLI (T028-T029)
- CLI before integration (T030-T033)
- Implementation before polish (T034-T040)

**Specific Blockers**:
- T016 (data models) blocks T019-T027 (core libraries)
- T019 (YAML manager) blocks T020-T024 (generators) and T025-T027 (validators)
- T020-T024 (all generators) block T030 (core dispatcher)
- T025-T027 (all validators) block T031 (validator integration)
- T028-T029 (CLI scripts) block T033 (error handling integration)

## Parallel Example

```bash
# Launch generator tests together (T011-T015):
Task: "Integration test move stage generation and validation in tests/integration/test_move_stages.py"
Task: "Integration test attack stage generation and validation in tests/integration/test_attack_stages.py"
Task: "Integration test pickup stage generation and validation in tests/integration/test_pickup_stages.py"
Task: "Integration test patrol stage generation and validation in tests/integration/test_patrol_stages.py"
Task: "Integration test special stage generation and validation in tests/integration/test_special_stages.py"

# Launch type-specific generators together (T020-T024):
Task: "Move stage generator in src/stage_generator/types/move_generator.py"
Task: "Attack stage generator in src/stage_generator/types/attack_generator.py"
Task: "Pickup stage generator in src/stage_generator/types/pickup_generator.py"
Task: "Patrol stage generator in src/stage_generator/types/patrol_generator.py"
Task: "Special stage generator in src/stage_generator/types/special_generator.py"

# Launch validation components together (T025-T027):
Task: "A* pathfinding algorithm in src/stage_validator/pathfinder.py"
Task: "Stage solution analyzer in src/stage_validator/analyzer.py"
Task: "Validation reporter with human-readable output in src/stage_validator/reporter.py"
```

## Notes
- [P] tasks = different files, no dependencies between them
- All tests must fail initially (TDD requirement)
- Seed reproducibility critical - same seed + type = identical stage
- YAML format compliance enforced - no new attributes allowed
- Generated files follow pattern: `stages/generated_[type]_[seed].yml`
- Performance targets: <1s generation, <5s validation, 60s max for complex stages

## Task Generation Rules Applied

1. **From Contracts**:
   - CLI interface contract → T004-T007 (CLI tests)
   - Library API contracts → T008-T010 (API tests)

2. **From Data Model**:
   - StageType, GenerationParameters → T016
   - StageConfiguration → T017
   - ValidationResult → T018

3. **From Research/Plan**:
   - 5 stage types → T020-T024 (type-specific generators)
   - A* pathfinding → T025 (pathfinding implementation)
   - YAML compliance → T019 (YAML manager)

4. **From Quickstart**:
   - Usage scenarios → T011-T015 (integration tests)
   - CLI examples → T040 (e2e scenarios)

## Validation Checklist
*GATE: Checked before task execution*

- [x] All contracts have corresponding tests (T004-T010)
- [x] All entities have model tasks (T016-T018)
- [x] All tests come before implementation (T004-T015 before T016+)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All 5 stage types have generators (T020-T024)
- [x] CLI contracts match quickstart examples
- [x] Performance requirements included (T037)

---
*24 tasks generated - ready for TDD implementation following constitutional principles*