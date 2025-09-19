# Implementation Plan: Random Stage Generation System

**Branch**: `001-docs-v1-2` | **Date**: 2025-09-13 | **Spec**: [spec.md](/Users/tnal/2025/lecture/prog1-exe/temp/copy/specs/001-docs-v1-2/spec.md)
**Input**: Feature specification from `/specs/001-docs-v1-2/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → Loaded: Random Stage Generation System
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Project Type: single (Python CLI tool)
   → Structure Decision: Option 1 (single project)
3. Evaluate Constitution Check section below
   → No constitutional violations - simple CLI tool approach
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → Resolved NEEDS CLARIFICATION items from user input
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md
6. Re-evaluate Constitution Check section
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
ランダムステージ生成システム - 5種類のステージタイプ（move, attack, pickup, patrol, special）をシード値で再現可能に生成し、クリア可能性を検証する教育用ツール。既存のYAML形式を維持し、main_*.pyファイルは変更しない制約付き。

## Technical Context
**Language/Version**: Python 3.8+ (existing project standard)
**Primary Dependencies**: PyYAML (YAML parsing), argparse (CLI interface), random (seeded generation)
**Storage**: YAML files in stages/ directory (existing format maintained)
**Testing**: pytest (existing test framework)
**Target Platform**: Cross-platform (Python standard library)
**Project Type**: single - CLI tool with library components
**Performance Goals**: Generate stage in <1 second, validate in <5 seconds
**Constraints**:
- Must use existing YAML format (no new attributes)
- Cannot modify main_*.py files (user exercise files)
- Must maintain backward compatibility with existing stages
- Centralized configuration requirement
**Scale/Scope**: Generate 5 stage types, support unlimited seed values, validate generated stages

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (CLI tool with stage generation library)
- Using framework directly? (yes - Python standard library + PyYAML)
- Single data model? (yes - YAML stage configuration)
- Avoiding patterns? (no Repository/UoW - direct file I/O)

**Architecture**:
- EVERY feature as library? (yes - stage_generator library + CLI interface)
- Libraries listed:
  - stage_generator: Core random generation logic
  - stage_validator: Solvability validation logic
  - yaml_manager: YAML file operations
- CLI per library: generate_stage.py --help/--version/--format
- Library docs: llms.txt format planned? (yes)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? (yes)
- Git commits show tests before implementation? (will verify)
- Order: Contract→Integration→E2E→Unit strictly followed? (yes)
- Real dependencies used? (yes - actual YAML files)
- Integration tests for: new libraries, contract changes, shared schemas? (yes)
- FORBIDDEN: Implementation before test, skipping RED phase (enforced)

**Observability**:
- Structured logging included? (yes - generation and validation logging)
- Frontend logs → backend? (N/A - CLI tool)
- Error context sufficient? (yes - detailed error reporting)

**Versioning**:
- Version number assigned? (v1.2.9)
- BUILD increments on every change? (yes)
- Breaking changes handled? (N/A - new feature, no breaking changes)

## Project Structure

### Documentation (this feature)
```
specs/001-docs-v1-2/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (SELECTED)
src/
├── stage_generator/     # Core generation logic
├── stage_validator/     # Validation logic
├── yaml_manager/        # YAML operations
└── cli/                # CLI interface

tests/
├── contract/           # CLI contract tests
├── integration/        # Cross-component tests
└── unit/              # Individual component tests

# New files to be created:
generate_stage.py       # Main CLI entry point
# Generated stages: stages/generated_[type]_[seed].yml
```

**Structure Decision**: Option 1 (single project) - Simple CLI tool with library components

## Phase 0: Outline & Research

### Research Findings

Based on existing project analysis and user requirements:

**YAML Stage Format Resolution**:
- **Decision**: Use existing YAML format from stages/*.yml files
- **Rationale**: User explicitly specified "既存のYAML形式に則ってください。ステージ設定に新しい属性は追加しないでください"
- **Alternatives considered**: JSON, custom format - rejected due to constraint

**File Storage Location**:
- **Decision**: Generate directly to stages/ directory with naming pattern `generated_[type]_[seed].yml`
- **Rationale**: Simple file structure, clear naming convention prevents conflicts with hand-crafted stages
- **Alternatives considered**: Subdirectory structure - rejected for simplicity

**Validation Script Execution**:
- **Decision**: Integrated validation with --validate flag, separate validate_stage.py script
- **Rationale**: Flexibility for both integrated and standalone validation workflows
- **Alternatives considered**: Auto-validation only - rejected for workflow flexibility

**Unsolvable Stage Handling**:
- **Decision**: Log warning, provide detailed report, continue (don't fail)
- **Rationale**: Educational context - allow analysis of why stage is unsolvable
- **Alternatives considered**: Auto-regenerate - rejected as it may hide generation issues

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts

### Data Model Design

**Key Entities Identified**:
- **StageType**: Enum of 5 types (move, attack, pickup, patrol, special)
- **GenerationParameters**: seed, stage_type, output_path
- **StageConfiguration**: Complete YAML structure matching existing format
- **ValidationResult**: success/failure, path_found, required_apis, error_details

### API Contracts

**CLI Interface**:
```bash
generate_stage.py --type move --seed 123 [--output stages/generated/] [--validate]
validate_stage.py --file stages/stage01.yml [--detailed]
```

**Library Interface**:
```python
# Core generation
def generate_stage(stage_type: StageType, seed: int) -> StageConfiguration
def save_stage(config: StageConfiguration, path: str) -> bool

# Validation
def validate_stage_solvability(stage_path: str) -> ValidationResult
def analyze_solution_path(stage_config: StageConfiguration) -> List[Action]
```

### Integration Strategy

**Phase 1 Components**:
- `stage_generator/` library with type-specific generators
- `stage_validator/` library with pathfinding validation
- `yaml_manager/` for file I/O operations
- CLI wrapper scripts

**Agent Context Update**: Will update CLAUDE.md with stage generation patterns and validation approaches

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load existing stage YAML files as reference templates
- Create type-specific generation modules (5 tasks)
- Generate CLI interface with argparse (2 tasks)
- Create validation pathfinding logic (3 tasks)
- Integration tests for each stage type (5 tasks)
- E2E tests for CLI workflows (3 tasks)

**Ordering Strategy**:
- TDD order: Tests for each component before implementation
- Dependency order: YAML manager → Generators → Validator → CLI
- Mark [P] for parallel execution of independent stage type generators

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md focusing on type-specific generation with existing YAML format compliance

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations identified*

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (via user input)
- [x] Complexity deviations documented (none)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*